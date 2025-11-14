"""
Statistics Schemas
~~~~~~~~~~~~~~~~~~

Models for statistics and metrics endpoints.
"""

from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PatternStats(BaseModel):
    """Statistics for a specific scam pattern."""

    pattern_name: str = Field(..., description="Name of the pattern")
    total_detections: int = Field(..., ge=0, description="Total number of detections")
    detection_rate: float = Field(..., ge=0.0, le=1.0, description="Detection rate")
    avg_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence")
    last_detected: Optional[datetime] = Field(None, description="Last detection timestamp")


class PerformanceMetrics(BaseModel):
    """Model performance metrics."""

    accuracy: float = Field(..., ge=0.0, le=1.0, description="Model accuracy")
    precision: float = Field(..., ge=0.0, le=1.0, description="Precision score")
    recall: float = Field(..., ge=0.0, le=1.0, description="Recall score")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    false_positive_rate: float = Field(..., ge=0.0, le=1.0, description="False positive rate")

    avg_processing_time_ms: float = Field(..., ge=0, description="Average processing time")
    p95_processing_time_ms: int = Field(..., ge=0, description="95th percentile processing time")
    p99_processing_time_ms: int = Field(..., ge=0, description="99th percentile processing time")

    total_requests: int = Field(..., ge=0, description="Total requests processed")
    scam_detected: int = Field(..., ge=0, description="Number of scams detected")
    legitimate_detected: int = Field(..., ge=0, description="Number of legitimate messages")


class DailyStats(BaseModel):
    """Daily statistics."""

    date: date = Field(..., description="Date of the statistics")
    total_reports: int = Field(..., ge=0, description="Total reports for the day")
    high_risk: int = Field(..., ge=0, description="High risk detections")
    medium_risk: int = Field(..., ge=0, description="Medium risk detections")
    low_risk: int = Field(..., ge=0, description="Low risk detections")
    avg_scam_probability: float = Field(..., ge=0.0, le=1.0)
    avg_processing_time_ms: float = Field(..., ge=0)


class StatsResponse(BaseModel):
    """Overall statistics response."""

    performance: PerformanceMetrics = Field(..., description="Performance metrics")
    top_patterns: List[PatternStats] = Field(..., description="Most detected patterns")
    daily_stats: List[DailyStats] = Field(..., description="Daily statistics")
    australian_specific_rate: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Percentage of Australian-specific scams"
    )


class HealthStatus(BaseModel):
    """Detailed health status."""

    status: str = Field(..., description="Overall status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    uptime_seconds: float = Field(..., ge=0, description="Uptime in seconds")
    models_loaded: bool = Field(..., description="Whether ML models are loaded")
    database_connected: bool = Field(..., description="Database connection status")
    redis_connected: bool = Field(..., description="Redis connection status")
    memory_usage_mb: float = Field(..., ge=0, description="Memory usage in MB")
    cpu_usage_percent: float = Field(..., ge=0.0, le=100.0, description="CPU usage percentage")
