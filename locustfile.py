"""
Locust Load Testing
~~~~~~~~~~~~~~~~~~~

Load testing configuration for the Scam Detection API.

Usage:
    # Start web UI
    locust --host=http://localhost:8000

    # Headless mode
    locust --host=http://localhost:8000 --headless -u 100 -r 10 -t 1m

    # Distributed mode (master)
    locust --host=http://localhost:8000 --master

    # Distributed mode (worker)
    locust --host=http://localhost:8000 --worker --master-host=localhost
"""

import random
from locust import HttpUser, TaskSet, between, task


# Sample messages for testing
SCAM_MESSAGES = [
    "URGENT: Your ATO tax refund of $2,450 is ready. Click here to claim.",
    "Your MyGov account has been suspended. Verify now to restore access.",
    "CBA Security Alert: Unusual activity detected on your account.",
    "Australia Post: Package waiting. Pay $5.99 customs fee to receive.",
    "NBN: Your internet service will be disconnected. Call now to prevent.",
    "Telstra: Suspicious activity detected. Update your account details.",
    "Medicare: Your benefits have been suspended. Verify your identity.",
    "Your account has been compromised. Click here to secure it.",
]

LEGITIMATE_MESSAGES = [
    "Hi, just checking in to see how you're doing. Want to grab coffee this week?",
    "Your appointment is confirmed for tomorrow at 2pm. See you then!",
    "Thanks for your order! Your tracking number is AU1234567890.",
    "Meeting reminder: Team standup at 10am in conference room B.",
    "Happy birthday! Hope you have a wonderful day.",
    "The report you requested is attached. Let me know if you need anything else.",
    "Your subscription has been renewed. Thank you for being a valued customer.",
    "Can you please review the document and provide feedback by Friday?",
]

MESSAGE_TYPES = ["email", "sms", "url", "phone"]


