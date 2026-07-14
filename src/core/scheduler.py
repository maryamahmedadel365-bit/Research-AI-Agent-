import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config import get_settings
from ..notifications.services import send_daily_reminder_to_all


logger = logging.getLogger(__name__)
scheduler = AsyncIOScheduler()

def start_scheduler() -> None:
    """Start the background scheduler for daily notifications."""
    settings = get_settings()
    
    # Schedule the daily push notification reminder
    scheduler.add_job(
        send_daily_reminder_to_all,
        "cron",
        hour=settings.DAILY_JOB_HOUR,
        minute=settings.DAILY_JOB_MINUTE,
        id="daily_paper_reminder",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info(f"Scheduler started. Daily job set for {settings.DAILY_JOB_HOUR:02d}:{settings.DAILY_JOB_MINUTE:02d}")

def stop_scheduler() -> None:
    """Shut down the background scheduler."""
    scheduler.shutdown()
