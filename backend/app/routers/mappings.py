"""
Mappings router - Handles column mapping and validation.

After file upload, users map their columns to process mining fields:
- Case ID (required)
- Activity (required)
- Timestamp (required)
- Resource (optional)
- Cost (optional)

This router validates mappings and stores them for processing.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from fastapi import APIRouter, HTTPException

from ..models.schemas import (
    MappingCreate,
    MappingResponse,
    ValidationResult,
)
from ..services import parse_file, validate_mapping
from .uploads import get_upload_info

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/mappings", tags=["mappings"])

# In-memory storage for MVP
mappings_store: dict[str, dict] = {}


@router.post("/uploads/{upload_id}/mappings", response_model=MappingResponse)
async def create_mapping(upload_id: str, mapping: MappingCreate):
    """
    Create a column mapping for an upload.
    
    Maps user's column names to standard process mining fields.
    Validates that columns exist and have appropriate data.
    """
    # Get upload info
    upload_info = get_upload_info(upload_id)
    if not upload_info:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Get column names from upload
    column_names = [c["name"] for c in upload_info["columns"]]
    
    # Validate columns exist
    required = {
        "case_id": mapping.case_id_column,
        "activity": mapping.activity_column,
        "timestamp": mapping.timestamp_column,
    }
    
    for field, col_name in required.items():
        if col_name not in column_names:
            raise HTTPException(
                status_code=400,
                detail=f"Column '{col_name}' not found for {field}"
            )
    
    # Optional columns
    if mapping.resource_column and mapping.resource_column not in column_names:
        raise HTTPException(
            status_code=400,
            detail=f"Resource column '{mapping.resource_column}' not found"
        )
    
    if mapping.cost_column and mapping.cost_column not in column_names:
        raise HTTPException(
            status_code=400,
            detail=f"Cost column '{mapping.cost_column}' not found"
        )
    
    # Generate mapping ID
    import uuid
    mapping_id = str(uuid.uuid4())
    
    # Store mapping
    mapping_data = {
        "mapping_id": mapping_id,
        "upload_id": upload_id,
        "case_id_column": mapping.case_id_column,
        "activity_column": mapping.activity_column,
        "timestamp_column": mapping.timestamp_column,
        "timestamp_format": mapping.timestamp_format,
        "resource_column": mapping.resource_column,
        "cost_column": mapping.cost_column,
        "created_at": datetime.now(timezone.utc),
    }
    mappings_store[mapping_id] = mapping_data
    
    logger.info(f"Created mapping {mapping_id} for upload {upload_id}")
    
    return MappingResponse(**mapping_data)


@router.get("/{mapping_id}", response_model=MappingResponse)
async def get_mapping(mapping_id: str):
    """Get mapping details by ID."""
    if mapping_id not in mappings_store:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    return MappingResponse(**mappings_store[mapping_id])


@router.post("/{mapping_id}/validate", response_model=ValidationResult)
async def validate_mapping_endpoint(mapping_id: str):
    """
    Validate a mapping against the actual data.
    
    Checks:
    - No null values in required columns
    - Timestamps are parseable
    - Case ID has reasonable cardinality
    - Activity count is reasonable
    
    Returns errors, warnings, and statistics.
    """
    if mapping_id not in mappings_store:
        raise HTTPException(status_code=404, detail="Mapping not found")
    
    mapping_data = mappings_store[mapping_id]
    upload_info = get_upload_info(mapping_data["upload_id"])
    
    if not upload_info:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Load data
    file_path = Path(upload_info["file_path"])
    df = parse_file(file_path, max_rows=10000)
    
    # Create mapping object
    mapping = MappingCreate(
        case_id_column=mapping_data["case_id_column"],
        activity_column=mapping_data["activity_column"],
        timestamp_column=mapping_data["timestamp_column"],
        timestamp_format=mapping_data.get("timestamp_format"),
        resource_column=mapping_data.get("resource_column"),
        cost_column=mapping_data.get("cost_column"),
    )
    
    # Run validation
    result = validate_mapping(df, mapping)
    
    logger.info(f"Validation result for {mapping_id}: valid={result.is_valid}")
    
    return result


# Export for use by other routers
def get_mapping_info(mapping_id: str) -> dict | None:
    """Get mapping info for internal use."""
    return mappings_store.get(mapping_id)