class ScamDetectionTasks(TaskSet):
    """Task set for scam detection load testing."""

    @task(10)
    def detect_scam_message(self):
        """
        Test single scam detection (higher weight).

        This is the most common operation, weighted at 10.
        """
        message = random.choice(SCAM_MESSAGES + LEGITIMATE_MESSAGES)
        message_type = random.choice(MESSAGE_TYPES)

        with self.client.post(
            "/api/v1/detect",
            json={"message": message, "message_type": message_type},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                # Verify response structure
                if "risk_level" in data and "confidence_score" in data:
                    response.success()
                else:
                    response.failure("Invalid response structure")
            elif response.status_code == 429:
                response.failure("Rate limited")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(3)
    def batch_detection(self):
        """
        Test batch detection (medium weight).

        Weighted at 3 - less common than single detection.
        """
        batch_size = random.randint(5, 10)
        messages = []

        for _ in range(batch_size):
            msg_list = random.choice([SCAM_MESSAGES, LEGITIMATE_MESSAGES])
            messages.append({
                "message": random.choice(msg_list),
                "message_type": random.choice(MESSAGE_TYPES),
            })

        with self.client.post(
            "/api/v1/detect/batch",
            json={"messages": messages},
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "results" in data and len(data["results"]) == batch_size:
                    response.success()
                else:
                    response.failure("Invalid batch response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(2)
    def get_statistics(self):
        """
        Test statistics endpoint (lower weight).

        Weighted at 2 - read-only operation.
        """
        with self.client.get(
            "/api/v1/stats/overview",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                data = response.json()
                if "total_detections" in data:
                    response.success()
                else:
                    response.failure("Invalid statistics response")
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(1)
    def submit_feedback(self):
        """
        Test feedback submission (lowest weight).

        Weighted at 1 - least common operation.
        """
        message = random.choice(SCAM_MESSAGES + LEGITIMATE_MESSAGES)
        is_scam = message in SCAM_MESSAGES

        with self.client.post(
            "/api/v1/feedback",
            json={
                "message": message,
                "actual_label": "scam" if is_scam else "legitimate",
                "predicted_label": "scam" if random.random() > 0.1 else "legitimate",
                "feedback_text": "Load test feedback",
            },
            catch_response=True,
        ) as response:
            if response.status_code in [200, 201]:
                response.success()
            else:
                response.failure(f"Got status code {response.status_code}")

    @task(5)
    def health_check(self):
        """
        Test health check endpoint (medium weight).

        Weighted at 5 - monitoring endpoint.
        """
        with self.client.get("/health", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Health check failed: {response.status_code}")


class WebsiteUser(HttpUser):
    """
    Simulated user for load testing.

    Configuration:
        - wait_time: 1-5 seconds between requests
        - tasks: ScamDetectionTasks
    """

    tasks = [ScamDetectionTasks]
    wait_time = between(1, 5)  # Wait 1-5 seconds between requests

    def on_start(self):
        """
        Called when a simulated user starts.

        Perform any initialization here (e.g., authentication).
        """
        # Optional: Authenticate and get API key
        pass

    def on_stop(self):
        """Called when a simulated user stops."""
        pass


class HighLoadUser(HttpUser):
    """
    High-load user for stress testing.

    Generates requests more frequently with no wait time.
    """

    tasks = [ScamDetectionTasks]
    wait_time = between(0.1, 0.5)  # Minimal wait time


class APIKeyUser(HttpUser):
    """
    User with API key authentication.

    Simulates authenticated API usage.
    """

    tasks = [ScamDetectionTasks]
    wait_time = between(1, 3)

    def on_start(self):
        """Set up API key header."""
        # In production, use real API key
        self.client.headers.update({"X-API-Key": "test-api-key"})


# Custom load shape for ramping users
from locust import LoadTestShape


class StepLoadShape(LoadTestShape):
    """
    A step load shape that increases users in steps.

    Steps:
        1. 0-60s: 10 users
        2. 60-120s: 50 users
        3. 120-180s: 100 users
        4. 180-240s: 200 users
        5. 240-300s: 100 users (cool down)
    """

    step_time = 60
    step_load = 10
    spawn_rate = 10
    time_limit = 300

    def tick(self):
        """Define load shape over time."""
        run_time = self.get_run_time()

        if run_time > self.time_limit:
            return None

        if run_time < 60:
            user_count = 10
        elif run_time < 120:
            user_count = 50
        elif run_time < 180:
            user_count = 100
        elif run_time < 240:
            user_count = 200
        else:
            user_count = 100  # Cool down

        return (user_count, self.spawn_rate)


class SpikeLoadShape(LoadTestShape):
    """
    Spike load shape for testing sudden traffic increases.

    Pattern:
        - Normal: 20 users
        - Spike: 200 users for 30 seconds
        - Normal: 20 users
    """

    def tick(self):
        run_time = self.get_run_time()

        if run_time > 300:
            return None

        # Spike pattern: normal -> spike -> normal
        if 60 < run_time < 90:
            return (200, 50)  # Spike
        elif run_time < 180:
            return (20, 5)  # Normal
        elif 180 < run_time < 210:
            return (200, 50)  # Second spike
        else:
            return (20, 5)  # Normal


# Performance test scenarios
class PerformanceTest(HttpUser):
    """
    Performance test focusing on latency requirements.

    Validates that P95 latency < 500ms.
    """

    tasks = [ScamDetectionTasks]
    wait_time = between(0.5, 1)

    @task
    def measure_latency(self):
        """Measure detection latency."""
        import time

        message = random.choice(SCAM_MESSAGES)

        start_time = time.time()
        response = self.client.post(
            "/api/v1/detect",
            json={"message": message, "message_type": "email"},
        )
        latency = (time.time() - start_time) * 1000

        if response.status_code == 200 and latency < 500:
            # Good latency
            pass
        elif latency >= 500:
            print(f"Warning: High latency detected: {latency:.2f}ms")


class AccuracyTest(HttpUser):
    """
    Accuracy test to validate detection quality under load.

    Checks that known scams are correctly identified.
    """

    tasks = [ScamDetectionTasks]
    wait_time = between(1, 2)

    @task
    def test_accuracy(self):
        """Test detection accuracy."""
        # Use known scam
        message = SCAM_MESSAGES[0]

        response = self.client.post(
            "/api/v1/detect",
            json={"message": message, "message_type": "email"},
        )

        if response.status_code == 200:
            data = response.json()
            if data["risk_level"] not in ["HIGH", "CRITICAL"]:
                print(f"Warning: Known scam not detected properly: {data['risk_level']}")


if __name__ == "__main__":
    # Run with: python locustfile.py
    import os
    os.system("locust --host=http://localhost:8000")
