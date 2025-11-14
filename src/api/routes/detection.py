"""
Detection Routes
~~~~~~~~~~~~~~~~

API endpoints for scam detection.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.schemas.detection import (
    BatchDetectionRequest,
    BatchDetectionResponse,
    DetectionRequest,
    DetectionResponse,
    FeedbackRequest,
    FeedbackResponse,
)
from src.database.connection import get_db
from src.database.repository import FeedbackRepository, ScamReportRepository
from src.models.detector import ScamDetector
from src.utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Detection"])

# Global detector instance (initialized on startup)
_detector: ScamDetector | None = None


def get_detector() -> ScamDetector:
    """Get or initialize the scam detector."""
    global _detector
    if _detector is None:
        _detector = ScamDetector()
    return _detector


@router.post(
    "/detect",
    response_model=DetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect scam in a single message",
    description="Analyze a message for scam indicators and return risk assessment"
)
async def detect_scam(
    request: DetectionRequest,
    detector: Annotated[ScamDetector, Depends(get_detector)],
    db: Session = Depends(get_db)
) -> DetectionResponse:
    """
    Detect if a message is a scam.

    Args:
        request: Detection request with message and metadata
        detector: Scam detector instance
        db: Database session

    Returns:
        Detection result with risk level and patterns

    Raises:
        HTTPException: If detection fails
    """
    try:
        # Run detection
        result = detector.detect(
            message=request.message,
            message_type=request.message_type.value,
            metadata=request.metadata or {},
            include_explanation=request.include_explanation
        )

        # Generate report ID
        report_id = str(uuid.uuid4())
        result["report_id"] = report_id

        # Save to database
        try:
            report_data = {
                "id": uuid.UUID(report_id),
                "message": request.message,
                "message_type": request.message_type.value,
                "scam_probability": result["scam_probability"],
                "risk_level": result["risk_level"],
                "confidence": result["confidence"],
                "detected_patterns": [p.model_dump() for p in result["detected_patterns"]],
                "metadata": request.metadata or {},
                "recommendations": result["recommendations"],
                "processing_time_ms": result["processing_time_ms"],
                "australian_specific": result["australian_specific"],
            }
            ScamReportRepository.create(db, report_data)
        except Exception as db_error:
            logger.error(f"Failed to save report to database: {db_error}")
            # Continue even if DB save fails

        return DetectionResponse(**result)

    except Exception as e:
        logger.error(f"Detection error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Detection failed: {str(e)}"
        )


@router.post(
    "/detect/batch",
    response_model=BatchDetectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Detect scams in multiple messages",
    description="Analyze multiple messages in a single request"
)
async def batch_detect_scam(
    request: BatchDetectionRequest,
    detector: Annotated[ScamDetector, Depends(get_detector)],
    db: Session = Depends(get_db)
) -> BatchDetectionResponse:
    """
    Detect scams in multiple messages.

    Args:
        request: Batch detection request
        detector: Scam detector instance
        db: Database session

    Returns:
        Batch detection results

    Raises:
        HTTPException: If batch detection fails
    """
    try:
        # Convert requests to dict format
        messages = [
            {
                "message": req.message,
                "message_type": req.message_type.value,
                "metadata": req.metadata or {},
            }
            for req in request.messages
        ]

        # Run batch detection
        batch_result = detector.batch_detect(
            messages=messages,
            include_explanation=True
        )

        # Save reports to database
        for i, result in enumerate(batch_result["results"]):
            try:
                report_id = str(uuid.uuid4())
                result["report_id"] = report_id

                report_data = {
                    "id": uuid.UUID(report_id),
                    "message": messages[i]["message"],
                    "message_type": messages[i]["message_type"],
                    "scam_probability": result["scam_probability"],
                    "risk_level": result["risk_level"],
                    "confidence": result["confidence"],
                    "detected_patterns": [p.model_dump() for p in result["detected_patterns"]],
                    "metadata": messages[i]["metadata"],
                    "recommendations": result["recommendations"],
                    "processing_time_ms": result["processing_time_ms"],
                    "australian_specific": result["australian_specific"],
                }
                ScamReportRepository.create(db, report_data)
            except Exception as db_error:
                logger.error(f"Failed to save batch report to database: {db_error}")

        return BatchDetectionResponse(**batch_result)

    except Exception as e:
        logger.error(f"Batch detection error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch detection failed: {str(e)}"
        )


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit feedback on detection result",
    description="Provide feedback to improve model accuracy"
)
async def submit_feedback(
    request: FeedbackRequest,
    db: Session = Depends(get_db)
) -> FeedbackResponse:
    """
    Submit user feedback on a detection result.

    Args:
        request: Feedback request
        db: Database session

    Returns:
        Feedback submission confirmation

    Raises:
        HTTPException: If report not found or feedback fails
    """
    try:
        # Verify report exists
        report_id = uuid.UUID(request.report_id)
        report = ScamReportRepository.get_by_id(db, report_id)

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {request.report_id} not found"
            )

        # Create feedback entry
        feedback_data = {
            "report_id": report_id,
            "user_feedback": request.user_feedback,
            "corrected_label": request.corrected_label,
            "feedback_text": request.feedback_text,
        }

        feedback = FeedbackRepository.create(db, feedback_data)

        logger.info(f"Feedback submitted for report {request.report_id}")

        return FeedbackResponse(
            success=True,
            message="Feedback recorded successfully",
            feedback_id=str(feedback.id)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback submission error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Feedback submission failed: {str(e)}"
        )


@router.get(
    "/report/{report_id}",
    response_model=DetectionResponse,
    summary="Get detection report by ID",
    description="Retrieve a previously generated detection report"
)
async def get_report(
    report_id: str,
    db: Session = Depends(get_db)
) -> DetectionResponse:
    """
    Get a detection report by ID.

    Args:
        report_id: Report UUID
        db: Database session

    Returns:
        Detection report

    Raises:
        HTTPException: If report not found
    """
    try:
        report = ScamReportRepository.get_by_id(db, uuid.UUID(report_id))

        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report {report_id} not found"
            )

        # Convert to response format
        from src.api.schemas.detection import DetectedPattern

        detected_patterns = [
            DetectedPattern(**p) for p in report.detected_patterns
        ]

        return DetectionResponse(
            scam_probability=report.scam_probability,
            risk_level=report.risk_level,
            detected_patterns=detected_patterns,
            confidence=report.confidence,
            recommendations=report.recommendations,
            processing_time_ms=report.processing_time_ms,
            report_id=str(report.id),
            australian_specific=report.australian_specific
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}"
        )
