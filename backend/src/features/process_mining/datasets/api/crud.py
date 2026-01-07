"""CRUD Router - List, Get, Delete dataset endpoints.

Dataset lifecycle management for process mining event logs.

## CQRS Pattern
- GET endpoints use ReadDBSession (read-optimized connection pool)
- DELETE endpoint uses WriteDBSession (write-optimized connection pool)
- DELETE emits domain events for cache invalidation

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

from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.api.dependencies import CurrentUser, ReadDBSession, WriteDBSession
from src.features.process_mining.models import Dataset
from src.features.process_mining.schemas.datasets import (
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetResponse,
)
from src.infra.core.logging_config import get_logger
from src.infra.core.permissions import Permission
from src.infra.infrastructure.cache import invalidate_dataset_cache
from src.infra.users.services import require_dataset_permission
from src.shared.events import DATASET_DELETED, log_dataset_event

logger = get_logger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=DatasetListResponse,
    summary="List Datasets",
    description="List all datasets with pagination and filtering.",
)
async def list_datasets(
    db: ReadDBSession,  # CQRS: Read-optimized pool for GET
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

    # Build query with eager loading of metadata_record
    query = select(Dataset).options(selectinload(Dataset.metadata_record))

    if project_id:
        query = query.where(Dataset.project_id == project_id)
    if source_format:
        query = query.where(Dataset.source_format == source_format.upper())
    if status:
        query = query.where(Dataset.status == status)

    # Get total count (without eager loading for performance)
    count_subquery = select(Dataset.id)
    if project_id:
        count_subquery = count_subquery.where(Dataset.project_id == project_id)
    if source_format:
        count_subquery = count_subquery.where(Dataset.source_format == source_format.upper())
    if status:
        count_subquery = count_subquery.where(Dataset.status == status)
    count_query = select(func.count()).select_from(count_subquery.subquery())
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

    # Convert to response - use DatasetMetadata for statistics
    items = []
    for ds in datasets:
        # Get statistics from DatasetMetadata (single source of truth)
        # Fall back to deprecated Dataset fields for backward compatibility
        metadata = ds.metadata_record
        if metadata:
            total_events = metadata.total_events
            total_cases = metadata.total_cases
            total_activities = metadata.total_activities
        else:
            # Fallback to deprecated fields for older datasets
            total_events = ds.total_events or 0
            total_cases = ds.total_cases or 0
            total_activities = ds.total_activities or 0

        # Activities list is deprecated on Dataset - skip for list view
        activities: list[str] = []

        items.append(
            DatasetResponse(
                id=ds.id,
                name=ds.name,
                source_format=ds.source_format,
                total_events=total_events,
                total_cases=total_cases,
                total_activities=total_activities,
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
    db: ReadDBSession,  # CQRS: Read-optimized pool for GET
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
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    logger.debug(
        "get_dataset_permission_verified",
        dataset_id=dataset_id,
        dataset_name=dataset.name,
        status=dataset.status,
    )

    # Get statistics from DatasetMetadata (single source of truth)
    metadata = dataset.metadata_record
    if metadata:
        total_events = metadata.total_events
        total_cases = metadata.total_cases
        total_activities = metadata.total_activities
        statistics = {
            "total_events": metadata.total_events,
            "total_cases": metadata.total_cases,
            "total_activities": metadata.total_activities,
            "total_variants": metadata.total_variants,
            "first_event_at": metadata.first_event_at.isoformat()
            if metadata.first_event_at
            else None,
            "last_event_at": metadata.last_event_at.isoformat()
            if metadata.last_event_at
            else None,
            "avg_case_duration": metadata.avg_case_duration,
            "min_case_duration": metadata.min_case_duration,
            "max_case_duration": metadata.max_case_duration,
            "total_resources": metadata.total_resources,
            "computed_at": metadata.computed_at.isoformat() if metadata.computed_at else None,
        }
        logger.debug(
            "get_dataset_metadata_loaded",
            dataset_id=dataset_id,
            has_metadata=True,
            total_events=total_events,
            total_cases=total_cases,
        )
    else:
        # Fallback to deprecated Dataset fields for older datasets
        total_events = dataset.total_events or 0
        total_cases = dataset.total_cases or 0
        total_activities = dataset.total_activities or 0
        statistics = None

    # Activities list - skip deprecated field, empty for now
    activities: list[str] = []

    logger.info(
        "get_dataset_success",
        dataset_id=dataset_id,
        dataset_name=dataset.name,
        status=dataset.status,
        total_events=total_events,
        total_cases=total_cases,
    )

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        source_format=dataset.source_format,
        total_events=total_events,
        total_cases=total_cases,
        total_activities=total_activities,
        activities=activities,
        created_at=dataset.created_at,
        source_file=dataset.source_file,
        status=dataset.status,
        file_size_bytes=dataset.file_size_bytes,
        statistics=statistics,
        updated_at=dataset.updated_at,
        error_message=dataset.error_message,
    )


@router.get(
    "/{dataset_id}/sheets",
    summary="Get Dataset Sheets",
    description="Get list of sheets for multi-sheet files (Excel). CSV/XES files return a single sheet.",
)
async def get_dataset_sheets(
    db: ReadDBSession,  # CQRS: Read-optimized pool for GET
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
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

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


@router.get(
    "/{dataset_id}/preview",
    summary="Get Raw Data Preview",
    description="""
Get a preview of the raw data from the uploaded file.

