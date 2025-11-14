"""
Database Module
~~~~~~~~~~~~~~~

Database models, connections, and repository layer.
"""

from src.database.models import Base, ScamReport, DetectionPattern, FeedbackEntry
from src.database.connection import get_db, init_db

__all__ = [
    "Base",
    "ScamReport",
    "DetectionPattern",
    "FeedbackEntry",
    "get_db",
    "init_db",
]
