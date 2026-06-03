import hashlib
from datetime import datetime, timedelta
from typing import Optional

import feedparser
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import NewsItem, NewsStockMapping
from app.feeds import FEED_SOURCES
from app.mapper import extract_tickers_from_text, classify_item
from app.config import settings


async def fetch_and_parse_feed(feed_config: dict) -> list[dict]:
    """Fetch and parse a single RSS feed."""
    try:
        feed = feedparser.parse(feed_config["url"])
        items = []
        for entry in feed.entries[:20]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            description = entry.get("description", entry.get("summary", "")).strip()

            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    pub_date = datetime(*entry.published_parsed[:6])
                except (TypeError, ValueError):
                    pass

            if not pub_date and hasattr(entry, "updated_parsed") and entry.updated_parsed:
                try:
                    pub_date = datetime(*entry.updated_parsed[:6])
                except (TypeError, ValueError):
                    pass

            items.append({
                "title": title,
                "link": link,
                "teaser": _clean_html(description)[:500] if description else "",
                "published_at": pub_date,
                "source": feed_config["name"],
                "feed_type": feed_config["type"],
            })
        return items
    except Exception as e:
        print(f"Error fetching feed {feed_config['name']}: {e}")
        return []


def _clean_html(html: str) -> str:
    clean = re.sub(r"<[^>]+>", "", html)
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


import re


def compute_dedupe_key(title: str, link: str) -> str:
    content = f"{title}|{link}"
    return hashlib.sha256(content.encode()).hexdigest()


async def ingest_feeds(db: AsyncSession) -> dict:
    """Fetch all feeds, parse, dedupe, map, and store."""
    stats = {"fetched": 0, "new": 0, "duplicates": 0, "errors": 0}

    for feed_config in FEED_SOURCES:
        try:
            items = await fetch_and_parse_feed(feed_config)
            stats["fetched"] += len(items)

            for item in items:
                if not item["title"] or not item["link"]:
                    stats["errors"] += 1
                    continue

                existing = await db.execute(
                    select(NewsItem).where(NewsItem.link == item["link"])
                )
                if existing.scalar_one_or_none():
                    stats["duplicates"] += 1
                    continue

                combined_text = f"{item['title']} {item['teaser']}"
                tickers_found = extract_tickers_from_text(combined_text)
                category = classify_item(tickers_found, item["feed_type"])

                news = NewsItem(
                    title=item["title"],
                    link=item["link"],
                    teaser=item["teaser"],
                    published_at=item["published_at"],
                    source=item["source"],
                    category=category,
                )
                db.add(news)
                await db.flush()

                for t in tickers_found:
                    mapping = NewsStockMapping(
                        news_id=news.id,
                        ticker=t["ticker"],
                        confidence=t["confidence"],
                    )
                    db.add(mapping)

                stats["new"] += 1

            await db.commit()

        except Exception as e:
            stats["errors"] += 1
            print(f"Error processing feed {feed_config['name']}: {e}")
            await db.rollback()

    return stats


async def cleanup_old_items(db: AsyncSession) -> int:
    """Delete news items older than retention period."""
    cutoff = datetime.utcnow() - timedelta(days=settings.NEWS_RETENTION_DAYS)

    result = await db.execute(
        delete(NewsStockMapping).where(
            NewsStockMapping.news_id.in_(
                select(NewsItem.id).where(NewsItem.created_at < cutoff)
            )
        )
    )
    await db.execute(
        delete(NewsItem).where(NewsItem.created_at < cutoff)
    )
    await db.commit()
    return result.rowcount
