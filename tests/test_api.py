"""
API Tests
~~~~~~~~~

Basic tests for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns correct response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Scam Detection API"


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data


def test_readiness_endpoint():
    """Test readiness check endpoint."""
    response = client.get("/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "ready"


# TODO: Add more tests when detection endpoints are implemented
# def test_detect_scam_endpoint():
#     """Test scam detection endpoint."""
#     response = client.post(
#         "/api/v1/detect",
#         json={
#             "message": "URGENT: Your ATO tax refund is ready",
#             "type": "email",
#             "metadata": {"sender": "scam@example.com"}
#         }
#     )
#     assert response.status_code == 200
#     data = response.json()
#     assert "scam_probability" in data
#     assert "risk_level" in data
