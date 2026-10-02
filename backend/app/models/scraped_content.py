# app/models/scraped_content.py

import uuid

from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class ScrapedContent(Base):
    """
    Raw log of every scrape attempt for a source — success or failure.
    Always written, even when content hasn't changed (so you can see
    when a source was last checked and whether it's erroring).
    """

    __tablename__ = "scraped_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    source_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # idx_scraped_content_source
    )

    status_code = Column(Integer, nullable=True)
    raw_html = Column(Text, nullable=True)
    content = Column(Text, nullable=True)  # extracted/cleaned text
    hash = Column(String(64), nullable=True)
    error = Column(Text, nullable=True)  # populated on failed scrape

    scraped_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,  # idx_scraped_content_date
    )
