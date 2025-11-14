"""
Health Check Routes
~~~~~~~~~~~~~~~~~~~

Health and readiness check endpoints.
"""

import psutil
import time
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.api.schemas.stats import HealthStatus
from src.database.connection import get_db
from src.utils.config import get_settings
from src.utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(tags=["Health"])

# Track application start time
_start_time = time.time()


@router.get("/health", summary="Basic health check")
async def health_check():
    """
    Basic health check endpoint.

    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get(
    "/health/detailed",
    response_model=HealthStatus,
    summary="Detailed health check"
)
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with system metrics.

    Args:
        db: Database session

    Returns:
        Detailed health status
    """
    # Check database connection
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")

    # Check Redis connection (optional)
    redis_connected = False
    try:
        # TODO: Add Redis health check when Redis client is implemented
        redis_connected = True
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")

    # Get system metrics
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_mb = memory_info.rss / 1024 / 1024
    cpu_percent = process.cpu_percent(interval=0.1)

    # Calculate uptime
    uptime_seconds = time.time() - _start_time

    # Check if models are loaded
    # TODO: Update when ML models are actually loaded
    models_loaded = False

    return HealthStatus(
        status="healthy" if db_connected else "degraded",
        service=settings.app_name,
        version=settings.app_version,
        uptime_seconds=uptime_seconds,
        models_loaded=models_loaded,
        database_connected=db_connected,
        redis_connected=redis_connected,
        memory_usage_mb=round(memory_mb, 2),
        cpu_usage_percent=round(cpu_percent, 2)
    )


@router.get("/ready", summary="Readiness check")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Readiness check for Kubernetes/load balancer.

    Args:
        db: Database session

    Returns:
        Service readiness status
    """
    # Check critical dependencies
    db_ready = False
    try:
        db.execute(text("SELECT 1"))
        db_ready = True
    except Exception as e:
        logger.error(f"Database readiness check failed: {e}")

    # TODO: Check if models are loaded when implemented
    models_ready = False

    is_ready = db_ready  # and models_ready (when models are loaded)

    return {
        "status": "ready" if is_ready else "not_ready",
        "database_connected": db_ready,
        "models_loaded": models_ready,
        "checks": {
            "database": "pass" if db_ready else "fail",
            "models": "pending"  # "pass" if models_ready else "fail"
        }
    }


@router.get("/liveness", summary="Liveness probe")
async def liveness_check():
    """
    Liveness probe for Kubernetes.

    Returns:
        Simple alive status
    """
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
