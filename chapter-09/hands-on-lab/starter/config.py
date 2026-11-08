"""
Configuration for DevMemory system.
"""
import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv


class DevMemoryConfig(BaseModel):
    """Configuration for DevMemory system."""
    project_name: str = "default"
    chromadb_host: str = "localhost"
    chromadb_port: int = 8000
    # Note on confidence_threshold and retention_days: the default exercise
    # path never reads them. Decay is the Exercise 5 extension (the age-decay
    # factor in starter/trust.py) and runs in full in the standalone
    # code-examples/confidence_decay.py demo. When you extend the lab, wire
    # confidence_threshold in as the min_trust cutoff for filter_by_trust()
    # and retention_days into a cleanup sweep of old episodes.
    confidence_threshold: float = 0.5
    consolidation_min_episodes: int = 3
    retention_days: int = 90


def load_config() -> DevMemoryConfig:
    """Load configuration from environment variables."""
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)

    return DevMemoryConfig(
        project_name=os.getenv("PROJECT_NAME", "devmemory-lab"),
        chromadb_host=os.getenv("CHROMADB_HOST", "localhost"),
        chromadb_port=int(os.getenv("CHROMADB_PORT", "8000")),
        confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.5")),
        consolidation_min_episodes=int(os.getenv("CONSOLIDATION_MIN_EPISODES", "3")),
        retention_days=int(os.getenv("RETENTION_DAYS", "90")),
    )
