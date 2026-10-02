# app/api/scraper.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.db.dependencies import get_db
from app.services import scraper_service, scheduler_service

router = APIRouter(prefix="/scraper", tags=["Scraper"])


@router.post("/source/{source_id}")
def scrape_source(source_id: UUID, db: Session = Depends(get_db)):
    """Scrape a single source: fetch → version → diff → AI classify → alert."""
    try:
        return scraper_service.scrape_source(db, source_id)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/due")
def list_due_sources(db: Session = Depends(get_db)):
    """
    Returns active sources that are overdue for scraping based on their
    scrape_frequency. Call this from a scheduler (n8n / cron) to get
    the list of source IDs that need a POST /scraper/source/{id} call.
    """
    sources = scraper_service.get_due_sources(db)
    return [
        {
            "source_id": str(s.id),
            "competitor_id": str(s.competitor_id),
            "url": s.url,
            "source_type": s.source_type.value if hasattr(s.source_type, "value") else s.source_type,
            "scrape_frequency_minutes": s.scrape_frequency,
            "last_scraped": s.last_scraped.isoformat() if s.last_scraped else None,
        }
        for s in sources
    ]


@router.get("/scheduler/status")
def get_scheduler_status():
    """Returns background automated scheduler telemetry and status."""
    return scheduler_service.get_scheduler_status()


@router.post("/scheduler/trigger")
async def trigger_scheduler_sweep():
    """Immediately triggers an on-demand background sweep across all due sources."""
    scraped = await scheduler_service.run_sweep()
    return {
        "status": "success",
        "message": f"Sweep completed. Scraped {scraped} overdue source(s).",
        "scraped_count": scraped,
    }


@router.post("/competitor/{competitor_id}/scrape-all")
def scrape_all_sources_for_competitor(
    competitor_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Triggers a scrape for ALL active sources of a competitor.
    Each source is scraped in sequence (background task) so the
    endpoint returns immediately with the list of source IDs queued.
    """
    from app.models.source import Source
    sources = (
        db.query(Source)
        .filter(Source.competitor_id == competitor_id, Source.is_active.is_(True))
        .all()
    )
    if not sources:
        raise HTTPException(status_code=404, detail="No active sources found for this competitor")

    source_ids = [str(s.id) for s in sources]

    def _scrape_all(ids: list[str]):
        from app.db.database import SessionLocal
        _db = SessionLocal()
        try:
            for sid in ids:
                try:
                    scraper_service.scrape_source(_db, UUID(sid))
                except Exception:
                    pass
        finally:
            _db.close()

    background_tasks.add_task(_scrape_all, source_ids)

    return {
        "status": "queued",
        "message": f"Scraping {len(source_ids)} source(s) in background",
        "source_ids": source_ids,
    }