"""
Australian-Specific Pattern Detection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specialized detectors for Australian scam patterns including ATO, MyGov,
banking, and delivery scams.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from src.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PatternMatch:
    """Represents a detected pattern match."""
    pattern_name: str
    confidence: float
    description: str
    severity: float
    matched_text: Optional[str] = None


class AustralianPatternDetector:
    """Detect Australian-specific scam patterns."""

    def __init__(self) -> None:
        """Initialize Australian pattern detector."""
        self._setup_patterns()
        logger.info("Australian pattern detector initialized")

    def _setup_patterns(self) -> None:
        """Set up pattern definitions."""
        # ATO Patterns
        self.ato_keywords = [
            "ato", "australian taxation office", "tax office",
            "tax refund", "tax return", "tax debt", "mygovid"
        ]

        self.ato_urgency = [
            "immediate action required", "urgent tax matter",
            "final notice", "overdue tax", "tax penalty"
        ]

        # MyGov Patterns
        self.mygov_keywords = [
            "mygov", "my gov", "mygovid", "my government",
            "centrelink", "medicare", "services australia"
        ]

        self.mygov_scams = [
            "account suspended", "verify your account",
            "update your details", "confirm your identity",
            "payment pending", "benefits available"
        ]

        # Banking Patterns
        self.australian_banks = [
            "commonwealth bank", "cba", "commbank",
            "nab", "national australia bank",
            "westpac", "anz", "bank of melbourne",
            "bankwest", "st george", "bendigo bank"
        ]

        self.banking_scams = [
            "unusual activity", "suspicious transaction",
            "account locked", "verify your card",
            "update payment details", "confirm transaction"
        ]

        # Delivery Patterns
        self.delivery_keywords = [
            "australia post", "auspost", "aus post",
            "toll", "startrack", "fastway",
            "customs", "border force", "parcel"
        ]

        self.delivery_scams = [
            "delivery failed", "customs fee",
            "unable to deliver", "parcel waiting",
            "additional charges", "redelivery fee"
        ]

        # Phone Scam Patterns
        self.phone_scams = [
            "nbn", "telstra", "optus", "vodafone",
            "microsoft support", "tech support",
            "computer issue", "virus detected"
        ]

        # Financial identifiers
        self.abn_pattern = r'\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b'  # ABN format
        self.tfn_pattern = r'\b\d{3}\s?\d{3}\s?\d{3}\b'  # TFN format
        self.bsb_pattern = r'\b\d{3}[-\s]?\d{3}\b'  # BSB format

        # Suspicious domains
        self.suspicious_tlds = [
            '.tk', '.ml', '.ga', '.cf', '.gq',  # Free domains
            '.xyz', '.top', '.click', '.link'
        ]

        self.fake_gov_domains = [
            'gov.au.com', 'gov-au', 'gov.com.au',
            'ato.com', 'myagov.com', 'australia-gov'
        ]

    def detect_ato_scam(self, text: str) -> Optional[PatternMatch]:
        """
        Detect ATO impersonation scams.

        Args:
            text: Text to analyze

        Returns:
            PatternMatch if detected, None otherwise
        """
        text_lower = text.lower()
        score = 0.0
        matched_elements = []

        # Check for ATO keywords
        for keyword in self.ato_keywords:
            if keyword in text_lower:
                score += 0.3
                matched_elements.append(keyword)

        # Check for urgency
        for urgency in self.ato_urgency:
            if urgency in text_lower:
                score += 0.2
                matched_elements.append(urgency)

        # Check for ABN/TFN mentions
        if re.search(self.abn_pattern, text):
            score += 0.2
            matched_elements.append("ABN pattern")

        if re.search(self.tfn_pattern, text):
            score += 0.3
            matched_elements.append("TFN pattern")

        # Check for financial requests
        financial_keywords = ["refund", "payment", "debt", "owing", "owed"]
        for keyword in financial_keywords:
            if keyword in text_lower:
                score += 0.1

        # Check for fake gov domains
        for domain in self.fake_gov_domains:
            if domain in text_lower:
                score += 0.4
                matched_elements.append(f"suspicious domain: {domain}")

        if score >= 0.4:
            confidence = min(score, 1.0)
            return PatternMatch(
                pattern_name="ato_impersonation",
                confidence=confidence,
                description="Australian Taxation Office impersonation detected",
                severity=1.0,
                matched_text=", ".join(matched_elements[:3])
            )

        return None

    def detect_mygov_scam(self, text: str) -> Optional[PatternMatch]:
        """
        Detect MyGov/Centrelink scams.

        Args:
            text: Text to analyze

        Returns:
            PatternMatch if detected, None otherwise
        """
        text_lower = text.lower()
        score = 0.0
        matched_elements = []

        # Check for MyGov keywords
        for keyword in self.mygov_keywords:
            if keyword in text_lower:
                score += 0.35
                matched_elements.append(keyword)

        # Check for common scam tactics
        for scam in self.mygov_scams:
            if scam in text_lower:
                score += 0.25
                matched_elements.append(scam)

        # Check for credential requests
        credential_keywords = ["password", "pin", "username", "login"]
        for keyword in credential_keywords:
            if keyword in text_lower:
                score += 0.2

        if score >= 0.5:
            confidence = min(score, 1.0)
            return PatternMatch(
                pattern_name="mygov_impersonation",
                confidence=confidence,
                description="MyGov/Centrelink impersonation detected",
                severity=0.95,
                matched_text=", ".join(matched_elements[:3])
            )

        return None

    def detect_banking_scam(self, text: str) -> Optional[PatternMatch]:
        """
        Detect Australian banking scams.

        Args:
            text: Text to analyze

        Returns:
            PatternMatch if detected, None otherwise
        """
        text_lower = text.lower()
        score = 0.0
        matched_elements = []

        # Check for bank names
        for bank in self.australian_banks:
            if bank in text_lower:
                score += 0.3
                matched_elements.append(bank)
                break  # Only count once

        # Check for banking scam tactics
        for scam in self.banking_scams:
            if scam in text_lower:
                score += 0.2
                matched_elements.append(scam)

        # Check for BSB pattern
        if re.search(self.bsb_pattern, text):
            score += 0.15
            matched_elements.append("BSB pattern")

        # Check for account number requests
        if "account number" in text_lower or "card number" in text_lower:
            score += 0.2

        if score >= 0.4:
            confidence = min(score, 1.0)
            return PatternMatch(
                pattern_name="banking_scam",
                confidence=confidence,
                description="Australian bank impersonation detected",
                severity=0.9,
                matched_text=", ".join(matched_elements[:3])
            )

        return None

    def detect_delivery_scam(self, text: str) -> Optional[PatternMatch]:
        """
        Detect Australia Post and delivery scams.

        Args:
            text: Text to analyze

        Returns:
            PatternMatch if detected, None otherwise
        """
        text_lower = text.lower()
        score = 0.0
        matched_elements = []

        # Check for delivery keywords
        for keyword in self.delivery_keywords:
            if keyword in text_lower:
                score += 0.3
                matched_elements.append(keyword)

        # Check for delivery scam tactics
        for scam in self.delivery_scams:
            if scam in text_lower:
                score += 0.25
                matched_elements.append(scam)

        # Check for payment requests
        payment_keywords = ["pay", "payment", "fee", "charge", "cost"]
        for keyword in payment_keywords:
            if keyword in text_lower:
                score += 0.1

        if score >= 0.4:
            confidence = min(score, 1.0)
            return PatternMatch(
                pattern_name="delivery_scam",
                confidence=confidence,
                description="Delivery/Australia Post scam detected",
                severity=0.7,
                matched_text=", ".join(matched_elements[:3])
            )

        return None

    def detect_phone_scam(self, text: str) -> Optional[PatternMatch]:
        """
        Detect phone/tech support scams.

        Args:
            text: Text to analyze

        Returns:
            PatternMatch if detected, None otherwise
        """
        text_lower = text.lower()
        score = 0.0
        matched_elements = []

        # Check for phone scam keywords
        for keyword in self.phone_scams:
            if keyword in text_lower:
                score += 0.25
                matched_elements.append(keyword)

        # Tech support indicators
        tech_keywords = ["refund", "subscription", "renewal", "virus", "infection"]
        for keyword in tech_keywords:
            if keyword in text_lower:
                score += 0.15

        if score >= 0.3:
            confidence = min(score, 1.0)
            return PatternMatch(
                pattern_name="phone_scam",
                confidence=confidence,
                description="Phone/tech support scam detected",
                severity=0.65,
                matched_text=", ".join(matched_elements[:3])
            )

        return None

    def detect_url_patterns(self, text: str) -> Optional[PatternMatch]:
        """
        Detect suspicious URLs and domains.

        Args:
            text: Text to analyze

        Returns:
            PatternMatch if detected, None otherwise
        """
        score = 0.0
        matched_elements = []

        # Check for suspicious TLDs
        for tld in self.suspicious_tlds:
            if tld in text.lower():
                score += 0.3
                matched_elements.append(f"suspicious TLD: {tld}")

        # Check for fake government domains
        for domain in self.fake_gov_domains:
            if domain in text.lower():
                score += 0.5
                matched_elements.append(f"fake gov domain: {domain}")

        # Check for shortened URLs
        short_urls = ['bit.ly', 'tinyurl', 'goo.gl', 't.co', 'ow.ly']
        for short_url in short_urls:
            if short_url in text.lower():
                score += 0.2
                matched_elements.append("shortened URL")

        # Check for IP addresses in URLs
        ip_pattern = r'https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.search(ip_pattern, text):
            score += 0.4
            matched_elements.append("IP-based URL")

        if score >= 0.3:
            confidence = min(score, 1.0)
            return PatternMatch(
                pattern_name="suspicious_url",
                confidence=confidence,
                description="Suspicious URL or domain detected",
                severity=0.8,
                matched_text=", ".join(matched_elements[:3])
            )

        return None

    def detect_all_patterns(self, text: str) -> List[PatternMatch]:
        """
        Run all pattern detectors on the text.

        Args:
            text: Text to analyze

        Returns:
            List of detected patterns
        """
        patterns = []

        # Run all detectors
        detectors = [
            self.detect_ato_scam,
            self.detect_mygov_scam,
            self.detect_banking_scam,
            self.detect_delivery_scam,
            self.detect_phone_scam,
            self.detect_url_patterns,
        ]

        for detector in detectors:
            try:
                result = detector(text)
                if result:
                    patterns.append(result)
                    logger.debug(f"Detected pattern: {result.pattern_name}")
            except Exception as e:
                logger.error(f"Error in {detector.__name__}: {e}")

        return patterns

    def get_australian_risk_score(self, patterns: List[PatternMatch]) -> Tuple[float, bool]:
        """
        Calculate overall Australian-specific risk score.

        Args:
            patterns: List of detected patterns

        Returns:
            Tuple of (risk_score, is_australian_specific)
        """
        if not patterns:
            return 0.0, False

        # Calculate weighted average
        total_weight = sum(p.severity * p.confidence for p in patterns)
        total_confidence = sum(p.confidence for p in patterns)

        if total_confidence == 0:
            return 0.0, False

        risk_score = total_weight / len(patterns)

        # Check if any Australian-specific patterns detected
        australian_patterns = [
            "ato_impersonation", "mygov_impersonation",
            "banking_scam", "delivery_scam"
        ]
        is_australian = any(p.pattern_name in australian_patterns for p in patterns)

        return min(risk_score, 1.0), is_australian
