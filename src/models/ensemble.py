"""
Ensemble Model
~~~~~~~~~~~~~~

Combines multiple models for robust scam detection.
"""

from typing import Optional, Tuple

import numpy as np
from src.utils.logger import get_logger

logger = get_logger(__name__)


class EnsembleModel:
    """
    Ensemble model combining XGBoost and BERT for scam detection.

    Uses weighted voting to combine predictions from multiple models.
    """

    def __init__(
        self,
        xgboost_model: Optional[object] = None,
        bert_model: Optional[object] = None,
        xgboost_weight: float = 0.4,
        bert_weight: float = 0.6
    ) -> None:
        """
        Initialize ensemble model.

        Args:
            xgboost_model: Trained XGBoost model
            bert_model: Trained BERT model
            xgboost_weight: Weight for XGBoost predictions
            bert_weight: Weight for BERT predictions
        """
        self.xgboost_model = xgboost_model
        self.bert_model = bert_model
        self.xgboost_weight = xgboost_weight
        self.bert_weight = bert_weight

        # Ensure weights sum to 1
        total_weight = xgboost_weight + bert_weight
        self.xgboost_weight = xgboost_weight / total_weight
        self.bert_weight = bert_weight / total_weight

        logger.info(
            f"Ensemble model initialized with weights: "
            f"XGBoost={self.xgboost_weight:.2f}, BERT={self.bert_weight:.2f}"
        )

    def predict_proba(self, features: dict) -> np.ndarray:
        """
        Predict scam probability using ensemble.

        Args:
            features: Dictionary containing model features
                - 'xgboost_features': Features for XGBoost model
                - 'bert_features': Features for BERT model

        Returns:
            Array of prediction probabilities [legitimate_prob, scam_prob]
        """
        predictions = []
        weights = []

        # XGBoost prediction
        if self.xgboost_model is not None and 'xgboost_features' in features:
            xgb_pred = self.xgboost_model.predict_proba([features['xgboost_features']])[0]
            predictions.append(xgb_pred)
            weights.append(self.xgboost_weight)
            logger.debug(f"XGBoost prediction: {xgb_pred}")

        # BERT prediction
        if self.bert_model is not None and 'bert_features' in features:
            bert_pred = self.bert_model.predict_proba([features['bert_features']])[0]
            predictions.append(bert_pred)
            weights.append(self.bert_weight)
            logger.debug(f"BERT prediction: {bert_pred}")

        if not predictions:
            raise ValueError("No valid predictions from any model")

        # Normalize weights
        weights = np.array(weights)
        weights = weights / weights.sum()

        # Weighted average
        ensemble_pred = np.average(predictions, axis=0, weights=weights)

        logger.debug(f"Ensemble prediction: {ensemble_pred}")

        return ensemble_pred

    def predict(self, features: dict, threshold: float = 0.5) -> int:
        """
        Predict scam class (0=legitimate, 1=scam).

        Args:
            features: Dictionary containing model features
            threshold: Classification threshold

        Returns:
            Predicted class (0 or 1)
        """
        proba = self.predict_proba(features)
        return int(proba[1] >= threshold)

    def predict_with_confidence(
        self,
        features: dict,
        threshold: float = 0.5
    ) -> Tuple[int, float, str]:
        """
        Predict with confidence level and risk assessment.

        Args:
            features: Dictionary containing model features
            threshold: Classification threshold

        Returns:
            Tuple of (prediction, confidence, risk_level)
        """
        proba = self.predict_proba(features)
        scam_probability = proba[1]
        prediction = int(scam_probability >= threshold)

        # Calculate confidence (distance from decision boundary)
        confidence = abs(scam_probability - threshold) / threshold

        # Determine risk level
        if scam_probability >= 0.8:
            risk_level = "high"
        elif scam_probability >= 0.5:
            risk_level = "medium"
        else:
            risk_level = "low"

        return prediction, confidence, risk_level
