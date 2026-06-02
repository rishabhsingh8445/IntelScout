from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from src.database import AsyncSessionLocal
from sqlalchemy import select
from src.models import Competitor
from src.tasks.scraping_tasks import run_scraping_job
import asyncio

scheduler = AsyncIOScheduler()

async def background_watcher_job():
    """
    This job runs automatically every 6 hours.
    It looks for any competitor that is being watched (is_watched = True)
    and triggers a deep scrape to find breaking news or insights.
    """
    print("Starting background watcher cron job...")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Competitor).where(Competitor.is_watched == True))
        watched_comps = result.scalars().all()
        
    for comp in watched_comps:
        print(f"[CRON] Rescraping watched competitor: {comp.name}")
        # In production, this would be pushed to a Celery worker queue
        # For now, we run it asynchronously in the scheduler
        await asyncio.to_thread(run_scraping_job, comp.id, "Short")
        
    print("[CRON] Watcher job finished.")

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
    print("APScheduler started successfully. 24/7 Monitoring is active.")
