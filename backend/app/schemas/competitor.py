# app/schemas/competitor.py
from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, HttpUrl


class CompetitorCreate(BaseModel):
    """
    Request body when creating a competitor.
    """
    name: str
    website: HttpUrl
    industry: Optional[str] = None
    description: Optional[str] = None


class CompetitorResponse(BaseModel):
    """
    Response returned to client.
    """
    id: UUID
    name: str
    website: HttpUrl
    industry: Optional[str]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CompetitorUpdate(BaseModel):
    """
    Schema for updating competitor details.
    """
    name: Optional[str] = None
    website: Optional[HttpUrl] = None
    industry: Optional[str] = None
    description: Optional[str] = None