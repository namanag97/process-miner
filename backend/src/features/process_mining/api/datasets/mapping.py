"""Mapping Router - Column detection and mapping endpoints.

Handles column detection suggestions and user-provided mappings.
Part of 4-Phase Upload Architecture: Upload → Validate → Map → Ingest
"""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Query
from sqlalchemy import select
from starlette.concurrency import run_in_threadpool

from src.api.dependencies import CurrentUser, ReadDBSession
from src.features.process_mining.models import (
    DatasetColumn,
    DatasetColumnMapping,
    DatasetStatus,
)
from src.features.process_mining.schemas import (
    ColumnDetectionResponse,
    ColumnTypeInfo,
    MappingUpdateRequest,
)
from src.features.process_mining.schemas.datasets import (
    MappingResponse,
    PreviewResponse,
)
from src.platform.core.exceptions import ValidationError
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.workspaces.authorization import require_dataset_permission

logger = get_logger(__name__)

router = APIRouter()


# =============================================================================
# Column Detection & Mapping APIs
# =============================================================================


@router.get(
    "/{dataset_id}/columns",
    response_model=ColumnDetectionResponse,
    summary="Get Detected Columns",
    description="""
Get detected columns with type information and mapping suggestions.

Returns each column with:
- Detected data type
- Sample values
- Suggested role (case_id, activity, timestamp, resource)
- Confidence score for suggestion ( 0.0-1.0)
    """,
    responses={
        200: {"description": "Column detection results"},
        404: {"description": "Dataset not found"},
    },
)
async def get_columns(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> ColumnDetectionResponse:
    """Get detected columns with suggestions."""
    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Get columns
    result = await db.execute(
        select(DatasetColumn)
        .where(DatasetColumn.dataset_id == dataset_id)
        .order_by(DatasetColumn.position)
    )
    columns = result.scalars().all()

    # Build suggestions dict
    suggestions = {}
    requires_user_input = False
    confidence_threshold = 0.8

    column_infos = []
    for col in columns:
        sample_values = json.loads(col.sample_values_json) if col.sample_values_json else []

        column_infos.append(
            ColumnTypeInfo(
                name=col.name,
                dtype=col.dtype,
                position=col.position,
                sample_values=sample_values,
                null_percentage=col.null_percentage,
                unique_count=col.unique_count,
                suggested_role=col.suggested_role,
                confidence=col.suggestion_confidence,
            )
        )

        # Build suggestions for mapping
        if col.suggested_role and col.suggestion_confidence:
            suggestions[col.suggested_role] = {
                "column": col.name,
                "confidence": col.suggestion_confidence,
            }
            if col.suggestion_confidence < confidence_threshold:
                requires_user_input = True

    # Check if all required columns have high-confidence suggestions
    required_roles = {"case_id", "activity", "timestamp"}
    for role in required_roles:
        if role not in suggestions:
            requires_user_input = True
            break
        if suggestions[role]["confidence"] < confidence_threshold:
            requires_user_input = True
            break

    return ColumnDetectionResponse(
        dataset_id=dataset_id,
        status=dataset.status,
        columns=column_infos,
        suggestions=suggestions,
        requires_user_input=requires_user_input,
    )


@router.post(
    "/{dataset_id}/mapping",
    summary="Submit Column Mapping",
    description="""
Submit column mapping for the dataset.

Required mappings:
- case_id_column: Column containing case/trace identifiers
- activity_column: Column containing activity names
- timestamp_column: Column containing event timestamps

Optional mappings:
- resource_column: Column containing performer/resource
- timestamp_format: Timestamp format string (auto-detected if not provided)
    """,
    responses={
        200: {"description": "Mapping saved, status → MAPPED"},
        400: {"description": "Invalid mapping (column not found)"},
        404: {"description": "Dataset not found"},
    },
)
async def submit_mapping(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
    request: MappingUpdateRequest,
) -> dict:
    """Submit and validate column mapping."""
    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_UPDATE)

    # Check status
    valid_statuses = [DatasetStatus.AWAITING_MAPPING.value, DatasetStatus.ERROR.value]
    if dataset.status not in valid_statuses:
        raise ValidationError(
            f"Dataset must be in AWAITING_MAPPING or ERROR state. Current: {dataset.status}"
        )

    # Get column names to validate mapping
    result = await db.execute(
        select(DatasetColumn.name).where(DatasetColumn.dataset_id == dataset_id)
    )
    valid_columns = {row[0] for row in result.all()}

    # Validate required columns exist
    errors = []
    for col_name, col_field in [
        (request.case_id_column, "case_id_column"),
        (request.activity_column, "activity_column"),
        (request.timestamp_column, "timestamp_column"),
    ]:
        if col_name not in valid_columns:
            errors.append(f"{col_field}: Column '{col_name}' not found in dataset")

    if request.resource_column and request.resource_column not in valid_columns:
        errors.append(f"resource_column: Column '{request.resource_column}' not found")

    if errors:
        raise ValidationError("; ".join(errors))

    # Create or update mapping
    existing_mapping = await db.execute(
        select(DatasetColumnMapping).where(DatasetColumnMapping.dataset_id == dataset_id)
    )
    mapping = existing_mapping.scalar_one_or_none()

    if mapping:
        # Update existing
        mapping.case_id_column = request.case_id_column
        mapping.activity_column = request.activity_column
        mapping.timestamp_column = request.timestamp_column
        mapping.resource_column = request.resource_column
        mapping.timestamp_format = request.timestamp_format
        mapping.additional_columns_json = json.dumps(request.additional_columns)
        mapping.auto_mapped = False
        mapping.updated_at = datetime.now(timezone.utc)
    else:
        # Create new
        mapping = DatasetColumnMapping(
            dataset_id=dataset_id,
            case_id_column=request.case_id_column,
            activity_column=request.activity_column,
            timestamp_column=request.timestamp_column,
            resource_column=request.resource_column,
            timestamp_format=request.timestamp_format,
            additional_columns_json=json.dumps(request.additional_columns),
            auto_mapped=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(mapping)

    # Update dataset status
    dataset.status = DatasetStatus.MAPPED.value
    dataset.error_message = None

    # Also store in legacy mapping_json for backward compatibility
    dataset.mapping_json = json.dumps(
        {
            "case_id_column": request.case_id_column,
            "activity_column": request.activity_column,
            "timestamp_column": request.timestamp_column,
            "resource_column": request.resource_column,
            "timestamp_format": request.timestamp_format,
            "additional_columns": request.additional_columns,
        }
    )

    await db.commit()

    logger.info(
        "mapping_submitted",
        dataset_id=dataset_id,
        case_id=request.case_id_column,
        activity=request.activity_column,
        timestamp=request.timestamp_column,
    )

    return {
        "status": "MAPPED",
        "dataset_id": dataset_id,
        "message": "Column mapping saved. Ready for ingestion.",
    }


# =============================================================================
# Additional Mapping Endpoints (per API spec)
# =============================================================================


@router.get(
    "/{dataset_id}/mapping",
    response_model=MappingResponse,
    summary="Get Current Mapping",
    description="Get the current column mapping for a dataset.",
    responses={
        200: {"description": "Current mapping"},
        404: {"description": "Dataset or mapping not found"},
    },
)
async def get_mapping(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> MappingResponse:
    """Get current column mapping."""
    from src.platform.core.exceptions import NotFoundError

    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Get mapping
    result = await db.execute(
        select(DatasetColumnMapping).where(DatasetColumnMapping.dataset_id == dataset_id)
    )
    mapping = result.scalar_one_or_none()

    if not mapping:
        # Try to get from legacy mapping_json
        if dataset.mapping_json:
            try:
                data = json.loads(dataset.mapping_json)
                return MappingResponse(
                    dataset_id=dataset_id,
                    case_id_column=data.get("case_id_column", ""),
                    activity_column=data.get("activity_column", ""),
                    timestamp_column=data.get("timestamp_column", ""),
                    resource_column=data.get("resource_column"),
                    timestamp_format=data.get("timestamp_format"),
                )
            except Exception:
                pass
        raise NotFoundError("Mapping", dataset_id)

    return MappingResponse(
        dataset_id=dataset_id,
        case_id_column=mapping.case_id_column,
        activity_column=mapping.activity_column,
        timestamp_column=mapping.timestamp_column,
        resource_column=mapping.resource_column,
        timestamp_format=mapping.timestamp_format,
        auto_mapped=mapping.auto_mapped or False,
        created_at=mapping.created_at,
        updated_at=mapping.updated_at,
    )


@router.put(
    "/{dataset_id}/mapping",
    response_model=MappingResponse,
    summary="Update Mapping",
    description="Update the column mapping for a dataset.",
    responses={
        200: {"description": "Mapping updated"},
        400: {"description": "Invalid mapping"},
        404: {"description": "Dataset not found"},
    },
)
async def update_mapping(
    request: MappingUpdateRequest,
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
) -> MappingResponse:
    """Update existing column mapping."""
    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_UPDATE)

    # Get column names to validate mapping
    result = await db.execute(
        select(DatasetColumn.name).where(DatasetColumn.dataset_id == dataset_id)
    )
    valid_columns = {row[0] for row in result.all()}

    # Validate required columns exist
    errors = []
    for col_name, col_field in [
        (request.case_id_column, "case_id_column"),
        (request.activity_column, "activity_column"),
        (request.timestamp_column, "timestamp_column"),
    ]:
        if col_name not in valid_columns:
            errors.append(f"{col_field}: Column '{col_name}' not found in dataset")

    if request.resource_column and request.resource_column not in valid_columns:
        errors.append(f"resource_column: Column '{request.resource_column}' not found")

    if errors:
        raise ValidationError("; ".join(errors))

    # Get or create mapping
    existing_mapping = await db.execute(
        select(DatasetColumnMapping).where(DatasetColumnMapping.dataset_id == dataset_id)
    )
    mapping = existing_mapping.scalar_one_or_none()

    if mapping:
        mapping.case_id_column = request.case_id_column
        mapping.activity_column = request.activity_column
        mapping.timestamp_column = request.timestamp_column
        mapping.resource_column = request.resource_column
        mapping.timestamp_format = request.timestamp_format
        mapping.auto_mapped = False
        mapping.updated_at = datetime.utcnow()
    else:
        mapping = DatasetColumnMapping(
            dataset_id=dataset_id,
            case_id_column=request.case_id_column,
            activity_column=request.activity_column,
            timestamp_column=request.timestamp_column,
            resource_column=request.resource_column,
            timestamp_format=request.timestamp_format,
            auto_mapped=False,
        )
        db.add(mapping)

    # Update dataset status if needed
    if dataset.status == DatasetStatus.AWAITING_MAPPING.value:
        dataset.status = DatasetStatus.MAPPED.value

    # Update legacy mapping_json
    dataset.mapping_json = json.dumps(
        {
            "case_id_column": request.case_id_column,
            "activity_column": request.activity_column,
            "timestamp_column": request.timestamp_column,
            "resource_column": request.resource_column,
            "timestamp_format": request.timestamp_format,
        }
    )

    await db.commit()

    logger.info("mapping_updated", dataset_id=dataset_id, user_id=user.id)

    return MappingResponse(
        dataset_id=dataset_id,
        case_id_column=mapping.case_id_column,
        activity_column=mapping.activity_column,
        timestamp_column=mapping.timestamp_column,
        resource_column=mapping.resource_column,
        timestamp_format=mapping.timestamp_format,
        auto_mapped=False,
        updated_at=datetime.now(timezone.utc),
    )


@router.post(
    "/{dataset_id}/preview",
    response_model=PreviewResponse,
    summary="Preview Mapped Data",
    description="""
Preview how data will look after applying the mapping.

Returns a sample of events with the mapping applied.
Useful for verifying column selections before ingestion.
    """,
    responses={
        200: {"description": "Preview generated"},
        400: {"description": "No mapping found"},
        404: {"description": "Dataset not found"},
    },
)
async def preview_mapped_data(
    db: ReadDBSession,
    dataset_id: str,
    user: CurrentUser,
    limit: int = Query(10, ge=1, le=100, description="Number of sample rows"),
) -> PreviewResponse:
    """Preview mapped data before ingestion."""
    import csv
    import io

    from src.platform.core.exceptions import NotFoundError
    from src.platform.infrastructure.object_storage import get_storage_client

    # Verify permission
    _, dataset = await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)

    # Get mapping
    mapping_result = await db.execute(
        select(DatasetColumnMapping).where(DatasetColumnMapping.dataset_id == dataset_id)
    )
    mapping = mapping_result.scalar_one_or_none()

    if not mapping and not dataset.mapping_json:
        raise NotFoundError("Mapping", dataset_id)

    # Get mapping data
    if mapping:
        case_col = mapping.case_id_column
        activity_col = mapping.activity_column
        timestamp_col = mapping.timestamp_column
        resource_col = mapping.resource_column
    else:
        data = json.loads(dataset.mapping_json)
        case_col = data.get("case_id_column")
        activity_col = data.get("activity_column")
        timestamp_col = data.get("timestamp_column")
        resource_col = data.get("resource_column")

    # Try to read sample from file
    sample_events = []
    parse_errors = []
    total_rows = 0

    if dataset.storage_key:
        try:
            storage_client = get_storage_client()
            content = await run_in_threadpool(
                storage_client.download_file, bucket_type="raw", key=dataset.storage_key
            )

            # Parse CSV
            text_content = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text_content))

            for i, row in enumerate(reader):
                total_rows += 1
                if i < limit:
                    try:
                        event = {
                            "case_id": row.get(case_col, ""),
                            "activity": row.get(activity_col, ""),
                            "timestamp": row.get(timestamp_col, ""),
                        }
                        if resource_col:
                            event["resource"] = row.get(resource_col, "")
                        sample_events.append(event)
                    except Exception as e:
                        parse_errors.append(f"Row {i + 1}: {e!s}")
        except Exception as e:
            logger.warning("preview_failed", dataset_id=dataset_id, error=str(e))
            parse_errors.append(f"Failed to read file: {e!s}")

    return PreviewResponse(
        dataset_id=dataset_id,
        sample_events=sample_events,
        total_rows=total_rows,
        parse_errors=parse_errors,
    )
