"""
Configuration Management
~~~~~~~~~~~~~~~~~~~~~~~~

Environment-based configuration using pydantic-settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = Field(default="scam-detector", alias="APP_NAME")
    app_version: str = Field(default="0.1.0", alias="APP_VERSION")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=True, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # API Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    api_workers: int = Field(default=4, alias="API_WORKERS")
    api_reload: bool = Field(default=True, alias="API_RELOAD")

    # Security
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    api_key_header: str = Field(default="X-API-Key", alias="API_KEY_HEADER")
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        alias="CORS_ORIGINS"
    )

    # Database Configuration
    database_url: str = Field(
        default="postgresql://scamdetector:password@localhost:5432/scamdetector",
        alias="DATABASE_URL"
    )
    db_pool_size: int = Field(default=20, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=10, alias="DB_MAX_OVERFLOW")

    # Redis Configuration
    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")
    redis_password: str = Field(default="", alias="REDIS_PASSWORD")
    cache_ttl: int = Field(default=86400, alias="CACHE_TTL")  # 24 hours

    # ML Model Configuration
    model_path: Path = Field(default=Path("data/models"), alias="MODEL_PATH")
    default_model: str = Field(default="ensemble_v1", alias="DEFAULT_MODEL")
    confidence_threshold: float = Field(default=0.75, alias="CONFIDENCE_THRESHOLD")
    batch_size: int = Field(default=32, alias="BATCH_SIZE")
    max_sequence_length: int = Field(default=512, alias="MAX_SEQUENCE_LENGTH")

    # BERT Configuration
    bert_model: str = Field(default="bert-base-uncased", alias="BERT_MODEL")
    bert_cache_dir: Path = Field(
        default=Path("data/models/bert_cache"),
        alias="BERT_CACHE_DIR"
    )

    # Performance Settings
    max_workers: int = Field(default=4, alias="MAX_WORKERS")
    request_timeout: int = Field(default=30, alias="REQUEST_TIMEOUT")
    max_content_length: int = Field(default=1048576, alias="MAX_CONTENT_LENGTH")  # 1MB
    rate_limit_per_minute: int = Field(default=100, alias="RATE_LIMIT_PER_MINUTE")

    # Feature Flags
    enable_australian_patterns: bool = Field(
        default=True,
        alias="ENABLE_AUSTRALIAN_PATTERNS"
    )
    enable_url_scanning: bool = Field(default=True, alias="ENABLE_URL_SCANNING")
    enable_phone_validation: bool = Field(default=True, alias="ENABLE_PHONE_VALIDATION")
    enable_metrics: bool = Field(default=True, alias="ENABLE_METRICS")

    # Monitoring
    prometheus_port: int = Field(default=9090, alias="PROMETHEUS_PORT")
    enable_prometheus: bool = Field(default=False, alias="ENABLE_PROMETHEUS")

    # Australian-specific Settings
    australian_tld_validation: bool = Field(
        default=True,
        alias="AUSTRALIAN_TLD_VALIDATION"
    )
    validate_abn: bool = Field(default=True, alias="VALIDATE_ABN")
    validate_tfn: bool = Field(default=False, alias="VALIDATE_TFN")
    whitelisted_domains: List[str] = Field(
        default=["ato.gov.au", "myagov.gov.au", "australia.gov.au"],
        alias="WHITELISTED_DOMAINS"
    )

    # Dataset Configuration
    dataset_size: int = Field(default=10000, alias="DATASET_SIZE")
    train_test_split: float = Field(default=0.8, alias="TRAIN_TEST_SPLIT")
    random_seed: int = Field(default=42, alias="RANDOM_SEED")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("whitelisted_domains", mode="before")
    @classmethod
    def parse_whitelisted_domains(cls, v: str | List[str]) -> List[str]:
        """Parse whitelisted domains from string or list."""
        if isinstance(v, str):
            return [domain.strip() for domain in v.split(",")]
        return v

    @property
    def redis_url(self) -> str:
        """Generate Redis connection URL."""
        if self.redis_password:
            return f"redis://:{self.redis_password}@{self.redis_host}:{self.redis_port}/{self.redis_db}"
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings instance loaded from environment
    """
    return Settings()
