"""
FastAPI Application
~~~~~~~~~~~~~~~~~~~

Main application entry point for scam detection API.
"""

from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.middleware import (
    RequestIDMiddleware,
    RateLimitMiddleware,
    error_handler_middleware,
    logging_middleware,
)
from src.api.routes import detection, health, stats
from src.database.connection import init_db
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # TODO: Load ML models here
    # app.state.detector = ScamDetector()
    # logger.info("ML models loaded successfully")

    yield

    # Cleanup
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Scam Detection Platform for Australian-specific threats",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add middleware (order matters - first added = outermost)
# 1. CORS (outermost - handles preflight requests)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Request ID tracking
app.add_middleware(RequestIDMiddleware)

# 3. Rate limiting (after request ID so limits are logged with ID)
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    requests_per_hour=1000,
)

# 4. Request/Response logging (inner - logs after rate limiting)
app.middleware("http")(logging_middleware)

# 5. Error handling (innermost - catches all errors)
app.middleware("http")(error_handler_middleware)

# Include routers
app.include_router(detection.router)
app.include_router(health.router)
app.include_router(stats.router)


@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint.

    Returns:
        Welcome message with API information
    """
    return {
        "message": "🛡️ AI-Powered Scam Detection API",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "disabled in production",
        "endpoints": {
            "detection": "/api/v1/detect",
            "batch_detection": "/api/v1/detect/batch",
            "feedback": "/api/v1/feedback",
            "statistics": "/api/v1/stats/overview",
            "health": "/health",
        },
        "description": "Real-time scam detection for Australian-specific threats",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
