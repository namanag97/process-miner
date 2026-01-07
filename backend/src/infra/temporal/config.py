"""Temporal Configuration.

Centralized configuration for Temporal workers, queues, and timeouts.
"""

from dataclasses import dataclass, field
from functools import lru_cache

from pydantic_settings import BaseSettings

from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)


class TemporalSettings(BaseSettings):
    """Environment-based Temporal settings."""

    temporal_host: str = "localhost:7233"
    temporal_namespace: str = "default"
    temporal_use_tls: bool = False

    class Config:
        env_prefix = ""
        case_sensitive = False


@dataclass
class TemporalConfig:
    """Temporal worker and queue configuration."""

    # Server connection
    host: str = "localhost:7233"
    namespace: str = "default"
    use_tls: bool = False

    # Task queues
    QUEUE_INGESTION: str = "ingestion-queue"
    QUEUE_ANALYSIS: str = "analysis-queue"
    QUEUE_ML: str = "ml-queue"

    # Worker scaling (per process)
    ingestion_workers: int = 2
    analysis_workers: int = 2
    ml_workers: int = 1

    # Concurrency limits
    max_concurrent_activities: int = 3
    max_cached_workflows: int = 100

    # Default timeouts (seconds)
    default_activity_timeout: int = 3600  # 1 hour
    default_heartbeat_timeout: int = 60  # 1 minute
    heartbeat_interval: int = 30  # 30 seconds

    # Retry policies
    default_max_retries: int = 3
    retry_initial_interval_seconds: float = 1.0
    retry_max_interval_seconds: float = 60.0
    retry_backoff_coefficient: float = 2.0

    # Feature flags
    use_temporal: bool = field(default=True)  # Enable Temporal by default
    use_temporal_v2: bool = field(
        default=True
    )  # Use Temporal-native v2 architecture (enabled - no customers to migrate)


@lru_cache
def get_temporal_config() -> TemporalConfig:
    """Get cached Temporal configuration from environment."""
    settings = TemporalSettings()
    return TemporalConfig(
        host=settings.temporal_host,
        namespace=settings.temporal_namespace,
        use_tls=settings.temporal_use_tls,
    )
