# app/models/change_detected.py

import uuid

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class ChangeDetected(Base):
    """
    A detected textual difference between two consecutive ContentVersions
    for a given source. Produced deterministically by change_detection_service.
    """

    __tablename__ = "changes_detected"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    source_id = Column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    previous_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("content_versions.id", ondelete="SET NULL"),
        nullable=True,
    )

    new_version_id = Column(
        UUID(as_uuid=True),
        ForeignKey("content_versions.id", ondelete="CASCADE"),
        nullable=False,
    )

    lines_added = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    lines_removed = Column(
        Integer,
        nullable=False,
        default=0,
        server_default="0",
    )

    similarity_ratio = Column(
        Float,
        nullable=False,
        default=0.0,
        server_default="0.0",
    )

    diff_text = Column(
        Text,
        nullable=False,
        default="",
        server_default="",
    )

    change_summary = Column(
        Text,
        nullable=True,
    )

    detected_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )