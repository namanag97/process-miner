"""Datasets Router.

Endpoints for uploading, listing, and managing datasets.

BUG-058 FIX: Added chunked file streaming to prevent OOM on large uploads.
"""

import json
import os
import tempfile
import time

import aiofiles
from fastapi import APIRouter, File, Form, HTTPException, Query, Request, Response, UploadFile
from sqlalchemy import func, select

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import Dataset, DatasetStatus, ProcessCase
from src.features.process_mining.schemas import (
    ActivityDetailResponse,
    CaseListResponse,
    CaseResponse,
    ColumnDetectionResponse,
    ColumnTypeInfo,
    DataPreviewResponse,
    DatasetDetailResponse,
    DatasetListResponse,
    DatasetResponse,
    IngestRequest,
    JobStatusResponse,
    PresignedUploadRequest,
    PresignedUploadResponse,
    SheetInfo,
    SheetsResponse,
    StatisticsResponse,
    VariantResponse,
)
from src.features.process_mining.services.ingestion import ingestion_service
from src.features.process_mining.services.ingestion.duckdb import duckdb_ingestion_service
from src.features.process_mining.services.ingestion.unified import unified_ingestion_service
from src.features.process_mining.services.mining import mining_service

# Repository imports from models layer (infrastructure)
from src.platform.infrastructure.repositories import SQLAlchemyDatasetRepository
from src.platform.core.config import get_settings
from src.platform.core.exceptions import (
    InvalidFileError,
    ProcessingError,
    ProcessNotFoundError,
    ValidationError,
)
from src.platform.core.logging_config import get_logger
from src.platform.core.rate_limit import limiter
from src.platform.devconsole import log_error, log_info
from src.platform.models import Project

logger = get_logger(__name__)
settings = get_settings()

# =============================================================================
# Constants
# =============================================================================

MAX_FILE_SIZE_MB = 100  # Maximum file upload size
MIN_EVENTS_FOR_ANALYSIS = 1  # Minimum events required for analysis
MIN_CASES_FOR_VARIANTS = 1  # Minimum cases required for variant analysis
CHUNK_SIZE = 64 * 1024  # 64KB chunks for streaming

router = APIRouter(prefix="/datasets", tags=["Datasets"])


# =============================================================================
# File Validation Helpers
# =============================================================================


def validate_file_upload(file: UploadFile) -> None:
    """Validate file extension and content type for security.

    Args:
        file: The uploaded file to validate

    Raises:
        InvalidFileError: If file validation fails
    """
    if not file.filename:
        raise InvalidFileError("No filename provided")

    # Validate file extension
    allowed_extensions = {".csv", ".xes"}
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed_extensions:
        logger.warning("upload_rejected_extension", filename=file.filename, extension=ext)
        raise InvalidFileError(
            f"Invalid file type '{ext}'. Allowed extensions: {', '.join(allowed_extensions)}",
            filename=file.filename,
            expected_types=list(allowed_extensions),
        )

    # Validate content type (allow common browser defaults)
    allowed_mimetypes = {
        "text/csv",
        "application/csv",
        "application/xml",
        "text/xml",
        "application/octet-stream",
        "text/plain",  # Common browser defaults
    }
    if file.content_type and file.content_type not in allowed_mimetypes:
        logger.warning(
            "upload_rejected_mimetype",
            filename=file.filename,
            content_type=file.content_type,
        )
        raise InvalidFileError(
            f"Invalid content type: {file.content_type}. Expected CSV or XML.",
            filename=file.filename,
        )


def validate_file_size(content: bytes, filename: str) -> None:
    """Validate file size is within limits.

    Args:
        content: File content as bytes
        filename: Original filename

    Raises:
        InvalidFileError: If file is too large
    """
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        logger.warning(
            "upload_rejected_size",
            filename=filename,
            size_mb=round(file_size_mb, 2),
            max_size_mb=MAX_FILE_SIZE_MB,
        )
        raise InvalidFileError(
            f"File too large ({file_size_mb:.1f}MB). Maximum size: {MAX_FILE_SIZE_MB}MB",
            filename=filename,
        )


async def validate_file_signature(content: bytes, filename: str) -> None:
    """Validate file content signature to prevent file type spoofing.

    Args:
        content: First bytes of the file
        filename: The filename with extension

    Raises:
        InvalidFileError: If file signature doesn't match extension
    """
    ext = os.path.splitext(filename)[1].lower()

    # Read first 512 bytes for signature check
    signature = content[:512]

    if ext == ".xes":
        # XES files should start with XML declaration
        if not (signature.startswith((b"<?xml", b"<log"))):
            logger.warning("file_signature_mismatch", filename=filename, extension=ext)
            raise InvalidFileError(
                "File appears to be invalid XES format (not valid XML)",
                filename=filename,
            )
    elif ext == ".csv":
        # CSV should be readable ASCII/UTF-8 text, check for binary content
        try:
            signature.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning("file_signature_mismatch", filename=filename, extension=ext)
            raise InvalidFileError(
                "File appears to be invalid CSV format (contains binary data)",
                filename=filename,
            )


# =============================================================================
# Upload & Ingest
# =============================================================================


async def _stream_upload_to_temp(file: UploadFile) -> tuple[str, int]:
    """BUG-058 FIX: Stream uploaded file to temp file in chunks to prevent OOM.

    Args:
        file: The uploaded file

    Returns:
        Tuple of (temp_file_path, total_bytes)
    """
    total_bytes = 0
    # Create temp file with same extension
    suffix = os.path.splitext(file.filename or "")[1]
    fd, temp_path = tempfile.mkstemp(suffix=suffix)
    os.close(fd)

    try:
        async with aiofiles.open(temp_path, "wb") as out:
            while chunk := await file.read(CHUNK_SIZE):
                await out.write(chunk)
                total_bytes += len(chunk)
                # Check size limit during streaming
                if total_bytes > MAX_FILE_SIZE_MB * 1024 * 1024:
                    os.unlink(temp_path)
                    raise InvalidFileError(
                        f"File too large. Maximum size: {MAX_FILE_SIZE_MB}MB",
                        filename=file.filename,
                    )
        return temp_path, total_bytes
    except Exception:
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        raise


# =============================================================================
# Presigned Upload (Phase 4: Direct Client-to-S3)
# =============================================================================


