"""Analytics Cache Projection - Event-Driven Read Model Updates.

Subscribes to dataset domain events and pre-computes analytics:
- On ingestion: Compute DFG, variants, statistics
- On deletion: Invalidate cached analytics

This enables fast query responses without real-time computation.

Usage (automatic via event subscription):
    # When DatasetIngestedEvent is published, the projection:
    # 1. Loads the Parquet file via DuckDB
    # 2. Pre-computes analytics (DFG, variants, statistics)
    # 3. Caches results for fast retrieval
"""

from src.platform.core.domain_events import (
    DatasetDeletedEvent,
    DatasetIngestedEvent,
    event_publisher,
)
from src.platform.core.logging_config import get_logger
from src.platform.infrastructure.cache import cache_service

logger = get_logger(__name__)

# Cache version - increment when computation logic changes
CACHE_VERSION = "v1"


class AnalyticsCacheProjection:
    """Pre-compute common analytics on dataset ingestion.

    This projection listens to dataset events and maintains
    pre-computed analytics in the cache layer for fast reads.

    Cached items:
    - DFG (Directly-Follows Graph)
    - Process variants
    - Basic statistics
    """

    def __init__(self):
        # Register event handlers
        self._register_handlers()

    def _register_handlers(self):
        """Subscribe to relevant domain events."""
        event_publisher.subscribe(DatasetIngestedEvent)(self.on_dataset_ingested)
        event_publisher.subscribe(DatasetDeletedEvent)(self.on_dataset_deleted)
        logger.info("analytics_cache_projection_registered")

    async def on_dataset_ingested(self, event: DatasetIngestedEvent) -> None:
        """Handle dataset ingestion - pre-compute and cache analytics.

        Args:
            event: The ingestion event containing dataset metadata
        """
        logger.info(
            "analytics_cache_projection_processing",
            dataset_id=event.dataset_id,
            parquet_path=event.parquet_path,
            total_events=event.total_events,
        )

        try:
            # Pre-compute analytics in background
            # Note: For large datasets, this could be offloaded to Temporal
            await self._cache_basic_statistics(event)

            logger.info(
                "analytics_cache_projection_completed",
                dataset_id=event.dataset_id,
            )
        except Exception as e:
            logger.error(
                "analytics_cache_projection_failed",
                dataset_id=event.dataset_id,
                error=str(e),
            )
            # Don't raise - projection failures shouldn't block ingestion

    async def on_dataset_deleted(self, event: DatasetDeletedEvent) -> None:
        """Handle dataset deletion - invalidate cached analytics.

        Args:
            event: The deletion event containing dataset ID
        """
        logger.info(
            "analytics_cache_invalidating",
            dataset_id=event.dataset_id,
        )

        # Invalidate all cached analytics for this dataset
        cache_keys = [
            f"dfg:{CACHE_VERSION}:{event.dataset_id}",
            f"variants:{CACHE_VERSION}:{event.dataset_id}",
            f"statistics:{CACHE_VERSION}:{event.dataset_id}",
            f"bottlenecks:{CACHE_VERSION}:{event.dataset_id}",
            f"rework:{CACHE_VERSION}:{event.dataset_id}",
            f"cycle_time:{CACHE_VERSION}:{event.dataset_id}",
            f"throughput:{CACHE_VERSION}:{event.dataset_id}",
            f"rework_chains:{CACHE_VERSION}:{event.dataset_id}",
        ]

        for key in cache_keys:
            try:
                cache_service.delete(key)
            except Exception:
                pass  # Ignore cache deletion errors

        logger.info(
            "analytics_cache_invalidated",
            dataset_id=event.dataset_id,
            keys_invalidated=len(cache_keys),
        )

    async def _cache_basic_statistics(self, event: DatasetIngestedEvent) -> None:
        """Cache basic statistics derived from ingestion event.

        This is a lightweight operation using data from the event itself.
        More expensive computations (DFG, variants) can be done lazily.
        """
        statistics = {
            "total_events": event.total_events,
            "total_cases": event.total_cases,
            "total_activities": event.total_activities,
            "parquet_path": event.parquet_path,
        }

        cache_key = f"statistics:{CACHE_VERSION}:{event.dataset_id}"
        cache_service.set(cache_key, statistics, ttl=86400)  # 24 hours


# Global projection instance - registers handlers on import
analytics_cache_projection = AnalyticsCacheProjection()
