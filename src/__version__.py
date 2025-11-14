"""
Version information for the scam detection platform.

This module provides version information that can be imported by other modules.
"""

__version__ = "0.1.0"
__version_info__ = (0, 1, 0)

__title__ = "scam-detector"
__description__ = "AI-Powered Scam Detection Platform for Australian-specific threats"
__author__ = "Your Name"
__author_email__ = "your.email@example.com"
__license__ = "MIT"
__url__ = "https://github.com/yourusername/scam-detector"

# Semantic version components
VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_PATCH = 0
VERSION_PRERELEASE = None  # e.g., "alpha", "beta", "rc1"
VERSION_BUILD = None  # e.g., build number or commit hash

def get_version() -> str:
    """
    Get the full version string.

    Returns:
        Version string in format: MAJOR.MINOR.PATCH[-PRERELEASE][+BUILD]
    """
    version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_PATCH}"

    if VERSION_PRERELEASE:
        version += f"-{VERSION_PRERELEASE}"

    if VERSION_BUILD:
        version += f"+{VERSION_BUILD}"

    return version


def get_version_info() -> dict:
    """
    Get detailed version information.

    Returns:
        Dictionary containing version components and metadata
    """
    return {
        "version": get_version(),
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH,
        "prerelease": VERSION_PRERELEASE,
        "build": VERSION_BUILD,
        "title": __title__,
        "description": __description__,
    }


# Backward compatibility
VERSION = get_version()
