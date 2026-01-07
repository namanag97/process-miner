"""Local file storage service for OCEL data.

BUG-077 FIX: Instead of storing large OCEL blobs (up to 100MB) directly
in the database, store them in the local filesystem and keep a reference.
"""

import hashlib
import os
from pathlib import Path

from src.platform.core.config import get_settings
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class LocalOCELStorage:
    """Local filesystem storage for OCEL data."""

    def __init__(self):
        """Initialize storage directory."""
        # Use data directory for storage
        self.storage_dir = Path(settings.upload_dir) / "ocel_storage"
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        logger.info("ocel_storage_initialized", path=str(self.storage_dir))

    def _get_file_path(self, file_key: str) -> Path:
        """Get full path for a file key.
        
        Args:
            file_key: Unique identifier for the file
            
        Returns:
            Full path to file
        """
        # Use first 2 chars of key as subdirectory to avoid too many files in one dir
        subdir = self.storage_dir / file_key[:2]
        subdir.mkdir(exist_ok=True)
        return subdir / file_key

    def generate_key(self, content: bytes, dataset_id: str) -> str:
        """Generate a unique storage key for content.
        
        Args:
            content: File content
            dataset_id: Dataset ID for additional uniqueness
            
        Returns:
            Unique storage key
        """
        # Use SHA256 hash of content + dataset_id for deduplication
        hasher = hashlib.sha256()
        hasher.update(content)
        hasher.update(dataset_id.encode())
        return hasher.hexdigest()

    def store(self, content: bytes, dataset_id: str) -> str:
        """Store OCEL data and return storage key.
        
        Args:
            content: OCEL file content
            dataset_id: Associated dataset ID
            
        Returns:
            Storage key that can be used to retrieve the data
        """
        file_key = self.generate_key(content, dataset_id)
        file_path = self._get_file_path(file_key)

        # Write file if it doesn't exist (deduplication)
        if not file_path.exists():
            file_path.write_bytes(content)
            logger.info(
                "ocel_data_stored",
                key=file_key,
                size_bytes=len(content),
                path=str(file_path),
            )
        else:
            logger.debug("ocel_data_already_exists", key=file_key)

        return file_key

    def retrieve(self, file_key: str) -> bytes:
        """Retrieve OCEL data by storage key.
        
        Args:
            file_key: Storage key from store()
            
        Returns:
            OCEL file content
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        file_path = self._get_file_path(file_key)
        
        if not file_path.exists():
            logger.error("ocel_data_not_found", key=file_key, path=str(file_path))
            raise FileNotFoundError(f"OCEL data not found for key: {file_key}")

        content = file_path.read_bytes()
        logger.debug("ocel_data_retrieved", key=file_key, size_bytes=len(content))
        return content

    def delete(self, file_key: str) -> bool:
        """Delete OCEL data by storage key.
        
        Args:
            file_key: Storage key from store()
            
        Returns:
            True if deleted, False if didn't exist
        """
        file_path = self._get_file_path(file_key)

        if file_path.exists():
            file_path.unlink()
            logger.info("ocel_data_deleted", key=file_key)
            return True
        
        return False

    def exists(self,file_key: str) -> bool:
        """Check if OCEL data exists.
        
        Args:
            file_key: Storage key from store()
            
        Returns:
            True if exists
        """
        return self._get_file_path(file_key).exists()


# Singleton instance
ocel_storage = LocalOCELStorage()
