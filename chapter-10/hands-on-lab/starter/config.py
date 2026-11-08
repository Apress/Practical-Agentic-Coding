"""
Configuration management for multi-agent swarm system.

Loads configuration from environment variables with sensible defaults.
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class SwarmConfig(BaseSettings):
    """Configuration for the multi-agent swarm system."""

    # Claude API Configuration
    anthropic_api_key: str = Field(
        ...,
        description="Anthropic API key for Claude"
    )

    # Redis Configuration
    redis_host: str = Field(
        default="localhost",
        description="Redis host address"
    )
    redis_port: int = Field(
        default=6379,
        description="Redis port"
    )
    redis_db: int = Field(
        default=0,
        description="Redis database number"
    )
    redis_password: Optional[str] = Field(
        default=None,
        description="Redis password (if required)"
    )

    # Swarm Configuration
    message_queue_size: int = Field(
        default=1000,
        description="Maximum message queue size"
    )
    agent_timeout_seconds: int = Field(
        default=30,
        description="Timeout for agent operations"
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts"
    )
    retry_delay_seconds: int = Field(
        default=2,
        description="Delay between retries"
    )

    # Agent Configuration
    dev_agent_model: str = Field(
        default="claude-sonnet-4-6",
        description="Model for developer agent"
    )
    qa_agent_model: str = Field(
        default="claude-sonnet-4-6",
        description="Model for QA agent"
    )
    scrum_agent_model: str = Field(
        default="claude-sonnet-4-6",
        description="Model for Scrum Master agent"
    )
    agent_max_tokens: int = Field(
        default=4096,
        description="Maximum tokens for agent responses"
    )
    agent_temperature: float = Field(
        default=0.7,
        description="Temperature for agent responses"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    log_format: str = Field(
        default="json",
        description="Log format (json or text)"
    )

    # Coordination Patterns
    default_coordination_pattern: str = Field(
        default="manager",
        description="Default coordination pattern"
    )
    enable_pattern_metrics: bool = Field(
        default=True,
        description="Enable pattern performance metrics"
    )

    # Performance Settings
    concurrent_tasks_limit: int = Field(
        default=5,
        description="Maximum concurrent tasks"
    )
    task_timeout_seconds: int = Field(
        default=120,
        description="Timeout for task completion"
    )
    blackboard_poll_interval_seconds: int = Field(
        default=1,
        description="Blackboard polling interval"
    )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def load_config() -> SwarmConfig:
    """
    Load configuration from environment variables.

    Returns:
        SwarmConfig: Configuration object

    Raises:
        ValueError: If required configuration is missing
    """
    try:
        return SwarmConfig()
    except Exception as e:
        raise ValueError(f"Failed to load configuration: {e}")


def get_redis_url(config: SwarmConfig) -> str:
    """
    Build Redis connection URL from configuration.

    Args:
        config: SwarmConfig object

    Returns:
        Redis connection URL
    """
    if config.redis_password:
        return f"redis://:{config.redis_password}@{config.redis_host}:{config.redis_port}/{config.redis_db}"
    return f"redis://{config.redis_host}:{config.redis_port}/{config.redis_db}"
