# app/models/alert.py

import uuid

from sqlalchemy import Column, Text, DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class Alert(Base):
    """
    Created automatically when an AIInsight's impact_score crosses
    settings.ALERT_IMPACT_THRESHOLD. `sent_at` stays null until a
    delivery channel (n8n -> Slack/email) marks it delivered — the
    FastAPI app's job is just to produce a correct alert row.
    """

    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    insight_id = Column(
        UUID(as_uuid=True),
        ForeignKey("ai_insights.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one alert per insight
    )

    competitor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competitor.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # idx_alerts_competitor
    )

    message = Column(Text, nullable=False)
    impact_score = Column(Integer, nullable=False)

    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
