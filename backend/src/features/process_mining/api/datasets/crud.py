"""CRUD Router - List, Get, Delete dataset endpoints.

Basic CRUD operations for datasets.
"""

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import Dataset, DatasetMetadata, DatasetStatus
from src.features.process_mining.schemas import (
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetResponse,
)
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.workspaces.authorization import require_dataset_permission

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

    # Convert to response
    items = []
    for ds in datasets:
        activities = []
        if ds.activities_json:
            try:
                import json
                activities = json.loads(ds.activities_json)
            except Exception:
                pass

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

    return DatasetListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
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
    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_READ
    )

    # Parse JSON fields
    activities = []
    statistics = None

    if dataset.activities_json:
        try:
            import json
            activities = json.loads(dataset.activities_json)
        except Exception:
            pass

    if dataset.statistics_json:
        try:
            import json
            statistics = json.loads(dataset.statistics_json)
        except Exception:
            pass

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
) -> dict:
    """Delete dataset and cascade to related records."""
    from src.platform.infrastructure.object_storage import get_storage_client

    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_DELETE
    )

    storage_key = dataset.storage_key

    # Delete from database (cascades to cases, events, etc.)
    await db.delete(dataset)
    await db.commit()

    # Delete from S3 if exists
    if storage_key:
        try:
            storage_client = get_storage_client()
            storage_client.delete_file(bucket_type="raw", key=storage_key)
        except Exception as e:
            logger.warning("failed_to_delete_s3_file", key=storage_key, error=str(e))

    logger.info("dataset_deleted", dataset_id=dataset_id, user_id=user.id)

    return {"status": "deleted", "dataset_id": dataset_id}
