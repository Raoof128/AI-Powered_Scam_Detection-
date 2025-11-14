#!/usr/bin/env python3
"""
Basic Usage Examples
~~~~~~~~~~~~~~~~~~~~

Simple examples demonstrating the Scam Detector API.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.client import ScamDetectorClient


def example_1_basic_detection():
    """Example 1: Basic scam detection."""
    print("\n" + "="*60)
    print("Example 1: Basic Scam Detection")
    print("="*60)

    client = ScamDetectorClient(base_url="http://localhost:8000")

    # Scam message
    result = client.detect(
        message="URGENT: Your ATO tax refund of $2,450 is ready. Click here to claim now!",
        message_type="email"
    )

    print(f"\n📧 Message: {result.get('detected_patterns', [{}])[0] if result.get('detected_patterns') else 'Unknown'}")
    print(f"🎯 Scam Probability: {result['scam_probability']:.2%}")
    print(f"⚠️  Risk Level: {result['risk_level'].upper()}")
    print(f"⏱️  Processing Time: {result['processing_time_ms']}ms")

    if result.get('detected_patterns'):
        print(f"\n🔍 Detected Patterns:")
        for pattern in result['detected_patterns']:
            print(f"  - {pattern['pattern_name']}: {pattern['confidence']:.2%} confidence")

    if result.get('recommendations'):
        print(f"\n💡 Recommendations:")
        for rec in result['recommendations'][:3]:
            print(f"  {rec}")


def example_2_legitimate_message():
    """Example 2: Legitimate message detection."""
    print("\n" + "="*60)
    print("Example 2: Legitimate Message")
    print("="*60)

    client = ScamDetectorClient(base_url="http://localhost:8000")

    result = client.detect(
        message="Your Amazon order #12345 has been shipped and will arrive by Friday.",
        message_type="email"
    )

    print(f"\n📧 Message: Order confirmation")
    print(f"🎯 Scam Probability: {result['scam_probability']:.2%}")
    print(f"✅ Risk Level: {result['risk_level'].upper()}")
    print(f"⏱️  Processing Time: {result['processing_time_ms']}ms")


def example_3_australian_patterns():
    """Example 3: Australian-specific scam detection."""
    print("\n" + "="*60)
    print("Example 3: Australian-Specific Scams")
    print("="*60)

    client = ScamDetectorClient(base_url="http://localhost:8000")

    messages = [
        ("MyGov account suspended. Verify now.", "mygov_impersonation"),
        ("CBA: Suspicious transaction detected.", "banking_scam"),
        ("Australia Post: Package waiting. Pay fee.", "delivery_scam"),
    ]

    for msg, expected in messages:
        result = client.detect(message=msg, message_type="sms")
        print(f"\n📱 SMS: {msg[:50]}...")
        print(f"   Risk: {result['risk_level'].upper()} | Probability: {result['scam_probability']:.2%}")
        print(f"   Australian-specific: {'Yes' if result.get('australian_specific') else 'No'}")


def example_4_batch_detection():
    """Example 4: Batch detection."""
    print("\n" + "="*60)
    print("Example 4: Batch Detection")
    print("="*60)

    client = ScamDetectorClient(base_url="http://localhost:8000")

    messages = [
        {"message": "URGENT: Tax refund available", "message_type": "email"},
        {"message": "Meeting at 2pm tomorrow", "message_type": "other"},
        {"message": "Your parcel needs customs fee payment", "message_type": "sms"},
        {"message": "Hi! How are you doing?", "message_type": "other"},
    ]

    result = client.batch_detect(messages)

    print(f"\n📦 Processed {result['total_processed']} messages")
    print(f"⏱️  Total time: {result['total_processing_time_ms']}ms")
    print(f"📊 Average: {result['average_processing_time_ms']:.1f}ms per message")

    print(f"\n📋 Results:")
    for i, res in enumerate(result['results'], 1):
        print(f"  {i}. {res['risk_level'].upper():8} - {res['scam_probability']:.2%} probability")


def example_5_statistics():
    """Example 5: Get statistics."""
    print("\n" + "="*60)
    print("Example 5: Platform Statistics")
    print("="*60)

    client = ScamDetectorClient(base_url="http://localhost:8000")

    try:
        summary = client.get_summary()

        print(f"\n📊 Summary Statistics:")
        print(f"  Total Reports (All Time): {summary.get('total_reports_all_time', 0)}")

        last_7 = summary.get('last_7_days', {})
        print(f"\n📅 Last 7 Days:")
        print(f"  Total: {last_7.get('total', 0)}")
        print(f"  High Risk: {last_7.get('high_risk', 0)}")
        print(f"  Medium Risk: {last_7.get('medium_risk', 0)}")
        print(f"  Low Risk: {last_7.get('low_risk', 0)}")
        print(f"  Australian-specific: {last_7.get('australian_specific', 0)}")

    except Exception as e:
        print(f"⚠️  Could not fetch statistics: {e}")


def example_6_health_check():
    """Example 6: Health check."""
    print("\n" + "="*60)
    print("Example 6: System Health Check")
    print("="*60)

    client = ScamDetectorClient(base_url="http://localhost:8000")

    try:
        health = client.detailed_health_check()

        print(f"\n🏥 System Status: {health['status'].upper()}")
        print(f"  Version: {health['version']}")
        print(f"  Uptime: {health['uptime_seconds']:.0f}s")
        print(f"  Memory: {health['memory_usage_mb']:.1f} MB")
        print(f"  CPU: {health['cpu_usage_percent']:.1f}%")
        print(f"  Database: {'✅ Connected' if health['database_connected'] else '❌ Disconnected'}")

    except Exception as e:
        print(f"⚠️  Could not check health: {e}")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("🛡️  AI-Powered Scam Detection - Usage Examples")
    print("="*60)
    print("\nMake sure the API is running: docker-compose up -d")
    print("Or: uvicorn src.api.main:app --reload")

    try:
        example_1_basic_detection()
        example_2_legitimate_message()
        example_3_australian_patterns()
        example_4_batch_detection()
        example_5_statistics()
        example_6_health_check()

        print("\n" + "="*60)
        print("✅ All examples completed successfully!")
        print("="*60 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("Make sure the API server is running on http://localhost:8000")
        sys.exit(1)


if __name__ == "__main__":
    main()
