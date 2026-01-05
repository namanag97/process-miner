"""Analytics Router - Statistics, cases, variants, activities endpoints.

Provides analytics and statistics APIs for datasets.
"""

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import func, select, text

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import Dataset, ProcessCase, ProcessEvent
from src.features.process_mining.schemas import (
    ActivityDetailResponse,
    CaseListResponse,
    CaseResponse,
    StatisticsResponse,
    VariantResponse,
)
from src.platform.core.exceptions import ProcessNotFoundError
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
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
) -> StatisticsResponse:
    """Get aggregate statistics for dataset."""
    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_READ
    )

    # Try to load from stored statistics
    if dataset.statistics_json:
        try:
            stats = json.loads(dataset.statistics_json)
            return StatisticsResponse(**stats)
        except Exception:
            pass

    # Compute basic statistics if not stored
    return StatisticsResponse(
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        total_variants=0,
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
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> CaseListResponse:
    """List cases with pagination."""
    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_READ
    )

    # Count total cases
    count_query = (
        select(func.count())
        .select_from(ProcessCase)
        .where(ProcessCase.dataset_id == dataset_id)
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

    return CaseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{dataset_id}/variants",
    summary="Get Process Variants",
    description="Get unique activity sequences (variants) with frequencies.",
)
async def get_variants(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
    top_n: int | None = Query(None, ge=1, le=100),
    top_k_percent: float | None = Query(None, ge=0.0, le=100.0),
) -> list[VariantResponse]:
    """Get process variants with frequencies."""
    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_READ
    )

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
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
    sort_by: str | None = Query(None, description="Sort by: frequency, duration"),
) -> list[ActivityDetailResponse]:
    """Get activity statistics."""
    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_READ
    )

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