@router.post(
    "/upload/presigned",
    response_model=PresignedUploadResponse,
    summary="Get Presigned S3 Upload URL",
    description="""
Generate a short-lived presigned URL for direct S3 upload.

## Use Case
*   **Large Files**: Bypass the API server for files > 10MB.
*   **Performance**: Faster upload speeds via direct S3 connection.

## Flow
1.  Call this endpoint to get `upload_url`.
2.  PUT the file to `upload_url`.
3.  Call `POST /datasets/{id}/trigger-validation` to start processing.
    """,
    responses={
        200: {
            "description": "Presigned URL generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "upload_url": "https://s3.aws.com/bucket/key?sig=...",
                        "storage_key": "123/456.csv",
                        "dataset_id": "123e4567-e89b-12d3-a456-426614174000",
                        "expires_in": 3600
                    }
                }
            }
        },
        429: {"description": "Rate limit exceeded (10/min)"},
        422: {"description": "Validation error (invalid extension)"}
    }
)
@limiter.limit("10/minute")  # Max 10 presigned URLs per minute per IP
async def get_presigned_upload_url(
    request: Request,
    response: Response,
    body: PresignedUploadRequest,
    db: DBSession,
    current_user: CurrentUser,
) -> PresignedUploadResponse:
    """
    Generate presigned URL for direct client-to-S3 upload.
    (Detailed docstring retained for code readability)
    """
    import uuid
    from datetime import datetime

    from src.features.process_mining.schemas import PresignedUploadResponse
    from src.platform.infrastructure.object_storage import get_storage_client

    logger.info(
        "🚀 [PRESIGNED] Request received",
        filename=body.filename,
        content_type=body.content_type,
        file_size_bytes=body.file_size_bytes,
        project_id=body.project_id,
        user_id=current_user.id,
        user_email=current_user.email,
        request_headers=dict(request.headers),
        client_host=request.client.host if request.client else None,
    )

    # Validate file extension
    logger.info("📋 [PRESIGNED] Step 1: Validating file extension", filename=body.filename)
    try:
        validate_file_upload_extension(body.filename)
        logger.info("✅ [PRESIGNED] File extension validated", filename=body.filename)
    except Exception as e:
        logger.error(
            "❌ [PRESIGNED] File extension validation failed", filename=body.filename, error=str(e)
        )
        raise

    # Validate file size (prevent storage quota attacks)
    logger.info("📏 [PRESIGNED] Step 2: Validating file size", file_size_bytes=body.file_size_bytes)
    from src.platform.core.config import get_settings

    settings = get_settings()
    if body.file_size_bytes and body.file_size_bytes > settings.s3_max_file_size_bytes:
        logger.error(
            "❌ [PRESIGNED] File size exceeds limit",
            file_size_bytes=body.file_size_bytes,
            max_size_bytes=settings.s3_max_file_size_bytes,
        )
        raise ValidationError(
            f"File size ({body.file_size_bytes} bytes) exceeds maximum allowed "
            f"({settings.s3_max_file_size_bytes} bytes / {settings.s3_max_file_size_bytes // (1024**3)} GB)"
        )
    logger.info("✅ [PRESIGNED] File size validated", file_size_bytes=body.file_size_bytes)

    # Validate project exists and check permission
    logger.info("🔐 [PRESIGNED] Step 3: Checking project permissions", project_id=body.project_id)
    if body.project_id:
        from src.platform.core.permissions import Permission
        from src.platform.workspaces.authorization import require_project_permission

        try:
            # Verify user has DATASET_CREATE permission in workspace
            _, _project = await require_project_permission(
                db, body.project_id, current_user, Permission.DATASET_CREATE
            )
            logger.info(
                "✅ [PRESIGNED] Project permissions validated",
                project_id=body.project_id,
                user_id=current_user.id,
            )
        except Exception as e:
            logger.error(
                "❌ [PRESIGNED] Project permission check failed",
                project_id=body.project_id,
                user_id=current_user.id,
                error=str(e),
                error_type=type(e).__name__,
            )
            raise
    else:
        # No project specified - user must provide one for RBAC
        logger.error("❌ [PRESIGNED] No project_id provided")
        raise ValidationError("project_id is required for dataset upload")

    # Generate unique storage key with UUID to prevent overwrites
    # Format: {dataset_id}/{uuid}.{extension}
    logger.info("🔑 [PRESIGNED] Step 4: Generating storage key")
    dataset_id = str(uuid.uuid4())
    file_extension = os.path.splitext(body.filename)[1]
    file_uuid = str(uuid.uuid4())
    storage_key = f"{dataset_id}/{file_uuid}{file_extension}"
    logger.info(
        "✅ [PRESIGNED] Storage key generated",
        dataset_id=dataset_id,
        storage_key=storage_key,
        file_extension=file_extension,
    )

    # Generate presigned upload URL FIRST (fail fast if S3 unavailable)
    logger.info("☁️ [PRESIGNED] Step 5: Generating presigned URL from storage client")
    storage_client = get_storage_client()
    logger.info(
        "📦 [PRESIGNED] Storage client initialized",
        storage_type=type(storage_client).__name__,
        bucket_type="raw",
    )
    try:
        upload_url = storage_client.get_presigned_upload_url(
            bucket_type="raw",
            key=storage_key,
            content_type=body.content_type,
        )
        logger.info(
            "✅ [PRESIGNED] Presigned URL generated successfully",
            storage_key=storage_key,
            url_length=len(upload_url),
            content_type=body.content_type,
        )
    except Exception as e:
        logger.error(
            "❌ [PRESIGNED] Presigned URL generation failed",
            storage_key=storage_key,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise ProcessingError(f"Failed to generate upload URL: {e}")

    # Create dataset record AFTER successful URL generation (transaction-safe)
    logger.info("💾 [PRESIGNED] Step 6: Creating dataset record in database")
    dataset_name = os.path.splitext(body.filename)[0]
    dataset = Dataset(
        id=dataset_id,
        name=dataset_name,
        project_id=body.project_id,
        source_format=file_extension.lstrip(".").upper(),
        status=DatasetStatus.PENDING.value,  # Waiting for client upload
        file_size_bytes=body.file_size_bytes,
        source_file=body.filename,
        storage_key=storage_key,  # Store for validation trigger
        created_at=datetime.utcnow(),
    )
    logger.info(
        "📝 [PRESIGNED] Dataset object created",
        dataset_id=dataset_id,
        dataset_name=dataset_name,
        status=DatasetStatus.PENDING.value,
    )

    try:
        db.add(dataset)
        await db.commit()
        logger.info("✅ [PRESIGNED] Dataset record committed to database", dataset_id=dataset_id)
    except Exception as e:
        logger.error(
            "❌ [PRESIGNED] Database commit failed",
            dataset_id=dataset_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise

    logger.info(
        "🎉 [PRESIGNED] SUCCESS - Presigned upload flow completed",
        dataset_id=dataset_id,
        storage_key=storage_key,
        expires_in=settings.s3_presigned_url_expiry,
        upload_url_preview=upload_url[:100] + "..." if len(upload_url) > 100 else upload_url,
    )

    response = PresignedUploadResponse(
        upload_url=upload_url,
        storage_key=storage_key,
        dataset_id=dataset_id,
        expires_in=settings.s3_presigned_url_expiry,
    )

    logger.info(
        "📤 [PRESIGNED] Returning response to client",
        dataset_id=response.dataset_id,
        has_upload_url=bool(response.upload_url),
        expires_in=response.expires_in,
    )

    return response


@router.post(
    "/{dataset_id}/trigger-validation",
    summary="Trigger Dataset Validation",
    description="""
Start the background validation and ingestion process after a successful S3 upload.

## When to use
Call this **only** after successfully uploading a file to the presigned URL obtained from `/upload/presigned`.
    """,
    responses={
        200: {
            "description": "Validation task queued",
            "content": {
                "application/json": {
                    "example": {
                        "status": "validation_queued",
                        "task_id": "task_12345",
                        "dataset_id": "123e4567-..."
                    }
                }
            }
        },
        400: {"description": "Dataset not in PENDING state"},
        404: {"description": "Dataset not found"}
    }
)
async def trigger_validation(
    dataset_id: str,
    db: DBSession,
    current_user: CurrentUser,
) -> dict[str, str]:
    """
    Trigger validation worker after client completes S3 upload.
    (Detailed docstring retained for code readability)
    """
    from src.platform.core.permissions import Permission
    from src.platform.infrastructure.tasks import validate_uploaded_file_task
    from src.platform.workspaces.authorization import require_dataset_permission

    # Check permission (also validates dataset exists)
    _, dataset = await require_dataset_permission(
        db, dataset_id, current_user, Permission.DATASET_UPDATE
    )

    if dataset.status != DatasetStatus.PENDING.value:
        raise ValidationError(f"Dataset must be in PENDING state. Current state: {dataset.status}")

    if not dataset.storage_key:
        raise ValidationError("Dataset missing storage_key. Cannot validate.")

    # Queue validation task
    task = validate_uploaded_file_task.delay(dataset_id, dataset.storage_key)

    logger.info(
        "validation_triggered",
        dataset_id=dataset_id,
        storage_key=dataset.storage_key,
        task_id=task.id,
        user_id=current_user.id,
    )

    return {
        "status": "validation_queued",
        "task_id": task.id,
        "dataset_id": dataset_id,
    }


@router.post("/webhooks/s3-upload-complete", include_in_schema=False)
async def handle_s3_upload_notification(
    http_request: Request,
    db: DBSession,
) -> dict[str, str]:
    """Handle S3 event notification after upload completes.

    Production flow (replaces manual trigger-validation):
    1. Client: POST /datasets/upload/presigned → Get presigned URL
    2. Client: PUT to presigned URL → Upload file to S3
    3. S3: Sends webhook to this endpoint → Automatic validation

    S3 Configuration Required:
    - Event: s3:ObjectCreated:*
    - Prefix: datasets/
    - Destination: https://api.example.com/api/v1/datasets/webhooks/s3-upload-complete

    Args:
        http_request: FastAPI request (contains S3 event JSON in body)
        db: Database session

    Returns:
        Status message

    Raises:
        ValidationError: If event format is invalid
        NotFoundError: If dataset doesn't exist
    """

    from src.platform.infrastructure.tasks import validate_uploaded_file_task

    # Parse S3 event notification
    try:
        event = await http_request.json()
    except Exception as e:
        logger.error("s3_webhook_parse_failed", error=str(e))
        raise ValidationError(f"Invalid S3 event format: {e}")

    # S3 events are wrapped in "Records" array
    if "Records" not in event:
        raise ValidationError("Missing 'Records' in S3 event")

    records = event["Records"]
    if not records:
        raise ValidationError("Empty 'Records' in S3 event")

    processed_keys = set()  # Idempotency: track processed keys

    for record in records:
        try:
            # Extract bucket and key from S3 event
            s3_info = record.get("s3", {})
            bucket = s3_info.get("bucket", {}).get("name")
            storage_key = s3_info.get("object", {}).get("key")

            if not bucket or not storage_key:
                logger.warning("s3_webhook_missing_fields", record=record)
                continue

            # Idempotency check: skip if already processed in this batch
            if storage_key in processed_keys:
                logger.info("s3_webhook_duplicate_skipped", storage_key=storage_key)
                continue

            processed_keys.add(storage_key)

            # Lookup dataset by storage_key
            result = await db.execute(select(Dataset).where(Dataset.storage_key == storage_key))
            dataset = result.scalar_one_or_none()

            if not dataset:
                logger.warning(
                    "s3_webhook_dataset_not_found",
                    storage_key=storage_key,
                    bucket=bucket,
                )
                continue

            # Only trigger if still in PENDING state
            if dataset.status != DatasetStatus.PENDING.value:
                logger.info(
                    "s3_webhook_dataset_not_pending",
                    dataset_id=dataset.id,
                    status=dataset.status,
                )
                continue

            # Queue validation task
            task = validate_uploaded_file_task.delay(dataset.id, storage_key)

            logger.info(
                "s3_webhook_validation_triggered",
                dataset_id=dataset.id,
                storage_key=storage_key,
                task_id=task.id,
                bucket=bucket,
            )

        except Exception as e:
            logger.error(
                "s3_webhook_record_processing_failed",
                error=str(e),
                record=record,
                exc_info=True,
            )
            # Continue processing other records

    return {
        "status": "processed",
        "records_processed": len(processed_keys),
    }


def validate_file_upload_extension(filename: str) -> None:
    """Validate file extension only (used for presigned uploads).

    Args:
        filename: The filename to validate

    Raises:
        InvalidFileError: If file extension is invalid
    """
    if not filename:
        raise InvalidFileError("No filename provided")

    allowed_extensions = {".csv", ".xes"}
    ext = os.path.splitext(filename)[1].lower()
    if ext not in allowed_extensions:
        logger.warning("upload_rejected_extension", filename=filename, extension=ext)
        raise InvalidFileError(
            f"Invalid file type '{ext}'. Allowed extensions: {', '.join(allowed_extensions)}",
            filename=filename,
            expected_types=list(allowed_extensions),
        )


@router.post(
    "/upload",
    response_model=DatasetResponse,
    summary="Upload Event Log File",
    description="""
Upload and ingest an event log file (CSV or XES).

## Features
*   **Auto-detection**: Smart column detection for CSV files.
*   **Streaming**: efficiently handles large files (up to 100MB) without memory issues.
*   **Async Store**: Optional deferred processing for very large datasets.

## Form Parameters
*   `file`: The file to upload.
*   `project_id`: Target project ID.
*   `case_id_column` etc.: Manual mapping overrides.
    """,
    responses={
        200: {
            "description": "Dataset created and ingested successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "name": "purchasing_log",
                        "status": "ready",
                        "total_events": 15400
                    }
                }
            }
        },
        400: {"description": "Invalid file format or missing columns"},
        413: {"description": "File too large (exceeds 100MB)"},
        422: {"description": "Validation error (missing project_id)"}
    }
)
async def upload_dataset(
    db: DBSession,
    user: CurrentUser,
    file: UploadFile = File(...),
    name: str | None = Form(None),
    project_id: str | None = Form(None, description="Project ID to assign dataset to"),
    case_id_column: str | None = Form(None),
    activity_column: str | None = Form(None),
    timestamp_column: str | None = Form(None),
    resource_column: str | None = Form(None),
    async_store: bool = Form(
        False, description="If true, store file only without parsing (deferred ingestion)"
    ),
):
    """
    Upload and ingest an event log file.
    
    (Detailed docstring retained for code readability)
    """
    # Validate file type and extension
    validate_file_upload(file)

    # Ensure filename is present (FastAPI UploadFile can have None filename)
    filename = file.filename
    if not filename:
        raise InvalidFileError("Filename is required")

    logger.info(
        "upload_started", filename=filename, name=name, project_id=project_id, user_id=user.id
    )
    start_time = time.perf_counter()

    # Validate project exists and check permission
    if project_id:
        from src.platform.core.permissions import Permission
        from src.platform.workspaces.authorization import require_project_permission

        # Verify user has DATASET_CREATE permission in workspace
        _, _project = await require_project_permission(
            db, project_id, user, Permission.DATASET_CREATE
        )
    else:
        # No project specified - user must provide one for RBAC
        raise ValidationError("project_id is required for dataset upload")

    # BUG-058 FIX: Stream file to disk in chunks to prevent OOM on large uploads
    import tempfile

    import aiofiles

    temp_file_path = None
    try:
        # Create temp file and stream content
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            temp_file_path = tmp.name

        total_size = 0
        async with aiofiles.open(temp_file_path, "wb") as out_file:
            # Read in 64KB chunks to prevent memory exhaustion
            while chunk := await file.read(64 * 1024):
                total_size += len(chunk)
                # Check size limit during streaming
                if total_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                    raise InvalidFileError(
                        f"File too large (>{MAX_FILE_SIZE_MB}MB). Maximum size: {MAX_FILE_SIZE_MB}MB",
                        filename=filename,
                    )
                await out_file.write(chunk)

        file_size_mb = total_size / (1024 * 1024)
        logger.info("file_streamed_to_disk", size_mb=round(file_size_mb, 2), path=temp_file_path)

        # Now read from temp file for processing
        async with aiofiles.open(temp_file_path, "rb") as f:
            content = await f.read()

        # Validate file signature to prevent spoofing
        await validate_file_signature(content, filename)

        # Deferred ingestion: store file only, return immediately
        if async_store:
            logger.info("async_store_mode", filename=filename)
            dataset = await ingestion_service.store_only(
                session=db,
                file_content=content,
                filename=filename,
                name=name,
                project_id=project_id,
            )
            logger.info(
                "async_store_completed",
                dataset_id=dataset.id,
                status=dataset.status,
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
            )

        # Use DuckDB for high-performance CSV ingestion if it's a CSV file
        ext = os.path.splitext(filename)[1].lower()
        if ext == ".csv":
            # Auto-detect columns if not provided
            if not all([case_id_column, activity_column, timestamp_column]):
                logger.info("auto_detecting_columns", filename=filename)
                # Use unified service for consistent column detection (routes to DuckDB for CSV)
                detection = unified_ingestion_service.detect_columns(content, filename)
                suggestions = detection.get("suggestions", {})

                case_id_column = case_id_column or suggestions.get("case_id_column")
                activity_column = activity_column or suggestions.get("activity_column")
                timestamp_column = timestamp_column or suggestions.get("timestamp_column")
                resource_column = resource_column or suggestions.get("resource_column")

                logger.info(
                    "columns_detected",
                    case=case_id_column,
                    activity=activity_column,
                    time=timestamp_column,
                    resource=resource_column,
                )

                # Validate detection success
                if not all([case_id_column, activity_column, timestamp_column]):
                    raise ValidationError(
                        f"Could not auto-detect required columns. Please provide mappings. Detected: {detection['columns']}",
                        field="columns",
                    )

            # DuckDB vectorized parse
            logger.info("using_duckdb_ingestion", filename=filename)
            duck_result = duckdb_ingestion_service.parse_csv(
                file_content=content,
                case_id_col=case_id_column,
                activity_col=activity_column,
                timestamp_col=timestamp_column,
                resource_col=resource_column,
            )

            # For now, we still save to SQLite through ingestion_service's logic
            # but we use the pre-parsed statistics and Arrow conversion
            dataset = await ingestion_service.ingest_file(
                session=db,
                file_content=content,
                filename=filename,
                name=name,
                case_id_col=case_id_column,
                activity_col=activity_column,
                timestamp_col=timestamp_column,
                resource_col=resource_column,
                precomputed_stats=duck_result["statistics"],
            )
        else:
            dataset = await ingestion_service.ingest_file(
                session=db,
                file_content=content,
                filename=filename,
                name=name,
                case_id_col=case_id_column,
                activity_col=activity_column,
                timestamp_col=timestamp_column,
                resource_col=resource_column,
            )

        activities = json.loads(dataset.activities_json) if dataset.activities_json else []
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Assign to project if project_id provided
        if project_id:
            dataset.project_id = project_id
            await db.flush()
            logger.info("dataset_assigned_to_project", dataset_id=dataset.id, project_id=project_id)

        logger.info(
            "upload_completed",
            dataset_id=dataset.id,
            total_events=dataset.total_events,
            total_cases=dataset.total_cases,
            total_activities=dataset.total_activities,
            duration_ms=round(duration_ms, 2),
        )

        return DatasetResponse(
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
        )
    except ValidationError as e:
        logger.warning("upload_validation_error", error=e.message, filename=filename)
        raise  # Let the AppException handler deal with it
    except InvalidFileError:
        raise  # Let the AppException handler deal with it
    except Exception as e:
        import traceback
        with open("upload_error_debug.log", "w") as f:
            f.write(traceback.format_exc())

        # Log full exception details for debugging
        logger.error(
            "upload_error",
            error=str(e),
            error_type=type(e).__name__,
            error_module=type(e).__module__,
            filename=filename,
            traceback=traceback.format_exc(),
            exc_info=True,
        )

        # Include exception type in error message for better debugging
        error_msg = f"[{type(e).__name__}] {e!s}"
        raise ProcessingError(f"Failed to process file: {error_msg}")
    finally:
        # BUG-058 FIX: Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                logger.warning("temp_file_cleanup_failed", path=temp_file_path)


