"""
Logging Configuration
~~~~~~~~~~~~~~~~~~~~~

Structured logging using loguru with support for file rotation and JSON formatting.
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


def get_logger(name: Optional[str] = None):
    """
    Get a configured logger instance.

    Args:
        name: Optional logger name for identification

    Returns:
        Configured logger instance
    """
    # Remove default handler
    logger.remove()

    # Console handler with color
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO",
        colorize=True,
    )

    # File handler with rotation
    log_path = Path("logs/scam-detector.log")
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger.add(
        log_path,
        rotation="10 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="DEBUG",
    )

    return logger


# Global logger instance
logger = get_logger()
