from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging

logger = logging.getLogger(__name__)
_scheduler = None


def _run_scrape():
    from apps.scraper.views import _save_jobs
    from apps.scraper import nerdin, linkedin

    logger.info("Scheduled scrape started")
    try:
        jobs = nerdin.fetch_jobs(pages=2) + linkedin.fetch_jobs(pages=2)
        count = _save_jobs(jobs)
        logger.info(f"Scheduled scrape saved {count} new jobs")
    except Exception as e:
        logger.error(f"Scheduled scrape failed: {e}")


def start(interval_minutes=30):
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler()
    _scheduler.add_job(_run_scrape, IntervalTrigger(minutes=interval_minutes), id="scrape_jobs", replace_existing=True)
    _scheduler.start()
    logger.info(f"Scrape scheduler started (every {interval_minutes} min)")


def stop():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