@router.post("/detect-columns", response_model=ColumnDetectionResponse)
async def detect_columns(
    user: CurrentUser,
    file: UploadFile = File(...),
):
    """
    Detect column mappings from a CSV file.

    Returns suggested mappings for case_id, activity, timestamp, and resource columns.

    Requires DATASET_READ permission (public utility endpoint for authenticated users).
    """
    # Validate file type and extension
    validate_file_upload(file)

    # Ensure filename is present
    filename = file.filename
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    logger.info("detect_columns_started", filename=filename)
    start_time = time.perf_counter()

    # BUG-061 FIX: Stream file to temp file to prevent OOM on large files
    temp_file_path = None
    try:
        suffix = os.path.splitext(filename)[1]
        fd, temp_file_path = tempfile.mkstemp(suffix=suffix)
        os.close(fd)

        total_size = 0
        MAX_DETECT_SIZE_MB = 50  # Column detection doesn't need full file

        async with aiofiles.open(temp_file_path, "wb") as out_file:
            while chunk := await file.read(CHUNK_SIZE):
                total_size += len(chunk)
                if total_size > MAX_DETECT_SIZE_MB * 1024 * 1024:
                    # For detection, we only need a sample - stop reading
                    await out_file.write(chunk)
                    break
                await out_file.write(chunk)

        file_size_mb = total_size / (1024 * 1024)

        # Read from temp file
        async with aiofiles.open(temp_file_path, "rb") as f:
            content = await f.read()

        read_time_ms = (time.perf_counter() - start_time) * 1000
        logger.debug(
            "file_read_for_detection",
            size_mb=round(file_size_mb, 2),
            duration_ms=round(read_time_ms, 2),
        )

        # Validate file signature to prevent spoofing
        await validate_file_signature(content, filename)

        detection_start = time.perf_counter()

        # Use unified ingestion service for consistent detection (BUG-004 fix)
        response_data = unified_ingestion_service.detect_columns(content, filename)

        detection_time_ms = (time.perf_counter() - detection_start) * 1000

        total_time_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "detect_columns_completed",
            columns_found=len(response_data.get("columns", [])),
            row_count=response_data.get("row_count", 0),
            file_size_mb=round(file_size_mb, 2),
            detection_ms=round(detection_time_ms, 2),
            total_ms=round(total_time_ms, 2),
        )

        return ColumnDetectionResponse(**response_data)
    finally:
        # BUG-061 FIX: Clean up temp file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except OSError:
                logger.warning("detect_columns_temp_cleanup_failed", path=temp_file_path)


