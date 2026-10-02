# app/api/insights.py

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services import ai_service
from app.schemas.insight import AIInsightResponse

router = APIRouter(prefix="/insights", tags=["Insights"])


@router.get("/", response_model=list[AIInsightResponse])
def list_all_insights(
    category: Optional[str] = Query(None, description="Filter by category (pricing, hiring, product, ...)"),
    min_impact: int = Query(0, ge=0, le=100, description="Minimum impact score"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """Global insights feed across all competitors, sorted by impact score desc."""
    return ai_service.list_all_insights(db, category, min_impact, skip, limit)


@router.get("/competitor/{competitor_id}", response_model=list[AIInsightResponse])
def list_insights_for_competitor(
    competitor_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """AI-classified insights for a competitor, most recent first."""
    return ai_service.list_insights_for_competitor(db, competitor_id, skip, limit)


@router.get("/{insight_id}", response_model=AIInsightResponse)
def get_insight(insight_id: UUID, db: Session = Depends(get_db)):
    insight = ai_service.get_insight(db, insight_id)
    if not insight:
        raise HTTPException(status_code=404, detail=f"Insight {insight_id} not found")
    return insight
