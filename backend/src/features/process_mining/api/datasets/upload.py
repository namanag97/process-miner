"""Upload Router - File upload endpoints.

Handles both direct upload and presigned S3 upload flows.
Part of 4-Phase Upload Architecture: Upload → Validate → Map → Ingest
"""

import os
import tempfile
from datetime import datetime
from uuid import uuid4

import aiofiles
from fastapi import APIRouter, File, Form, Request, Response, UploadFile

from src.api.dependencies import CurrentUser, ReadDBSession
from src.features.process_mining.models import Dataset, DatasetStatus, UploadedFile
from src.features.process_mining.schemas import (
    DatasetResponse,
    PresignedUploadRequest,
    PresignedUploadResponse,
)
from src.infra.core.config import get_settings
from src.infra.core.exceptions import InvalidFileError, ProcessingError, ValidationError
from src.infra.core.logging_config import get_logger
from src.infra.core.rate_limit import limiter

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter()

# =============================================================================
# Constants
# =============================================================================

MAX_FILE_SIZE_MB = 100  # Maximum file upload size
CHUNK_SIZE = 64 * 1024  # 64KB chunks for streaming
ALLOWED_EXTENSIONS = {".csv", ".xes"}
ALLOWED_MIMETYPES = {
    "text/csv",
    "application/csv",
    "application/xml",
    "text/xml",
    "application/octet-stream",
    "text/plain",
}


# =============================================================================
# Validation Helpers
# =============================================================================


def validate_file_extension(filename: str) -> None:
    """Validate file extension.

    Args:
        filename: The filename to validate

    Raises:
        InvalidFileError: If file extension is invalid
    """
    if not filename:
        raise InvalidFileError("No filename provided")

    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(
            "upload_rejected_extension",
            filename=filename,
            extension=ext,
            allowed=list(ALLOWED_EXTENSIONS),
        )
        raise InvalidFileError(
            f"File type '{ext}' is not supported. Please upload a CSV or XES file.",
            filename=filename,
            expected_types=list(ALLOWED_EXTENSIONS),
        )


def validate_file_upload(file: UploadFile) -> None:
    """Validate file extension and content type.

    Args:
        file: The uploaded file to validate

    Raises:
        InvalidFileError: If validation fails
    """
    validate_file_extension(file.filename or "")

    if file.content_type and file.content_type not in ALLOWED_MIMETYPES:
        logger.warning(
            "upload_rejected_mimetype",
            filename=file.filename,
            content_type=file.content_type,
        )
        raise InvalidFileError(
            f"Invalid content type: {file.content_type}. Expected CSV or XML.",
            filename=file.filename,
        )


async def validate_file_signature(content: bytes, filename: str) -> None:
    """Validate file content signature to prevent spoofing.

    Args:
        content: First bytes of the file
        filename: The filename with extension

    Raises:
        InvalidFileError: If signature doesn't match extension
    """
    ext = os.path.splitext(filename)[1].lower()
    signature = content[:512]

    if ext == ".xes":
        if not signature.startswith((b"<?xml", b"<log")):
            logger.warning("file_signature_mismatch", filename=filename, extension=ext)
            raise InvalidFileError(
                "File appears to be invalid XES format (not valid XML)",
                filename=filename,
            )
    elif ext == ".csv":
        try:
            signature.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning("file_signature_mismatch", filename=filename, extension=ext)
            raise InvalidFileError(
                "File appears to be invalid CSV format (contains binary data)",
                filename=filename,
            )


# =============================================================================
# Presigned Upload Flow
# =============================================================================


