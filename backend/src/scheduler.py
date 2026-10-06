import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import select

from src.database import AsyncSessionLocal
from src.models import Competitor
from src.tasks.scraping_tasks import _async_run_scraping_job

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def background_watcher_job():
    """
    This job runs automatically every 6 hours.
    It looks for any competitor that is being watched (is_watched = True)
    and triggers a deep scrape to find breaking news or insights.
    """
    logger.info("Starting background watcher cron job...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Competitor).where(Competitor.is_watched == True))
        watched_comps = result.scalars().all()

    for comp in watched_comps:
        logger.info("[CRON] Running V2 Autonomous Agent Pipeline for: %s", comp.name)
        try:
            await _async_run_scraping_job(comp.id, "Short")
        except Exception:
            logger.exception("[CRON] Pipeline failed for %s", comp.name)

    logger.info("[CRON] Autonomous Pipeline watcher job finished.")


def start_scheduler():
    # Schedule the job to run every 6 hours
    scheduler.add_job(
        background_watcher_job,
        trigger=IntervalTrigger(hours=6),
        id="watcher_job",
        name="Scrape watched competitors every 6 hours",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("APScheduler started successfully. 24/7 Monitoring is active.")