@router.post("/{dataset_id}/ingest", response_model=JobStatusResponse, status_code=202)
async def ingest_dataset(
    db: DBSession,
    dataset_id: str,
    request: IngestRequest,
    user: CurrentUser,
):
    """
    Trigger background ingestion for an AWAITING_MAPPING dataset.

    Job-Centric Architecture: Returns 202 with job_id for progress tracking.

    Phase 2 of deferred ingestion: user provides column mapping,
    background worker parses file and computes variants.

    Returns AsyncJob status for progress tracking via GET /jobs/{job_id}.

    Requires DATASET_UPDATE permission in the workspace.
    """
    from src.platform.core.enums import EntityType, JobStatus, JobType
    from src.platform.core.permissions import Permission
    from src.platform.infrastructure.tasks import ingest_dataset_task
    from src.platform.models import AsyncJob
    from src.platform.workspaces.authorization import require_dataset_permission

    logger.info("ingest_dataset_started", dataset_id=dataset_id, user_id=user.id)

    # Check permission (also validates dataset exists)
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_UPDATE)

    # Idempotency: reject if already ingesting
    if dataset.status in [DatasetStatus.INGESTING.value, DatasetStatus.ANALYZING.value]:
        raise ValidationError(
            f"Dataset {dataset_id} is already being ingested. Check job status.",
            field="status",
        )

    # Only allow ingestion for AWAITING_MAPPING, UNSTRUCTURED (legacy), or ERROR datasets
    valid_statuses = [
        DatasetStatus.AWAITING_MAPPING.value,
        DatasetStatus.UNSTRUCTURED.value,  # Legacy support
        DatasetStatus.ERROR.value,
    ]
    if dataset.status not in valid_statuses:
        raise ValidationError(
            f"Dataset {dataset_id} has status '{dataset.status}'. Only AWAITING_MAPPING or ERROR datasets can be ingested.",
            field="status",
        )

    # Store mapping
    import json

    mapping = {
        "case_id_column": request.case_id_column,
        "activity_column": request.activity_column,
        "timestamp_column": request.timestamp_column,
        "resource_column": request.resource_column,
    }
    dataset.mapping_json = json.dumps(mapping)
    dataset.status = DatasetStatus.INGESTING.value  # Job-centric status
    dataset.error_message = None  # Clear previous errors
    await db.flush()

    # Create AsyncJob record with new job-centric fields
    job = AsyncJob(
        job_type=JobType.INGESTION.value,
        status=JobStatus.PENDING.value,
        entity_type=EntityType.DATASET.value,
        entity_id=dataset_id,
        parameters_json=json.dumps({"dataset_id": dataset_id, "mapping": mapping}),
    )
    db.add(job)
    await db.flush()

    # Link job to dataset
    dataset.ingestion_job_id = job.id
    await db.flush()

    # Queue Celery task
    task = ingest_dataset_task.delay(dataset_id=dataset_id, mapping=mapping)

    # Link task_id to job
    job.task_id = task.id
    await db.flush()

    logger.info(
        "ingest_dataset_queued",
        dataset_id=dataset_id,
        job_id=job.id,
        task_id=task.id,
    )

    return JobStatusResponse(
        id=job.id,
        job_type=job.job_type,
        status=job.status,
        progress=0,
        created_at=job.created_at,
    )


