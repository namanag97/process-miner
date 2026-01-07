"""Statistics Service for On-Demand Computation.

Provides centralized statistics management for datasets:
- Get cached statistics from DatasetMetadata
- Recompute statistics on-demand
- Invalidate statistics when data changes

Per tech spec: Statistics are computed during ingestion and stored in DatasetMetadata.
This service provides the API for accessing and refreshing those statistics.
"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.process_mining.models import (
    Dataset,
    DatasetMetadata,
    ProcessCase,
    ProcessEvent,
)
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DatasetStatistics:
    """Computed statistics for a dataset."""

    dataset_id: str
    total_events: int
    total_cases: int
    total_activities: int
    total_variants: int
    first_event_at: datetime | None
    last_event_at: datetime | None
    avg_case_duration: float | None
    min_case_duration: float | None
    max_case_duration: float | None
    total_resources: int | None
    computed_at: datetime
    computation_time_ms: int | None
    from_cache: bool = True


class StatisticsService:
    """Service for dataset statistics management.

    Single source of truth for statistics is DatasetMetadata table.
    This service provides access and on-demand computation.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_statistics(
        self,
        dataset_id: str,
        force_recompute: bool = False,
    ) -> DatasetStatistics | None:
        """Get statistics for a dataset.

        Args:
            dataset_id: Dataset identifier
            force_recompute: If True, bypass cache and recompute

        Returns:
            DatasetStatistics or None if dataset doesn't exist
        """
        if not force_recompute:
            # Try to get from DatasetMetadata cache
            cached = await self._get_cached_statistics(dataset_id)
            if cached:
                logger.debug("statistics_cache_hit", dataset_id=dataset_id)
                return cached

        # Recompute statistics
        logger.info("statistics_computing", dataset_id=dataset_id)
        return await self.compute_statistics(dataset_id)

    async def compute_statistics(self, dataset_id: str) -> DatasetStatistics | None:
        """Force recompute statistics for a dataset.

        Computes fresh statistics from ProcessCase/ProcessEvent tables
        and stores in DatasetMetadata.

        Args:
            dataset_id: Dataset identifier

        Returns:
            DatasetStatistics or None if dataset doesn't exist
        """
        start_time = time.perf_counter()

        # Verify dataset exists
        dataset = await self.db.get(Dataset, dataset_id)
        if not dataset:
            logger.warning("statistics_dataset_not_found", dataset_id=dataset_id)
            return None

        # Compute counts
        case_count = (
            await self.db.scalar(
                select(func.count())
                .select_from(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
            )
            or 0
        )

        event_count = (
            await self.db.scalar(
                select(func.count())
                .select_from(ProcessEvent)
                .join(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
            )
            or 0
        )

        activity_count = (
            await self.db.scalar(
                select(func.count(func.distinct(ProcessEvent.activity)))
                .select_from(ProcessEvent)
                .join(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
            )
            or 0
        )

        variant_count = (
            await self.db.scalar(
                select(func.count(func.distinct(ProcessCase.variant_key)))
                .select_from(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
                .where(ProcessCase.variant_key.isnot(None))
            )
            or 0
        )

        # Compute time range
        time_range = await self.db.execute(
            select(
                func.min(ProcessEvent.timestamp),
                func.max(ProcessEvent.timestamp),
            )
            .select_from(ProcessEvent)
            .join(ProcessCase)
            .where(ProcessCase.dataset_id == dataset_id)
        )
        time_result = time_range.one_or_none()
        first_event_at = time_result[0] if time_result else None
        last_event_at = time_result[1] if time_result else None

        # Compute case duration stats (if cases have end_time)
        duration_stats = await self.db.execute(
            select(
                func.avg(ProcessCase.duration_seconds),
                func.min(ProcessCase.duration_seconds),
                func.max(ProcessCase.duration_seconds),
            )
            .select_from(ProcessCase)
            .where(ProcessCase.dataset_id == dataset_id)
            .where(ProcessCase.duration_seconds.isnot(None))
        )
        duration_result = duration_stats.one_or_none()
        avg_duration = float(duration_result[0]) if duration_result and duration_result[0] else None
        min_duration = float(duration_result[1]) if duration_result and duration_result[1] else None
        max_duration = float(duration_result[2]) if duration_result and duration_result[2] else None

        # Count resources
        resource_count = (
            await self.db.scalar(
                select(func.count(func.distinct(ProcessEvent.resource)))
                .select_from(ProcessEvent)
                .join(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
                .where(ProcessEvent.resource.isnot(None))
            )
            or 0
        )

        computation_time_ms = int((time.perf_counter() - start_time) * 1000)
        computed_at = datetime.utcnow()

        # Store in DatasetMetadata
        await self._store_statistics(
            dataset_id=dataset_id,
            total_events=event_count,
            total_cases=case_count,
            total_activities=activity_count,
            total_variants=variant_count,
            first_event_at=first_event_at,
            last_event_at=last_event_at,
            avg_case_duration=avg_duration,
            min_case_duration=min_duration,
            max_case_duration=max_duration,
            total_resources=resource_count if resource_count > 0 else None,
            computed_at=computed_at,
            computation_time_ms=computation_time_ms,
        )

        logger.info(
            "statistics_computed",
            dataset_id=dataset_id,
            total_events=event_count,
            total_cases=case_count,
            total_activities=activity_count,
            computation_time_ms=computation_time_ms,
        )

        return DatasetStatistics(
            dataset_id=dataset_id,
            total_events=event_count,
            total_cases=case_count,
            total_activities=activity_count,
            total_variants=variant_count,
            first_event_at=first_event_at,
            last_event_at=last_event_at,
            avg_case_duration=avg_duration,
            min_case_duration=min_duration,
            max_case_duration=max_duration,
            total_resources=resource_count if resource_count > 0 else None,
            computed_at=computed_at,
            computation_time_ms=computation_time_ms,
            from_cache=False,
        )

    async def invalidate_statistics(self, dataset_id: str) -> None:
        """Invalidate cached statistics for a dataset.

        Called when dataset data changes (e.g., after filtering).
        Next call to get_statistics will recompute.

        Args:
            dataset_id: Dataset identifier
        """
        from sqlalchemy import delete

        await self.db.execute(
            delete(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
        )
        await self.db.commit()
        logger.info("statistics_invalidated", dataset_id=dataset_id)

    async def _get_cached_statistics(self, dataset_id: str) -> DatasetStatistics | None:
        """Get statistics from DatasetMetadata cache."""
        result = await self.db.execute(
            select(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
        )
        metadata = result.scalar_one_or_none()

        if not metadata:
            return None

        return DatasetStatistics(
            dataset_id=dataset_id,
            total_events=metadata.total_events,
            total_cases=metadata.total_cases,
            total_activities=metadata.total_activities,
            total_variants=metadata.total_variants,
            first_event_at=metadata.first_event_at,
            last_event_at=metadata.last_event_at,
            avg_case_duration=metadata.avg_case_duration,
            min_case_duration=metadata.min_case_duration,
            max_case_duration=metadata.max_case_duration,
            total_resources=metadata.total_resources,
            computed_at=metadata.computed_at,
            computation_time_ms=metadata.computation_time_ms,
            from_cache=True,
        )

    async def _store_statistics(
        self,
        dataset_id: str,
        total_events: int,
        total_cases: int,
        total_activities: int,
        total_variants: int,
        first_event_at: datetime | None,
        last_event_at: datetime | None,
        avg_case_duration: float | None,
        min_case_duration: float | None,
        max_case_duration: float | None,
        total_resources: int | None,
        computed_at: datetime,
        computation_time_ms: int,
    ) -> None:
        """Store statistics in DatasetMetadata table."""
        # Check if metadata exists
        existing = await self.db.execute(
            select(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
        )
        metadata = existing.scalar_one_or_none()

        if metadata:
            # Update existing
            metadata.total_events = total_events
            metadata.total_cases = total_cases
            metadata.total_activities = total_activities
            metadata.total_variants = total_variants
            metadata.first_event_at = first_event_at
            metadata.last_event_at = last_event_at
            metadata.avg_case_duration = avg_case_duration
            metadata.min_case_duration = min_case_duration
            metadata.max_case_duration = max_case_duration
            metadata.total_resources = total_resources
            metadata.computed_at = computed_at
            metadata.computation_time_ms = computation_time_ms
        else:
            # Create new
            metadata = DatasetMetadata(
                dataset_id=dataset_id,
                total_events=total_events,
                total_cases=total_cases,
                total_activities=total_activities,
                total_variants=total_variants,
                first_event_at=first_event_at,
                last_event_at=last_event_at,
                avg_case_duration=avg_case_duration,
                min_case_duration=min_case_duration,
                max_case_duration=max_case_duration,
                total_resources=total_resources,
                computed_at=computed_at,
                computation_time_ms=computation_time_ms,
            )
            self.db.add(metadata)

        await self.db.commit()


async def get_dataset_statistics(
    db: AsyncSession,
    dataset_id: str,
    force_recompute: bool = False,
) -> DatasetStatistics | None:
    """Convenience function for getting dataset statistics.

    Args:
        db: Database session
        dataset_id: Dataset identifier
        force_recompute: If True, bypass cache and recompute

    Returns:
        DatasetStatistics or None
    """
    service = StatisticsService(db)
    return await service.get_statistics(dataset_id, force_recompute)


def statistics_to_dict(stats: DatasetStatistics) -> dict[str, Any]:
    """Convert DatasetStatistics to dict for API response."""
    return {
        "dataset_id": stats.dataset_id,
        "total_events": stats.total_events,
        "total_cases": stats.total_cases,
        "total_activities": stats.total_activities,
        "total_variants": stats.total_variants,
        "first_event_at": stats.first_event_at.isoformat() if stats.first_event_at else None,
        "last_event_at": stats.last_event_at.isoformat() if stats.last_event_at else None,
        "avg_case_duration": stats.avg_case_duration,
        "min_case_duration": stats.min_case_duration,
        "max_case_duration": stats.max_case_duration,
        "total_resources": stats.total_resources,
        "computed_at": stats.computed_at.isoformat() if stats.computed_at else None,
        "computation_time_ms": stats.computation_time_ms,
        "from_cache": stats.from_cache,
    }
