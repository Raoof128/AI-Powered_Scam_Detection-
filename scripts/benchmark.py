#!/usr/bin/env python3
"""
Performance Benchmarking Script
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Benchmark the scam detection platform for performance metrics.
"""

import statistics
import sys
import time
from pathlib import Path
from typing import List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.client import ScamDetectorClient


class PerformanceBenchmark:
    """Performance benchmarking for scam detection."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize benchmark."""
        self.client = ScamDetectorClient(base_url=base_url)
        self.results = []

    def benchmark_single_detection(self, iterations: int = 100) -> dict:
        """
        Benchmark single message detection.

        Args:
            iterations: Number of iterations to run

        Returns:
            Benchmark results
        """
        print(f"\n{'='*60}")
        print(f"Benchmarking Single Detection ({iterations} iterations)")
        print(f"{'='*60}")

        test_message = "URGENT: Your ATO tax refund of $2,450 is ready. Click here to claim."
        latencies = []

        for i in range(iterations):
            start = time.time()
            try:
                result = self.client.detect(message=test_message, message_type="email")
                latency_ms = (time.time() - start) * 1000
                latencies.append(latency_ms)

                if (i + 1) % 10 == 0:
                    print(f"  Progress: {i+1}/{iterations} requests completed")

            except Exception as e:
                print(f"  Error on iteration {i+1}: {e}")
                continue

        # Calculate statistics
        results = {
            "test": "single_detection",
            "iterations": len(latencies),
            "avg_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies),
            "p95_latency_ms": self._percentile(latencies, 95),
            "p99_latency_ms": self._percentile(latencies, 99),
            "stdev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0,
        }

        self._print_results(results)
        return results

    def benchmark_batch_detection(
        self, batch_size: int = 10, iterations: int = 10
    ) -> dict:
        """
        Benchmark batch message detection.

        Args:
            batch_size: Number of messages per batch
            iterations: Number of batch iterations

        Returns:
            Benchmark results
        """
        print(f"\n{'='*60}")
        print(f"Benchmarking Batch Detection ({iterations} batches of {batch_size})")
        print(f"{'='*60}")

        test_messages = [
            {"message": f"Test message {i}", "message_type": "email"}
            for i in range(batch_size)
        ]

        latencies = []
        throughput = []

        for i in range(iterations):
            start = time.time()
            try:
                result = self.client.batch_detect(test_messages)
                elapsed = time.time() - start
                latency_ms = elapsed * 1000
                msgs_per_sec = batch_size / elapsed

                latencies.append(latency_ms)
                throughput.append(msgs_per_sec)

                print(f"  Batch {i+1}/{iterations}: {latency_ms:.1f}ms, {msgs_per_sec:.1f} msg/s")

            except Exception as e:
                print(f"  Error on batch {i+1}: {e}")
                continue

        # Calculate statistics
        results = {
            "test": "batch_detection",
            "batch_size": batch_size,
            "iterations": len(latencies),
            "avg_latency_ms": statistics.mean(latencies),
            "avg_throughput_msgs_per_sec": statistics.mean(throughput),
            "median_latency_ms": statistics.median(latencies),
            "p95_latency_ms": self._percentile(latencies, 95),
            "max_throughput_msgs_per_sec": max(throughput),
        }

        self._print_results(results)
        return results

    def benchmark_australian_patterns(self, iterations: int = 50) -> dict:
        """
        Benchmark Australian-specific pattern detection.

        Args:
            iterations: Number of iterations

        Returns:
            Benchmark results
        """
        print(f"\n{'='*60}")
        print(f"Benchmarking Australian Pattern Detection ({iterations} iterations)")
        print(f"{'='*60}")

        test_cases = [
            "URGENT: Your ATO tax refund of $2,450 is ready",
            "Your MyGov account has been suspended. Verify now",
            "CBA Security: Suspicious transaction detected",
            "Australia Post: Package waiting. Pay customs fee",
            "NBN: Your internet service will be disconnected",
        ]

        latencies = []
        pattern_detections = []

        for i in range(iterations):
            message = test_cases[i % len(test_cases)]
            start = time.time()

            try:
                result = self.client.detect(message=message, message_type="email")
                latency_ms = (time.time() - start) * 1000
                latencies.append(latency_ms)

                # Count patterns detected
                pattern_count = len(result.get("detected_patterns", []))
                pattern_detections.append(pattern_count)

            except Exception as e:
                print(f"  Error on iteration {i+1}: {e}")
                continue

        results = {
            "test": "australian_patterns",
            "iterations": len(latencies),
            "avg_latency_ms": statistics.mean(latencies),
            "avg_patterns_detected": statistics.mean(pattern_detections),
            "total_patterns_detected": sum(pattern_detections),
        }

        self._print_results(results)
        return results

    def run_full_benchmark(self) -> dict:
        """Run complete benchmark suite."""
        print("\n" + "="*60)
        print("🚀 Starting Performance Benchmark Suite")
        print("="*60)
        print(f"Target: http://localhost:8000")

        # Check API is available
        try:
            health = self.client.health_check()
            print(f"✅ API Status: {health['status']}")
        except Exception as e:
            print(f"❌ Error: Cannot connect to API - {e}")
            print("Make sure the API is running: docker-compose up -d")
            return {}

        all_results = {
            "single_detection": self.benchmark_single_detection(iterations=100),
            "batch_detection": self.benchmark_batch_detection(batch_size=10, iterations=10),
            "australian_patterns": self.benchmark_australian_patterns(iterations=50),
        }

        self._print_summary(all_results)
        return all_results

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile."""
        sorted_data = sorted(data)
        index = int((percentile / 100) * len(sorted_data))
        return sorted_data[min(index, len(sorted_data) - 1)]

    @staticmethod
    def _print_results(results: dict) -> None:
        """Print formatted results."""
        print(f"\n📊 Results:")
        for key, value in results.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")

    @staticmethod
    def _print_summary(all_results: dict) -> None:
        """Print summary of all benchmarks."""
        print("\n" + "="*60)
        print("📈 Benchmark Summary")
        print("="*60)

        single = all_results.get("single_detection", {})
        batch = all_results.get("batch_detection", {})
        patterns = all_results.get("australian_patterns", {})

        print(f"\n🎯 Single Detection Performance:")
        print(f"  Average Latency: {single.get('avg_latency_ms', 0):.1f}ms")
        print(f"  Median Latency: {single.get('median_latency_ms', 0):.1f}ms")
        print(f"  P95 Latency: {single.get('p95_latency_ms', 0):.1f}ms")
        print(f"  P99 Latency: {single.get('p99_latency_ms', 0):.1f}ms")

        print(f"\n📦 Batch Detection Performance:")
        print(f"  Average Latency: {batch.get('avg_latency_ms', 0):.1f}ms")
        print(f"  Throughput: {batch.get('avg_throughput_msgs_per_sec', 0):.1f} msg/s")

        print(f"\n🇦🇺 Australian Pattern Detection:")
        print(f"  Average Latency: {patterns.get('avg_latency_ms', 0):.1f}ms")
        print(f"  Avg Patterns per Message: {patterns.get('avg_patterns_detected', 0):.2f}")

        print(f"\n{'='*60}")
        print("✅ Benchmark Complete!")
        print("="*60 + "\n")


def main():
    """Run benchmark."""
    benchmark = PerformanceBenchmark()
    benchmark.run_full_benchmark()


if __name__ == "__main__":
    main()
