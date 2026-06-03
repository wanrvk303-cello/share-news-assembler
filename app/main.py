import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.database import init_db, async_session
from app.routes_holdings import router as holdings_router
from app.routes_news import router as news_router
from app.ingestion import ingest_feeds, cleanup_old_items
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def scheduled_ingest():
    async with async_session() as db:
        stats = await ingest_feeds(db)
        logger.info(f"Ingestion complete: {stats}")


async def scheduled_cleanup():
    async with async_session() as db:
        deleted = await cleanup_old_items(db)
        if deleted:
            logger.info(f"Cleaned up {deleted} old news items")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler.add_job(scheduled_ingest, "interval", minutes=settings.RSS_POLL_INTERVAL_MINUTES, id="rss_ingest")
    scheduler.add_job(scheduled_cleanup, "interval", hours=24, id="cleanup")
    scheduler.start()
    asyncio.create_task(scheduled_ingest())
    yield
    scheduler.shutdown()


app = FastAPI(
    title="Share News Assembler",
    description="RSS-driven share news assembler with real-time UI",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(holdings_router, prefix="/api")
app.include_router(news_router, prefix="/api")


@app.post("/api/ingest")
async def trigger_ingest():
    async with async_session() as db:
        stats = await ingest_feeds(db)
        return stats


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api/version")
async def get_version():
    return {"version": "1.0.0", "poll_interval_minutes": settings.RSS_POLL_INTERVAL_MINUTES}


@app.get("/api/stats")
async def get_stats():
    from sqlalchemy import select, func
    from app.models import User, Holding, NewsItem, NewsStockMapping

    async with async_session() as db:
        users = (await db.execute(select(func.count(User.id)))).scalar()
        holdings = (await db.execute(select(func.count(Holding.id)))).scalar()
        news = (await db.execute(select(func.count(NewsItem.id)))).scalar()
        mappings = (await db.execute(select(func.count(NewsStockMapping.id)))).scalar()
        return {
            "users": users,
            "holdings": holdings,
            "news_items": news,
            "stock_mappings": mappings,
        }


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")
