"""
Preprocessing Tests
~~~~~~~~~~~~~~~~~~~

Tests for text cleaning and feature extraction.
"""

import pytest

from src.preprocessing.feature_extractor import FeatureExtractor
from src.preprocessing.text_cleaner import TextCleaner


class TestTextCleaner:
    """Tests for TextCleaner class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.cleaner = TextCleaner()

    def test_basic_cleaning(self):
        """Test basic text cleaning."""
        text = "URGENT: Click NOW!!!"
        result = self.cleaner.clean(text)
        assert result == "urgent click now"

    def test_url_replacement(self):
        """Test URL replacement."""
        text = "Visit https://scam.com for details"
        result = self.cleaner.clean(text)
        assert "URL" in result
        assert "https" not in result.lower()

    def test_email_replacement(self):
        """Test email address replacement."""
        text = "Contact us at scam@example.com"
        result = self.cleaner.clean(text)
        assert "EMAIL" in result
        assert "@" not in result

    def test_phone_replacement(self):
        """Test Australian phone number replacement."""
        text = "Call us on 0412 345 678"
        result = self.cleaner.clean(text)
        assert "PHONE" in result

    def test_empty_text(self):
        """Test handling of empty text."""
        result = self.cleaner.clean("")
        assert result == ""

    def test_whitespace_normalization(self):
        """Test whitespace normalization."""
        text = "Too    many   spaces"
        result = self.cleaner.clean(text)
        assert "  " not in result

    def test_tokenization(self):
        """Test text tokenization."""
        text = "Hello world"
        tokens = self.cleaner.tokenize(text)
        assert len(tokens) > 0
        assert isinstance(tokens, list)


class TestFeatureExtractor:
    """Tests for FeatureExtractor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.extractor = FeatureExtractor()

    def test_text_features(self):
        """Test basic text feature extraction."""
        text = "URGENT: Your tax refund is ready!"
        features = self.extractor.extract_text_features(text)

        assert "length" in features
        assert "word_count" in features
        assert "uppercase_ratio" in features
        assert features["length"] > 0

    def test_urgency_detection(self):
        """Test urgency keyword detection."""
        text = "URGENT: Act now or lose your refund!"
        features = self.extractor.extract_urgency_features(text)

        assert "urgency_keyword_count" in features
        assert features["urgency_keyword_count"] > 0
        assert features["has_urgency"] == 1

    def test_no_urgency(self):
        """Test no urgency keywords."""
        text = "Your order has been shipped"
        features = self.extractor.extract_urgency_features(text)

        assert features["has_urgency"] == 0

    def test_australian_features_ato(self):
        """Test ATO keyword detection."""
        text = "ATO tax refund available"
        features = self.extractor.extract_australian_features(text)

        assert "has_ato" in features
        assert features["has_ato"] == 1

    def test_australian_features_mygov(self):
        """Test MyGov keyword detection."""
        text = "Your MyGov account requires verification"
        features = self.extractor.extract_australian_features(text)

        assert "has_mygov" in features
        assert features["has_mygov"] == 1

    def test_australian_features_banks(self):
        """Test Australian bank detection."""
        text = "Commonwealth Bank security alert"
        features = self.extractor.extract_australian_features(text)

        assert "has_banks" in features
        assert features["has_banks"] == 1

    def test_abn_mention(self):
        """Test ABN mention detection."""
        text = "Update your ABN details"
        features = self.extractor.extract_australian_features(text)

        assert features["mentions_abn"] == 1

    def test_all_features(self):
        """Test extracting all features."""
        text = "URGENT: Your ATO tax refund is ready!"
        features = self.extractor.extract_all_features(text)

        # Should have features from all categories
        assert "length" in features
        assert "urgency_keyword_count" in features
        assert "has_ato" in features
        assert isinstance(features, dict)
        assert len(features) > 10