@router.get("/{dataset_id}/detect-columns", response_model=ColumnDetectionResponse)
async def detect_columns_for_dataset(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
):
    """
    Detect column mappings from an already-uploaded UNSTRUCTURED dataset.

    Reads the stored file and returns suggested mappings for case_id,
    activity, timestamp, and resource columns.

    Requires DATASET_READ permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission
    from src.platform.storage.storage import storage_service

    logger.info("detect_columns_for_dataset_started", dataset_id=dataset_id, user_id=user.id)
    start_time = time.perf_counter()

    # Check permission (also validates dataset exists)
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Only allow for UNSTRUCTURED or ERROR datasets
    if dataset.status not in [DatasetStatus.UNSTRUCTURED.value, DatasetStatus.ERROR.value]:
        raise ValidationError(
            f"Dataset {dataset_id} has status '{dataset.status}'. Column detection is only available for UNSTRUCTURED datasets.",
            field="status",
        )

    # Get the stored file
    if not dataset.source_file:
        raise ValidationError(
            f"Dataset {dataset_id} has no source file stored.",
            field="source_file",
        )

    try:
        content = await storage_service.retrieve_dataset_file(
            dataset_id=dataset_id,
            filename=dataset.source_file,
        )
    except FileNotFoundError:
        raise ProcessNotFoundError(dataset_id, resource_name="Source file")

    file_size_mb = len(content) / (1024 * 1024)
    logger.info("file_read_for_detection", dataset_id=dataset_id, size_mb=round(file_size_mb, 2))

    # Use unified ingestion service for consistent detection (BUG-004 fix)
    response_data = unified_ingestion_service.detect_columns(content, dataset.source_file)

    detection_time_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "detect_columns_for_dataset_completed",
        dataset_id=dataset_id,
        columns_found=len(response_data.get("columns", [])),
        row_count=response_data.get("row_count", 0),
        duration_ms=round(detection_time_ms, 2),
    )

    return ColumnDetectionResponse(**response_data)


# =============================================================================
# Upload Wizard: Preview & Sheets (Celonis-style 5-step wizard)
# =============================================================================


@router.get("/{dataset_id}/preview", response_model=DataPreviewResponse)
async def get_data_preview(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
    rows: int = Query(10, ge=1, le=50, description="Number of preview rows"),
):
    """
    Get data preview with column types for upload wizard Configure step.

    Returns:
    - Column names with detected types (STRING, INTEGER, DATETIME, etc.)
    - Sample preview rows
    - Parsing configuration info

    Supports navigation away and back - data is preserved in storage.

    Requires DATASET_READ permission in the workspace.
    """
    import csv
    import io

    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission
    from src.platform.storage.storage import storage_service

    logger.info("get_data_preview_started", dataset_id=dataset_id, rows=rows, user_id=user.id)
    start_time = time.perf_counter()

    # Check permission (also validates dataset exists)
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    if not dataset.source_file:
        raise ValidationError(
            f"Dataset {dataset_id} has no source file stored.",
            field="source_file",
        )

    # Retrieve stored file
    try:
        content = await storage_service.retrieve_dataset_file(
            dataset_id=dataset_id,
            filename=dataset.source_file,
        )
    except FileNotFoundError:
        raise ProcessNotFoundError(dataset_id, resource_name="Source file")

    # Parse CSV for preview
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    text.split("\n")
    reader = csv.reader(io.StringIO(text))
    all_rows = list(reader)

    if len(all_rows) < 1:
        raise ValidationError("File contains no data", field="file")

    # First row is header
    headers = all_rows[0]
    data_rows = all_rows[1 : rows + 1]  # Get requested number of rows

    # Detect column types from sample data
    columns = []
    for i, header in enumerate(headers):
        sample_values = [row[i] for row in data_rows if i < len(row)]
        detected_type = _detect_column_type(sample_values)
        date_format = None

        if detected_type == "DATETIME":
            date_format = _detect_date_format(sample_values)

        null_count = sum(1 for v in sample_values if not v or v.strip() == "")

        columns.append(
            ColumnTypeInfo(
                name=header,
                detected_type=detected_type,
                sample_values=sample_values[:5],
                null_count=null_count,
                date_format=date_format,
            )
        )

    # Create row dictionaries
    preview_rows = []
    for row in data_rows:
        row_dict = {}
        for i, header in enumerate(headers):
            row_dict[header] = row[i] if i < len(row) else ""
        preview_rows.append(row_dict)

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "get_data_preview_completed",
        dataset_id=dataset_id,
        columns=len(columns),
        rows_returned=len(preview_rows),
        duration_ms=round(duration_ms, 2),
    )

    return DataPreviewResponse(
        dataset_id=dataset_id,
        filename=dataset.source_file,
        columns=columns,
        rows=preview_rows,
        total_rows=len(all_rows) - 1,  # Exclude header
        has_header=True,
        field_separator=",",
        encoding="utf-8",
    )


def _detect_column_type(values: list[str]) -> str:
    """Detect column type from sample values."""
    non_empty = [v for v in values if v and v.strip()]
    if not non_empty:
        return "STRING"

    # Check for datetime patterns
    datetime_patterns = [
        r"\d{4}-\d{2}-\d{2}",  # 2024-01-15
        r"\d{1,2}/\d{1,2}/\d{2,4}",  # 1/15/2024 or 01/15/24
        r"\d{4}/\d{2}/\d{2}",  # 2024/01/15
    ]
    import re

    for v in non_empty[:5]:
        for pattern in datetime_patterns:
            if re.match(pattern, v.strip()):
                return "DATETIME"

    # Check for numbers
    try:
        for v in non_empty[:10]:
            v = v.strip().replace(",", "").replace(" ", "")
            if v:
                float(v)
        # Check if integers
        if all("." not in v for v in non_empty[:10] if v.strip()):
            return "INTEGER"
        return "DECIMAL"
    except ValueError:
        pass

    # Check for boolean
    bool_values = {"true", "false", "1", "0", "yes", "no", "y", "n"}
    if all(v.lower().strip() in bool_values for v in non_empty[:10]):
        return "BOOLEAN"

    return "STRING"


def _detect_date_format(values: list[str]) -> str:
    """Detect date format from sample values."""
    import re

    for v in values:
        if not v or not v.strip():
            continue
        v = v.strip()

        # MM/dd/yyyy HH:mm
        if re.match(r"\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2}", v):
            return "MM/dd/yyyy HH:mm"
        # yyyy-MM-dd HH:mm:ss
        if re.match(r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}", v):
            return "yyyy-MM-dd HH:mm:ss"
        # yyyy-MM-dd
        if re.match(r"\d{4}-\d{2}-\d{2}$", v):
            return "yyyy-MM-dd"
        # dd/MM/yyyy
        if re.match(r"\d{2}/\d{2}/\d{4}$", v):
            return "dd/MM/yyyy"

    return "yyyy-MM-dd HH:mm:ss"


@router.get("/{dataset_id}/sheets", response_model=SheetsResponse)
async def get_sheets(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
):
    """
    List available sheets in an Excel file.

    For CSV files, returns a single pseudo-sheet.
    Required for upload wizard Step 2 (Select Sheet).

    Requires DATASET_READ permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission
    from src.platform.storage.storage import storage_service

    logger.info("get_sheets_started", dataset_id=dataset_id, user_id=user.id)

    # Check permission (also validates dataset exists)
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    if not dataset.source_file:
        raise ValidationError(
            f"Dataset {dataset_id} has no source file stored.",
            field="source_file",
        )

    filename = dataset.source_file
    ext = os.path.splitext(filename)[1].lower()

    # For CSV files, return single sheet
    if ext == ".csv":
        return SheetsResponse(
            dataset_id=dataset_id,
            filename=filename,
            sheets=[SheetInfo(name="Sheet1", index=0, row_count=0, column_count=0)],
        )

    # For Excel files, parse sheet names
    if ext in [".xlsx", ".xls"]:
        try:
            content = await storage_service.retrieve_dataset_file(
                dataset_id=dataset_id,
                filename=filename,
            )

            # Use openpyxl for xlsx
            from io import BytesIO

            import openpyxl

            workbook = openpyxl.load_workbook(BytesIO(content), read_only=True)
            sheets = []
            for idx, sheet_name in enumerate(workbook.sheetnames):
                sheet = workbook[sheet_name]
                sheets.append(
                    SheetInfo(
                        name=sheet_name,
                        index=idx,
                        row_count=sheet.max_row or 0,
                        column_count=sheet.max_column or 0,
                    )
                )
            workbook.close()

            logger.info("get_sheets_completed", dataset_id=dataset_id, sheets=len(sheets))
            return SheetsResponse(
                dataset_id=dataset_id,
                filename=filename,
                sheets=sheets,
            )
        except Exception as e:
            logger.error("get_sheets_error", dataset_id=dataset_id, error=str(e))
            raise ProcessingError(f"Failed to read Excel file: {e!s}")

    # Unsupported format
    raise ValidationError(f"Unsupported file format: {ext}", field="source_file")


