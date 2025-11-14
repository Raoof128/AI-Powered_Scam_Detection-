"""
Scam Detector Service
~~~~~~~~~~~~~~~~~~~~~

Main detection service that integrates all components.
"""

import time
from typing import Dict, List

from src.api.schemas.detection import DetectedPattern, RiskLevel
from src.preprocessing.australian_patterns import AustralianPatternDetector, PatternMatch
from src.preprocessing.feature_extractor import FeatureExtractor
from src.preprocessing.text_cleaner import TextCleaner
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ScamDetector:
    """Main scam detection service."""

    def __init__(self) -> None:
        """Initialize scam detector with all components."""
        self.text_cleaner = TextCleaner()
        self.feature_extractor = FeatureExtractor()
        self.australian_detector = AustralianPatternDetector()

        # TODO: Load ML models (XGBoost and BERT) when available
        self.ml_model_loaded = False

        logger.info("Scam detector initialized")

    def _calculate_risk_level(self, probability: float) -> RiskLevel:
        """
        Calculate risk level from probability.

        Args:
            probability: Scam probability (0-1)

        Returns:
            RiskLevel enum
        """
        if probability >= 0.85:
            return RiskLevel.CRITICAL
        elif probability >= 0.65:
            return RiskLevel.HIGH
        elif probability >= 0.35:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _pattern_to_detected_pattern(self, pattern: PatternMatch) -> DetectedPattern:
        """Convert PatternMatch to DetectedPattern schema."""
        return DetectedPattern(
            pattern_name=pattern.pattern_name,
            confidence=pattern.confidence,
            description=pattern.description,
            severity=pattern.severity,
        )

    def _generate_recommendations(
        self,
        risk_level: RiskLevel,
        patterns: List[PatternMatch],
        australian_specific: bool
    ) -> List[str]:
        """
        Generate recommendations based on detection results.

        Args:
            risk_level: Detected risk level
            patterns: Detected patterns
            australian_specific: Whether Australian-specific patterns detected

        Returns:
            List of recommendations
        """
        recommendations = []

        if risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
            recommendations.append("⚠️ Do not click any links in this message")
            recommendations.append("⚠️ Do not provide any personal information")
            recommendations.append("🗑️ Delete this message immediately")

        # Pattern-specific recommendations
        pattern_names = [p.pattern_name for p in patterns]

        if "ato_impersonation" in pattern_names:
            recommendations.append("📞 Contact the ATO directly at ato.gov.au or 13 28 61")
            recommendations.append("🚫 The ATO never asks for personal details via email or SMS")

        if "mygov_impersonation" in pattern_names:
            recommendations.append("🔐 Log in directly to myGov at my.gov.au (not via links)")
            recommendations.append("📧 MyGov never sends emails asking you to verify your account")

        if "banking_scam" in pattern_names:
            recommendations.append("🏦 Contact your bank directly using the number on your card")
            recommendations.append("💳 Banks never ask for full passwords or PINs")

        if "delivery_scam" in pattern_names:
            recommendations.append("📦 Check Australia Post website directly for tracking")
            recommendations.append("💰 Australia Post never asks for payment via links")

        if "suspicious_url" in pattern_names:
            recommendations.append("🔗 Never click on shortened or suspicious URLs")
            recommendations.append("🔍 Check the full URL before clicking")

        # General recommendations
        if australian_specific:
            recommendations.append("📢 Report to ACCC Scamwatch at scamwatch.gov.au")
            recommendations.append("🔔 Forward scam messages to the ACCC")

        if risk_level == RiskLevel.MEDIUM:
            recommendations.append("🤔 Exercise caution and verify sender authenticity")
            recommendations.append("🔍 Look for spelling errors and grammatical mistakes")

        if not recommendations:
            recommendations.append("✅ This message appears legitimate, but stay vigilant")

        return recommendations

    def detect(
        self,
        message: str,
        message_type: str = "other",
        metadata: Dict = None,
        include_explanation: bool = True
    ) -> Dict:
        """
        Detect if a message is a scam.

        Args:
            message: Text content to analyze
            message_type: Type of message (email, sms, etc.)
            metadata: Additional metadata
            include_explanation: Whether to include detailed explanation

        Returns:
            Detection result dictionary
        """
        start_time = time.time()

        try:
            # Clean and preprocess text
            cleaned_text = self.text_cleaner.clean(message)

            # Extract features
            text_features = self.feature_extractor.extract_all_features(message)

            # Run Australian pattern detection
            australian_patterns = self.australian_detector.detect_all_patterns(message)

            # Calculate Australian-specific risk
            australian_risk, is_australian = (
                self.australian_detector.get_australian_risk_score(australian_patterns)
            )

            # TODO: Run ML model prediction when available
            # For now, use rule-based scoring
            ml_probability = 0.0  # Placeholder

            # Combine rule-based and ML scores
            if australian_patterns:
                # Use pattern-based scoring
                pattern_score = sum(p.confidence * p.severity for p in australian_patterns) / len(australian_patterns)
                scam_probability = max(pattern_score, australian_risk)
            else:
                # Fall back to feature-based heuristics
                urgency_score = text_features.get("urgency_keyword_count", 0) * 0.1
                url_score = text_features.get("url_count", 0) * 0.15
                scam_probability = min(urgency_score + url_score, 0.5)

            # Ensure probability is in valid range
            scam_probability = max(0.0, min(1.0, scam_probability))

            # Calculate risk level
            risk_level = self._calculate_risk_level(scam_probability)

            # Convert patterns to schema format
            detected_patterns = [
                self._pattern_to_detected_pattern(p) for p in australian_patterns
            ]

            # Generate recommendations
            recommendations = self._generate_recommendations(
                risk_level,
                australian_patterns,
                is_australian
            )

            # Calculate confidence (for now, use pattern confidence)
            if australian_patterns:
                confidence = sum(p.confidence for p in australian_patterns) / len(australian_patterns)
            else:
                confidence = 0.6  # Moderate confidence for heuristic-based

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            result = {
                "scam_probability": round(scam_probability, 4),
                "risk_level": risk_level.value,
                "detected_patterns": detected_patterns,
                "confidence": round(confidence, 4),
                "recommendations": recommendations,
                "processing_time_ms": processing_time_ms,
                "australian_specific": is_australian,
            }

            logger.info(
                f"Detection completed: probability={scam_probability:.2f}, "
                f"risk={risk_level.value}, time={processing_time_ms}ms"
            )

            return result

        except Exception as e:
            logger.error(f"Error during detection: {e}", exc_info=True)
            raise

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
        """
        start_time = time.time()

        results = []
        for msg in messages:
            result = self.detect(
                message=msg.get("message", ""),
                message_type=msg.get("message_type", "other"),
                metadata=msg.get("metadata"),
                include_explanation=include_explanation
            )
            results.append(result)

        total_time_ms = int((time.time() - start_time) * 1000)
        avg_time_ms = total_time_ms / len(messages) if messages else 0

        return {
            "results": results,
            "total_processed": len(messages),
            "total_processing_time_ms": total_time_ms,
            "average_processing_time_ms": round(avg_time_ms, 2),
        }
