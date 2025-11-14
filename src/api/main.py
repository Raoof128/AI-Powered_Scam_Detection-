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

    # TODO: Load ML models here
    # app.state.model = load_model()

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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root() -> Dict[str, str]:
    """
    Root endpoint.

    Returns:
        Welcome message
    """
    return {
        "message": "Scam Detection API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "disabled in production"
    }


@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }


@app.get("/ready", tags=["Health"])
async def readiness_check() -> Dict[str, str]:
    """
    Readiness check endpoint.

    Returns:
        Service readiness status
    """
    # TODO: Check if models are loaded, database is accessible, etc.
    return {
        "status": "ready",
        "models_loaded": False,  # TODO: Update when models are loaded
        "database_connected": False,  # TODO: Update when DB is connected
        "redis_connected": False,  # TODO: Update when Redis is connected
    }


# TODO: Add detection endpoints
# @app.post("/api/v1/detect", tags=["Detection"])
# async def detect_scam(request: DetectionRequest) -> DetectionResponse:
#     """Detect if a message is a scam."""
#     pass


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_reload,
        log_level=settings.log_level.lower()
    )
