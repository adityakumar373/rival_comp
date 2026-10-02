# app/api/changes.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services import change_detection_service
from app.schemas.change import ChangeDetectedResponse

router = APIRouter(prefix="/changes", tags=["Changes"])


@router.get("/source/{source_id}", response_model=list[ChangeDetectedResponse])
def list_changes_for_source(
    source_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Detected changes for a source, most recent first."""
    return change_detection_service.list_changes_for_source(db, source_id, skip, limit)


@router.get("/{change_id}", response_model=ChangeDetectedResponse)
def get_change(change_id: UUID, db: Session = Depends(get_db)):
    change = change_detection_service.get_change(db, change_id)
    if not change:
        raise HTTPException(status_code=404, detail=f"Change {change_id} not found")
    return change
