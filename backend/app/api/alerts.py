# app/api/alerts.py

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services import alert_service
from app.schemas.alert import AlertResponse

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=list[AlertResponse])
def list_all_alerts(
    unsent_only: bool = Query(False, description="Only alerts not yet marked delivered"),
    min_impact: int = Query(0, ge=0, le=100, description="Minimum impact score"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Global alerts feed across all competitors, sorted by impact score desc."""
    return alert_service.list_all_alerts(db, unsent_only, min_impact, skip, limit)


@router.get("/competitor/{competitor_id}", response_model=list[AlertResponse])
def list_alerts_for_competitor(
    competitor_id: UUID,
    unsent_only: bool = Query(False, description="Only alerts not yet marked delivered"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Alerts for a competitor, most recent first. n8n polls this
    (or ?unsent_only=true) to pick up new alerts for delivery."""
    return alert_service.list_alerts_for_competitor(db, competitor_id, unsent_only, skip, limit)


@router.post("/{alert_id}/mark-sent", response_model=AlertResponse)
def mark_alert_sent(alert_id: UUID, db: Session = Depends(get_db)):
    """Called by the delivery workflow (n8n) once an alert has actually
    been sent to Slack/email, so it isn't picked up again."""
    alert = alert_service.mark_alert_sent(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return alert

