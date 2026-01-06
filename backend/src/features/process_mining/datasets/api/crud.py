"""CRUD Router - List, Get, Delete dataset endpoints.

Dataset lifecycle management for process mining event logs.

## Business Context
Datasets (event logs) are the foundation of process mining:
- Upload CSV/XES files containing process execution data
- Map columns to case_id, activity, timestamp, resource
- Ingest to create queryable event/case tables
- Analyze with process discovery, conformance checking, analytics

## Dataset Status Flow
```
PENDING → UPLOADED → VALIDATING → VALIDATED → MAPPED → INGESTING → READY
                                                      ↘ ERROR
```

## Testing Instructions

### Prerequisites
1. Create a project first: `POST /api/v1/projects?workspace_id={workspace_id}`
2. Have a sample CSV file with columns: case_id, activity, timestamp

### Test Flow
1. **Upload File**: `POST /api/v1/datasets/` (multipart form with `file` + `project_id`)
2. **Poll Status**: `GET /api/v1/datasets/{dataset_id}` until status != PENDING
3. **Get Columns**: `GET /api/v1/datasets/{dataset_id}/columns` → See detected columns
4. **Submit Mapping**: `POST /api/v1/datasets/{dataset_id}/mapping` with column mappings
5. **Trigger Ingestion**: `POST /api/v1/datasets/{dataset_id}/ingest`
6. **Poll Until READY**: `GET /api/v1/datasets/{dataset_id}` until status == READY
7. **Query Data**: `GET /api/v1/datasets/{dataset_id}/events`, `/cases`, `/variants`

### Common Errors
- **400**: Dataset not in correct state (check current status)
- **404**: Dataset not found (verify dataset_id UUID)
- **413**: File too large (max 100MB for direct upload)
- **422**: Invalid file type (only .csv and .xes supported)
"""

import json
from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import Dataset
from src.features.process_mining.schemas.datasets import (
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetResponse,
)
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.users.services import require_dataset_permission

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=DatasetListResponse,
    summary="List Datasets",
    description="List all datasets with pagination and filtering.",
)
async def list_datasets(
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_format: str | None = Query(None),
    project_id: str | None = Query(None),
    status: str | None = Query(None, description="Filter by status"),
) -> DatasetListResponse:
    """List datasets with optional filters."""
    logger.info(
        "list_datasets_request",
        user_id=user.id,
        page=page,
        page_size=page_size,
        project_id=project_id,
        source_format=source_format,
        status_filter=status,
    )

    # Build query
    query = select(Dataset)

    if project_id:
        query = query.where(Dataset.project_id == project_id)
    if source_format:
        query = query.where(Dataset.source_format == source_format.upper())
    if status:
        query = query.where(Dataset.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    # Apply pagination
    offset = (page - 1) * page_size
    query = query.order_by(Dataset.created_at.desc()).offset(offset).limit(page_size)

    result = await db.execute(query)
    datasets = result.scalars().all()

    logger.debug(
        "list_datasets_query_executed",
        total_count=total,
        fetched_count=len(datasets),
        offset=offset,
    )

    # Convert to response
    items = []
    for ds in datasets:
        activities = []
        if ds.activities_json:
            try:
                activities = json.loads(ds.activities_json)
            except json.JSONDecodeError as e:
                logger.warning(
                    "failed_to_parse_activities_json",
                    dataset_id=ds.id,
                    error=str(e),
                )

        items.append(
            DatasetResponse(
                id=ds.id,
                name=ds.name,
                source_format=ds.source_format,
                total_events=ds.total_events,
                total_cases=ds.total_cases,
                total_activities=ds.total_activities,
                activities=activities,
                created_at=ds.created_at,
                source_file=ds.source_file,
                status=ds.status,
                file_size_bytes=ds.file_size_bytes,
            )
        )

    # Calculate total pages
    pages = (total + page_size - 1) // page_size if total > 0 else 1

    logger.info(
        "list_datasets_success",
        user_id=user.id,
        total=total,
        page=page,
        pages=pages,
        items_returned=len(items),
    )

    return DatasetListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages,
    )


