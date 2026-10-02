# app/schemas/dashboard.py
from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.schemas.competitor import CompetitorResponse
from app.schemas.source import SourceResponse
from app.schemas.insight import AIInsightResponse
from app.schemas.alert import AlertResponse


class CompetitorOverviewItem(BaseModel):
    competitor_id: UUID
    name: str
    industry: Optional[str]
    source_count: int
    last_scraped_at: Optional[datetime]
    insight_count: int
    avg_impact_score: Optional[float]
    unsent_alert_count: int


class CompetitorDetailResponse(BaseModel):
    competitor: CompetitorResponse
    sources: list[SourceResponse]
    recent_insights: list[AIInsightResponse]
    recent_alerts: list[AlertResponse]
