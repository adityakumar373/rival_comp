# app/core/exceptions.py
"""
Domain-level exceptions.

Services raise these; the API layer (routers) is responsible for
translating them into HTTPException / status codes. This keeps
business logic free of any FastAPI/HTTP coupling, so it stays
reusable by the future scraping/n8n workflows too.
"""


class AppError(Exception):
    """Base class for all domain errors."""


class NotFoundError(AppError):
    """Requested entity does not exist (or is soft-deleted)."""


class ConflictError(AppError):
    """Entity violates a uniqueness / business rule constraint."""
