"""
Text Cleaning and Normalization
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Preprocessing pipeline for cleaning and normalizing text data.
"""

import re
from typing import Optional

import spacy
from src.utils.logger import get_logger

logger = get_logger(__name__)


class TextCleaner:
    """Clean and normalize text data for scam detection."""

    def __init__(self, language: str = "en_core_web_sm") -> None:
        """
        Initialize text cleaner with spaCy model.

        Args:
            language: spaCy language model name
        """
        try:
            self.nlp = spacy.load(language)
            logger.info(f"Loaded spaCy model: {language}")
        except OSError:
            logger.warning(f"spaCy model {language} not found. Using blank model.")
            self.nlp = spacy.blank("en")

    def clean(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw input text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Convert to lowercase
        text = text.lower()

        # Remove URLs (but keep for later analysis)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', ' URL ', text)

        # Remove email addresses
        text = re.sub(r'\S+@\S+', ' EMAIL ', text)

        # Remove phone numbers (Australian format)
        text = re.sub(r'(\+?61|0)[2-478](?:[ -]?[0-9]){8}', ' PHONE ', text)

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', text)

        return text.strip()

    def tokenize(self, text: str) -> list[str]:
        """
        Tokenize text using spaCy.

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        doc = self.nlp(text)
        return [token.text for token in doc]

    def lemmatize(self, text: str) -> str:
        """
        Lemmatize text using spaCy.

        Args:
            text: Input text

        Returns:
            Lemmatized text
        """
        doc = self.nlp(text)
        return " ".join([token.lemma_ for token in doc])

    def remove_stopwords(self, text: str) -> str:
        """
        Remove stopwords from text.

        Args:
            text: Input text

        Returns:
            Text without stopwords
        """
        doc = self.nlp(text)
        return " ".join([token.text for token in doc if not token.is_stop])

    def extract_entities(self, text: str) -> dict[str, list[str]]:
        """
        Extract named entities from text.

        Args:
            text: Input text

        Returns:
            Dictionary mapping entity types to entity values
        """
        doc = self.nlp(text)
        entities = {}

        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            entities[ent.label_].append(ent.text)

        return entities

    def preprocess(
        self,
        text: str,
        remove_stopwords: bool = False,
        lemmatize: bool = False
    ) -> str:
        """
        Full preprocessing pipeline.

        Args:
            text: Raw input text
            remove_stopwords: Whether to remove stopwords
            lemmatize: Whether to lemmatize

        Returns:
            Preprocessed text
        """
        text = self.clean(text)

        if lemmatize:
            text = self.lemmatize(text)

        if remove_stopwords:
            text = self.remove_stopwords(text)

        return text
