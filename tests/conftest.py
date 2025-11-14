"""
Pytest Configuration and Shared Fixtures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Shared test fixtures for unit, integration, and E2E tests.
"""

import os
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.api.main import app
from src.database.models import Base
from src.utils.config import Settings, get_settings


# Test database URL
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """
    Create test settings.

    Returns:
        Test configuration settings
    """
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    os.environ["DEBUG"] = "true"
    return get_settings()


@pytest.fixture(scope="function")
def test_db() -> Generator[Session, None, None]:
    """
    Create a fresh test database for each test.

    Yields:
        Database session
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(test_db: Session) -> TestClient:
    """
    Create a test client with database override.

    Args:
        test_db: Test database session

    Returns:
        FastAPI test client
    """
    from src.database.connection import get_db

    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_scam_messages():
    """
    Sample scam messages for testing.

    Returns:
        List of sample scam messages
    """
    return [
        {
            "message": "URGENT: Your ATO tax refund of $2,450 is ready. Click here: http://ato-refund-au.com",
            "message_type": "email",
            "expected_risk": "HIGH",
            "patterns": ["ATO", "urgent", "suspicious_url"],
        },
        {
            "message": "Your MyGov account has been suspended. Verify now: https://mygov-verify.net",
            "message_type": "email",
            "expected_risk": "HIGH",
            "patterns": ["MyGov", "account_suspension", "suspicious_url"],
        },
        {
            "message": "CBA Security Alert: Unusual activity detected. Click to secure account.",
            "message_type": "sms",
            "expected_risk": "MEDIUM",
            "patterns": ["banking", "urgency"],
        },
        {
            "message": "Australia Post: Your package is waiting. Pay $5.99 customs fee.",
            "message_type": "sms",
            "expected_risk": "MEDIUM",
            "patterns": ["delivery", "payment_request"],
        },
        {
            "message": "Hi mate, this is just a regular message about meeting for coffee.",
            "message_type": "sms",
            "expected_risk": "LOW",
            "patterns": [],
        },
    ]


@pytest.fixture
def sample_legitimate_messages():
    """
    Sample legitimate messages for testing.

    Returns:
        List of sample legitimate messages
    """
    return [
        {
            "message": "Your appointment is confirmed for tomorrow at 2pm.",
            "message_type": "sms",
        },
        {
            "message": "Thank you for your order. Your tracking number is 12345.",
            "message_type": "email",
        },
        {
            "message": "Meeting reminder: Team standup at 10am in conference room.",
            "message_type": "email",
        },
        {
            "message": "Your subscription has been renewed. Thank you for being a valued customer.",
            "message_type": "email",
        },
    ]