# =============================================================================
# List & Get
# =============================================================================


@router.get("", response_model=DatasetListResponse)
async def list_datasets(
    db: DBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    source_format: str | None = Query(None),
    project_id: str | None = Query(None, description="Filter by project ID"),
):
    """
    List all uploaded datasets.

    Supports pagination and filtering by source format.

    Requires DATASET_READ permission.
    Automatically filtered by workspace membership (RLS).
    """
    from src.platform.models import Workspace, WorkspaceMember

    logger.debug(
        "list_datasets",
        page=page,
        page_size=page_size,
        source_format=source_format,
        project_id=project_id,
        user_id=user.id,
    )

    # Build query with RLS filtering (user's workspaces only)
    query = (
        select(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .join(Workspace, Project.workspace_id == Workspace.id)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user.id)
        .order_by(Dataset.created_at.desc())
    )

    if source_format:
        query = query.where(Dataset.source_format == source_format)

    if project_id:
        # Verify user has access to this project
        from src.platform.core.permissions import Permission
        from src.platform.workspaces.authorization import require_project_permission

        await require_project_permission(db, project_id, user, Permission.PROJECT_READ)
        query = query.where(Dataset.project_id == project_id)

    # Count total with same RLS filtering
    count_query = (
        select(func.count())
        .select_from(Dataset)
        .join(Project, Dataset.project_id == Project.id)
        .join(Workspace, Project.workspace_id == Workspace.id)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .filter(WorkspaceMember.user_id == user.id)
    )
    if source_format:
        count_query = count_query.where(Dataset.source_format == source_format)
    if project_id:
        count_query = count_query.where(Dataset.project_id == project_id)

    total = await db.scalar(count_query) or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    logs = result.scalars().all()

    items = []
    for log in logs:
        items.append(DatasetResponse.model_validate(log))

    return DatasetListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
async def get_dataset(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
):
    """
    Get detailed information about an event log.

    Requires DATASET_READ permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission

    logger.info("fetching_dataset", dataset_id=dataset_id, user_id=user.id)

    # Check permission (also validates dataset exists)
    try:
        _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    except HTTPException as e:
        if e.status_code == 404:
            logger.warning("dataset_not_found", dataset_id=dataset_id, user_id=user.id)
            log_error(
                "Dataset",
                "Dataset not found",
                error_code="DS_NOT_FOUND",
                dataset_id=dataset_id,
            )
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Dataset not found",
                    "error_code": "DS_NOT_FOUND",
                    "dataset_id": dataset_id,
                    "suggestion": "Check that the dataset ID is correct and you have access to it"
                }
            )
        raise

    activities = json.loads(dataset.activities_json) if dataset.activities_json else []
    statistics = json.loads(dataset.statistics_json) if dataset.statistics_json else None

    logger.info(
        "dataset_fetched",
        dataset_id=dataset_id,
        dataset_name=dataset.name,
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        status=dataset.status,
        user_id=user.id,
    )
    log_info(
        "Dataset",
        "Dataset fetched successfully",
        dataset_id=dataset_id,
        name=dataset.name,
        events=dataset.total_events,
        cases=dataset.total_cases,
        status=dataset.status,
    )

    return DatasetDetailResponse(
        id=dataset.id,
        name=dataset.name,
        source_format=dataset.source_format,
        source_file=dataset.source_file,
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        activities=activities,
        statistics=statistics,
        created_at=dataset.created_at,
        updated_at=dataset.updated_at,
        status=dataset.status,
    )


@router.delete("/{dataset_id}")
async def delete_dataset(
    dataset_id: str,
    db: DBSession,
    user: CurrentUser,
):
    """
    Delete an event log and all associated data.

    Requires DATASET_DELETE permission in the workspace.

    BUG-052 FIX: Also deletes orphaned recommendations.
    SECURITY: Added authentication and permission check (Phase 6.2)
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission

    logger.info("deleting_dataset", dataset_id=dataset_id, user_id=user.id)

    # Check permission (also validates dataset exists and user has access)
    try:
        _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_DELETE)
    except HTTPException as e:
        if e.status_code == 404:
            logger.warning("dataset_not_found_for_deletion", dataset_id=dataset_id, user_id=user.id)
            log_error(
                "Dataset",
                "Cannot delete - dataset not found",
                error_code="DS_NOT_FOUND",
                dataset_id=dataset_id,
            )
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "Dataset not found",
                    "error_code": "DS_NOT_FOUND",
                    "dataset_id": dataset_id,
                    "suggestion": "Verify the dataset ID before attempting deletion"
                }
            )
        raise

    # BUG-052 FIX: Clean up recommendations before deleting dataset
    from sqlalchemy import delete

    from src.features.process_mining.models import Recommendation

    try:
        await db.execute(delete(Recommendation).where(Recommendation.dataset_id == dataset_id))
        await db.delete(dataset)
        await db.commit()

        logger.info(
            "dataset_deleted",
            dataset_id=dataset_id,
            dataset_name=dataset.name,
            total_events=dataset.total_events,
            user_id=user.id,
        )
        log_info(
            "Dataset",
            "Dataset deleted successfully",
            dataset_id=dataset_id,
            name=dataset.name,
            events=dataset.total_events,
        )

        return {"status": "deleted", "id": dataset_id}
    except Exception as e:
        logger.error("dataset_deletion_failed", dataset_id=dataset_id, error=str(e), exc_info=True)
        log_error(
            "Dataset",
            "Failed to delete dataset",
            error_code="DS_DELETE_FAILED",
            dataset_id=dataset_id,
            reason=str(e),
        )
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to delete dataset",
                "error_code": "DS_DELETE_FAILED",
                "dataset_id": dataset_id,
                "reason": str(e),
                "suggestion": "Check database connectivity and ensure no foreign key constraints are blocking deletion"
            }
        )


