# app/schemas/alert.py
from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class AlertResponse(BaseModel):
    id: UUID
    insight_id: UUID
    competitor_id: UUID
    message: str
    impact_score: int
    sent_at: Optional[datetime]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
