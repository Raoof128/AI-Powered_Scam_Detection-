"""
AI-Powered Scam Detection Platform
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A production-ready scam detection system specialized for Australian-specific threats.

:copyright: (c) 2024
:license: MIT, see LICENSE for more details.
"""

from src.__version__ import (
    __version__,
    __author__,
    __author_email__,
    __title__,
    __description__,
    __license__,
    __url__,
    get_version,
    get_version_info,
)
from src.utils.logger import get_logger

# Backward compatibility
__email__ = __author_email__

logger = get_logger(__name__)

__all__ = [
    "__version__",
    "__author__",
    "__email__",
    "__title__",
    "__description__",
    "__license__",
    "__url__",
    "get_version",
    "get_version_info",
    "logger",
]
