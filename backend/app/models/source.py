# app/models/source.py

import uuid
import enum

from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class SourceType(str, enum.Enum):
    COMPANY_WEBSITE = "company_website"
    BLOG = "blog"
    PRICING_PAGE = "pricing_page"
    CAREER_PAGE = "career_page"
    NEWS_FEED = "news_feed"
    LINKEDIN = "linkedin"
    G2 = "g2"
    TRUSTPILOT = "trustpilot"


class Source(Base):
    """
    A specific URL/feed monitored for a given competitor
    (e.g. their pricing page, their careers page, their G2 profile).
    """

    __tablename__ = "sources"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    competitor_id = Column(
        UUID(as_uuid=True),
        ForeignKey("competitor.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # idx_sources_competitor
    )

    source_type = Column(
        Enum(SourceType, name="source_type_enum"),
        nullable=False,
    )

    url = Column(
        String(1000),
        nullable=False,
    )

    # How often (in minutes) this source should be re-scraped.
    scrape_frequency = Column(
        Integer,
        nullable=False,
        default=1440,  # daily
        server_default="1440",
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    competitor = relationship("Competitor", backref="sources")

    last_scraped = Column(
        DateTime(timezone=True),
        nullable=True
    )