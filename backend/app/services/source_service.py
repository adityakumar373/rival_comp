# app/services/source_service.py

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logger import get_logger
from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate
from app.services import competitor_service

logger = get_logger(__name__)


def create_source(db: Session, data: SourceCreate) -> Source:
    # Ensures the competitor exists (and is active) before attaching a source.
    # Raises NotFoundError otherwise, which the router turns into a 404.
    competitor_service.get_competitor(db, data.competitor_id)

    url_str = str(data.url)
    duplicate = (
        db.query(Source)
        .filter(
            Source.competitor_id == data.competitor_id,
            Source.url == url_str,
        )
        .first()
    )
    if duplicate:
        if not duplicate.is_active:
            duplicate.is_active = True
            duplicate.source_type = data.source_type
            duplicate.scrape_frequency = data.scrape_frequency
            db.commit()
            db.refresh(duplicate)
            return duplicate
        raise ConflictError("This source URL is already tracked for this competitor")

    # If global unique constraint exists on URL
    global_dup = db.query(Source).filter(Source.url == url_str).first()
    if global_dup:
        if global_dup.competitor_id == data.competitor_id:
            if not global_dup.is_active:
                global_dup.is_active = True
                global_dup.source_type = data.source_type
                global_dup.scrape_frequency = data.scrape_frequency
                db.commit()
                db.refresh(global_dup)
                return global_dup
            raise ConflictError("This source URL is already tracked for this competitor")
        raise ConflictError(f"This source URL is already tracked")

    source = Source(
        competitor_id=data.competitor_id,
        source_type=data.source_type,
        url=url_str,
        scrape_frequency=data.scrape_frequency,
    )
    db.add(source)
    db.commit()
    db.refresh(source)

    logger.info(
        "source_created",
        extra={"source_id": str(source.id), "competitor_id": str(source.competitor_id)},
    )
    return source


def list_sources(
    db: Session,
    competitor_id: UUID | None = None,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
) -> list[Source]:
    query = db.query(Source)
    if competitor_id is not None:
        query = query.filter(Source.competitor_id == competitor_id)
    if active_only:
        query = query.filter(Source.is_active.is_(True))
    return (
        query.order_by(Source.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_source(db: Session, source_id: UUID, active_only: bool = True) -> Source:
    query = db.query(Source).filter(Source.id == source_id)
    if active_only:
        query = query.filter(Source.is_active.is_(True))

    source = query.first()
    if not source:
        raise NotFoundError(f"Source {source_id} not found")
    return source


def update_source(db: Session, source_id: UUID, data: SourceUpdate) -> Source:
    source = get_source(db, source_id)

    if data.source_type is not None:
        source.source_type = data.source_type
    if data.url is not None:
        source.url = str(data.url)
    if data.scrape_frequency is not None:
        source.scrape_frequency = data.scrape_frequency

    db.commit()
    db.refresh(source)

    logger.info("source_updated", extra={"source_id": str(source.id)})
    return source


def soft_delete_source(db: Session, source_id: UUID) -> None:
    source = get_source(db, source_id)
    source.is_active = False
    db.commit()

    logger.info("source_deleted", extra={"source_id": str(source.id)})
