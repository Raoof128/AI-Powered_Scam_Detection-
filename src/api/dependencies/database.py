"""
Database Dependencies
~~~~~~~~~~~~~~~~~~~~

Database session dependencies for dependency injection.
"""

from typing import Generator

from sqlalchemy.orm import Session

from src.database.connection import SessionLocal
from src.utils.logger import get_logger

logger = get_logger(__name__)


def get_db() -> Generator[Session, None, None]:
    """
    Get database session.

    Yields:
        Database session

    Example:
        ```python
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