# =============================================================================
# Statistics & Analysis
# =============================================================================


@router.get("/{dataset_id}/statistics", response_model=StatisticsResponse)
async def get_statistics(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
):
    """
    Get comprehensive statistics for an event log.

    Includes activities, variants, case durations, and more.

    PERFORMANCE: Uses SQL aggregations instead of ORM eager loading
    to prevent OOM on large datasets (1M+ events).

    Requires DATASET_READ permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission

    logger.info("get_statistics_started", dataset_id=dataset_id, user_id=user.id)
    start_time = time.perf_counter()

    # Check permission (also validates dataset exists)
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    activities = json.loads(dataset.activities_json) if dataset.activities_json else []

    # Get start/end activities from mining service (uses fast DuckDB path)
    start_activities = mining_service.get_start_activities(dataset)
    end_activities = mining_service.get_end_activities(dataset)

    # Get variants using mining service (uses fast DuckDB path)
    variants_data = mining_service.get_variants(dataset)

    # Get case duration stats via SQL aggregation (NO ORM object instantiation!)
    from sqlalchemy import func as sql_func

    duration_stats = await db.execute(
        select(
            sql_func.avg(
                sql_func.extract("epoch", ProcessCase.end_time)
                - sql_func.extract("epoch", ProcessCase.start_time)
            ).label("avg_duration"),
            sql_func.min(
                sql_func.extract("epoch", ProcessCase.end_time)
                - sql_func.extract("epoch", ProcessCase.start_time)
            ).label("min_duration"),
            sql_func.max(
                sql_func.extract("epoch", ProcessCase.end_time)
                - sql_func.extract("epoch", ProcessCase.start_time)
            ).label("max_duration"),
            sql_func.min(ProcessCase.start_time).label("date_start"),
            sql_func.max(ProcessCase.end_time).label("date_end"),
        )
        .where(ProcessCase.dataset_id == dataset_id)
        .where(ProcessCase.start_time.isnot(None))
        .where(ProcessCase.end_time.isnot(None))
    )
    stats_row = duration_stats.one_or_none()

    # Extract values from SQL result (handles None cases)
    avg_duration = float(stats_row.avg_duration) if stats_row and stats_row.avg_duration else None
    min_duration = float(stats_row.min_duration) if stats_row and stats_row.min_duration else None
    max_duration = float(stats_row.max_duration) if stats_row and stats_row.max_duration else None

    date_range = None
    if stats_row and stats_row.date_start and stats_row.date_end:
        date_range = {
            "start": stats_row.date_start,
            "end": stats_row.date_end,
        }

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "get_statistics_completed",
        dataset_id=dataset_id,
        total_variants=variants_data.get("total_variants", 0),
        duration_ms=round(duration_ms, 2),
    )

    return StatisticsResponse(
        total_events=dataset.total_events,
        total_cases=dataset.total_cases,
        total_activities=dataset.total_activities,
        total_variants=variants_data.get("total_variants", 0),
        activities=activities,
        start_activities=start_activities,
        end_activities=end_activities,
        avg_case_duration_seconds=avg_duration,
        min_case_duration_seconds=min_duration,
        max_case_duration_seconds=max_duration,
        date_range=date_range,
    )


@router.get("/{dataset_id}/cases", response_model=CaseListResponse)
async def list_cases(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """
    List cases in an event log with pagination.

    Requires DATASET_READ permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission

    logger.debug(
        "list_cases", dataset_id=dataset_id, page=page, page_size=page_size, user_id=user.id
    )

    # Check permission (also validates dataset exists)
    _, _dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Count total cases
    count_query = (
        select(func.count()).select_from(ProcessCase).where(ProcessCase.dataset_id == dataset_id)
    )
    total = await db.scalar(count_query) or 0

    # Paginate cases with event count via SQL subquery (avoid loading events)
    from src.features.process_mining.models import ProcessEvent

    # Create a subquery to count events per case
    event_count_subq = (
        select(func.count(ProcessEvent.id).label("event_count"))
        .where(ProcessEvent.case_ref_id == ProcessCase.id)
        .scalar_subquery()
    )

    offset = (page - 1) * page_size
    cases_query = (
        select(ProcessCase, event_count_subq.label("event_count"))
        .where(ProcessCase.dataset_id == dataset_id)
        .order_by(ProcessCase.case_id)
        .offset(offset)
        .limit(page_size)
    )
    result = await db.execute(cases_query)
    cases_with_counts = result.all()

    items = []
    for case, event_count in cases_with_counts:
        duration = None
        if case.start_time and case.end_time:
            duration = (case.end_time - case.start_time).total_seconds()

        items.append(
            CaseResponse(
                case_id=case.case_id,
                event_count=event_count or 0,
                variant=case.variant_key,
                start_time=case.start_time,
                end_time=case.end_time,
                duration_seconds=duration,
            )
        )

    return CaseListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{dataset_id}/variants", response_model=list[VariantResponse])
