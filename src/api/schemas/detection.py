"""
Detection Schemas
~~~~~~~~~~~~~~~~~

Request/response models for scam detection endpoints.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class MessageType(str, Enum):
    """Types of messages that can be analyzed."""
    EMAIL = "email"
    SMS = "sms"
    CALL = "call"
    URL = "url"
    SOCIAL_MEDIA = "social_media"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Risk level classification."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DetectionRequest(BaseModel):
    """Request model for scam detection."""

    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Text content to analyze for scam detection",
        examples=["URGENT: Your ATO tax refund of $2,450 is ready. Click here to claim."]
    )

    message_type: MessageType = Field(
        default=MessageType.OTHER,
        description="Type of message being analyzed"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata about the message",
        examples=[{
            "sender": "no-reply@ato-gov.au.scam.com",
            "timestamp": "2024-01-15T10:30:00Z",
            "subject": "Tax Refund Available",
            "recipient": "user@example.com"
        }]
    )

    include_explanation: bool = Field(
        default=True,
        description="Include detailed explanation of detected patterns"
    )

    @field_validator("message")
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Validate message is not empty or whitespace only."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty or whitespace only")
        return v.strip()


class DetectedPattern(BaseModel):
    """Individual detected scam pattern."""

    pattern_name: str = Field(..., description="Name of the detected pattern")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    description: str = Field(..., description="Human-readable description")
    severity: float = Field(..., ge=0.0, le=1.0, description="Severity score")


class DetectionResponse(BaseModel):
    """Response model for scam detection."""

    scam_probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Probability that the message is a scam (0-1)"
    )

    risk_level: RiskLevel = Field(
        ...,
        description="Overall risk level classification"
    )

    detected_patterns: List[DetectedPattern] = Field(
        default_factory=list,
        description="List of detected scam patterns"
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence in the prediction"
    )

    recommendations: List[str] = Field(
        default_factory=list,
        description="Recommended actions for the user"
    )

    processing_time_ms: int = Field(
        ...,
        ge=0,
        description="Processing time in milliseconds"
    )

    report_id: Optional[str] = Field(
        default=None,
        description="Unique identifier for this detection report"
    )

    australian_specific: bool = Field(
        default=False,
        description="Whether Australian-specific patterns were detected"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "scam_probability": 0.94,
                "risk_level": "high",
                "detected_patterns": [
                    {
                        "pattern_name": "ato_impersonation",
                        "confidence": 0.92,
                        "description": "Australian Taxation Office impersonation detected",
                        "severity": 1.0
                    },
                    {
                        "pattern_name": "urgent_action",
                        "confidence": 0.88,
                        "description": "Urgency tactics to pressure immediate action",
                        "severity": 0.7
                    }
                ],
                "confidence": 0.91,
                "recommendations": [
                    "Do not click any links in this message",
                    "Verify directly with the ATO at ato.gov.au",
                    "Report to ACCC Scamwatch",
                    "Delete this message immediately"
                ],
                "processing_time_ms": 287,
                "report_id": "550e8400-e29b-41d4-a716-446655440000",
                "australian_specific": True
            }
        }


class BatchDetectionRequest(BaseModel):
    """Request model for batch scam detection."""

    messages: List[DetectionRequest] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of messages to analyze (max 100)"
    )


class BatchDetectionResponse(BaseModel):
    """Response model for batch scam detection."""

    results: List[DetectionResponse] = Field(
        ...,
        description="List of detection results"
    )

    total_processed: int = Field(
        ...,
        description="Total number of messages processed"
    )

    total_processing_time_ms: int = Field(
        ...,
        description="Total processing time in milliseconds"
    )

    average_processing_time_ms: float = Field(
        ...,
        description="Average processing time per message"
    )


class FeedbackRequest(BaseModel):
    """Request model for user feedback on detection."""

    report_id: str = Field(
        ...,
        description="ID of the detection report to provide feedback on"
    )

    user_feedback: str = Field(
        ...,
        description="User's feedback (e.g., 'correct', 'false_positive', 'false_negative')"
    )

    corrected_label: Optional[str] = Field(
        default=None,
        description="User's correction if the prediction was wrong"
    )

    feedback_text: Optional[str] = Field(
        default=None,
        max_length=1000,
        description="Additional comments from the user"
    )


class FeedbackResponse(BaseModel):
    """Response model for feedback submission."""

    success: bool = Field(..., description="Whether feedback was recorded successfully")
    message: str = Field(..., description="Response message")
    feedback_id: str = Field(..., description="Unique identifier for the feedback")