@router.get(
    "/{dataset_id}",
    response_model=DatasetDetailResponse,
    summary="Get Dataset Details",
    description="Get detailed information about a dataset.",
)
async def get_dataset(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
) -> DatasetDetailResponse:
    """Get dataset with full details and metadata."""
    logger.info(
        "get_dataset_request",
        dataset_id=dataset_id,
        user_id=user.id,
    )

    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_READ
    )

    logger.debug(
        "get_dataset_permission_verified",
        dataset_id=dataset_id,
        dataset_name=dataset.name,
        status=dataset.status,
    )

    # Parse JSON fields
    activities = []
    statistics = None

    if dataset.activities_json:
        try:
            activities = json.loads(dataset.activities_json)
        except json.JSONDecodeError as e:
            logger.warning(
                "failed_to_parse_activities_json",
                dataset_id=dataset_id,
                error=str(e),
            )

    if dataset.statistics_json:
        try:
            statistics = json.loads(dataset.statistics_json)
        except json.JSONDecodeError as e:
            logger.warning(
                "failed_to_parse_statistics_json",
                dataset_id=dataset_id,
                error=str(e),
            )

    # Get metadata if available
    metadata = None
    if dataset.metadata_record:
        metadata = {
            "total_events": dataset.metadata_record.total_events,
            "total_cases": dataset.metadata_record.total_cases,
            "total_activities": dataset.metadata_record.total_activities,
            "total_variants": dataset.metadata_record.total_variants,
            "first_event_at": dataset.metadata_record.first_event_at.isoformat() if dataset.metadata_record.first_event_at else None,
            "last_event_at": dataset.metadata_record.last_event_at.isoformat() if dataset.metadata_record.last_event_at else None,
            "avg_case_duration": dataset.metadata_record.avg_case_duration,
        }
        logger.debug(
            "get_dataset_metadata_loaded",
            dataset_id=dataset_id,
            has_metadata=True,
            total_events=metadata.get("total_events"),
            total_cases=metadata.get("total_cases"),
        )

    logger.info(
        "get_dataset_success",
        dataset_id=dataset_id,
        dataset_name=dataset.name,
        status=dataset.status,
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
    )

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        source_format=dataset.source_format,
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        activities=activities,
        created_at=dataset.created_at,
        source_file=dataset.source_file,
        status=dataset.status,
        file_size_bytes=dataset.file_size_bytes,
        statistics=statistics or metadata,
        updated_at=dataset.updated_at,
        error_message=dataset.error_message,
    )


@router.get(
    "/{dataset_id}/sheets",
    summary="Get Dataset Sheets",
    description="Get list of sheets for multi-sheet files (Excel). CSV/XES files return a single sheet.",
)
async def get_dataset_sheets(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
) -> dict[str, Any]:
    """Get list of sheets for dataset (stub for MVP - returns single sheet)."""
    logger.info(
        "get_dataset_sheets_request",
        dataset_id=dataset_id,
        user_id=user.id,
    )

    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_READ
    )

    # For MVP: CSV and XES files are single-sheet
    # Future: Add Excel multi-sheet support
    sheets = [
        {
            "name": dataset.source_file or "Sheet1",
            "index": 0,
            "is_default": True,
        }
    ]

    logger.info(
        "get_dataset_sheets_success",
        dataset_id=dataset_id,
        sheet_count=len(sheets),
    )

    return {
        "sheets": sheets,
        "total": len(sheets),
    }


@router.delete(
    "/{dataset_id}",
    summary="Delete Dataset",
    description="Delete a dataset and all associated data.",
    responses={
        200: {"description": "Dataset deleted"},
        404: {"description": "Dataset not found"},
    },
)
async def delete_dataset(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
) -> dict[str, Any]:
    """Delete dataset and cascade to related records."""
    from src.platform.infrastructure.object_storage import get_storage_client

    logger.info(
        "delete_dataset_request",
        dataset_id=dataset_id,
        user_id=user.id,
    )

    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_DELETE
    )

    dataset_name = dataset.name
    storage_key = dataset.storage_key
    total_events = dataset.total_events
    total_cases = dataset.total_cases

    logger.debug(
        "delete_dataset_permission_verified",
        dataset_id=dataset_id,
        dataset_name=dataset_name,
        storage_key=storage_key,
    )

    # Delete from database (cascades to cases, events, etc.)
    await db.delete(dataset)
    await db.commit()

    logger.debug(
        "delete_dataset_db_deleted",
        dataset_id=dataset_id,
        dataset_name=dataset_name,
    )

    # Delete from S3 if exists
    if storage_key:
        try:
            storage_client = get_storage_client()
            storage_client.delete_file(bucket_type="raw", key=storage_key)
            logger.debug(
                "delete_dataset_s3_deleted",
                dataset_id=dataset_id,
                storage_key=storage_key,
            )
        except Exception as e:
            logger.warning(
                "delete_dataset_s3_failed",
                dataset_id=dataset_id,
                storage_key=storage_key,
                error=str(e),
                error_type=type(e).__name__,
            )

    logger.info(
        "delete_dataset_success",
        dataset_id=dataset_id,
        dataset_name=dataset_name,
        user_id=user.id,
        events_deleted=total_events,
        cases_deleted=total_cases,
    )

    return {"status": "deleted", "dataset_id": dataset_id}
