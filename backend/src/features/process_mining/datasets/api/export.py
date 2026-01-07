"""Export Router - Dataset export endpoints.

Handles exporting datasets to various formats and downloading original files.
"""

from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Query

from src.api.dependencies import CurrentUser, ReadDBSession
from src.features.process_mining.models import DatasetStatus
from src.features.process_mining.schemas.analyses import JobStatusResponse
from src.features.process_mining.schemas.datasets import DownloadResponse
from src.platform.core.exceptions import NotFoundError, ValidationError
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.models import AsyncJob
from src.platform.users.services import require_dataset_permission

logger = get_logger(__name__)

router = APIRouter()


# =============================================================================
# Export Endpoints
# =============================================================================


# =============================================================================
# Export Endpoints
# =============================================================================


@router.post(
    "/{dataset_id}/export",
    response_model=JobStatusResponse,
    summary="Export Dataset",
    description="""
Export dataset to specified format (async job).

Supported formats:
- csv: Standard CSV file
- xes: XES format for process mining tools
- parquet: Columnar format for big data tools

Returns job ID to track export progress.
    """,
    responses={
        202: {"description": "Export job queued"},
        400: {"description": "Invalid format or dataset not ready"},
        404: {"description": "Dataset not found"},
    },
)
async def export_dataset(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
    export_format: str = Query("csv", pattern=r"^(csv|xes|parquet)$"),
) -> JobStatusResponse:
    """Start async export job."""
    from src.platform.core.enums import JobStatus

    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Check dataset is ready for export
    if dataset.status != DatasetStatus.READY.value:
        raise ValidationError(
            f"Dataset must be in READY state for export. Current: {dataset.status}"
        )

    # Create async job
    job = AsyncJob(
        id=str(uuid4()),
        job_type="export_dataset",
        status=JobStatus.PENDING.value,
        entity_type="dataset",
        entity_id=dataset_id,
        user_id=user.id,
        created_at=datetime.utcnow(),
        metadata_json=f'{{"format": "{export_format}"}}',
    )
    db.add(job)
    await db.commit()

    # Note: In production, would queue Celery task here
    logger.info(
        "export_job_created",
        dataset_id=dataset_id,
        job_id=job.id,
        format=export_format,
    )

    return JobStatusResponse(
        id=job.id,
        status=JobStatus.PENDING.value,
        job_type="export_dataset",
        progress=0,
        stage=f"Export to {export_format} queued",
        created_at=job.created_at,
    )


@router.get(
    "/{dataset_id}/download",
    response_model=DownloadResponse,
    summary="Download Original File",
    description="""
Get presigned URL to download the original uploaded file.

Returns a temporary URL that expires after 1 hour.
    """,
    responses={
        200: {"description": "Download URL generated"},
        404: {"description": "Dataset or file not found"},
    },
)
async def download_original_file(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> DownloadResponse:
    """Get download URL for original file."""
    from src.platform.infrastructure.object_storage import get_storage_client

    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Check storage key exists
    if not dataset.storage_key:
        raise NotFoundError("File", dataset_id)

    # Generate presigned download URL
    try:
        storage_client = get_storage_client()
        download_url = storage_client.generate_presigned_url(
            bucket_type="raw",
            key=dataset.storage_key,
            expires_in=3600,
            method="GET",
        )
    except Exception as e:
        logger.error("download_url_generation_failed", dataset_id=dataset_id, error=str(e))
        raise ValidationError("Failed to generate download URL")

    # Determine filename
    filename = dataset.source_file or f"dataset_{dataset_id}.csv"

    logger.info("download_url_generated", dataset_id=dataset_id, user_id=user.id)

    return DownloadResponse(
        download_url=download_url,
        filename=filename,
        expires_in=3600,
    )
