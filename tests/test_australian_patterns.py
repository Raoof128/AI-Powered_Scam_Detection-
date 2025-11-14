"""
Australian Pattern Detection Tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tests for Australian-specific scam pattern detection.
"""

import pytest

from src.preprocessing.australian_patterns import AustralianPatternDetector, PatternMatch


class TestAustralianPatternDetector:
    """Tests for AustralianPatternDetector class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.detector = AustralianPatternDetector()

    def test_ato_impersonation_detection(self):
        """Test ATO impersonation scam detection."""
        text = "URGENT: Your ATO tax refund of $2,450 is ready. Click here to claim."
        result = self.detector.detect_ato_scam(text)

        assert result is not None
        assert isinstance(result, PatternMatch)
        assert result.pattern_name == "ato_impersonation"
        assert result.confidence > 0.4
        assert result.severity == 1.0

    def test_ato_with_abn(self):
        """Test ATO scam with ABN pattern."""
        text = "ATO notice: Your ABN 12 345 678 901 requires verification"
        result = self.detector.detect_ato_scam(text)

        assert result is not None
        assert result.confidence > 0.5

    def test_no_ato_scam(self):
        """Test legitimate message doesn't trigger ATO detection."""
        text = "Your order has been shipped"
        result = self.detector.detect_ato_scam(text)

        assert result is None

    def test_mygov_impersonation(self):
        """Test MyGov impersonation detection."""
        text = "Your MyGov account has been suspended. Verify now to restore access."
        result = self.detector.detect_mygov_scam(text)

        assert result is not None
        assert result.pattern_name == "mygov_impersonation"
        assert result.confidence > 0.5

    def test_centrelink_scam(self):
        """Test Centrelink scam detection."""
        text = "Centrelink payment of $1,200 is pending. Confirm details to receive."
        result = self.detector.detect_mygov_scam(text)

        assert result is not None

    def test_banking_scam_cba(self):
        """Test Commonwealth Bank scam detection."""
        text = "Commonwealth Bank Alert: Suspicious activity detected. Verify at secure-cba.com"
        result = self.detector.detect_banking_scam(text)

        assert result is not None
        assert result.pattern_name == "banking_scam"

    def test_banking_scam_nab(self):
        """Test NAB scam detection."""
        text = "NAB Security: Your account has been locked. Click here to unlock."
        result = self.detector.detect_banking_scam(text)

        assert result is not None

    def test_delivery_scam_auspost(self):
        """Test Australia Post scam detection."""
        text = "Australia Post: Package waiting. Pay $5 customs fee for delivery."
        result = self.detector.detect_delivery_scam(text)

        assert result is not None
        assert result.pattern_name == "delivery_scam"

    def test_delivery_scam_generic(self):
        """Test generic delivery scam."""
        text = "Your parcel requires additional payment. Pay now to avoid return."
        result = self.detector.detect_delivery_scam(text)

        # May or may not detect without specific keywords
        # Just ensure it doesn't crash
        assert result is None or isinstance(result, PatternMatch)

    def test_phone_scam_nbn(self):
        """Test NBN phone scam detection."""
        text = "NBN: Your internet service will be disconnected. Call us immediately."
        result = self.detector.detect_phone_scam(text)

        assert result is not None
        assert result.pattern_name == "phone_scam"

    def test_suspicious_url_detection(self):
        """Test suspicious URL detection."""
        text = "Click here: http://ato-refund.tk to claim your refund"
        result = self.detector.detect_url_patterns(text)

        assert result is not None
        assert result.pattern_name == "suspicious_url"

    def test_fake_gov_domain(self):
        """Test fake government domain detection."""
        text = "Visit gov.au.com for your refund"
        result = self.detector.detect_url_patterns(text)

        assert result is not None
        assert result.confidence > 0.5

    def test_ip_based_url(self):
        """Test IP-based URL detection."""
        text = "Login at http://192.168.1.1/verify"
        result = self.detector.detect_url_patterns(text)

        assert result is not None

    def test_detect_all_patterns(self):
        """Test detecting all patterns in a complex scam."""
        text = "URGENT: ATO tax refund available. Click http://ato-gov.tk to claim $2,500 now!"
        patterns = self.detector.detect_all_patterns(text)

        assert len(patterns) > 0
        assert any(p.pattern_name == "ato_impersonation" for p in patterns)
        assert any(p.pattern_name == "suspicious_url" for p in patterns)

    def test_risk_score_calculation(self):
        """Test risk score calculation."""
        text = "ATO: Your tax refund is ready. Visit ato-refund.tk"
        patterns = self.detector.detect_all_patterns(text)
        risk_score, is_australian = self.detector.get_australian_risk_score(patterns)

        assert 0.0 <= risk_score <= 1.0
        assert is_australian is True

    def test_no_patterns_detected(self):
        """Test when no patterns are detected."""
        text = "Hello, how are you doing today?"
        patterns = self.detector.detect_all_patterns(text)
        risk_score, is_australian = self.detector.get_australian_risk_score(patterns)

        assert len(patterns) == 0
        assert risk_score == 0.0
        assert is_australian is False

    def test_multiple_patterns_same_message(self):
        """Test multiple patterns in same message."""
        text = """
        URGENT: Your MyGov and ATO accounts require verification.
        Commonwealth Bank has also flagged suspicious activity.
        Click http://verify-gov.tk immediately.
        """
        patterns = self.detector.detect_all_patterns(text)

        # Should detect multiple patterns
        assert len(patterns) >= 2
        pattern_names = [p.pattern_name for p in patterns]
        assert any("ato" in name or "mygov" in name or "banking" in name for name in pattern_names)
