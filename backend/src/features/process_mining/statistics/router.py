"""Analytics Router - Statistics, cases, variants, activities endpoints.

Provides analytics and statistics APIs for datasets.
"""

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query
from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy import func, select, text

from src.api.dependencies import CurrentUser
from src.features.process_mining.models import ProcessCase, ProcessEvent
from src.features.process_mining.schemas import (
    ActivityDetailResponse,
    CaseListResponse,
    CaseResponse,
    StatisticsResponse,
    VariantResponse,
)
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.workspaces.authorization import require_dataset_permission

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/{dataset_id}/statistics",
    response_model=StatisticsResponse,
    summary="Get Dataset Statistics",
    description="Get comprehensive statistics for a dataset.",
)
async def get_statistics(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> StatisticsResponse:
    """Get aggregate statistics for dataset."""
    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Try to load from stored statistics
    if dataset.statistics_json:
        try:
            stats = json.loads(dataset.statistics_json)
            return StatisticsResponse(**stats)
        except json.JSONDecodeError as e:
            logger.warning(
                "statistics_json_parse_failed",
                dataset_id=dataset_id,
                error=str(e),
            )
        except PydanticValidationError as e:
            logger.warning(
                "statistics_validation_failed",
                dataset_id=dataset_id,
                error=str(e),
            )

    # Compute basic statistics if not stored
    # Compute total_variants from ProcessCase
    variant_count_result = await db.execute(
        select(func.count(func.distinct(ProcessCase.variant_key)))
        .where(ProcessCase.dataset_id == dataset_id)
        .where(ProcessCase.variant_key.isnot(None))
    )
    total_variants = variant_count_result.scalar() or 0

    return StatisticsResponse(
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        total_variants=total_variants,
        activities=[],
        start_activities={},
        end_activities={},
        avg_case_duration_seconds=None,
        min_case_duration_seconds=None,
        max_case_duration_seconds=None,
        date_range=None,
    )


@router.get(
    "/{dataset_id}/cases",
    response_model=CaseListResponse,
    summary="List Cases",
    description="List cases/traces in a dataset with pagination.",
)
async def list_cases(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> CaseListResponse:
    """List cases with pagination."""
    # Verify permission
    _, _dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Count total cases
    count_query = (
        select(func.count()).select_from(ProcessCase).where(ProcessCase.dataset_id == dataset_id)
    )
    total = (await db.execute(count_query)).scalar() or 0

    # Get cases with event count
    offset = (page - 1) * page_size
    query = (
        select(
            ProcessCase.case_id,
            ProcessCase.variant_key,
            ProcessCase.start_time,
            ProcessCase.end_time,
            func.count(ProcessEvent.id).label("event_count"),
        )
        .join(ProcessEvent, ProcessEvent.case_ref_id == ProcessCase.id)
        .where(ProcessCase.dataset_id == dataset_id)
        .group_by(ProcessCase.id)
        .order_by(ProcessCase.start_time.desc())
        .offset(offset)
        .limit(page_size)
    )

    result = await db.execute(query)
    rows = result.all()

    items = []
    for row in rows:
        duration = None
        if row.start_time and row.end_time:
            duration = (row.end_time - row.start_time).total_seconds()

        items.append(
            CaseResponse(
                case_id=row.case_id,
                event_count=row.event_count,
                variant=row.variant_key,
                start_time=row.start_time,
                end_time=row.end_time,
                duration_seconds=duration,
            )
        )

    # Calculate total pages
    pages = (total + page_size - 1) // page_size if total > 0 else 1

    return CaseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{dataset_id}/variants",
    summary="Get Process Variants",
    description="Get unique activity sequences (variants) with frequencies.",
)
async def get_variants(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
    top_n: int | None = Query(None, ge=1, le=100),
    top_k_percent: float | None = Query(None, ge=0.0, le=100.0),
) -> list[VariantResponse]:
    """Get process variants with frequencies."""
    # Verify permission
    _, _dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Group by variant_key
    query = (
        select(
            ProcessCase.variant_key,
            func.count(ProcessCase.id).label("case_count"),
        )
        .where(ProcessCase.dataset_id == dataset_id)
        .where(ProcessCase.variant_key.isnot(None))
        .group_by(ProcessCase.variant_key)
        .order_by(text("case_count DESC"))
    )

    if top_n:
        query = query.limit(top_n)

    result = await db.execute(query)
    rows = result.all()

    # Calculate total for percentages
    total_cases = sum(r.case_count for r in rows)

    variants = []
    cumulative_percent = 0.0

    for row in rows:
        freq_percent = (row.case_count / total_cases * 100) if total_cases > 0 else 0
        cumulative_percent += freq_percent

        # Parse activities from variant key
        activities = row.variant_key.split(" → ") if row.variant_key else []

        variants.append(
            VariantResponse(
                variant_key=row.variant_key or "",
                activity_trace=row.variant_key or "",
                activities=activities,
                case_count=row.case_count,
                frequency_percent=round(freq_percent, 2),
                unique_activity_count=len(set(activities)),
            )
        )

        # Stop if hit top_k_percent
        if top_k_percent and cumulative_percent >= top_k_percent:
            break

    return variants


@router.get(
    "/{dataset_id}/activities",
    summary="Get Activity Statistics",
    description="Get detailed statistics for each activity.",
)
async def get_activities(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
    sort_by: str | None = Query(None, description="Sort by: frequency, duration"),
) -> list[ActivityDetailResponse]:
    """Get activity statistics."""
    # Verify permission
    _, _dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Group by activity
    query = (
        select(
            ProcessEvent.activity,
            func.count(ProcessEvent.id).label("frequency"),
        )
        .join(ProcessCase, ProcessCase.id == ProcessEvent.case_ref_id)
        .where(ProcessCase.dataset_id == dataset_id)
        .group_by(ProcessEvent.activity)
        .order_by(text("frequency DESC"))
    )

    result = await db.execute(query)
    rows = result.all()

    # Calculate total for percentages
    total_events = sum(r.frequency for r in rows)

    activities = []
    for row in rows:
        freq_percent = (row.frequency / total_events * 100) if total_events > 0 else 0

        activities.append(
            ActivityDetailResponse(
                activity=row.activity,
                frequency=row.frequency,
                frequency_percent=round(freq_percent, 2),
            )
        )

    return activities


# =============================================================================
# Events and Metadata (per API spec)
# =============================================================================


class EventResponse(BaseModel):
    """Event response."""

    id: str
    case_id: str
    activity: str
    timestamp: datetime
    resource: str | None = None
    attributes: dict[str, Any] | None = None


class EventListResponse(BaseModel):
    """Paginated event list."""

    items: list[EventResponse]
    total: int
    page: int
    page_size: int


class MetadataResponse(BaseModel):
    """Dataset metadata response."""

    dataset_id: str
    total_events: int
    total_cases: int
    total_activities: int
    total_variants: int
    first_event_at: datetime | None = None
    last_event_at: datetime | None = None
    avg_case_duration_seconds: float | None = None
    activities: list[str] = []
    date_range: dict | None = None


@router.get(
    "/{dataset_id}/events",
    response_model=EventListResponse,
    summary="Query Events",
    description="""
Query events with pagination and filtering.

Use this to browse individual events in the event log.
    """,
)
async def list_events(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000, alias="limit"),
    case_id: str | None = Query(None, description="Filter by case ID"),
    activity: str | None = Query(None, description="Filter by activity"),
    from_date: datetime | None = Query(None, alias="from", description="Start date"),
    to_date: datetime | None = Query(None, alias="to", description="End date"),
) -> EventListResponse:
    """Query events with pagination."""
    # Verify permission
    _, _dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Build query
    query = (
        select(ProcessEvent, ProcessCase.case_id)
        .join(ProcessCase, ProcessCase.id == ProcessEvent.case_ref_id)
        .where(ProcessCase.dataset_id == dataset_id)
    )

    # Apply filters
    if case_id:
        query = query.where(ProcessCase.case_id == case_id)
    if activity:
        query = query.where(ProcessEvent.activity == activity)
    if from_date:
        query = query.where(ProcessEvent.timestamp >= from_date)
    if to_date:
        query = query.where(ProcessEvent.timestamp <= to_date)

    # Count
    count_query = (
        select(func.count())
        .select_from(ProcessEvent)
        .join(ProcessCase, ProcessCase.id == ProcessEvent.case_ref_id)
        .where(ProcessCase.dataset_id == dataset_id)
    )
    if case_id:
        count_query = count_query.where(ProcessCase.case_id == case_id)
    if activity:
        count_query = count_query.where(ProcessEvent.activity == activity)

    total = (await db.execute(count_query)).scalar() or 0

    # Paginate
    offset = (page - 1) * limit
    query = query.order_by(ProcessEvent.timestamp.asc()).offset(offset).limit(limit)

    result = await db.execute(query)
    rows = result.all()

    items = [
        EventResponse(
            id=event.id,
            case_id=case_id_val,
            activity=event.activity,
            timestamp=event.timestamp,
            resource=event.resource,
            attributes=json.loads(event.attributes_json) if event.attributes_json else None,
        )
        for event, case_id_val in rows
    ]

    return EventListResponse(
        items=items,
        total=total,
        page=page,
        page_size=limit,
    )


