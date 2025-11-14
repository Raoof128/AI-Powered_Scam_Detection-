#!/usr/bin/env python3
"""
Sample Data Generator
~~~~~~~~~~~~~~~~~~~~~

Generate synthetic scam and legitimate message samples for testing and training.
"""

import csv
import random
from pathlib import Path
from typing import List, Tuple

# Australian scam templates
SCAM_TEMPLATES = [
    # ATO Scams
    ("URGENT: Your ATO tax refund of ${} is ready. Click here: {} to claim now.", "ato_impersonation", 1),
    ("Final notice from ATO. You owe ${} in unpaid taxes. Pay immediately or face legal action.", "ato_impersonation", 1),
    ("Your tax return has been processed. Refund of ${} pending. Verify your ABN {} at {}.", "ato_impersonation", 1),
    ("Australian Taxation Office: Urgent action required. Update your TFN {} details at {}.", "ato_impersonation", 1),

    # MyGov Scams
    ("Your MyGov account has been suspended. Verify identity at {} to restore access.", "mygov_impersonation", 1),
    ("Centrelink payment of ${} available. Confirm details at {} to receive funds.", "mygov_impersonation", 1),
    ("Medicare: Update your details within 24 hours or lose benefits. Visit {}.", "mygov_impersonation", 1),
    ("myGov alert: Unusual activity detected. Secure your account now at {}.", "mygov_impersonation", 1),

    # Banking Scams
    ("CBA Alert: Suspicious transaction of ${} detected. Verify at {}.", "banking_scam", 1),
    ("NAB Security: Your account has been locked. Unlock at {} immediately.", "banking_scam", 1),
    ("Westpac: Update your payment details to avoid account suspension. Click {}.", "banking_scam", 1),
    ("ANZ: Unusual login attempt detected. Confirm your identity at {}.", "banking_scam", 1),

    # Delivery Scams
    ("Australia Post: Package waiting. Pay ${} customs fee at {} for delivery.", "delivery_scam", 1),
    ("Auspost: Failed delivery attempt. Reschedule at {} within 48 hours.", "delivery_scam", 1),
    ("Your parcel requires additional payment of ${}. Pay at {} to avoid return to sender.", "delivery_scam", 1),
    ("Toll: Delivery delayed. Update details at {} to receive package.", "delivery_scam", 1),

    # Phone/Tech Scams
    ("NBN: Your internet service requires upgrade. Call {} to avoid disconnection.", "phone_scam", 1),
    ("Microsoft Support: Virus detected on your computer. Call {} immediately.", "phone_scam", 1),
    ("Telstra: Refund of ${} available for overcharges. Claim at {}.", "phone_scam", 1),

    # Generic Scams
    ("Congratulations! You've won ${}. Claim prize at {}.", "lottery_scam", 1),
    ("URGENT: Account compromised. Reset password at {}.", "phishing", 1),
    ("Click here {} to claim your reward of ${}. Limited time offer!", "phishing", 1),
]

# Legitimate message templates
LEGITIMATE_TEMPLATES = [
    ("Your order #{} has been shipped and will arrive by {}.", "notification", 0),
    ("Meeting reminder: Team sync tomorrow at 2pm in conference room B.", "reminder", 0),
    ("Hi! Hope you're doing well. Let's catch up for coffee next week.", "personal", 0),
    ("Your subscription to {} is expiring on {}. Renew on our website.", "subscription", 0),
    ("Thanks for your purchase! Order #{} is being processed.", "confirmation", 0),
    ("Welcome to {}! We're excited to have you join our community.", "welcome", 0),
    ("Your appointment is scheduled for {} at {}. See you then!", "appointment", 0),
    ("Project update: Phase 1 completed successfully. Moving to Phase 2.", "work", 0),
    ("Don't forget: Event registration closes on {}.", "reminder", 0),
    ("Check out our latest blog post: {} - available on our website.", "marketing", 0),
]

# Suspicious URLs for scams
SUSPICIOUS_URLS = [
    "http://bit.ly/{}",
    "http://tinyurl.com/{}",
    "http://ato-refund.com.au",
    "http://mygov-verify.tk",
    "http://secure-banking.xyz",
    "http://auspost-delivery.ml",
    "http://192.168.1.{}/verify",
]

