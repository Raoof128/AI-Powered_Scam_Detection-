"""
Models Module
~~~~~~~~~~~~~

Machine learning models for scam detection.

Modules:
    - xgboost_model: XGBoost classifier for metadata features
    - bert_model: Fine-tuned BERT for content analysis
    - ensemble: Ensemble voting system combining multiple models
"""

from src.models.ensemble import EnsembleModel

__all__ = ["EnsembleModel"]
