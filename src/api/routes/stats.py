"""
Statistics Routes
~~~~~~~~~~~~~~~~~

Endpoints for statistics and analytics.
"""

from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.api.schemas.stats import (
    DailyStats,
    PatternStats,
    PerformanceMetrics,
    StatsResponse,
)
from src.database.connection import get_db
from src.database.repository import (
    PerformanceMetricRepository,
    ScamReportRepository,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1/stats", tags=["Statistics"])


@router.get(
    "/overview",
    response_model=StatsResponse,
    summary="Get overall statistics",
    description="Get comprehensive statistics about scam detection"
)
async def get_stats_overview(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to include"),
    db: Session = Depends(get_db)
) -> StatsResponse:
    """
    Get overall statistics.

    Args:
        days: Number of days to include in statistics
        db: Database session

    Returns:
        Comprehensive statistics
    """
    try:
        # Get report statistics
        report_stats = ScamReportRepository.get_stats(db, days=days)

        # TODO: Calculate actual performance metrics when we have enough data
        performance = PerformanceMetrics(
            accuracy=0.942,
            precision=0.935,
            recall=0.921,
            f1_score=0.928,
            false_positive_rate=0.023,
            avg_processing_time_ms=report_stats.get("avg_processing_time_ms", 287.0),
            p95_processing_time_ms=445,
            p99_processing_time_ms=680,
            total_requests=report_stats.get("total", 0),
            scam_detected=report_stats.get("high_risk", 0) + report_stats.get("medium_risk", 0),
            legitimate_detected=report_stats.get("low_risk", 0),
        )

        # Top patterns (placeholder - would come from actual pattern detection stats)
        top_patterns = [
            PatternStats(
                pattern_name="ato_impersonation",
                total_detections=45,
                detection_rate=0.12,
                avg_confidence=0.89,
                last_detected=datetime.utcnow()
            ),
            PatternStats(
                pattern_name="banking_scam",
                total_detections=38,
                detection_rate=0.10,
                avg_confidence=0.85,
                last_detected=datetime.utcnow()
            ),
            PatternStats(
                pattern_name="delivery_scam",
                total_detections=29,
                detection_rate=0.08,
                avg_confidence=0.81,
                last_detected=datetime.utcnow()
            ),
        ]

        # Daily stats (placeholder - would aggregate from database)
        daily_stats = [
            DailyStats(
                date=datetime.utcnow().date(),
                total_reports=report_stats.get("total", 0),
                high_risk=report_stats.get("high_risk", 0),
                medium_risk=report_stats.get("medium_risk", 0),
                low_risk=report_stats.get("low_risk", 0),
                avg_scam_probability=report_stats.get("avg_scam_probability", 0.0),
                avg_processing_time_ms=report_stats.get("avg_processing_time_ms", 0.0)
            )
        ]

        return StatsResponse(
            performance=performance,
            top_patterns=top_patterns,
            daily_stats=daily_stats,
            australian_specific_rate=report_stats.get("australian_specific_rate", 0.0)
        )

    except Exception as e:
        logger.error(f"Error fetching statistics: {e}", exc_info=True)
        raise


@router.get(
    "/reports/recent",
    summary="Get recent detection reports",
    description="Get the most recent scam detection reports"
)
async def get_recent_reports(
    limit: int = Query(default=50, ge=1, le=1000),
    risk_level: Optional[str] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Get recent detection reports.

    Args:
        limit: Maximum number of reports to return
        risk_level: Filter by risk level (optional)
        db: Database session

    Returns:
        List of recent reports
    """
    try:
        if risk_level:
            reports = ScamReportRepository.get_by_risk_level(db, risk_level, limit)
        else:
            reports = ScamReportRepository.get_recent(db, limit)

        return {
            "total": len(reports),
            "reports": [
                {
                    "id": str(report.id),
                    "message_type": report.message_type,
                    "risk_level": report.risk_level,
                    "scam_probability": report.scam_probability,
                    "australian_specific": report.australian_specific,
                    "created_at": report.created_at.isoformat(),
                }
                for report in reports
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching recent reports: {e}", exc_info=True)
        raise


@router.get(
    "/performance/daily",
    summary="Get daily performance metrics",
    description="Get performance metrics aggregated by day"
)
async def get_daily_performance(
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get daily performance metrics.

    Args:
        days: Number of days to include
        db: Database session

    Returns:
        Daily performance metrics
    """
    try:
        metrics = PerformanceMetricRepository.get_recent_metrics(db, days=days)

        return {
            "total": len(metrics),
            "metrics": [
                {
                    "date": metric.date.isoformat(),
                    "total_requests": metric.total_requests,
                    "scam_detected": metric.scam_detected,
                    "accuracy": metric.accuracy,
                    "avg_processing_time_ms": metric.avg_processing_time_ms,
                }
                for metric in metrics
            ]
        }

    except Exception as e:
        logger.error(f"Error fetching daily performance: {e}", exc_info=True)
        raise


@router.get(
    "/summary",
    summary="Get summary statistics",
    description="Get quick summary of key metrics"
)
async def get_summary_stats(db: Session = Depends(get_db)):
    """
    Get summary statistics.

    Args:
        db: Database session

    Returns:
        Summary statistics
    """
    try:
        # Get stats for last 7 days
        stats = ScamReportRepository.get_stats(db, days=7)

        total_reports = ScamReportRepository.count_total(db)

        return {
            "total_reports_all_time": total_reports,
            "last_7_days": stats,
            "detection_rate": {
                "high_risk": stats.get("high_risk", 0) / stats.get("total", 1),
                "medium_risk": stats.get("medium_risk", 0) / stats.get("total", 1),
                "low_risk": stats.get("low_risk", 0) / stats.get("total", 1),
            },
            "australian_specific_percentage": stats.get("australian_specific_rate", 0.0) * 100,
        }

    except Exception as e:
        logger.error(f"Error fetching summary stats: {e}", exc_info=True)
        raise
