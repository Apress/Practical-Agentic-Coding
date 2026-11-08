"""
Configuration management for Zero-Downtime Deployer.
Loads configuration from environment variables and provides typed access.
"""

import os
from typing import List
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class DeploymentConfig:
    """Configuration for a deployment."""

    service_name: str
    version: str
    image: str
    replicas: int
    # Defaults come from .env (CANARY_PERCENTAGE, VALIDATION_DURATION_SECONDS,
    # TRAFFIC_SHIFT_STEPS) when you do not pass them; the tests pass their own.
    canary_percentage: int = None
    validation_duration_seconds: int = None
    traffic_shift_steps: List[int] = None

    def __post_init__(self):
        """Fill in any setting the caller left out from the environment."""
        if self.canary_percentage is None:
            self.canary_percentage = int(os.getenv("CANARY_PERCENTAGE", "10"))
        if self.validation_duration_seconds is None:
            self.validation_duration_seconds = int(
                os.getenv("VALIDATION_DURATION_SECONDS", "300")
            )
        if self.traffic_shift_steps is None:
            steps_str = os.getenv("TRAFFIC_SHIFT_STEPS", "10,25,50,100")
            self.traffic_shift_steps = [int(s.strip()) for s in steps_str.split(",")]


@dataclass
class ThresholdConfig:
    """Health check thresholds."""

    error_rate: float
    latency_p99_ms: float
    cpu_percent: float
    memory_percent: float

    @classmethod
    def from_env(cls) -> "ThresholdConfig":
        """Load thresholds from environment variables."""
        return cls(
            error_rate=float(os.getenv("ERROR_RATE_THRESHOLD", "0.01")),
            latency_p99_ms=float(os.getenv("LATENCY_P99_THRESHOLD_MS", "500")),
            cpu_percent=float(os.getenv("CPU_THRESHOLD_PERCENT", "80")) / 100,
            memory_percent=float(os.getenv("MEMORY_THRESHOLD_PERCENT", "80")) / 100
        )


class Config:
    """Global configuration for the deployer."""

    def __init__(self):
        """Initialize configuration from environment."""
        # Claude API
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")

        # Kubernetes
        self.k8s_namespace = os.getenv("DEPLOYMENT_NAMESPACE", "default")
        self.k8s_context = os.getenv("K8S_CONTEXT")  # None = use current context

        # Deployment settings
        self.canary_percentage = int(os.getenv("CANARY_PERCENTAGE", "10"))
        self.validation_duration = int(os.getenv("VALIDATION_DURATION_SECONDS", "300"))
        # Pause after each traffic shift so metrics reflect the new split before
        # the next health check. Realistic in production, so tests pass 0.
        self.traffic_stabilization_seconds = int(
            os.getenv("TRAFFIC_STABILIZATION_SECONDS", "30")
        )
        self.auto_rollback_enabled = os.getenv("AUTO_ROLLBACK_ENABLED", "true").lower() == "true"
        self.rollback_timeout = int(os.getenv("ROLLBACK_TIMEOUT_SECONDS", "600"))

        # Thresholds
        self.thresholds = ThresholdConfig.from_env()

        # Memory (DevMemory from Chapter 9)
        self.memory_backend = os.getenv("MEMORY_BACKEND", "chroma")
        self.memory_persist_dir = os.getenv("MEMORY_PERSIST_DIR", "./data/memory")
        self.memory_collection = os.getenv("MEMORY_COLLECTION_NAME", "deployments")

        # Sentry (optional)
        self.sentry_dsn = os.getenv("SENTRY_DSN")
        self.sentry_environment = os.getenv("SENTRY_ENVIRONMENT", "lab")

        # Observability
        self.prometheus_url = os.getenv("PROMETHEUS_URL", "http://localhost:9090")
        self.grafana_url = os.getenv("GRAFANA_URL", "http://localhost:3000")

        # Testing
        self.use_mock_infrastructure = os.getenv("USE_MOCK_INFRASTRUCTURE", "true").lower() == "true"
        self.mock_api_url = os.getenv("MOCK_API_URL", "http://localhost:5678")

        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_format = os.getenv("LOG_FORMAT", "json")


# Global config instance
config = Config()
