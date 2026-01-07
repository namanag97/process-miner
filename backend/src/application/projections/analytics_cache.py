"""Analytics Cache Projection.

Listens to domain events and updates read model caches.
This enables pre-computation of analytics for fast reads.

Usage:
    # Register projection with event bus
    projection = AnalyticsCacheProjection(cache_service)
    event_bus.subscribe(DatasetIngestedEvent, projection.on_dataset_ingested)
    event_bus.subscribe(DatasetDeletedEvent, projection.on_dataset_deleted)
"""

from dataclasses import dataclass
from typing import Any

from src.platform.core.logging_config import get_logger
from src.platform.infrastructure.cache import cache_service, invalidate_dataset_cache

logger = get_logger(__name__)


# =============================================================================
# Event Types (mirrors from events.py)
# =============================================================================

DATASET_INGESTED = "dataset.ingestion_completed"
DATASET_DELETED = "dataset.deleted"
MODEL_DISCOVERED = "model.discovered"


# =============================================================================
# Projection
# =============================================================================


@dataclass
class AnalyticsCacheProjection:
    """Projection that updates analytics caches based on domain events.
    
    When a dataset is ingested:
    - Pre-compute common analytics (DFG, variants, bottlenecks)
    - Store in cache for fast reads
    
    When a dataset is deleted:
    - Invalidate all related caches
    """
    
    cache: Any = None
    
    def __post_init__(self):
        if self.cache is None:
            self.cache = cache_service
    
    async def on_dataset_ingested(
        self,
        dataset_id: str,
        parquet_path: str,
        event_count: int,
    ) -> None:
        """Handle dataset ingestion completion.
        
        Pre-computes analytics that are commonly requested.
        This runs asynchronously after ingestion completes.
        """
        logger.info(
            "projection_processing",
            event="dataset_ingested",
            dataset_id=dataset_id,
            event_count=event_count,
        )
        
        try:
            # Pre-compute and cache DFG
            # This is handled by the analytics service directly
            # Just set a flag that fresh data is available
            self.cache.set(
                f"dataset:{dataset_id}:ready", 
                {"parquet_path": parquet_path, "event_count": event_count},
                ttl=86400,  # 24 hours
            )
            
            logger.info(
                "projection_completed",
                event="dataset_ingested", 
                dataset_id=dataset_id,
            )
            
        except Exception as e:
            logger.error(
                "projection_failed",
                event="dataset_ingested",
                dataset_id=dataset_id,
                error=str(e),
            )
    
    async def on_dataset_deleted(
        self,
        dataset_id: str,
        parquet_path: str | None = None,
    ) -> None:
        """Handle dataset deletion.
        
        Invalidates all caches related to the dataset.
        """
        logger.info(
            "projection_processing",
            event="dataset_deleted",
            dataset_id=dataset_id,
        )
        
        try:
            # Invalidate all analytics caches for this dataset
            deleted = invalidate_dataset_cache(dataset_id)
            
            # Also remove ready flag
            self.cache.delete(f"dataset:{dataset_id}:ready")
            
            logger.info(
                "projection_completed",
                event="dataset_deleted",
                dataset_id=dataset_id,
                keys_deleted=deleted,
            )
            
        except Exception as e:
            logger.error(
                "projection_failed",
                event="dataset_deleted",
                dataset_id=dataset_id,
                error=str(e),
            )
    
    async def on_model_discovered(
        self,
        model_id: str,
        dataset_id: str,
        algorithm: str,
    ) -> None:
        """Handle process model discovery.
        
        Caches the discovered model for fast retrieval.
        """
        logger.info(
            "projection_processing",
            event="model_discovered",
            model_id=model_id,
            dataset_id=dataset_id,
            algorithm=algorithm,
        )
        
        # Model itself is stored in PostgreSQL
        # Just invalidate any cached DFG that might be stale
        self.cache.delete(f"dfg:{dataset_id}")


# =============================================================================
# Event Handlers Registry
# =============================================================================


def register_projections() -> AnalyticsCacheProjection:
    """Create and return projection instance for event registration."""
    return AnalyticsCacheProjection(cache=cache_service)


# Global projection instance
analytics_projection = AnalyticsCacheProjection()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "AnalyticsCacheProjection",
    "analytics_projection",
    "register_projections",
]
