# app/api/competitor.py

from uuid import UUID

# FastAPI utilities
from fastapi import APIRouter, Depends, HTTPException, Query

# SQLAlchemy session type
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logger import get_logger

# Database dependency
from app.db.dependencies import get_db

from app.services import competitor_service

# Pydantic schemas
from app.schemas.competitor import (
    CompetitorCreate,
    CompetitorResponse,
    CompetitorUpdate,
)

logger = get_logger(__name__)

# Create router
router = APIRouter(
    prefix="/competitor",
    tags=["Competitor"],
)


@router.post("/", response_model=CompetitorResponse, status_code=201)
def create_competitor(
    competitor: CompetitorCreate,
    db: Session = Depends(get_db),
):
    """
    Create a new competitor.
    """
    try:
        return competitor_service.create_competitor(db, competitor)
    except ConflictError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[CompetitorResponse])
def get_competitors(
    include_inactive: bool = Query(
        False, description="Include soft-deleted competitors"
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    Get all competitors (active only, unless include_inactive=true).
    """
    return competitor_service.list_competitors(
        db, active_only=not include_inactive, skip=skip, limit=limit
    )


@router.get("/{competitor_id}", response_model=CompetitorResponse)
def get_competitor(
    competitor_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Get competitor by ID.
    """
    try:
        return competitor_service.get_competitor(db, competitor_id, active_only=False)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{competitor_id}", response_model=CompetitorResponse)
def update_competitor(
    competitor_id: UUID,
    competitor_update: CompetitorUpdate,
    db: Session = Depends(get_db),
):
    """
    Update competitor.
    """
    try:
        return competitor_service.update_competitor(db, competitor_id, competitor_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{competitor_id}")
def delete_competitor(
    competitor_id: UUID,
    db: Session = Depends(get_db),
):
    """
    Soft-delete a competitor (sets is_active = False; does not remove the row).
    """
    try:
        competitor_service.soft_delete_competitor(db, competitor_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"message": "Competitor deleted successfully"}
