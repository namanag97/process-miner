"""Filtering Router - Event Log Filtering API.

Provides endpoints for filtering event logs using various criteria:
- Time-based filtering
- Variant-based filtering (top-k, coverage)
- Activity-based filtering
- Performance-based filtering (duration, case size)
"""

import json
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.core.logging_config import get_logger
from src.models.orm import Dataset, ProcessCase, ProcessEvent
from src.models.schemas import (
    FilterConfig,
    FilteredLogListResponse,
    FilteredLogResponse,
    FilterOptionsResponse,
    FilterPreviewRequest,
    FilterPreviewResponse,
    FilterRequest,
    FilterStatistics,
    FilterTemplateListResponse,
    FilterTemplateResponse,
)
from src.services.filtering import filtering_service

logger = get_logger(__name__)

router = APIRouter(prefix="/filtering", tags=["Filtering"])


# =============================================================================
# Apply Filters
# =============================================================================


@router.post("/logs/{log_id}/apply", response_model=FilteredLogResponse)
async def apply_filters(
    log_id: str,
    request: FilterRequest,
    db: AsyncSession = Depends(get_db),
) -> FilteredLogResponse:
    """
    Apply filters to an event log and create a new filtered log.

    This creates a new event log that is a filtered version of the source log.
    The original log is not modified.
    """
    logger.info("applying_filters", log_id=log_id, filter_count=len(request.filters))

    # Get source log with cases and events
    query = select(Dataset).where(Dataset.id == log_id)
    result = await db.execute(query)
    source_log = result.scalar_one_or_none()

    if not source_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")

    # Convert to PM4Py log
    pm4py_log = filtering_service.to_pm4py_log(source_log)
    original_pm4py = pm4py_log  # Keep reference for statistics

    # Apply filter chain
    filters_config = [{"type": f.type, "params": f.params} for f in request.filters]
    filtered_pm4py = filtering_service.apply_filter_chain(pm4py_log, filters_config)

    # Compute statistics
    stats = filtering_service.compute_filter_statistics(original_pm4py, filtered_pm4py)

    if not request.save_result:
        # Return preview-style response without saving
        return FilteredLogResponse(
            id="preview",
            name=request.name or f"Filtered {source_log.name}",
            source_dataset_id=log_id,
            is_filtered=True,
            filter_config=request.filters,
            total_events=stats["filtered_events"],
            total_cases=stats["filtered_cases"],
            total_activities=stats["filtered_activities"],
            statistics=FilterStatistics(**stats),
            created_at=datetime.utcnow(),
        )

    # Create new filtered Dataset
    filtered_name = request.name or f"Filtered {source_log.name}"

    # Get unique activities from filtered log
    activities = set()
    for trace in filtered_pm4py:
        for event in trace:
            activities.add(event.get("concept:name", ""))

    new_log = Dataset(
        name=filtered_name,
        source_file=source_log.source_file,
        source_format=source_log.source_format,
        total_cases=len(filtered_pm4py),
        total_events=sum(len(trace) for trace in filtered_pm4py),
        total_activities=len(activities),
        activities_json=json.dumps(sorted(activities)),
        source_log_id=log_id,
        filter_config_json=json.dumps(filters_config),
        is_filtered=True,
        filter_stats_json=json.dumps(stats),
    )
    db.add(new_log)
    await db.flush()

    # Create cases and events for filtered log
    for trace in filtered_pm4py:
        case_id = trace.attributes.get("concept:name", "")

        # Calculate case timestamps
        timestamps = [e.get("time:timestamp") for e in trace if "time:timestamp" in e]
        start_time = min(timestamps) if timestamps else None
        end_time = max(timestamps) if timestamps else None

        # Create variant key
        activity_sequence = tuple(e.get("concept:name", "") for e in trace)
        variant_key = " -> ".join(activity_sequence)

        case = ProcessCase(
            log_id=new_log.id,
            case_id=case_id,
            variant_key=variant_key,
            start_time=start_time,
            end_time=end_time,
        )
        db.add(case)
        await db.flush()

        # Create events
        for event in trace:
            attrs = {
                k: v
                for k, v in event.items()
                if k not in ["concept:name", "time:timestamp", "org:resource"]
            }

            process_event = ProcessEvent(
                case_ref_id=case.id,
                activity=event.get("concept:name", ""),
                timestamp=event.get("time:timestamp", datetime.utcnow()),
                resource=event.get("org:resource"),
                attributes_json=json.dumps(attrs) if attrs else None,
            )
            db.add(process_event)

    await db.commit()

    logger.info(
        "filters_applied",
        log_id=log_id,
        new_log_id=new_log.id,
        original_cases=stats["original_cases"],
        filtered_cases=stats["filtered_cases"],
    )

    return FilteredLogResponse(
        id=new_log.id,
        name=new_log.name,
        source_dataset_id=log_id,
        is_filtered=True,
        filter_config=request.filters,
        total_events=new_log.total_events,
        total_cases=new_log.total_cases,
        total_activities=new_log.total_activities,
        statistics=FilterStatistics(**stats),
        created_at=new_log.created_at,
    )


# =============================================================================
# Preview Filters
# =============================================================================


