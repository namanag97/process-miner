"""Mapping Router - Column detection and mapping endpoints.

Handles column detection suggestions and user-provided mappings.
Part of 4-Phase Upload Architecture: Upload → Validate → Map → Ingest
"""

import json
from datetime import datetime

from fastapi import APIRouter, Query
from sqlalchemy import select

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.models import (
    Dataset,
    DatasetColumn,
    DatasetColumnMapping,
    DatasetStatus,
)
from src.features.process_mining.schemas import ColumnDetectionResponse, ColumnTypeInfo
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
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
) -> ColumnDetectionResponse:
    """Get detected columns with suggestions."""
    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_READ
    )

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
    db: DBSession,
    dataset_id: str,
    user: CurrentUser,
    case_id_column: str,
    activity_column: str,
    timestamp_column: str,
    resource_column: str | None = None,
    timestamp_format: str | None = None,
) -> dict:
    """Submit and validate column mapping."""
    # Verify permission
    _, dataset = await require_dataset_permission(
        db, dataset_id, user, Permission.DATASET_UPDATE
    )

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
        (case_id_column, "case_id_column"),
        (activity_column, "activity_column"),
        (timestamp_column, "timestamp_column"),
    ]:
        if col_name not in valid_columns:
            errors.append(f"{col_field}: Column '{col_name}' not found in dataset")

    if resource_column and resource_column not in valid_columns:
        errors.append(f"resource_column: Column '{resource_column}' not found")

    if errors:
        raise ValidationError("; ".join(errors))

    # Create or update mapping
    existing_mapping = await db.execute(
        select(DatasetColumnMapping).where(DatasetColumnMapping.dataset_id == dataset_id)
    )
    mapping = existing_mapping.scalar_one_or_none()

    if mapping:
        # Update existing
        mapping.case_id_column = case_id_column
        mapping.activity_column = activity_column
        mapping.timestamp_column = timestamp_column
        mapping.resource_column = resource_column
        mapping.timestamp_format = timestamp_format
        mapping.auto_mapped = False
        mapping.updated_at = datetime.utcnow()
    else:
        # Create new
        mapping = DatasetColumnMapping(
            dataset_id=dataset_id,
            case_id_column=case_id_column,
            activity_column=activity_column,
            timestamp_column=timestamp_column,
            resource_column=resource_column,
            timestamp_format=timestamp_format,
            auto_mapped=False,
        )
        db.add(mapping)

    # Update dataset status
    dataset.status = DatasetStatus.MAPPED.value
    dataset.error_message = None
    
    # Also store in legacy mapping_json for backward compatibility
    dataset.mapping_json = json.dumps({
        "case_id_column": case_id_column,
        "activity_column": activity_column,
        "timestamp_column": timestamp_column,
        "resource_column": resource_column,
        "timestamp_format": timestamp_format,
    })

    await db.commit()

    logger.info(
        "mapping_submitted",
        dataset_id=dataset_id,
        case_id=case_id_column,
        activity=activity_column,
        timestamp=timestamp_column,
    )

    return {
        "status": "MAPPED",
        "dataset_id": dataset_id,
        "message": "Column mapping saved. Ready for ingestion.",
    }
