# app/schemas/change.py
from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ChangeDetectedResponse(BaseModel):
    id: UUID
    source_id: UUID
    previous_version_id: Optional[UUID]
    new_version_id: UUID
    lines_added: int
    lines_removed: int
    similarity_ratio: float
    diff_text: str
    change_summary: Optional[str]
    detected_at: datetime

    model_config = ConfigDict(from_attributes=True)
