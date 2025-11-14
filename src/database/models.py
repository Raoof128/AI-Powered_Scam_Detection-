"""
Database Models
~~~~~~~~~~~~~~~

SQLAlchemy models for database tables.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class ScamReport(Base):
    """Scam detection report model."""

    __tablename__ = "scam_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    message = Column(Text, nullable=False)
    message_type = Column(String(50), nullable=False)
    scam_probability = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False)
    confidence = Column(Float, nullable=False)

    detected_patterns = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    recommendations = Column(JSON, default=list)

    processing_time_ms = Column(Integer, nullable=False)
    australian_specific = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    feedback = relationship("FeedbackEntry", back_populates="report", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ScamReport(id={self.id}, risk_level={self.risk_level}, probability={self.scam_probability:.2f})>"


class DetectionPattern(Base):
    """Detection pattern configuration model."""

    __tablename__ = "detection_patterns"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pattern_name = Column(String(100), unique=True, nullable=False)
    pattern_type = Column(String(50), nullable=False)
    pattern_regex = Column(Text, nullable=True)
    weight = Column(Float, default=1.0)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<DetectionPattern(name={self.pattern_name}, type={self.pattern_type})>"


class FeedbackEntry(Base):
    """User feedback on detection results."""

    __tablename__ = "feedback_loop"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("scam_reports.id", ondelete="CASCADE"), nullable=False)

    user_feedback = Column(String(20), nullable=False)
    corrected_label = Column(String(20), nullable=True)
    feedback_text = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    report = relationship("ScamReport", back_populates="feedback")

    def __repr__(self) -> str:
        return f"<FeedbackEntry(id={self.id}, feedback={self.user_feedback})>"


class PerformanceMetric(Base):
    """Daily performance metrics."""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, unique=True, nullable=False)

    total_requests = Column(Integer, default=0)
    scam_detected = Column(Integer, default=0)
    legitimate_detected = Column(Integer, default=0)

    avg_processing_time_ms = Column(Float, nullable=True)
    p95_processing_time_ms = Column(Integer, nullable=True)
    p99_processing_time_ms = Column(Integer, nullable=True)

    accuracy = Column(Float, nullable=True)
    precision_score = Column(Float, nullable=True)
    recall_score = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    false_positive_rate = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return f"<PerformanceMetric(date={self.date}, requests={self.total_requests})>"


class APIKey(Base):
    """API key for authentication."""

    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    rate_limit = Column(Integer, default=100)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<APIKey(name={self.name}, active={self.is_active})>"
