"""
Uploads router - Handles file uploads for process mining.

Now uses:
- SQLModel unified models
- Structured logging
- Column metadata caching (no more re-parsing on GET)
"""

import json
from typing import Annotated

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Upload, UploadResponse, ColumnMetadata, User
from ..database import get_db
from ..services import storage_service, parse_file, detect_columns, get_row_count
from ..services.repository import BaseRepository
from ..config import get_settings
from ..core import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/uploads", tags=["uploads"])


async def get_upload_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[Upload]:
    """Dependency for Upload repository."""
    return BaseRepository(Upload, db)


async def get_user_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[User]:
    """Dependency for User repository."""
    return BaseRepository(User, db)


@router.post("", response_model=UploadResponse)
async def upload_file(
    x_user_id: Annotated[str | None, Header()] = None,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_repo: BaseRepository[User] = Depends(get_user_repo),
):
    """Upload a CSV or Excel file for process mining."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header required")

    # Verify user exists
    user = await user_repo.get(x_user_id)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid User ID")

    settings = get_settings()
    
    # Validate file
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
    
    if file_size > settings.max_file_size_bytes:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size is {settings.max_file_size_mb}MB"
        )
    
    log.info("file_received", filename=file.filename, size_bytes=file_size)
    
    # Save to storage
    upload_id, file_path = storage_service.save_file(content, file.filename)
    
    try:
        # Parse file to detect columns (limit rows for performance)
        # Use asyncio.to_thread to avoid blocking the event loop
        import asyncio
        df = await asyncio.to_thread(parse_file, file_path, max_rows=10000)
        columns = await asyncio.to_thread(detect_columns, df)
        row_count = await asyncio.to_thread(get_row_count, file_path)
        
        # Create upload with cached columns (KEY IMPROVEMENT!)
        new_upload = Upload(
            id=upload_id,
            user_id=x_user_id,
            filename=file.filename,
            file_path=str(file_path),
            file_size_bytes=file_size,
            row_count=row_count,
            status="uploaded",
            columns_json=json.dumps([c.model_dump() for c in columns]),  # Cache columns!
        )
        db.add(new_upload)
        await db.commit()
        
        log.info(
            "upload_complete",
            upload_id=upload_id,
            row_count=row_count,
            column_count=len(columns),
        )
        
        return UploadResponse(
            upload_id=upload_id,
            filename=file.filename,
            file_size_bytes=file_size,
            row_count=row_count,
            columns=columns,
            created_at=new_upload.created_at,
        )
        
    except Exception as e:
        storage_service.delete_upload(upload_id)
        log.error("upload_failed", upload_id=upload_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.get("/{upload_id}", response_model=UploadResponse)
async def get_upload(
    upload_id: str,
    x_user_id: Annotated[str | None, Header()] = None,
    upload_repo: BaseRepository[Upload] = Depends(get_upload_repo),
):
    """Get upload details by ID."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header required")

    upload = await upload_repo.get_or_404(upload_id)
    
    if upload.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Use cached columns instead of re-parsing! (KEY IMPROVEMENT!)
    columns = []
    if upload.columns_json:
        columns = [ColumnMetadata(**c) for c in json.loads(upload.columns_json)]

    return UploadResponse(
        upload_id=upload.id,
        filename=upload.filename,
        file_size_bytes=upload.file_size_bytes,
        row_count=upload.row_count,
        columns=columns,
        created_at=upload.created_at,
    )


@router.get("/{upload_id}/columns")
async def get_upload_columns(
    upload_id: str,
    x_user_id: Annotated[str | None, Header()] = None,
    upload_repo: BaseRepository[Upload] = Depends(get_upload_repo),
):
    """Get just the columns for an upload."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header required")

    upload = await upload_repo.get_or_404(upload_id)
    
    if upload.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Use cached columns
    columns = []
    if upload.columns_json:
        columns = json.loads(upload.columns_json)
    
    return {"upload_id": upload_id, "columns": columns}


@router.delete("/{upload_id}")
async def delete_upload(
    upload_id: str,
    x_user_id: Annotated[str | None, Header()] = None,
    db: AsyncSession = Depends(get_db),
    upload_repo: BaseRepository[Upload] = Depends(get_upload_repo),
):
    """Delete an upload and its files."""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-ID header required")

    upload = await upload_repo.get_or_404(upload_id)
    
    if upload.user_id != x_user_id:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    # Delete file from storage
    storage_service.delete_upload(upload_id)
    
    # Delete from DB
    await db.delete(upload)
    await db.commit()
    
    log.info("upload_deleted", upload_id=upload_id)
    
    return {"status": "deleted", "upload_id": upload_id}
