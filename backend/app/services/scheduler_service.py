# app/services/scheduler_service.py
"""
Embedded asynchronous scheduler for continuous background competitor monitoring.
Runs inside FastAPI without requiring external cron/n8n services.
"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any

from app.core.config import settings
from app.core.logger import get_logger
from app.db.database import SessionLocal
from app.services import scraper_service

logger = get_logger(__name__)

_scheduler_task: asyncio.Task | None = None
_scheduler_stats: Dict[str, Any] = {
    "is_running": False,
    "last_run_at": None,
    "total_sweeps": 0,
    "sources_scraped_total": 0,
    "last_sweep_sources_count": 0,
    "last_error": None,
}


def get_scheduler_status() -> Dict[str, Any]:
    """Returns real-time status and telemetry of the background scheduler."""
    return {
        "enabled": settings.SCHEDULER_ENABLED,
        "interval_seconds": settings.SCHEDULER_INTERVAL_SECONDS,
        **_scheduler_stats,
    }


async def run_sweep() -> int:
    """
    Executes a single sweep across all overdue sources.
    Returns the number of sources scraped.
    """
    _scheduler_stats["last_run_at"] = datetime.now(timezone.utc).isoformat()
    scraped_count = 0

    def _sync_sweep():
        nonlocal scraped_count
        db = SessionLocal()
        try:
            due_sources = scraper_service.get_due_sources(db)
            for source in due_sources:
                try:
                    scraper_service.scrape_source(db, source.id)
                    scraped_count += 1
                except Exception as e:
                    logger.error("scheduled_scrape_failed", extra={"source_id": str(source.id), "error": str(e)})
        finally:
            db.close()

    try:
        # Run blocking scraper loop in worker thread so event loop remains responsive
        await asyncio.to_thread(_sync_sweep)
        _scheduler_stats["total_sweeps"] += 1
        _scheduler_stats["sources_scraped_total"] += scraped_count
        _scheduler_stats["last_sweep_sources_count"] = scraped_count
        _scheduler_stats["last_error"] = None
        if scraped_count > 0:
            logger.info("scheduler_sweep_completed", extra={"scraped_count": scraped_count})
    except Exception as exc:
        _scheduler_stats["last_error"] = str(exc)
        logger.error("scheduler_sweep_error", extra={"error": str(exc)})

    return scraped_count


async def _scheduler_loop():
    """Background loop that periodically executes sweeps."""
    logger.info("background_scheduler_started", extra={"interval": settings.SCHEDULER_INTERVAL_SECONDS})
    _scheduler_stats["is_running"] = True

    try:
        # Initial short grace delay on server startup (5s)
        await asyncio.sleep(5)
        while True:
            if settings.SCHEDULER_ENABLED:
                await run_sweep()
            await asyncio.sleep(settings.SCHEDULER_INTERVAL_SECONDS)
    except asyncio.CancelledError:
        logger.info("background_scheduler_cancelled")
    except Exception as exc:
        logger.error("background_scheduler_crashed", extra={"error": str(exc)})
    finally:
        _scheduler_stats["is_running"] = False


def start_scheduler():
    """Starts the background scheduler task on FastAPI application startup."""
    global _scheduler_task
    if settings.SCHEDULER_ENABLED and (_scheduler_task is None or _scheduler_task.done()):
        _scheduler_task = asyncio.create_task(_scheduler_loop())


def stop_scheduler():
    """Stops the background scheduler gracefully on shutdown."""
    global _scheduler_task
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        _scheduler_task = None
        _scheduler_stats["is_running"] = False
