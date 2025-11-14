"""
Logging Middleware
~~~~~~~~~~~~~~~~~

Request/response logging middleware.
"""

import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.logger import get_logger

logger = get_logger(__name__)


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """
    Log request and response details.

    Args:
        request: Incoming request
        call_next: Next middleware/route handler

    Returns:
        Response with timing information
    """
    # Start timer
    start_time = time.time()

    # Get request ID if available
    request_id = getattr(request.state, "request_id", "unknown")

    # Log request
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"from {request.client.host if request.client else 'unknown'}"
    )

    # Process request
    try:
        response = await call_next(request)
    except Exception as e:
        logger.error(f"[{request_id}] Request failed: {e}", exc_info=True)
        raise

    # Calculate duration
    duration_ms = (time.time() - start_time) * 1000

    # Log response
    logger.info(
        f"[{request_id}] {request.method} {request.url.path} "
        f"completed with {response.status_code} in {duration_ms:.2f}ms"
    )

    # Add timing header
    response.headers["X-Process-Time"] = f"{duration_ms:.2f}ms"

    return response