@router.post("/logs/{log_id}/preview", response_model=FilterPreviewResponse)
async def preview_filters(
    log_id: str,
    request: FilterPreviewRequest,
    db: AsyncSession = Depends(get_db),
) -> FilterPreviewResponse:
    """
    Preview the impact of filters without saving.

    Returns statistics on how many cases/events would be retained.
    """
    logger.info("previewing_filters", log_id=log_id, filter_count=len(request.filters))

    # Get source log
    query = select(Dataset).where(Dataset.id == log_id)
    result = await db.execute(query)
    source_log = result.scalar_one_or_none()

    if not source_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")

    # Convert to PM4Py log
    pm4py_log = filtering_service.to_pm4py_log(source_log)
    original_pm4py = pm4py_log

    # Apply filter chain
    filters_config = [{"type": f.type, "params": f.params} for f in request.filters]
    filtered_pm4py = filtering_service.apply_filter_chain(pm4py_log, filters_config)

    # Compute statistics
    stats = filtering_service.compute_filter_statistics(original_pm4py, filtered_pm4py)

    logger.info(
        "filter_preview_completed",
        log_id=log_id,
        would_retain_cases=stats["filtered_cases"],
    )

    return FilterPreviewResponse(
        would_retain_cases=stats["filtered_cases"],
        would_retain_events=stats["filtered_events"],
        statistics=FilterStatistics(**stats),
        filters_applied=request.filters,
    )


# =============================================================================
# Filter Options
# =============================================================================


@router.get("/logs/{log_id}/options", response_model=FilterOptionsResponse)
async def get_filter_options(
    log_id: str,
    db: AsyncSession = Depends(get_db),
) -> FilterOptionsResponse:
    """
    Get available filter options based on log contents.

    Returns activities, resources, time ranges, and other values
    that can be used for filtering.
    """
    logger.info("getting_filter_options", log_id=log_id)

    # Get source log
    query = select(Dataset).where(Dataset.id == log_id)
    result = await db.execute(query)
    source_log = result.scalar_one_or_none()

    if not source_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")

    # Convert to PM4Py log
    pm4py_log = filtering_service.to_pm4py_log(source_log)

    # Get filter options
    options = filtering_service.get_filter_options(pm4py_log)

    return FilterOptionsResponse(**options)


# =============================================================================
# List Filtered Logs
# =============================================================================


@router.get("/logs/{log_id}/results", response_model=FilteredLogListResponse)
async def list_filtered_logs(
    log_id: str,
    db: AsyncSession = Depends(get_db),
) -> FilteredLogListResponse:
    """
    List all filtered versions of an event log.
    """
    logger.info("listing_filtered_logs", source_log_id=log_id)

    # Get source log
    query = select(Dataset).where(Dataset.id == log_id)
    result = await db.execute(query)
    source_log = result.scalar_one_or_none()

    if not source_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")

    # Get filtered logs
    query = (
        select(Dataset)
        .where(Dataset.source_dataset_id == log_id)
        .where(Dataset.is_filtered.is_(True))
        .order_by(Dataset.created_at.desc())
    )
    result = await db.execute(query)
    filtered_logs = result.scalars().all()

    items = []
    for log in filtered_logs:
        filter_config = []
        if log.filter_config_json:
            try:
                config_list = json.loads(log.filter_config_json)
                filter_config = [FilterConfig(**c) for c in config_list]
            except Exception:
                pass

        stats = None
        if log.filter_stats_json:
            try:
                stats_dict = json.loads(log.filter_stats_json)
                stats = FilterStatistics(**stats_dict)
            except Exception:
                pass

        items.append(
            FilteredLogResponse(
                id=log.id,
                name=log.name,
                source_dataset_id=log_id,
                is_filtered=True,
                filter_config=filter_config,
                total_events=log.total_events,
                total_cases=log.total_cases,
                total_activities=log.total_activities,
                statistics=stats,
                created_at=log.created_at,
            )
        )

    return FilteredLogListResponse(
        source_dataset_id=log_id,
        source_dataset_name=source_log.name,
        filtered_logs=items,
        total=len(items),
    )


# =============================================================================
# Delete Filtered Log
# =============================================================================


@router.delete("/logs/{log_id}/results/{filtered_id}")
async def delete_filtered_log(
    log_id: str,
    filtered_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Delete a filtered log.
    """
    logger.info("deleting_filtered_log", source_log_id=log_id, filtered_id=filtered_id)

    # Verify the filtered log exists and belongs to the source log
    query = (
        select(Dataset)
        .where(Dataset.id == filtered_id)
        .where(Dataset.source_dataset_id == log_id)
        .where(Dataset.is_filtered.is_(True))
    )
    result = await db.execute(query)
    filtered_log = result.scalar_one_or_none()

    if not filtered_log:
        raise HTTPException(
            status_code=404,
            detail=f"Filtered log {filtered_id} not found for source log {log_id}",
        )

    await db.delete(filtered_log)
    await db.commit()

    logger.info("filtered_log_deleted", filtered_id=filtered_id)

    return {"message": f"Filtered log {filtered_id} deleted successfully"}


# =============================================================================
# Filter Templates
# =============================================================================


@router.get("/templates", response_model=FilterTemplateListResponse)
async def get_filter_templates() -> FilterTemplateListResponse:
    """
    Get pre-built filter templates.
    """
    logger.info("getting_filter_templates")

    templates_raw = filtering_service.get_filter_templates()
    templates = [
        FilterTemplateResponse(
            id=t["id"],
            name=t["name"],
            description=t["description"],
            filters=[FilterConfig(**f) for f in t["filters"]],
        )
        for t in templates_raw
    ]

    return FilterTemplateListResponse(templates=templates)
