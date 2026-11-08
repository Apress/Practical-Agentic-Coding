"""
Centralized configuration management for the Daily Briefing Agent.

This module provides a single source of truth for all application configuration,
following the pattern defined in the tech.md steering file.

Configuration is loaded with the following precedence (highest to lowest):
1. System environment variables
2. .env files, first file that defines a key wins
   (.env.local, then .env.dev, then .env.prod, then .env)
3. Default values in this Config class
"""

import os
from functools import lru_cache
from typing import Optional

# Optional: Load .env files if python-dotenv is available.
# Files are loaded in the documented precedence order. load_dotenv() never
# overrides a variable that is already set, so system environment variables
# always win, and the first file that defines a key wins among the files.
try:
    from dotenv import load_dotenv

    for _env_file in (".env.local", ".env.dev", ".env.prod", ".env"):
        load_dotenv(_env_file)
except ImportError:
    pass


class Config:
    """Application configuration with environment-based overrides.

    Usage:
        config = get_config()
        db_url = config.database_url
        bedrock_model = config.BEDROCK_MODEL_ID
    """

    # Environment
    ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Database Configuration
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    DATABASE_SECRET_ARN: Optional[str] = os.getenv("DATABASE_SECRET_ARN")

    # AWS Configuration
    AWS_REGION: str = os.getenv("AWS_REGION", "us-east-1")
    AWS_PROFILE: Optional[str] = os.getenv("AWS_PROFILE")

    # LocalStack (for local development)
    LOCALSTACK_ENDPOINT: Optional[str] = os.getenv("LOCALSTACK_ENDPOINT")
    USE_LOCALSTACK: bool = os.getenv("USE_LOCALSTACK", "false").lower() == "true"

    # Amazon Bedrock Configuration
    #
    # The defaults are inference profile IDs, which is what the bedrock-runtime
    # InvokeModel and Converse APIs expect for current Claude models. Bedrock's
    # Claude lineup changes, so confirm the IDs on each model's card under
    # "Models at a glance" in the Amazon Bedrock User Guide (.env.example has
    # the details) and override them through the environment rather than
    # editing here.
    BEDROCK_MODEL_ID: str = os.getenv("BEDROCK_MODEL_ID", "global.anthropic.claude-haiku-5-5")
    # The fallback is used when the primary model call fails, so it defaults to
    # a different model: the Sonnet tier backs up the Haiku tier.
    BEDROCK_FALLBACK_MODEL_ID: str = os.getenv(
        "BEDROCK_FALLBACK_MODEL_ID", "global.anthropic.claude-sonnet-5-5"
    )
    BEDROCK_MAX_TOKENS: int = int(os.getenv("BEDROCK_MAX_TOKENS", "4096"))

    # S3 Configuration
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "daily-briefing-briefings")

    # Web Scraping Configuration
    HN_BASE_URL: str = "https://news.ycombinator.com"
    HN_RATE_LIMIT_DELAY: float = float(os.getenv("HN_RATE_LIMIT_DELAY", "1.0"))
    MAX_STORIES_PER_COLLECTION: int = int(os.getenv("MAX_STORIES_PER_COLLECTION", "30"))

    # Flask Configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")

    # Feature Flags
    ENABLE_BEDROCK: bool = os.getenv("ENABLE_BEDROCK", "true").lower() == "true"
    ENABLE_CACHING: bool = os.getenv("ENABLE_CACHING", "true").lower() == "true"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENV == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENV == "production"

    @property
    def database_url(self) -> str:
        """Get database URL, falling back to a local SQLite for development."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        if self.is_development:
            return "sqlite:///daily_briefing_dev.db"
        raise ValueError(f"DATABASE_URL must be set when FLASK_ENV is {self.ENV!r}")

    def get_aws_endpoint_url(self, service: str) -> Optional[str]:
        """Get endpoint URL for an AWS service, using LocalStack if configured.

        Args:
            service: AWS service name (e.g., 's3', 'bedrock-runtime')

        Returns:
            Endpoint URL if using LocalStack, None for real AWS
        """
        if self.USE_LOCALSTACK and self.LOCALSTACK_ENDPOINT:
            return self.LOCALSTACK_ENDPOINT
        return None


@lru_cache()
def get_config() -> Config:
    """Get the application configuration (cached singleton).

    Returns:
        Config instance with all settings loaded
    """
    return Config()


# Convenience function for quick access
def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Get a specific configuration setting by key.

    Args:
        key: Configuration key name
        default: Default value if not found

    Returns:
        Configuration value or default
    """
    config = get_config()
    return getattr(config, key.upper(), default)
