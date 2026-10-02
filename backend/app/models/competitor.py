# app/models/competitor.py

import uuid

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import Boolean
from sqlalchemy import DateTime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.database import Base


class Competitor(Base):
    """
    Represents a competitor company that we want to monitor.
    """

    __tablename__ = "competitor"

    # Unique identifier
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    # Company name
    name = Column(
        String(255),
        nullable=False,
        unique=True
    )

    # Main website URL
    website = Column(
        String(500),
        nullable=False
    )

    # Industry category
    industry = Column(
        String(255),
        nullable=True
    )

    # Company description
    description = Column(
        Text,
        nullable=True
    )

    # Soft delete flag. False = "deleted" but retained for audit history.
    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    # Record creation timestamp
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    # Record update timestamp
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )
