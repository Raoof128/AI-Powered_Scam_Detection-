"""
Authentication Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~

API authentication and authorization dependencies.
"""

from typing import Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.database.models import APIKey
from src.utils.logger import get_logger

logger = get_logger(__name__)

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_api_key(
    api_key: Optional[str] = Security(api_key_header),
    db: Session = Depends(get_db),
) -> Optional[str]:
    """
    Get API key from request header.

    Args:
        api_key: API key from header
        db: Database session

    Returns:
        API key if valid

    Raises:
        HTTPException: If API key is invalid
    """
    if not api_key:
        # Allow requests without API key in development
        return None

    # Verify API key in database
    db_key = db.query(APIKey).filter(APIKey.key == api_key, APIKey.is_active).first()

    if not db_key:
        logger.warning(f"Invalid API key attempted: {api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    logger.debug(f"API key validated: {db_key.name}")
    return api_key


async def verify_api_key(
    api_key: Optional[str] = Depends(get_api_key),
) -> str:
    """
    Verify that API key is present and valid.

    Args:
        api_key: API key from get_api_key dependency

    Returns:
        Validated API key

    Raises:
        HTTPException: If no API key provided
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key
