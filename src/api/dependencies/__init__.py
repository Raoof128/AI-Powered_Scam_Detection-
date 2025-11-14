"""
API Dependencies
~~~~~~~~~~~~~~~~

Dependency injection functions for FastAPI routes.
"""

from src.api.dependencies.auth import get_api_key, verify_api_key
from src.api.dependencies.database import get_db
from src.api.dependencies.detector import get_detector

__all__ = [
    "get_api_key",
    "verify_api_key",
    "get_db",
    "get_detector",
]