@router.post(
    "/presign",
    response_model=PresignedUploadResponse,
    summary="Get Presigned S3 Upload URL",
    description="""
Generate a presigned URL for direct S3 upload.

## Flow
1. Call this endpoint to get `upload_url`
2. PUT the file to `upload_url`
3. Call `POST /datasets/{id}/uploaded` to trigger validation
    """,
    responses={
        200: {"description": "Presigned URL generated successfully"},
        429: {"description": "Rate limit exceeded (10/min)"},
        422: {"description": "Validation error (invalid extension)"},
    },
)
@limiter.limit("10/minute")
async def create_presigned_upload(
    request: Request,
    response: Response,
    body: PresignedUploadRequest,
    db: ReadDBSession,
    current_user: CurrentUser,
) -> PresignedUploadResponse:
    """Generate presigned URL for direct client-to-S3 upload.

    Creates a dataset record and returns a presigned S3 URL for direct upload.
    After uploading, call POST /datasets/{id}/uploaded to trigger validation.
    """
    from src.infra.core.permissions import Permission
    from src.infra.infrastructure.object_storage import get_storage_client
    from src.infra.workspaces.authorization import require_project_permission

    logger.info(
        "presigned_upload_request",
        filename=body.filename,
        file_size_bytes=body.file_size_bytes,
        project_id=body.project_id,
        user_id=current_user.id,
    )

    # Validate file extension
    validate_file_extension(body.filename)

    # Validate file size
    if body.file_size_bytes and body.file_size_bytes > settings.s3_max_file_size_bytes:
        raise ValidationError(
            f"File size ({body.file_size_bytes} bytes) exceeds maximum "
            f"({settings.s3_max_file_size_bytes} bytes)"
        )

    # Validate project permission
    if not body.project_id:
        raise ValidationError("project_id is required for dataset upload")

    await require_project_permission(db, body.project_id, current_user, Permission.DATASET_CREATE)

    # Generate storage key
    dataset_id = str(uuid4())
    file_extension = os.path.splitext(body.filename)[1]
    file_uuid = str(uuid4())
    storage_key = f"{dataset_id}/{file_uuid}{file_extension}"

    # Generate presigned URL
    storage_client = get_storage_client()
    try:
        upload_url = storage_client.get_presigned_upload_url(
            bucket_type="raw",
            key=storage_key,
            content_type=body.content_type,
        )
    except Exception as e:
        logger.error("presigned_url_generation_failed", error=str(e))
        raise ProcessingError(f"Failed to generate upload URL: {e}")

    # Create dataset record
    dataset = Dataset(
        id=dataset_id,
        name=os.path.splitext(body.filename)[0],
        project_id=body.project_id,
        source_format=file_extension.lstrip(".").upper(),
        status=DatasetStatus.PENDING.value,
        file_size_bytes=body.file_size_bytes,
        source_file=body.filename,
        storage_key=storage_key,
        created_at=datetime.utcnow(),
    )

    db.add(dataset)
    await db.commit()

    logger.info(
        "presigned_upload_created",
        dataset_id=dataset_id,
        storage_key=storage_key,
    )

    return PresignedUploadResponse(
        upload_url=upload_url,
        storage_key=storage_key,
        dataset_id=dataset_id,
        expires_in=settings.s3_presigned_url_expiry,
    )


@router.post(
    "/{dataset_id}/uploaded",
    summary="Confirm Upload Complete",
    description="""
Confirm that S3 upload is complete and trigger validation.

Call this after successfully uploading to the presigned URL.
    """,
    responses={
        200: {"description": "Validation queued"},
        400: {"description": "Dataset not in PENDING state"},
        404: {"description": "Dataset not found"},
    },
)
async def confirm_upload_complete(
    dataset_id: str,
    db: ReadDBSession,
    current_user: CurrentUser,
) -> dict:
    """Trigger validation after S3 upload complete."""

    from src.infra.core.permissions import Permission
    from src.infra.workspaces.authorization import require_dataset_permission

    # Verify permission and get dataset
    _, dataset = await require_dataset_permission(
        db, dataset_id, current_user, Permission.DATASET_UPDATE
    )

    if dataset.status != DatasetStatus.PENDING.value:
        raise ValidationError(f"Dataset must be in PENDING state. Current: {dataset.status}")

    if not dataset.storage_key:
        raise ValidationError("Dataset missing storage_key. Cannot validate.")

    # Update status to UPLOADED
    dataset.status = DatasetStatus.UPLOADED.value
    await db.commit()

    # Queue validation workflow via Temporal v2
    from temporalio.common import WorkflowIDReusePolicy

    from src.infra.temporal.client import get_temporal_client
    from src.infra.temporal.config import get_temporal_config
    from src.infra.temporal.workflows_v2.ingestion import DatasetValidationWorkflowV2

    config = get_temporal_config()
    workflow_id = f"validate-dataset-{dataset_id}"

    try:
        client = await get_temporal_client()
        await client.start_workflow(
            DatasetValidationWorkflowV2.run,
            args=[dataset_id, dataset.storage_key],
            id=workflow_id,
            task_queue=config.QUEUE_INGESTION,
            id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
        )
    except Exception as e:
        logger.error("validation_workflow_start_failed", error=str(e), dataset_id=dataset_id)
        # Fall back to manual validation

    logger.info(
        "upload_confirmed_validation_queued",
        dataset_id=dataset_id,
        workflow_id=workflow_id,
    )

    return {
        "status": "validation_queued",
        "dataset_id": dataset_id,
        "workflow_id": workflow_id,
        "poll_endpoint": f"/api/v1/operations/{workflow_id}",
    }


