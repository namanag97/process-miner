"""
Storage Service - Handles file storage operations.

For MVP, uses local filesystem storage. Can be extended to S3/R2.
"""

import logging
import shutil
import uuid
from pathlib import Path

from ..config import get_settings

logger = logging.getLogger(__name__)


class StorageService:
    """
    Handles file storage operations.
    
    MVP implementation uses local filesystem.
    Can be extended to support S3/R2 for production.
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.upload_dir = self.settings.upload_path
    
    def save_file(self, file_content: bytes, filename: str) -> tuple[str, Path]:
        """
        Save uploaded file to storage.
        
        Args:
            file_content: File bytes
            filename: Original filename
            
        Returns:
            Tuple of (upload_id, file_path)
        """
        # Generate unique ID for this upload
        upload_id = str(uuid.uuid4())
        
        # Create subdirectory for this upload
        upload_path = self.upload_dir / upload_id
        upload_path.mkdir(parents=True, exist_ok=True)
        
        # Keep original filename
        file_path = upload_path / filename
        
        # Write file
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        logger.info(f"Saved file: {file_path} ({len(file_content)} bytes)")
        
        return upload_id, file_path
    
    def get_file_path(self, upload_id: str, filename: str) -> Path | None:
        """
        Get the path to a stored file.
        
        Args:
            upload_id: Upload ID
            filename: Original filename
            
        Returns:
            Path to file or None if not found
        """
        file_path = self.upload_dir / upload_id / filename
        
        if file_path.exists():
            return file_path
        
        # Try to find any file in the upload directory
        upload_path = self.upload_dir / upload_id
        if upload_path.exists():
            files = list(upload_path.glob("*"))
            if files:
                return files[0]
        
        return None
    
    def delete_upload(self, upload_id: str) -> bool:
        """
        Delete an upload and all its files.
        
        Args:
            upload_id: Upload ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        upload_path = self.upload_dir / upload_id
        
        if upload_path.exists():
            shutil.rmtree(upload_path)
            logger.info(f"Deleted upload: {upload_id}")
            return True
        
        return False
    
    def get_upload_size(self, upload_id: str) -> int:
        """
        Get total size of all files in an upload.
        
        Args:
            upload_id: Upload ID
            
        Returns:
            Total size in bytes
        """
        upload_path = self.upload_dir / upload_id
        
        if not upload_path.exists():
            return 0
        
        return sum(f.stat().st_size for f in upload_path.glob("*") if f.is_file())


# Singleton instance
storage_service = StorageService()
