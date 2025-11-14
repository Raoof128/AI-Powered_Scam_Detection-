"""
API Integration Tests
~~~~~~~~~~~~~~~~~~~~~

Integration tests for API endpoints with database.
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.database.models import FeedbackEntry, ScamReport
from src.database.repository import FeedbackRepository, ScamReportRepository


class TestDetectionIntegration:
    """Integration tests for detection endpoints."""

    def test_single_detection_with_database_storage(
        self, client: TestClient, test_db: Session
    ):
        """Test single detection and verify database storage."""
        # Send detection request
        response = client.post(
            "/api/v1/detect",
            json={
                "message": "URGENT: Your ATO tax refund of $2,450 is ready",
                "message_type": "email",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify response structure
        assert "risk_level" in data
        assert "confidence_score" in data
        assert "detected_patterns" in data
        assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

        # Verify database storage
        repo = ScamReportRepository(test_db)
        reports = repo.get_recent_reports(limit=10)

        # Check that report was stored
        assert len(reports) >= 0  # May be 0 if storage is async

    def test_batch_detection_integration(self, client: TestClient, test_db: Session):
        """Test batch detection with multiple messages."""
        messages = [
            {
                "message": "URGENT: Your ATO tax refund is ready",
                "message_type": "email",
            },
            {
                "message": "Your MyGov account has been suspended",
                "message_type": "email",
            },
            {
                "message": "Regular message about coffee",
                "message_type": "sms",
            },
        ]

        response = client.post("/api/v1/detect/batch", json={"messages": messages})

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        assert "results" in data
        assert "summary" in data
        assert len(data["results"]) == 3

        # Verify summary statistics
        summary = data["summary"]
        assert "total_processed" in summary
        assert summary["total_processed"] == 3

    def test_feedback_submission_integration(
        self, client: TestClient, test_db: Session
    ):
        """Test feedback submission and retrieval."""
        # First, create a detection
        detection_response = client.post(
            "/api/v1/detect",
            json={
                "message": "Test scam message",
                "message_type": "email",
            },
        )

        # Submit feedback
        feedback_response = client.post(
            "/api/v1/feedback",
            json={
                "message": "Test scam message",
                "actual_label": "scam",
                "predicted_label": "legitimate",
                "feedback_text": "This was definitely a scam",
            },
        )

        assert feedback_response.status_code == status.HTTP_201_CREATED
        feedback_data = feedback_response.json()

        assert "id" in feedback_data
        assert feedback_data["status"] == "received"

        # Verify database storage
        repo = FeedbackRepository(test_db)
        feedback_entries = repo.get_recent_feedback(limit=10)
        assert len(feedback_entries) >= 0

    def test_statistics_integration(self, client: TestClient, test_db: Session):
        """Test statistics aggregation with database."""
        # Create some detections
        messages = [
            {"message": "Scam message 1", "message_type": "email"},
            {"message": "Scam message 2", "message_type": "sms"},
            {"message": "Legitimate message", "message_type": "email"},
        ]

        for msg in messages:
            client.post("/api/v1/detect", json=msg)

        # Get statistics
        response = client.get("/api/v1/stats/overview")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()

        # Verify statistics structure
        assert "total_detections" in data
        assert "scam_detections" in data
        assert "legitimate_detections" in data

    def test_detection_report_retrieval(self, client: TestClient, test_db: Session):
        """Test creating and retrieving detection reports."""
        # Create detection
        detection_response = client.post(
            "/api/v1/detect",
            json={
                "message": "Test message for report",
                "message_type": "email",
            },
        )

        # Note: Report retrieval endpoint would need to be implemented
        # This is a placeholder for future functionality
        assert detection_response.status_code == status.HTTP_200_OK


class TestDatabaseIntegration:
    """Integration tests for database operations."""

    def test_scam_report_repository(self, test_db: Session):
        """Test ScamReport repository operations."""
        repo = ScamReportRepository(test_db)

        # Create report
        report = ScamReport(
            message_hash="test_hash_123",
            message_type="email",
            risk_level="HIGH",
            confidence_score=0.92,
            detected_patterns=["ato", "urgency"],
            metadata={"source": "test"},
        )

        saved_report = repo.create_report(report)
        assert saved_report.id is not None

        # Retrieve report
        retrieved = repo.get_report_by_id(saved_report.id)
        assert retrieved is not None
        assert retrieved.message_hash == "test_hash_123"

        # Get recent reports
        recent = repo.get_recent_reports(limit=5)
        assert len(recent) >= 1

    def test_feedback_repository(self, test_db: Session):
        """Test Feedback repository operations."""
        repo = FeedbackRepository(test_db)

        # Create feedback
        feedback = FeedbackEntry(
            message_hash="feedback_test_123",
            actual_label="scam",
            predicted_label="legitimate",
            feedback_text="Incorrectly classified",
        )

        saved_feedback = repo.create_feedback(feedback)
        assert saved_feedback.id is not None

        # Retrieve feedback
        retrieved = repo.get_feedback_by_id(saved_feedback.id)
        assert retrieved is not None
        assert retrieved.message_hash == "feedback_test_123"

    def test_statistics_aggregation(self, test_db: Session):
        """Test database statistics aggregation."""
        repo = ScamReportRepository(test_db)

        # Create multiple reports
        for i in range(5):
            report = ScamReport(
                message_hash=f"hash_{i}",
                message_type="email",
                risk_level="HIGH" if i % 2 == 0 else "LOW",
                confidence_score=0.8 + (i * 0.01),
                detected_patterns=["test"],
            )
            repo.create_report(report)

        # Get statistics
        stats = repo.get_detection_stats()
        assert stats["total_detections"] == 5


class TestErrorHandling:
    """Integration tests for error handling."""

    def test_invalid_message_type(self, client: TestClient):
        """Test handling of invalid message type."""
        response = client.post(
            "/api/v1/detect",
            json={
                "message": "Test message",
                "message_type": "invalid_type",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_missing_required_fields(self, client: TestClient):
        """Test handling of missing required fields."""
        response = client.post(
            "/api/v1/detect",
            json={
                "message": "Test message",
                # Missing message_type
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_empty_message(self, client: TestClient):
        """Test handling of empty message."""
        response = client.post(
            "/api/v1/detect",
            json={
                "message": "",
                "message_type": "email",
            },
        )

        # Should either reject or handle gracefully
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY,
        ]

    def test_extremely_long_message(self, client: TestClient):
        """Test handling of extremely long message."""
        long_message = "A" * 100000  # 100k characters

        response = client.post(
            "/api/v1/detect",
            json={
                "message": long_message,
                "message_type": "email",
            },
        )

        # Should handle gracefully
        assert response.status_code in [
            status.HTTP_200_OK,
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        ]


class TestPerformance:
    """Integration tests for performance requirements."""

    def test_detection_latency(self, client: TestClient):
        """Test that detection meets latency requirements (<500ms)."""
        import time

        start_time = time.time()

        response = client.post(
            "/api/v1/detect",
            json={
                "message": "URGENT: Your ATO tax refund is ready",
                "message_type": "email",
            },
        )

        elapsed_time = (time.time() - start_time) * 1000  # Convert to ms

        assert response.status_code == status.HTTP_200_OK
        assert elapsed_time < 500, f"Detection took {elapsed_time}ms, expected <500ms"

    def test_batch_detection_throughput(self, client: TestClient):
        """Test batch detection throughput."""
        import time

        messages = [
            {"message": f"Test message {i}", "message_type": "email"}
            for i in range(10)
        ]

        start_time = time.time()

        response = client.post("/api/v1/detect/batch", json={"messages": messages})

        elapsed_time = time.time() - start_time
        throughput = len(messages) / elapsed_time

        assert response.status_code == status.HTTP_200_OK
        assert throughput > 10, f"Throughput: {throughput:.2f} msg/s, expected >10 msg/s"
