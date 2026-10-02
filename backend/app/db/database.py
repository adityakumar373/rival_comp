# app/db/database.py

# SQLAlchemy engine
from sqlalchemy import create_engine

# Session management
from sqlalchemy.orm import sessionmaker

# Base class for all models
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Create PostgreSQL connection engine.
# pool_pre_ping avoids "server closed the connection unexpectedly"
# errors after periods of idleness (common on free-tier DBs).
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all models
Base = declarative_base()
