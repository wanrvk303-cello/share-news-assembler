from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import NewsItem, NewsStockMapping, Holding
from app.schemas import NewsItemResponse, NewsListResponse

router = APIRouter()


async def _get_news_with_tickers(db: AsyncSession, query, limit: int = 50, offset: int = 0):
    result = await db.execute(query.offset(offset).limit(limit))
    items = result.scalars().all()

    response_items = []
    for item in items:
        mapping_result = await db.execute(
            select(NewsStockMapping.ticker).where(NewsStockMapping.news_id == item.id)
        )
        tickers = [row[0] for row in mapping_result.all()]
        response_items.append(
            NewsItemResponse(
                id=item.id,
                title=item.title,
                link=item.link,
                teaser=item.teaser,
                published_at=item.published_at,
                source=item.source,
                category=item.category,
                tickers=tickers,
            )
        )
    return response_items


@router.get("/news/personal/{user_id}", response_model=NewsListResponse)
async def get_personal_news(
    user_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    age_filter: str = Query("all", regex="^(24h|7d|all)$"),
    db: AsyncSession = Depends(get_db),
):
    holdings_result = await db.execute(
        select(Holding.ticker).where(Holding.user_id == user_id)
    )
    user_tickers = [row[0] for row in holdings_result.all()]

    if not user_tickers:
        return NewsListResponse(items=[], total=0, page=page, page_size=page_size)

    ticker_subquery = (
        select(NewsStockMapping.news_id)
        .where(NewsStockMapping.ticker.in_(user_tickers))
        .distinct()
    )

    query = select(NewsItem).where(NewsItem.id.in_(ticker_subquery))

    if age_filter == "24h":
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        query = query.where(NewsItem.created_at >= cutoff)
    elif age_filter == "7d":
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=7)
        query = query.where(NewsItem.created_at >= cutoff)

    query = query.order_by(NewsItem.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    items = await _get_news_with_tickers(db, query, limit=page_size, offset=offset)

    return NewsListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/news/stock/{ticker}", response_model=NewsListResponse)
async def get_stock_news(
    ticker: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    age_filter: str = Query("all", regex="^(24h|7d|all)$"),
    db: AsyncSession = Depends(get_db),
):
    ticker_upper = ticker.upper()

    ticker_subquery = (
        select(NewsStockMapping.news_id)
        .where(NewsStockMapping.ticker == ticker_upper)
        .distinct()
    )

    query = select(NewsItem).where(NewsItem.id.in_(ticker_subquery))

    if age_filter == "24h":
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        query = query.where(NewsItem.created_at >= cutoff)
    elif age_filter == "7d":
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=7)
        query = query.where(NewsItem.created_at >= cutoff)

    query = query.order_by(NewsItem.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    items = await _get_news_with_tickers(db, query, limit=page_size, offset=offset)

    return NewsListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/news/market", response_model=NewsListResponse)
async def get_market_news(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    age_filter: str = Query("all", regex="^(24h|7d|all)$"),
    db: AsyncSession = Depends(get_db),
):
    query = select(NewsItem).where(NewsItem.category == "market_wide")

    if age_filter == "24h":
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(hours=24)
        query = query.where(NewsItem.created_at >= cutoff)
    elif age_filter == "7d":
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=7)
        query = query.where(NewsItem.created_at >= cutoff)

    query = query.order_by(NewsItem.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    offset = (page - 1) * page_size
    items = await _get_news_with_tickers(db, query, limit=page_size, offset=offset)

    return NewsListResponse(items=items, total=total, page=page, page_size=page_size)