async def get_variants(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
    top_n: int = Query(20, ge=1, le=100),
    top_k_percent: float | None = Query(
        None, ge=0, le=100, description="Return variants covering top K% of cases"
    ),
    include_complexity: bool = Query(
        False, description="Include complexity metrics (score, rework count, unique activities)"
    ),
    sort_by: str | None = Query(
        None,
        description="Sort variants by: 'frequency', 'complexity', 'duration'. Default: frequency",
    ),
):
    """
    Get process variants (unique activity sequences) with frequencies.

    Supports filtering by:
    - top_n: Return top N variants by case count
    - top_k_percent: Return variants covering top K% of cases

    When include_complexity=true, each variant includes:
    - complexity_score: 0-1 score based on length, rework, and repetition
    - rework_count: Number of repeated activities
    - unique_activity_count: Number of distinct activities

    PERFORMANCE: Uses SQL aggregation instead of ORM iteration to avoid loading
    millions of objects into memory.

    Requires DATASET_READ permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission

    logger.info(
        "get_variants_started",
        dataset_id=dataset_id,
        top_n=top_n,
        top_k_percent=top_k_percent,
        include_complexity=include_complexity,
        user_id=user.id,
    )
    start_time = time.perf_counter()

    # Check permission (also validates dataset exists)
    _, _dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Use SQL aggregation to compute variant statistics
    # This is 100x faster than loading all cases into memory
    variant_query = (
        select(
            ProcessCase.variant_key,
            func.count(ProcessCase.id).label("case_count"),
            func.avg(
                func.extract("epoch", ProcessCase.end_time)
                - func.extract("epoch", ProcessCase.start_time)
            ).label("avg_duration"),
        )
        .where(ProcessCase.dataset_id == dataset_id)
        .group_by(ProcessCase.variant_key)
        .order_by(func.count(ProcessCase.id).desc())
    )

    variant_results = await db.execute(variant_query)
    all_variants = variant_results.all()

    total_cases = sum(v.case_count for v in all_variants)

    # Apply top_k_percent filtering if specified
    if top_k_percent is not None:
        target_cases = int(total_cases * top_k_percent / 100)
        cumulative = 0
        filtered_variants = []
        for variant_row in all_variants:
            filtered_variants.append(variant_row)
            cumulative += variant_row.case_count
            if cumulative >= target_cases:
                break
        selected_variants = filtered_variants
    else:
        selected_variants = all_variants[:top_n]

    # Build response
    variants = []
    for variant_row in selected_variants:
        variant_key = variant_row.variant_key or "unknown"

        # Optional complexity calculation
        complexity_score: float | None = None
        rework_count: int | None = None
        unique_activity_count: int | None = None

        if include_complexity:
            complexity = mining_service.calculate_variant_complexity(variant_key)
            complexity_score = complexity.get("complexity_score")
            rework_count = complexity.get("rework_count")
            unique_activity_count = complexity.get("unique_activity_count")

        # Parse activities from variant_key
        if " → " in variant_key:
            activities = [a.strip() for a in variant_key.split(" → ")]
        elif " -> " in variant_key:
            activities = [a.strip() for a in variant_key.split(" -> ")]
        else:
            activities = [variant_key.strip()] if variant_key.strip() else []

        variants.append(
            VariantResponse(
                variant_key=variant_key,
                activity_trace=variant_key,
                activities=activities,
                case_count=variant_row.case_count,
                frequency_percent=round(variant_row.case_count / total_cases * 100, 2)
                if total_cases > 0
                else 0.0,
                avg_duration_seconds=float(variant_row.avg_duration)
                if variant_row.avg_duration
                else None,
                complexity_score=complexity_score,
                rework_count=rework_count,
                unique_activity_count=unique_activity_count,
            )
        )

    # Apply sorting if specified
    if sort_by == "complexity" and include_complexity:
        variants.sort(key=lambda v: v.complexity_score or 0, reverse=True)
    elif sort_by == "duration":
        variants.sort(key=lambda v: v.avg_duration_seconds or 0, reverse=True)
    # Default (frequency) is already sorted

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "get_variants_completed",
        dataset_id=dataset_id,
        variants_count=len(variants),
        duration_ms=round(duration_ms, 2),
    )
    return variants


@router.get("/{dataset_id}/activities", response_model=list[ActivityDetailResponse])
async def get_activities(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
    sort_by: str | None = Query(
        None,
        description="Sort activities by: 'frequency', 'duration', 'position'. Default: frequency",
    ),
):
    """
    Get detailed activity statistics for a process.

    Returns each activity with:
    - frequency: Total occurrences
    - frequency_percent: Percentage of total events
    - avg/min/max_duration_seconds: Time to next activity
    - is_start_activity/is_end_activity: Position flags
    - position_avg: Average normalized position (0=start, 1=end)

    PERFORMANCE: Uses event_log_loader (DuckDB/Arrow) instead of ORM iteration
    to avoid loading millions of objects into memory.

    Requires DATASET_READ permission in the workspace.
    """
    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission

    logger.info("get_activities_started", dataset_id=dataset_id, sort_by=sort_by, user_id=user.id)
    start_time = time.perf_counter()

    # Check permission (also validates dataset exists)
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Get activity statistics using fast path
    # mining_service.get_activity_statistics already uses event_log_loader internally
    activities_data = mining_service.get_activity_statistics(dataset)

    # Convert to response objects
    activities = [ActivityDetailResponse(**a) for a in activities_data]

    # Apply sorting if specified
    if sort_by == "duration":
        activities.sort(key=lambda a: a.avg_duration_seconds or 0, reverse=True)
    elif sort_by == "position":
        activities.sort(key=lambda a: a.position_avg or 0.5)
    # Default (frequency) is already sorted

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "get_activities_completed",
        dataset_id=dataset_id,
        activities_count=len(activities),
        duration_ms=round(duration_ms, 2),
    )
    return activities


# =============================================================================
# Domain Model Integration (New Architecture Demo)
# =============================================================================


@router.get("/{dataset_id}/domain/analysis")
async def get_domain_analysis(
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
):
    """
    Get process analysis using the new rich domain model.

    This endpoint demonstrates the improved architecture:
    1. Repository pattern for data access
    2. DatasetAggregate for domain logic
    3. PM4Py log caching (single conversion)
    4. Computed properties on domain entities

    Returns aggregate statistics, variant analysis, and PM4Py cache status.

    Requires DATASET_READ permission in the workspace.
    """
    import pm4py

    from src.platform.core.permissions import Permission
    from src.platform.workspaces.authorization import require_dataset_permission

    logger.info("domain_analysis_started", dataset_id=dataset_id, user_id=user.id)
    start_time = time.perf_counter()

    # Check permission first
    _, _dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # 1. Load via repository (eager loading)
    repo = SQLAlchemyDatasetRepository(db)
    aggregate = await repo.get(dataset_id)

    if not aggregate:
        logger.warning("process_not_found", dataset_id=dataset_id)
        raise ProcessNotFoundError(dataset_id)

    repo_load_ms = (time.perf_counter() - start_time) * 1000

    # 2. First PM4Py conversion (builds cache)
    pm4py_start = time.perf_counter()
    aggregate.to_pm4py_log()
    first_conversion_ms = (time.perf_counter() - pm4py_start) * 1000

    # 3. Second PM4Py access (cache hit)
    cache_start = time.perf_counter()
    pm4py_log_cached = aggregate.to_pm4py_log()  # Should be instant
    cache_hit_ms = (time.perf_counter() - cache_start) * 1000

    # 4. Use PM4Py for analysis (uses cached log)
    pm4py_analysis_start = time.perf_counter()
    dfg, start_acts, end_acts = pm4py.discover_dfg(pm4py_log_cached)
    pm4py_analysis_ms = (time.perf_counter() - pm4py_analysis_start) * 1000

    # 5. Get domain computed properties
    stats = aggregate.statistics
    variant_stats = aggregate.get_variant_stats(top_n=5)

    total_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "domain_analysis_completed",
        dataset_id=dataset_id,
        repo_load_ms=round(repo_load_ms, 2),
        first_conversion_ms=round(first_conversion_ms, 2),
        cache_hit_ms=round(cache_hit_ms, 2),
        pm4py_analysis_ms=round(pm4py_analysis_ms, 2),
        total_ms=round(total_ms, 2),
    )

    return {
        "dataset_id": aggregate.id,
        "name": aggregate.name,
        # Statistics from domain aggregate
        "statistics": {
            "total_events": stats.total_events,
            "total_cases": stats.total_cases,
            "total_activities": stats.total_activities,
            "total_variants": stats.total_variants,
            "avg_events_per_case": round(stats.avg_events_per_case, 2),
            "avg_case_duration_seconds": stats.avg_case_duration_seconds,
        },
        # Top variants from domain model
        "top_variants": [
            {
                "variant": v.sequence.to_trace_string(),
                "case_count": v.case_count,
                "frequency_percent": round(v.frequency_percent, 2),
                "complexity_score": round(v.complexity_score, 4),
                "has_rework": v.sequence.has_rework,
            }
            for v in variant_stats
        ],
        # DFG summary from PM4Py (using cached log)
        "dfg_summary": {
            "edges_count": len(dfg),
            "start_activities": list(start_acts.keys())[:5],
            "end_activities": list(end_acts.keys())[:5],
        },
        # Performance metrics (demonstrates caching benefit)
        "performance": {
            "repository_load_ms": round(repo_load_ms, 2),
            "first_pm4py_conversion_ms": round(first_conversion_ms, 2),
            "cached_pm4py_access_ms": round(cache_hit_ms, 2),
            "pm4py_dfg_analysis_ms": round(pm4py_analysis_ms, 2),
            "total_ms": round(total_ms, 2),
            "cache_speedup": f"{round(first_conversion_ms / max(cache_hit_ms, 0.001), 1)}x",
        },
    }
