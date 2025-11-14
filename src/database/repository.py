"""
Database Repository
~~~~~~~~~~~~~~~~~~~

Data access layer for database operations.
"""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from src.database.models import (
    APIKey,
    DetectionPattern,
    FeedbackEntry,
    PerformanceMetric,
    ScamReport,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScamReportRepository:
    """Repository for scam report operations."""

    @staticmethod
    def create(db: Session, report_data: dict) -> ScamReport:
        """
        Create a new scam report.

        Args:
            db: Database session
            report_data: Report data dictionary

        Returns:
            Created ScamReport instance
        """
        report = ScamReport(**report_data)
        db.add(report)
        db.commit()
        db.refresh(report)
        logger.info(f"Created scam report: {report.id}")
        return report

    @staticmethod
    def get_by_id(db: Session, report_id: UUID) -> Optional[ScamReport]:
        """Get scam report by ID."""
        return db.query(ScamReport).filter(ScamReport.id == report_id).first()

    @staticmethod
    def get_recent(db: Session, limit: int = 100) -> List[ScamReport]:
        """Get recent scam reports."""
        return (
            db.query(ScamReport)
            .order_by(desc(ScamReport.created_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def get_by_risk_level(db: Session, risk_level: str, limit: int = 100) -> List[ScamReport]:
        """Get reports by risk level."""
        return (
            db.query(ScamReport)
            .filter(ScamReport.risk_level == risk_level)
            .order_by(desc(ScamReport.created_at))
            .limit(limit)
            .all()
        )

    @staticmethod
    def count_total(db: Session) -> int:
        """Get total number of reports."""
        return db.query(func.count(ScamReport.id)).scalar()

    @staticmethod
    def get_stats(db: Session, days: int = 30) -> dict:
        """Get statistics for the last N days."""
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        total = db.query(func.count(ScamReport.id)).filter(
            ScamReport.created_at >= cutoff_date
        ).scalar()

        high_risk = db.query(func.count(ScamReport.id)).filter(
            ScamReport.created_at >= cutoff_date,
            ScamReport.risk_level == "high"
        ).scalar()

        medium_risk = db.query(func.count(ScamReport.id)).filter(
            ScamReport.created_at >= cutoff_date,
            ScamReport.risk_level == "medium"
        ).scalar()

        low_risk = db.query(func.count(ScamReport.id)).filter(
            ScamReport.created_at >= cutoff_date,
            ScamReport.risk_level == "low"
        ).scalar()

        avg_probability = db.query(func.avg(ScamReport.scam_probability)).filter(
            ScamReport.created_at >= cutoff_date
        ).scalar()

        avg_processing = db.query(func.avg(ScamReport.processing_time_ms)).filter(
            ScamReport.created_at >= cutoff_date
        ).scalar()

        australian_specific = db.query(func.count(ScamReport.id)).filter(
            ScamReport.created_at >= cutoff_date,
            ScamReport.australian_specific == True
        ).scalar()

        return {
            "total": total or 0,
            "high_risk": high_risk or 0,
            "medium_risk": medium_risk or 0,
            "low_risk": low_risk or 0,
            "avg_scam_probability": float(avg_probability) if avg_probability else 0.0,
            "avg_processing_time_ms": float(avg_processing) if avg_processing else 0.0,
            "australian_specific": australian_specific or 0,
            "australian_specific_rate": float(australian_specific / total) if total else 0.0,
        }


class FeedbackRepository:
    """Repository for feedback operations."""

    @staticmethod
    def create(db: Session, feedback_data: dict) -> FeedbackEntry:
        """Create a new feedback entry."""
        feedback = FeedbackEntry(**feedback_data)
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        logger.info(f"Created feedback entry: {feedback.id}")
        return feedback

    @staticmethod
    def get_by_report_id(db: Session, report_id: UUID) -> List[FeedbackEntry]:
        """Get all feedback for a report."""
        return (
            db.query(FeedbackEntry)
            .filter(FeedbackEntry.report_id == report_id)
            .all()
        )


class DetectionPatternRepository:
    """Repository for detection pattern operations."""

    @staticmethod
    def get_active_patterns(db: Session) -> List[DetectionPattern]:
        """Get all active detection patterns."""
        return (
            db.query(DetectionPattern)
            .filter(DetectionPattern.is_active == True)
            .all()
        )

    @staticmethod
    def get_by_name(db: Session, pattern_name: str) -> Optional[DetectionPattern]:
        """Get pattern by name."""
        return (
            db.query(DetectionPattern)
            .filter(DetectionPattern.pattern_name == pattern_name)
            .first()
        )


class PerformanceMetricRepository:
    """Repository for performance metrics operations."""

    @staticmethod
    def get_recent_metrics(db: Session, days: int = 30) -> List[PerformanceMetric]:
        """Get recent performance metrics."""
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return (
            db.query(PerformanceMetric)
            .filter(PerformanceMetric.date >= cutoff_date)
            .order_by(desc(PerformanceMetric.date))
            .all()
        )