Returns column information with detected types and sample row data.
Used by the upload wizard's Configure step before mapping is applied.
    """,
    responses={
        200: {"description": "Preview data with columns and sample rows"},
        404: {"description": "Dataset not found or file not accessible"},
    },
)
async def get_dataset_preview(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
    rows: int = Query(10, ge=1, le=100, description="Number of sample rows to return"),
) -> dict[str, Any]:
    """Get raw data preview for upload wizard Configure step."""
    import csv
    import io

    from starlette.concurrency import run_in_threadpool

    from src.infra.infrastructure.object_storage import get_storage_client

    logger.info(
        "get_dataset_preview_request",
        dataset_id=dataset_id,
        user_id=user.id,
        rows=rows,
    )

    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    if not dataset.storage_key:
        from src.infra.core.exceptions import NotFoundError

        raise NotFoundError("Dataset file", dataset_id)

    # Read file from storage
    try:
        storage_client = get_storage_client()
        file_obj = await run_in_threadpool(
            storage_client.download_fileobj, bucket_type="raw", key=dataset.storage_key
        )
        content = file_obj.read()
    except Exception as e:
        logger.error(
            "get_dataset_preview_storage_error",
            dataset_id=dataset_id,
            storage_key=dataset.storage_key,
            error=str(e),
        )
        from src.infra.core.exceptions import NotFoundError

        raise NotFoundError("Dataset file", dataset_id)

    # Parse CSV to extract preview
    text_content = content.decode("utf-8")
    reader = csv.DictReader(io.StringIO(text_content))

    # Get column info
    columns = []
    fieldnames = reader.fieldnames or []

    # Read sample rows
    sample_rows = []
    for i, row in enumerate(reader):
        if i < rows:
            sample_rows.append(row)
        if i >= rows:
            break

    # Count total rows (rough estimate from remaining content)
    total_rows = len(sample_rows)
    for _ in reader:
        total_rows += 1

    # Detect column types from sample values
    for col_name in fieldnames:
        sample_values = [row.get(col_name) for row in sample_rows if row.get(col_name)]
        null_count = sum(1 for row in sample_rows if not row.get(col_name))

        # Simple type detection
        detected_type = "STRING"
        date_format = None

        if sample_values:
            # Check if numeric
            try:
                [float(str(v).replace(",", "")) for v in sample_values[:5] if v]
                # Check if integer
                if all(float(str(v).replace(",", "")).is_integer() for v in sample_values[:5] if v):
                    detected_type = "INTEGER"
                else:
                    detected_type = "DECIMAL"
            except (ValueError, AttributeError):
                pass

            # Check if datetime
            if detected_type == "STRING":
                import re

                date_patterns = [
                    (r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}", "yyyy-MM-dd HH:mm:ss"),
                    (r"^\d{4}-\d{2}-\d{2}$", "yyyy-MM-dd"),
                    (r"^\d{2}/\d{2}/\d{4}", "MM/dd/yyyy"),
                    (r"^\d{2}\.\d{2}\.\d{4}", "dd.MM.yyyy"),
                ]
                for pattern, fmt in date_patterns:
                    if any(re.match(pattern, str(v)) for v in sample_values[:5] if v):
                        detected_type = "DATETIME"
                        date_format = fmt
                        break

        columns.append({
            "name": col_name,
            "detected_type": detected_type,
            "sample_values": sample_values[:5],
            "null_count": null_count,
            "date_format": date_format,
        })

    logger.info(
        "get_dataset_preview_success",
        dataset_id=dataset_id,
        column_count=len(columns),
        row_count=len(sample_rows),
        total_rows=total_rows,
    )

    return {
        "dataset_id": dataset_id,
        "filename": dataset.source_file or dataset.name,
        "columns": columns,
        "rows": sample_rows,
        "total_rows": total_rows,
        "has_header": True,
        "field_separator": ",",
        "encoding": "utf-8",
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
    db: WriteDBSession,  # CQRS: Write-optimized pool for DELETE
    dataset_id: str,
    user: CurrentUser,
) -> dict[str, Any]:
    """Delete dataset and cascade to related records.

    CQRS: Uses WriteDBSession for transactional delete.
    Emits DATASET_DELETED event for cache invalidation.
    """
    from src.infra.infrastructure.object_storage import get_storage_client

    logger.info(
        "delete_dataset_request",
        dataset_id=dataset_id,
        user_id=user.id,
    )

    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_DELETE)

    dataset_name = dataset.name
    storage_key = dataset.storage_key
    # Get stats from metadata if available, otherwise fallback to deprecated fields
    metadata = dataset.metadata_record
    total_events = metadata.total_events if metadata else (dataset.total_events or 0)
    total_cases = metadata.total_cases if metadata else (dataset.total_cases or 0)

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

    # CQRS: Emit domain event for read model sync
    await log_dataset_event(
        session=db,
        dataset_id=dataset_id,
        event_type=DATASET_DELETED,
        payload={
            "dataset_name": dataset_name,
            "storage_key": storage_key,
            "events_deleted": total_events,
            "cases_deleted": total_cases,
        },
        user_id=user.id,
    )

    # CQRS: Invalidate analytics caches
    invalidate_dataset_cache(dataset_id)

    logger.info(
        "delete_dataset_success",
        dataset_id=dataset_id,
        dataset_name=dataset_name,
        user_id=user.id,
        events_deleted=total_events,
        cases_deleted=total_cases,
    )

    return {"status": "deleted", "dataset_id": dataset_id}
