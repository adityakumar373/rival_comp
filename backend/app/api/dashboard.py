# app/api/dashboard.py

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services import dashboard_service
from app.schemas.dashboard import CompetitorOverviewItem, CompetitorDetailResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/competitors", response_model=list[CompetitorOverviewItem])
def get_competitor_overview(db: Session = Depends(get_db)):
    """
    One row per active competitor: source count, last scrape time,
    insight count, average impact score, unsent alert count. This is
    the main dashboard landing view.
    """
    return dashboard_service.competitor_overview(db)


@router.get("/competitor/{competitor_id}", response_model=CompetitorDetailResponse)
def get_competitor_detail(competitor_id: UUID, db: Session = Depends(get_db)):
    """
    Drill-down for one competitor: its sources, recent AI insights,
    and recent alerts.
    """
    detail = dashboard_service.competitor_detail(db, competitor_id)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Competitor {competitor_id} not found")
    return detail


@router.get("/analytics")
def get_analytics_summary(db: Session = Depends(get_db)):
    """
    Real aggregated analytics: totals, category breakdown, top insights
    by impact score, and per-competitor activity for bar charts.
    """
    return dashboard_service.get_analytics_summary(db)

