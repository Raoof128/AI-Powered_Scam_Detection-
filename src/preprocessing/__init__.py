"""
Preprocessing Module
~~~~~~~~~~~~~~~~~~~~

Text cleaning, normalization, and feature extraction for scam detection.

Modules:
    - text_cleaner: Text normalization and cleaning
    - feature_extractor: TF-IDF and embedding generation
    - australian_patterns: Australian-specific pattern detectors
"""

from src.preprocessing.text_cleaner import TextCleaner
from src.preprocessing.feature_extractor import FeatureExtractor

__all__ = ["TextCleaner", "FeatureExtractor"]
