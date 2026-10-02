# app/models/content_version.py

import uuid

from sqlalchemy import Column, Text, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class ContentVersion(Base):
    """
    A distinct version of a source's content — only created when the
    content hash differs from the previous version for that source.
    This is what change detection diffs between.
    """

    __tablename__ = "content_versions"

    __table_args__ = (
        UniqueConstraint("source_id", "version_number", name="uq_content_versions_source_version"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    source_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,  # idx_content_versions_source
    )

    version_number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    hash = Column(String(64), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