# =============================================================================
# Direct Upload Flow
# =============================================================================


@router.post(
    "/",
    response_model=DatasetResponse,
    summary="Upload Event Log File",
    description="""
Upload and store an event log file (CSV or XES).

For small files (< 50MB), use this direct upload.
For large files (> 50MB), use the presigned upload flow.

## Flow
1. File is validated and stored
2. Validation job is queued automatically
3. Poll `GET /datasets/{id}` for status updates
    """,
    responses={
        200: {"description": "Dataset created and validation queued"},
        400: {"description": "Invalid file format"},
        413: {"description": "File too large (> 100MB)"},
        422: {"description": "Validation error"},
    },
)
async def upload_dataset(
    db: ReadDBSession,
    user: CurrentUser,
    file: UploadFile = File(...),
    name: str | None = Form(None),
    project_id: str | None = Form(None, description="Project ID to assign dataset to"),
) -> DatasetResponse:
    """Upload and store an event log file.

    Validates, stores, and queues the file for processing.
    Use presigned upload for files larger than 50MB.
    """
    from src.infra.core.permissions import Permission
    from src.infra.infrastructure.object_storage import get_storage_client
    from src.infra.workspaces.authorization import require_project_permission

    # Validate file type
    validate_file_upload(file)
    filename = file.filename
    if not filename:
        raise InvalidFileError("Filename is required")

    logger.info(
        "direct_upload_started",
        filename=filename,
        project_id=project_id,
        user_id=user.id,
    )

    # Validate project permission
    if not project_id:
        raise ValidationError("project_id is required for dataset upload")

    await require_project_permission(db, project_id, user, Permission.DATASET_CREATE)

    # Stream file to temp location
    temp_file_path = None
    try:
        suffix = os.path.splitext(filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            temp_file_path = tmp.name

        total_size = 0
        async with aiofiles.open(temp_file_path, "wb") as out_file:
            while chunk := await file.read(CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise InvalidFileError(
                        f"File too large. Maximum: {MAX_FILE_SIZE_MB}MB",
                        filename=filename,
                    )
                await out_file.write(chunk)

        # Read content for validation
        async with aiofiles.open(temp_file_path, "rb") as f:
            content = await f.read()

        # Validate file signature
        await validate_file_signature(content, filename)

        # Upload to S3
        dataset_id = str(uuid4())
        file_extension = os.path.splitext(filename)[1]
        storage_key = f"{dataset_id}/{uuid4()}{file_extension}"

        storage_client = get_storage_client()
        import io

        storage_client.upload_fileobj(
            bucket_type="raw",
            key=storage_key,
            file_obj=io.BytesIO(content),
            content_type=file.content_type,
        )

        # Create dataset record
        dataset_name = name or os.path.splitext(filename)[0]
        dataset = Dataset(
            id=dataset_id,
            name=dataset_name,
            project_id=project_id,
            source_format=file_extension.lstrip(".").upper(),
            status=DatasetStatus.UPLOADED.value,
            file_size_bytes=total_size,
            source_file=filename,
            storage_key=storage_key,
            created_at=datetime.utcnow(),
        )

        db.add(dataset)

        # Create UploadedFile record (required for ingestion)
        uploaded_file_record = UploadedFile(
            dataset_id=dataset_id,
            filename=filename,
            storage_path=storage_key,
            size_bytes=total_size,
            mime_type=file.content_type,
            checksum=None,
        )
        db.add(uploaded_file_record)

        await db.commit()

        # Queue validation workflow via Temporal v2 (with inline fallback)
        from temporalio.common import WorkflowIDReusePolicy

        from src.infra.temporal.client import get_temporal_client
        from src.infra.temporal.config import get_temporal_config
        from src.infra.temporal.workflows_v2.ingestion import DatasetValidationWorkflowV2

        config = get_temporal_config()
        workflow_id = f"validate-dataset-{dataset_id}"

        temporal_available = False
        try:
            client = await get_temporal_client()
            await client.start_workflow(
                DatasetValidationWorkflowV2.run,
                args=[dataset_id, storage_key],
                id=workflow_id,
                task_queue=config.QUEUE_INGESTION,
                id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
            )
            temporal_available = True
        except Exception as e:
            logger.warning("validation_workflow_start_failed", error=str(e))

        # Fallback: Inline column detection when Temporal is unavailable
        if not temporal_available:
            try:
                from starlette.concurrency import run_in_threadpool

                from src.features.process_mining.ingestion.unified import (
                    unified_ingestion_service,
                )
                from src.features.process_mining.models import DatasetColumn

                logger.info("inline_column_detection_start", dataset_id=dataset_id)

                # Detect columns synchronously
                detection = await run_in_threadpool(
                    unified_ingestion_service.detect_columns, content, filename
                )

                # Save columns to database
                columns = detection.get("columns", [])
                suggestions = detection.get("suggestions", {})

                for idx, col_info in enumerate(columns):
                    col_name = (
                        col_info.get("name") if isinstance(col_info, dict) else col_info
                    )
                    col = DatasetColumn(
                        dataset_id=dataset_id,
                        name=col_name,
                        dtype=col_info.get("dtype", "string")
                        if isinstance(col_info, dict)
                        else "string",
                        position=idx,
                        sample_values_json="[]",
                        null_percentage=0.0,
                        unique_count=0,
                        suggested_role=None,
                        suggestion_confidence=0.0,
                    )

                    # Check if this column is suggested for a role
                    for role, suggestion in suggestions.items():
                        if isinstance(suggestion, dict):
                            if suggestion.get("column") == col_name:
                                col.suggested_role = role.replace("_column", "")
                                col.suggestion_confidence = suggestion.get(
                                    "confidence", 0.8
                                )
                        elif suggestion == col_name:
                            col.suggested_role = role.replace("_column", "")
                            col.suggestion_confidence = 0.8

                    db.add(col)

                # Update dataset status to AWAITING_MAPPING
                dataset.status = DatasetStatus.AWAITING_MAPPING.value
                await db.commit()

                logger.info(
                    "inline_column_detection_complete",
                    dataset_id=dataset_id,
                    columns_found=len(columns),
                )
            except Exception as fallback_err:
                logger.error(
                    "inline_column_detection_failed",
                    dataset_id=dataset_id,
                    error=str(fallback_err),
                )

        logger.info(
            "direct_upload_complete",
            dataset_id=dataset_id,
            storage_key=storage_key,
            workflow_id=workflow_id,
        )

        return DatasetResponse(
            id=dataset.id,
            name=dataset.name,
            source_format=dataset.source_format,
            total_events=0,
            total_cases=0,
            total_activities=0,
            activities=[],
            created_at=dataset.created_at,
            source_file=dataset.source_file,
            status=dataset.status,
            file_size_bytes=total_size,
        )

    except InvalidFileError:
        raise
    except ValidationError:
        raise
    except Exception as e:
        logger.exception("direct_upload_failed_exception", error=str(e))
        raise ProcessingError(f"Upload failed: {e!s}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass


@router.post(
    "/{dataset_id}/validate",
    summary="Trigger Column Detection",
    description="""
Manually trigger column detection for an existing dataset.

Use this when:
- Columns were not detected during upload (e.g., Temporal unavailable)
- You want to re-detect columns with updated settings

Works on datasets in UPLOADED or AWAITING_MAPPING status.
    """,
    responses={
        200: {"description": "Column detection completed"},
        400: {"description": "Dataset not in valid state"},
        404: {"description": "Dataset not found"},
    },
)
async def validate_dataset(
    dataset_id: str,
    db: ReadDBSession,
    current_user: CurrentUser,
) -> dict:
    """Manually trigger column detection for an existing dataset."""
    from sqlalchemy import delete
    from starlette.concurrency import run_in_threadpool

    from src.features.process_mining.ingestion.unified import unified_ingestion_service
    from src.features.process_mining.models import DatasetColumn
    from src.infra.core.permissions import Permission
    from src.infra.infrastructure.object_storage import get_storage_client
    from src.infra.workspaces.authorization import require_dataset_permission

    # Verify permission and get dataset
    _, dataset = await require_dataset_permission(
        db, dataset_id, current_user, Permission.DATASET_UPDATE
    )

    valid_statuses = [
        DatasetStatus.UPLOADED.value,
        DatasetStatus.AWAITING_MAPPING.value,
        DatasetStatus.ERROR.value,
    ]
    if dataset.status not in valid_statuses:
        raise ValidationError(
            f"Dataset must be in UPLOADED, AWAITING_MAPPING, or ERROR state. Current: {dataset.status}"
        )

    if not dataset.storage_key:
        raise ValidationError("Dataset missing storage_key. Cannot validate.")

    logger.info("manual_validate_start", dataset_id=dataset_id)

    # Download file from storage
    storage_client = get_storage_client()
    try:
        content = await run_in_threadpool(
            storage_client.download_file, bucket_type="raw", key=dataset.storage_key
        )
    except Exception as e:
        logger.error("validate_download_failed", dataset_id=dataset_id, error=str(e))
        raise ProcessingError(f"Failed to download file: {e}")

    # Detect columns
    filename = dataset.source_file or "file.csv"
    detection = await run_in_threadpool(
        unified_ingestion_service.detect_columns, content, filename
    )

    columns = detection.get("columns", [])
    suggestions = detection.get("suggestions", {})

    # Clear existing columns
    await db.execute(delete(DatasetColumn).where(DatasetColumn.dataset_id == dataset_id))

    # Save columns to database
    for idx, col_info in enumerate(columns):
        col_name = col_info.get("name") if isinstance(col_info, dict) else col_info
        col = DatasetColumn(
            dataset_id=dataset_id,
            name=col_name,
            dtype=col_info.get("dtype", "string") if isinstance(col_info, dict) else "string",
            position=idx,
            sample_values_json="[]",
            null_percentage=0.0,
            unique_count=0,
            suggested_role=None,
            suggestion_confidence=0.0,
        )

        # Check if this column is suggested for a role
        for role, suggestion in suggestions.items():
            if isinstance(suggestion, dict):
                if suggestion.get("column") == col_name:
                    col.suggested_role = role.replace("_column", "")
                    col.suggestion_confidence = suggestion.get("confidence", 0.8)
            elif suggestion == col_name:
                col.suggested_role = role.replace("_column", "")
                col.suggestion_confidence = 0.8

        db.add(col)

    # Update dataset status
    dataset.status = DatasetStatus.AWAITING_MAPPING.value
    dataset.error_message = None
    await db.commit()

    logger.info(
        "manual_validate_complete",
        dataset_id=dataset_id,
        columns_found=len(columns),
    )

    return {
        "status": "validation_complete",
        "dataset_id": dataset_id,
        "columns_detected": len(columns),
        "suggestions": suggestions,
        "next_step": "Submit column mapping via POST /datasets/{id}/mapping",
    }
