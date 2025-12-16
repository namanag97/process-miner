"""
Upload router - Handles file upload and column detection.

This is the first step in the process mining pipeline:
1. User uploads a CSV/Excel file
2. Backend detects columns, types, and sample values
3. Frontend displays this for column mapping
"""

import logging
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException

from ..models.schemas import UploadResponse, UploadInfo, ColumnMetadata
from ..services import storage_service, parse_file, detect_columns, get_row_count
from ..config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/uploads", tags=["uploads"])

# In-memory storage for MVP (would use database in production)
uploads_store: dict[str, dict] = {}


@router.post("", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload a CSV or Excel file for process mining.
    
    The file is saved to storage and analyzed to detect:
    - Column names
    - Column types (string, number, datetime, boolean)
    - Sample values
    - Null percentages
    - Unique counts
    
    Returns metadata needed for the column mapping step.
    """
    settings = get_settings()
    
    # Validate file type
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    filename = file.filename.lower()
    if not (filename.endswith(".csv") or filename.endswith(".xlsx") or filename.endswith(".xls")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload CSV or Excel file."
        )
    
    # Read file content
    content = await file.read()
    file_size = len(content)
    
    # Check file size
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
        )
    
    logger.info(f"Received file: {file.filename} ({file_size} bytes)")
    
    # Save to storage
    upload_id, file_path = storage_service.save_file(content, file.filename)
    
    try:
        # Parse file to detect columns (limit rows for performance)
        df = parse_file(file_path, max_rows=10000)
        
        # Detect column metadata
        columns = detect_columns(df)
        
        # Get full row count
        row_count = get_row_count(file_path)
        
        # Store metadata
        upload_info = {
            "upload_id": upload_id,
            "filename": file.filename,
            "file_path": str(file_path),
            "file_size_bytes": file_size,
            "row_count": row_count,
            "columns": [c.model_dump() for c in columns],
            "created_at": datetime.now(timezone.utc),
        }
        uploads_store[upload_id] = upload_info
        
        logger.info(f"Upload complete: {upload_id} - {row_count} rows, {len(columns)} columns")
        
        return UploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            file_size_bytes=file_size,
            row_count=row_count,
            columns=columns,
            created_at=upload_info["created_at"],
        )
        
    except Exception as e:
        # Clean up on error
        storage_service.delete_upload(upload_id)
        logger.error(f"Upload processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.get("/{upload_id}", response_model=UploadResponse)
async def get_upload(upload_id: str):
    """Get upload details by ID."""
    if upload_id not in uploads_store:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    info = uploads_store[upload_id]
    return UploadResponse(
        upload_id=info["upload_id"],
        filename=info["filename"],
        file_size_bytes=info["file_size_bytes"],
        row_count=info["row_count"],
        columns=[ColumnMetadata(**c) for c in info["columns"]],
        created_at=info["created_at"],
    )


@router.get("/{upload_id}/columns")
async def get_upload_columns(upload_id: str):
    """Get just the columns for an upload."""
    if upload_id not in uploads_store:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    return {
        "upload_id": upload_id,
        "columns": uploads_store[upload_id]["columns"],
    }


@router.delete("/{upload_id}")
async def delete_upload(upload_id: str):
    """Delete an upload and its files."""
    if upload_id not in uploads_store:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    storage_service.delete_upload(upload_id)
    del uploads_store[upload_id]
    
    return {"status": "deleted", "upload_id": upload_id}


# Export for use by other routers
def get_upload_info(upload_id: str) -> dict | None:
    """Get upload info for internal use."""
    return uploads_store.get(upload_id)