@router.get(
    "/{dataset_id}/metadata",
    response_model=MetadataResponse,
    summary="Get Computed Metadata",
    description="""
Get computed metadata for a dataset.

Includes aggregated statistics computed during ingestion.
    """,
)
async def get_metadata(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> MetadataResponse:
    """Get computed dataset metadata."""
    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Get metadata from dataset record
    activities = []
    if dataset.activities_json:
        try:
            activities = json.loads(dataset.activities_json)
        except json.JSONDecodeError as e:
            logger.warning(
                "activities_json_parse_failed",
                dataset_id=dataset_id,
                error=str(e),
            )

    # Try to get detailed metadata
    date_range = None
    first_event = None
    last_event = None
    avg_duration = None

    if dataset.metadata_record:
        meta = dataset.metadata_record
        first_event = meta.first_event_at
        last_event = meta.last_event_at
        avg_duration = meta.avg_case_duration

        if first_event and last_event:
            date_range = {
                "start": first_event.isoformat(),
                "end": last_event.isoformat(),
            }

    # Compute total_variants from ProcessCase
    variant_count_result = await db.execute(
        select(func.count(func.distinct(ProcessCase.variant_key)))
        .where(ProcessCase.dataset_id == dataset_id)
        .where(ProcessCase.variant_key.isnot(None))
    )
    total_variants = variant_count_result.scalar() or 0

    return MetadataResponse(
        dataset_id=dataset_id,
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        total_variants=total_variants,
        first_event_at=first_event,
        last_event_at=last_event,
        avg_case_duration_seconds=avg_duration,
        activities=activities,
        date_range=date_range,
    )
