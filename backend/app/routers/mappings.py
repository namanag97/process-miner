"""
Mappings router - Handles column mapping and validation.

After file upload, users map their columns to process mining fields:
- Case ID (required)
- Activity (required)  
- Timestamp (required)
- Resource (optional)
- Cost (optional)
"""

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import (
    Mapping,
    MappingCreate,
    MappingResponse,
    Upload,
    ColumnMetadata,
    ValidationResult,
)
from ..database import get_db
from ..services import parse_file, validate_mapping as validate_mapping_fn
from ..services.repository import BaseRepository
from ..core import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/mappings", tags=["mappings"])


async def get_mapping_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[Mapping]:
    """Dependency for Mapping repository."""
    return BaseRepository(Mapping, db)


async def get_upload_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[Upload]:
    """Dependency for Upload repository."""
    return BaseRepository(Upload, db)


@router.post("/uploads/{upload_id}/mappings", response_model=MappingResponse)
async def create_mapping(
    upload_id: str, 
    mapping: MappingCreate,
    db: AsyncSession = Depends(get_db),
    upload_repo: BaseRepository[Upload] = Depends(get_upload_repo),
):
    """
    Create a column mapping for an upload.
    Maps user's column names to standard process mining fields.
    """
    # Get upload
    upload = await upload_repo.get_or_404(upload_id)
    
    # Get column names from cached columns
    if not upload.columns_json:
        raise HTTPException(status_code=500, detail="Upload has no column metadata")
    
    columns = [ColumnMetadata(**c) for c in json.loads(upload.columns_json)]
    column_names = [c.name for c in columns]
    
    # Validate required columns exist
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
    
    # Validate optional columns
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
    
    # Create mapping
    new_mapping = Mapping(
        upload_id=upload_id,
        case_id_column=mapping.case_id_column,
        activity_column=mapping.activity_column,
        timestamp_column=mapping.timestamp_column,
        timestamp_format=mapping.timestamp_format,
        resource_column=mapping.resource_column,
        cost_column=mapping.cost_column,
    )
    
    db.add(new_mapping)
    await db.commit()
    await db.refresh(new_mapping)
    
    log.info("mapping_created", mapping_id=new_mapping.id, upload_id=upload_id)
    
    return MappingResponse(
        mapping_id=new_mapping.id,
        upload_id=new_mapping.upload_id,
        case_id_column=new_mapping.case_id_column,
        activity_column=new_mapping.activity_column,
        timestamp_column=new_mapping.timestamp_column,
        timestamp_format=new_mapping.timestamp_format,
        resource_column=new_mapping.resource_column,
        cost_column=new_mapping.cost_column,
        created_at=new_mapping.created_at,
    )


@router.get("/{mapping_id}", response_model=MappingResponse)
async def get_mapping(
    mapping_id: str,
    mapping_repo: BaseRepository[Mapping] = Depends(get_mapping_repo),
):
    """Get mapping details by ID."""
    mapping = await mapping_repo.get_or_404(mapping_id)
    
    return MappingResponse(
        mapping_id=mapping.id,
        upload_id=mapping.upload_id,
        case_id_column=mapping.case_id_column,
        activity_column=mapping.activity_column,
        timestamp_column=mapping.timestamp_column,
        timestamp_format=mapping.timestamp_format,
        resource_column=mapping.resource_column,
        cost_column=mapping.cost_column,
        created_at=mapping.created_at,
    )


@router.post("/{mapping_id}/validate", response_model=ValidationResult)
async def validate_mapping_endpoint(
    mapping_id: str,
    mapping_repo: BaseRepository[Mapping] = Depends(get_mapping_repo),
    upload_repo: BaseRepository[Upload] = Depends(get_upload_repo),
):
    """Validate a mapping against the actual data."""
    mapping = await mapping_repo.get_or_404(mapping_id)
    upload = await upload_repo.get_or_404(mapping.upload_id)
    
    # Load data
    file_path = Path(upload.file_path)
    df = parse_file(file_path, max_rows=10000)
    
    # Create MappingCreate for validation function
    mapping_for_validation = MappingCreate(
        case_id_column=mapping.case_id_column,
        activity_column=mapping.activity_column,
        timestamp_column=mapping.timestamp_column,
        timestamp_format=mapping.timestamp_format,
        resource_column=mapping.resource_column,
        cost_column=mapping.cost_column,
    )
    
    # Run validation
    result = validate_mapping_fn(df, mapping_for_validation)
    
    log.info(
        "mapping_validated",
        mapping_id=mapping_id,
        is_valid=result.is_valid,
        error_count=len(result.errors),
    )
    
    return result
