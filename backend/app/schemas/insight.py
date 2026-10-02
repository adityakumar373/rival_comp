# app/schemas/insight.py
from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.ai_insight import InsightCategory


class AIInsightResponse(BaseModel):
    id: UUID
    change_id: UUID
    competitor_id: UUID
    source_id: UUID
    category: InsightCategory
    summary: str
    reasoning: str
    impact_score: int
    confidence_score: float
    created_at: datetime
    # Enriched fields — populated by dashboard_service when available
    source_url: Optional[str] = None
    competitor_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
