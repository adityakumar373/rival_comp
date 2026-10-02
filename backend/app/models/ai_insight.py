# app/models/ai_insight.py

import uuid
import enum

from sqlalchemy import Column, Text, DateTime, ForeignKey, Integer, Float, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class InsightCategory(str, enum.Enum):
    PRICING = "pricing"
    HIRING = "hiring"
    PRODUCT = "product"
    PARTNERSHIP = "partnership"
    MARKETING = "marketing"
    NEWS = "news"
    MARKET_ACTIVITY = "market_activity"
    OTHER = "other"


class AIInsight(Base):
    """
    AI-generated classification of a ChangeDetected row: what kind of
    change it is, a plain-language summary, why it matters (reasoning),
    and an impact score. This is what alerts and the dashboard read —
    they never read diff_text or raw scraped content directly.
    """

    __tablename__ = "ai_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    change_id = Column(
        UUID(as_uuid=True),
        ForeignKey("changes_detected.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,  # one insight per change
    )

    # Denormalized so dashboard/alert queries don't need to join through
    # changes_detected -> sources every time.
    competitor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competitor.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # idx_ai_insights_competitor
    )
    source_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
    )

    category = Column(Enum(InsightCategory, name="insight_category_enum"), nullable=False)
    summary = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=False)

    # 0-100: how much this matters for competitive strategy.
    impact_score = Column(Integer, nullable=False, index=True)  # idx_ai_insights_impact

    # 0.0-1.0: the model's own confidence in this classification.
    confidence_score = Column(Float, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
