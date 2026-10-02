# Import database session factory
from app.db.database import SessionLocal


def get_db():
    """
    Create a database session for each request.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()