# Legitimate URLs
LEGITIMATE_URLS = [
    "https://www.example.com",
    "https://shop.example.com",
    "https://company.com.au",
]


def generate_scam_message() -> Tuple[str, str, int]:
    """Generate a random scam message."""
    template, category, label = random.choice(SCAM_TEMPLATES)

    # Fill in placeholders
    amount = random.randint(100, 5000)
    abn = f"{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
    tfn = f"{random.randint(100, 999)} {random.randint(100, 999)} {random.randint(100, 999)}"
    url = random.choice(SUSPICIOUS_URLS).format(random.randint(10000, 99999))

    # Count format specifiers
    format_count = template.count("{}")

    if format_count == 0:
        message = template
    elif format_count == 1:
        message = template.format(random.choice([amount, url, abn]))
    elif format_count == 2:
        message = template.format(amount, url)
    else:
        message = template.format(amount, abn, url)

    return message, category, label


def generate_legitimate_message() -> Tuple[str, str, int]:
    """Generate a random legitimate message."""
    template, category, label = random.choice(LEGITIMATE_TEMPLATES)

    # Fill in placeholders
    order_num = random.randint(100000, 999999)
    date = f"2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}"
    service = random.choice(["Netflix", "Spotify", "Amazon Prime", "Microsoft 365"])
    url = random.choice(LEGITIMATE_URLS)

    # Count format specifiers
    format_count = template.count("{}")

    if format_count == 0:
        message = template
    elif format_count == 1:
        message = template.format(random.choice([order_num, date, service, url]))
    elif format_count == 2:
        message = template.format(order_num, date)
    else:
        message = template

    return message, category, label


def generate_dataset(num_samples: int = 10000, scam_ratio: float = 0.4) -> List[Tuple[str, str, int]]:
    """
    Generate a balanced dataset of scam and legitimate messages.

    Args:
        num_samples: Total number of samples to generate
        scam_ratio: Ratio of scam messages (0-1)

    Returns:
        List of (message, category, label) tuples
    """
    dataset = []

    num_scams = int(num_samples * scam_ratio)
    num_legitimate = num_samples - num_scams

    print(f"Generating {num_scams} scam messages...")
    for _ in range(num_scams):
        dataset.append(generate_scam_message())

    print(f"Generating {num_legitimate} legitimate messages...")
    for _ in range(num_legitimate):
        dataset.append(generate_legitimate_message())

    # Shuffle the dataset
    random.shuffle(dataset)

    return dataset


def save_to_csv(dataset: List[Tuple[str, str, int]], output_path: Path) -> None:
    """Save dataset to CSV file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['message', 'category', 'label'])
        writer.writerows(dataset)

    print(f"✅ Dataset saved to {output_path}")


def main():
    """Main function to generate and save dataset."""
    print("🚀 Sample Data Generator for Scam Detection")
    print("=" * 60)

    # Generate dataset
    dataset = generate_dataset(num_samples=10000, scam_ratio=0.4)

    # Save to CSV
    output_path = Path("data/raw/sample_scams.csv")
    save_to_csv(dataset, output_path)

    # Print statistics
    scam_count = sum(1 for _, _, label in dataset if label == 1)
    legitimate_count = len(dataset) - scam_count

    print("\n📊 Dataset Statistics:")
    print(f"  Total samples: {len(dataset)}")
    print(f"  Scam messages: {scam_count} ({scam_count/len(dataset)*100:.1f}%)")
    print(f"  Legitimate messages: {legitimate_count} ({legitimate_count/len(dataset)*100:.1f}%)")

    # Show sample messages
    print("\n📝 Sample Messages:")
    print("\nScam Examples:")
    for msg, cat, lbl in dataset[:3]:
        if lbl == 1:
            print(f"  - [{cat}] {msg[:80]}...")

    print("\nLegitimate Examples:")
    for msg, cat, lbl in dataset[:10]:
        if lbl == 0:
            print(f"  - [{cat}] {msg[:80]}...")
            break

    print("\n✨ Done! Use this data for model training and testing.")


if __name__ == "__main__":
    random.seed(42)  # For reproducibility
    main()
