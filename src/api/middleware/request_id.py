"""
Request ID Middleware
~~~~~~~~~~~~~~~~~~~~

Add unique request ID to each request for tracing.
"""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.logger import get_logger

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add unique request ID to each request.

    Adds X-Request-ID header to both request context and response.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request with unique request ID.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response with X-Request-ID header
        """
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Add to request state for access in routes
        request.state.request_id = request_id

        # Process request
        try:
            response = await call_next(request)
        except Exception as e:
            logger.error(f"Request {request_id} failed: {e}")
            raise

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response
