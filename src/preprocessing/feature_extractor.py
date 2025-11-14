"""
Feature Extraction
~~~~~~~~~~~~~~~~~~

Extract features from text for ML models (TF-IDF, embeddings, etc.)
"""

from typing import Optional, Union

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from src.utils.logger import get_logger

logger = get_logger(__name__)


class FeatureExtractor:
    """Extract features from text for machine learning models."""

    def __init__(
        self,
        max_features: int = 5000,
        ngram_range: tuple[int, int] = (1, 3),
        min_df: int = 2,
        max_df: float = 0.95
    ) -> None:
        """
        Initialize feature extractor.

        Args:
            max_features: Maximum number of features to extract
            ngram_range: Range of n-grams to consider
            min_df: Minimum document frequency
            max_df: Maximum document frequency
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        self.min_df = min_df
        self.max_df = max_df

        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self._is_fitted = False

        logger.info("FeatureExtractor initialized")

    def fit_tfidf(self, texts: list[str]) -> None:
        """
        Fit TF-IDF vectorizer on training texts.

        Args:
            texts: List of training texts
        """
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=self.max_features,
            ngram_range=self.ngram_range,
            min_df=self.min_df,
            max_df=self.max_df,
            strip_accents='unicode',
            lowercase=True,
            analyzer='word',
            token_pattern=r'\w{1,}',
            stop_words='english'
        )

        self.tfidf_vectorizer.fit(texts)
        self._is_fitted = True

        logger.info(
            f"TF-IDF vectorizer fitted on {len(texts)} documents. "
            f"Vocabulary size: {len(self.tfidf_vectorizer.vocabulary_)}"
        )

    def transform_tfidf(self, texts: Union[str, list[str]]) -> np.ndarray:
        """
        Transform texts to TF-IDF features.

        Args:
            texts: Text or list of texts to transform

        Returns:
            TF-IDF feature matrix

        Raises:
            ValueError: If vectorizer is not fitted
        """
        if not self._is_fitted or self.tfidf_vectorizer is None:
            raise ValueError("TF-IDF vectorizer must be fitted before transform")

        if isinstance(texts, str):
            texts = [texts]

        features = self.tfidf_vectorizer.transform(texts)
        return features.toarray()

    def extract_text_features(self, text: str) -> dict[str, Union[int, float]]:
        """
        Extract basic text features.

        Args:
            text: Input text

        Returns:
            Dictionary of text features
        """
        features = {
            'length': len(text),
            'word_count': len(text.split()),
            'avg_word_length': np.mean([len(word) for word in text.split()]) if text else 0,
            'unique_word_ratio': len(set(text.split())) / len(text.split()) if text else 0,
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'digit_ratio': sum(1 for c in text if c.isdigit()) / len(text) if text else 0,
            'special_char_ratio': sum(1 for c in text if not c.isalnum() and not c.isspace()) / len(text) if text else 0,
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'url_count': text.lower().count('http'),
            'email_count': text.count('@'),
        }

        return features

    def extract_urgency_features(self, text: str) -> dict[str, int]:
        """
        Extract urgency-related features common in scams.

        Args:
            text: Input text

        Returns:
            Dictionary of urgency features
        """
        urgency_keywords = [
            'urgent', 'immediately', 'now', 'asap', 'hurry', 'quick',
            'expire', 'limited time', 'act now', 'don\'t wait',
            'final notice', 'last chance', 'verify now'
        ]

        text_lower = text.lower()

        features = {
            'urgency_keyword_count': sum(
                text_lower.count(keyword) for keyword in urgency_keywords
            ),
            'has_urgency': int(any(keyword in text_lower for keyword in urgency_keywords)),
        }

        return features

    def extract_australian_features(self, text: str) -> dict[str, int]:
        """
        Extract features specific to Australian scams.

        Args:
            text: Input text

        Returns:
            Dictionary of Australian-specific features
        """
        australian_keywords = {
            'ato': ['ato', 'australian taxation office', 'tax office'],
            'mygov': ['mygov', 'my gov', 'mygovid'],
            'centrelink': ['centrelink', 'centre link'],
            'medicare': ['medicare'],
            'auspost': ['australia post', 'auspost', 'aus post'],
            'banks': ['cba', 'commonwealth bank', 'nab', 'westpac', 'anz'],
        }

        text_lower = text.lower()

        features = {}
        for category, keywords in australian_keywords.items():
            features[f'has_{category}'] = int(
                any(keyword in text_lower for keyword in keywords)
            )

        # Check for ABN/TFN patterns
        features['mentions_abn'] = int('abn' in text_lower)
        features['mentions_tfn'] = int('tfn' in text_lower)
        features['mentions_bsb'] = int('bsb' in text_lower)

        return features

    def extract_all_features(self, text: str) -> dict[str, Union[int, float]]:
        """
        Extract all available features from text.

        Args:
            text: Input text

        Returns:
            Dictionary containing all features
        """
        features = {}

        # Basic text features
        features.update(self.extract_text_features(text))

        # Urgency features
        features.update(self.extract_urgency_features(text))

        # Australian-specific features
        features.update(self.extract_australian_features(text))

        return features
