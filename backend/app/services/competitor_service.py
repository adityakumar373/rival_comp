# app/services/competitor_service.py
"""
Business logic for Competitor entities.

API routes should be thin: parse request -> call service -> return
response. All rules (uniqueness, soft delete, what "active" means)
live here so they're consistent whether called from a route, a
future n8n webhook handler, or a background job.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logger import get_logger
from app.models.competitor import Competitor
from app.schemas.competitor import CompetitorCreate, CompetitorUpdate

logger = get_logger(__name__)


def create_competitor(db: Session, data: CompetitorCreate) -> Competitor:
    existing = (
        db.query(Competitor)
        .filter(Competitor.name == data.name)
        .first()
    )
    if existing:
        raise ConflictError(f"Competitor '{data.name}' already exists")

    competitor = Competitor(
        name=data.name,
        website=str(data.website),
        industry=data.industry,
        description=data.description,
    )
    db.add(competitor)
    db.commit()
    db.refresh(competitor)

    logger.info(
        "competitor_created",
        extra={"competitor_id": str(competitor.id), "name": competitor.name},
    )
    return competitor


def list_competitors(
    db: Session,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 100,
) -> list[Competitor]:
    query = db.query(Competitor)
    if active_only:
        query = query.filter(Competitor.is_active.is_(True))
    return (
        query.order_by(Competitor.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_competitor(
    db: Session,
    competitor_id: UUID,
    active_only: bool = True,
) -> Competitor:
    query = db.query(Competitor).filter(Competitor.id == competitor_id)
    if active_only:
        query = query.filter(Competitor.is_active.is_(True))

    competitor = query.first()
    if not competitor:
        raise NotFoundError(f"Competitor {competitor_id} not found")
    return competitor


def update_competitor(
    db: Session,
    competitor_id: UUID,
    data: CompetitorUpdate,
) -> Competitor:
    competitor = get_competitor(db, competitor_id)

    if data.name is not None and data.name != competitor.name:
        name_clash = (
            db.query(Competitor)
            .filter(Competitor.name == data.name, Competitor.id != competitor_id)
            .first()
        )
        if name_clash:
            raise ConflictError(f"Competitor '{data.name}' already exists")
        competitor.name = data.name

    if data.website is not None:
        competitor.website = str(data.website)

    if data.industry is not None:
        competitor.industry = data.industry

    if data.description is not None:
        competitor.description = data.description

    db.commit()
    db.refresh(competitor)

    logger.info("competitor_updated", extra={"competitor_id": str(competitor.id)})
    return competitor


def soft_delete_competitor(db: Session, competitor_id: UUID) -> None:
    competitor = get_competitor(db, competitor_id)
    competitor.is_active = False
    db.commit()

    logger.info("competitor_deleted", extra={"competitor_id": str(competitor.id)})
