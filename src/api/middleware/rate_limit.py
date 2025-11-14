"""
Rate Limiting Middleware
~~~~~~~~~~~~~~~~~~~~~~~

Rate limiting to prevent API abuse.
"""

import time
from collections import defaultdict
from typing import Callable, Dict, Tuple

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.

    Limits requests per IP address or API key.
    """

    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
    ):
        """
        Initialize rate limiter.

        Args:
            app: FastAPI application
            requests_per_minute: Maximum requests per minute
            requests_per_hour: Maximum requests per hour
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour

        # Store: client_id -> (minute_window, hour_window)
        self.request_history: Dict[str, Tuple[list, list]] = defaultdict(
            lambda: ([], [])
        )

    def _get_client_id(self, request: Request) -> str:
        """
        Get unique client identifier.

        Args:
            request: Incoming request

        Returns:
            Client identifier (API key or IP address)
        """
        # Prefer API key if available
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"key:{api_key[:16]}"

        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"

    def _is_rate_limited(self, client_id: str) -> Tuple[bool, str]:
        """
        Check if client has exceeded rate limit.

        Args:
            client_id: Client identifier

        Returns:
            Tuple of (is_limited, limit_type)
        """
        current_time = time.time()
        minute_ago = current_time - 60
        hour_ago = current_time - 3600

        minute_requests, hour_requests = self.request_history[client_id]

        # Clean old requests
        minute_requests[:] = [t for t in minute_requests if t > minute_ago]
        hour_requests[:] = [t for t in hour_requests if t > hour_ago]

        # Check minute limit
        if len(minute_requests) >= self.requests_per_minute:
            return True, "minute"

        # Check hour limit
        if len(hour_requests) >= self.requests_per_hour:
            return True, "hour"

        # Record new request
        minute_requests.append(current_time)
        hour_requests.append(current_time)

        return False, ""

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Process request with rate limiting.

        Args:
            request: Incoming request
            call_next: Next middleware/route handler

        Returns:
            Response or rate limit error
        """
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/health/ready", "/health/live"]:
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_id(request)

        # Check rate limit
        is_limited, limit_type = self._is_rate_limited(client_id)

        if is_limited:
            logger.warning(
                f"Rate limit exceeded for {client_id} ({limit_type} limit)"
            )

            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Too many requests. Limit: {self.requests_per_minute}/min, {self.requests_per_hour}/hour",
                    "limit_type": limit_type,
                },
                headers={
                    "X-RateLimit-Limit-Minute": str(self.requests_per_minute),
                    "X-RateLimit-Limit-Hour": str(self.requests_per_hour),
                    "Retry-After": "60" if limit_type == "minute" else "3600",
                },
            )

        # Process request
        response = await call_next(request)

        # Add rate limit headers to response
        minute_requests, hour_requests = self.request_history[client_id]
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Minute"] = str(
            max(0, self.requests_per_minute - len(minute_requests))
        )
        response.headers["X-RateLimit-Remaining-Hour"] = str(
            max(0, self.requests_per_hour - len(hour_requests))
        )

        return response
