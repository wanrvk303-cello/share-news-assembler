import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
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
    title="Stock News Aggregator",
    description="RSS-driven stock news aggregator with real-time UI",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(holdings_router, prefix="/api")
app.include_router(news_router, prefix="/api")


@app.post("/api/ingest")
async def trigger_ingest():
    async with async_session() as db:
        stats = await ingest_feeds(db)
        return stats


app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def index():
    return FileResponse("static/index.html")
