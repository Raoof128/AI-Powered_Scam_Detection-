"""
Detector Dependencies
~~~~~~~~~~~~~~~~~~~~

Scam detector instance dependencies.
"""

from functools import lru_cache

from src.models.detector import ScamDetector
from src.utils.logger import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_detector() -> ScamDetector:
    """
    Get or create cached scam detector instance.

    Returns:
        Scam detector instance

    Note:
        Cached to avoid reloading models on every request.
    """
    logger.info("Initializing scam detector...")
    detector = ScamDetector()
    logger.info("Scam detector initialized successfully")
    return detector
