# app/api/source.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.logger import get_logger
from app.db.dependencies import get_db
from app.services import source_service
from app.schemas.source import SourceCreate, SourceResponse, SourceUpdate

logger = get_logger(__name__)

router = APIRouter(
    prefix="/sources",
    tags=["Sources"],
)


@router.post("/", response_model=SourceResponse, status_code=201)
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    """
    Attach a new monitored source (pricing page, careers page, G2, etc.)
    to a competitor.
    """
    try:
        return source_service.create_source(db, source)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[SourceResponse])
def get_sources(
    competitor_id: UUID | None = Query(
        default=None, description="Filter by competitor"
    ),
    include_inactive: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    """
    List sources, optionally filtered by competitor.
    """
    return source_service.list_sources(
        db,
        competitor_id=competitor_id,
        active_only=not include_inactive,
        skip=skip,
        limit=limit,
    )


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: UUID, db: Session = Depends(get_db)):
    try:
        return source_service.get_source(db, source_id, active_only=False)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(source_id: UUID, source_update: SourceUpdate, db: Session = Depends(get_db)):
    try:
        return source_service.update_source(db, source_id, source_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{source_id}")
def delete_source(source_id: UUID, db: Session = Depends(get_db)):
    try:
        source_service.soft_delete_source(db, source_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return {"message": "Source deleted successfully"}
