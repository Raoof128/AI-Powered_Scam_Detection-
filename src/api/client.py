"""
API Client
~~~~~~~~~~

Python client library for the Scam Detection API.
"""

from typing import Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScamDetectorClient:
    """Client for interacting with the Scam Detection API."""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3
    ) -> None:
        """
        Initialize the scam detector client.

        Args:
            base_url: Base URL of the API
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        # Configure session with retries
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS", "TRACE"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "User-Agent": "ScamDetectorClient/0.1.0"
        })

        if api_key:
            self.session.headers.update({"X-API-Key": api_key})

        logger.info(f"Scam detector client initialized for {base_url}")

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make a request to the API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for requests

        Returns:
            Response JSON

        Raises:
            requests.HTTPError: If request fails
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

    def detect(
        self,
        message: str,
        message_type: str = "other",
        metadata: Optional[Dict] = None,
        include_explanation: bool = True
    ) -> Dict:
        """
        Detect if a message is a scam.

        Args:
            message: Text content to analyze
            message_type: Type of message (email, sms, call, url, other)
            metadata: Additional metadata about the message
            include_explanation: Whether to include detailed explanation

        Returns:
            Detection result dictionary

        Example:
            >>> client = ScamDetectorClient()
            >>> result = client.detect(
            ...     message="URGENT: Your ATO tax refund is ready",
            ...     message_type="email"
            ... )
            >>> print(result['risk_level'])
            'high'
        """
        payload = {
            "message": message,
            "message_type": message_type,
            "metadata": metadata or {},
            "include_explanation": include_explanation
        }

        logger.info(f"Detecting scam for message type: {message_type}")
        return self._request("POST", "/api/v1/detect", json=payload)

    def batch_detect(
        self,
        messages: List[Dict],
        include_explanation: bool = True
    ) -> Dict:
        """
        Detect scams in multiple messages.

        Args:
            messages: List of messages to analyze
            include_explanation: Whether to include detailed explanation

        Returns:
            Batch detection results

        Example:
            >>> client = ScamDetectorClient()
            >>> messages = [
            ...     {"message": "Tax refund available", "message_type": "email"},
            ...     {"message": "Meeting at 2pm", "message_type": "other"}
            ... ]
            >>> results = client.batch_detect(messages)
            >>> print(len(results['results']))
            2
        """
        payload = {
            "messages": messages,
            "include_explanation": include_explanation
        }

        logger.info(f"Batch detecting {len(messages)} messages")
        return self._request("POST", "/api/v1/detect/batch", json=payload)

    def submit_feedback(
        self,
        report_id: str,
        user_feedback: str,
        corrected_label: Optional[str] = None,
        feedback_text: Optional[str] = None
    ) -> Dict:
        """
        Submit feedback on a detection result.

        Args:
            report_id: ID of the detection report
            user_feedback: User's feedback (e.g., 'correct', 'false_positive')
            corrected_label: Corrected label if prediction was wrong
            feedback_text: Additional comments

        Returns:
            Feedback submission confirmation

        Example:
            >>> client = ScamDetectorClient()
            >>> feedback = client.submit_feedback(
            ...     report_id="550e8400-e29b-41d4-a716-446655440000",
            ...     user_feedback="false_positive",
            ...     feedback_text="This was actually a legitimate message"
            ... )
        """
        payload = {
            "report_id": report_id,
            "user_feedback": user_feedback,
            "corrected_label": corrected_label,
            "feedback_text": feedback_text
        }

        logger.info(f"Submitting feedback for report: {report_id}")
        return self._request("POST", "/api/v1/feedback", json=payload)

    def get_report(self, report_id: str) -> Dict:
        """
        Get a detection report by ID.

        Args:
            report_id: Report UUID

        Returns:
            Detection report

        Example:
            >>> client = ScamDetectorClient()
            >>> report = client.get_report("550e8400-e29b-41d4-a716-446655440000")
        """
        return self._request("GET", f"/api/v1/report/{report_id}")

    def get_stats(self, days: int = 30) -> Dict:
        """
        Get overall statistics.

        Args:
            days: Number of days to include in statistics

        Returns:
            Statistics dictionary

        Example:
            >>> client = ScamDetectorClient()
            >>> stats = client.get_stats(days=7)
            >>> print(stats['performance']['accuracy'])
            0.942
        """
        return self._request("GET", f"/api/v1/stats/overview?days={days}")

    def get_summary(self) -> Dict:
        """
        Get summary statistics.

        Returns:
            Summary statistics

        Example:
            >>> client = ScamDetectorClient()
            >>> summary = client.get_summary()
            >>> print(summary['total_reports_all_time'])
            1250
        """
        return self._request("GET", "/api/v1/stats/summary")

    def health_check(self) -> Dict:
        """
        Check API health.

        Returns:
            Health status

        Example:
            >>> client = ScamDetectorClient()
            >>> health = client.health_check()
            >>> assert health['status'] == 'healthy'
        """
        return self._request("GET", "/health")

    def detailed_health_check(self) -> Dict:
        """
        Get detailed health status.

        Returns:
            Detailed health status

        Example:
            >>> client = ScamDetectorClient()
            >>> health = client.detailed_health_check()
            >>> print(health['models_loaded'])
            True
        """
        return self._request("GET", "/health/detailed")

    def close(self) -> None:
        """Close the session."""
        self.session.close()
        logger.info("Client session closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Convenience function
def detect_scam(message: str, **kwargs) -> Dict:
    """
    Convenience function to detect a single scam.

    Args:
        message: Message to analyze
        **kwargs: Additional arguments for ScamDetectorClient

    Returns:
        Detection result

    Example:
        >>> result = detect_scam("URGENT: Tax refund available")
        >>> print(result['risk_level'])
        'high'
    """
    with ScamDetectorClient() as client:
        return client.detect(message, **kwargs)
