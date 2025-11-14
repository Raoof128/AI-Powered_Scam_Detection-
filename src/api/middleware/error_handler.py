"""
Error Handler Middleware
~~~~~~~~~~~~~~~~~~~~~~~

Global error handling middleware.
"""

from typing import Callable

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from src.utils.logger import get_logger

logger = get_logger(__name__)


async def error_handler_middleware(
    request: Request, call_next: Callable
) -> Response:
    """
    Handle errors globally and return consistent error responses.

    Args:
        request: Incoming request
        call_next: Next middleware/route handler

    Returns:
        Response or error response
    """
    request_id = getattr(request.state, "request_id", "unknown")

    try:
        response = await call_next(request)
        return response

    except ValidationError as e:
        logger.warning(f"[{request_id}] Validation error: {e}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error",
                "detail": e.errors(),
                "request_id": request_id,
            },
        )

    except SQLAlchemyError as e:
        logger.error(f"[{request_id}] Database error: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Database error",
                "detail": "An error occurred while accessing the database",
                "request_id": request_id,
            },
        )

    except ValueError as e:
        logger.warning(f"[{request_id}] Value error: {e}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "Invalid input",
                "detail": str(e),
                "request_id": request_id,
            },
        )

    except Exception as e:
        logger.error(
            f"[{request_id}] Unexpected error: {type(e).__name__}: {e}",
            exc_info=True,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "detail": "An unexpected error occurred",
                "request_id": request_id,
            },
        )
