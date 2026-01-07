"""Dataset Statistics Endpoint.

Provides cached computed statistics from the dataset_statistics table.
"""

from fastapi import APIRouter
from sqlalchemy import select

from src.api.dependencies import CurrentUser, ReadDBSession
from src.features.process_mining.models.dataset import DatasetMetadata
from src.features.process_mining.schemas.datasets import DatasetStatisticsResponse
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.workspaces.authorization import require_dataset_permission

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/{dataset_id}/statistics",
    response_model=DatasetStatisticsResponse,
    summary="Get Dataset Statistics",
    description="""
Get pre-computed statistics for a dataset.

These statistics are cached after ingestion for performance.
Includes volume metrics, duration statistics, and variant analysis.
""",
    responses={
        200: {"description": "Computed statistics"},
        404: {"description": "Dataset or statistics not found"},
    },
)
async def get_dataset_statistics(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> DatasetStatisticsResponse:
    """Get cached statistics for a dataset."""

    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Get computed statistics from metadata table
    result = await db.execute(
        select(DatasetMetadata).where(DatasetMetadata.dataset_id == dataset_id)
    )
    metadata = result.scalar_one_or_none()

    if not metadata:
        # Return basic stats from dataset if no computed metadata
        logger.warning("statistics_not_computed", dataset_id=dataset_id)
        from datetime import datetime

        return DatasetStatisticsResponse(
            dataset_id=dataset_id,
            total_events=dataset.total_events,
            total_cases=dataset.total_cases,
            total_activities=dataset.total_activities,
            total_variants=0,
            computed_at=dataset.created_at or datetime.utcnow(),
        )

    # Build response from metadata
    return DatasetStatisticsResponse(
        dataset_id=dataset_id,
        total_events=metadata.total_events,
        total_cases=metadata.total_cases,
        total_activities=metadata.total_activities,
        total_variants=metadata.total_variants,
        total_resources=metadata.total_resources,
        first_event_at=metadata.first_event_at,
        last_event_at=metadata.last_event_at,
        avg_case_duration=metadata.avg_case_duration,
        min_case_duration=metadata.min_case_duration,
        max_case_duration=metadata.max_case_duration,
        computed_at=metadata.computed_at,
        computation_time_ms=metadata.computation_time_ms,
    )
