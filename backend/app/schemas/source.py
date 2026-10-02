# app/schemas/source.py
from uuid import UUID
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, HttpUrl, Field

from app.models.source import SourceType


class SourceCreate(BaseModel):
    competitor_id: UUID
    source_type: SourceType
    url: HttpUrl
    scrape_frequency: int = Field(
        default=1440, ge=15, description="Minutes between scrapes (min 15)"
    )


class SourceUpdate(BaseModel):
    source_type: Optional[SourceType] = None
    url: Optional[HttpUrl] = None
    scrape_frequency: Optional[int] = Field(default=None, ge=15)


class SourceResponse(BaseModel):
    id: UUID
    competitor_id: UUID
    source_type: SourceType
    url: HttpUrl
    scrape_frequency: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
