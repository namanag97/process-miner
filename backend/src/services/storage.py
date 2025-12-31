"""Storage Service - Abstraction for file storage (local/S3/MinIO).

Provides unified interface for file operations that works with:
- Local filesystem (development)
- S3/MinIO (production) - future implementation

Usage:
    from src.services.storage import storage_service
    
    # Store a file
    path = await storage_service.store(content, "logs/abc123/data.csv")
    
    # Retrieve a file
    content = await storage_service.retrieve(path)
"""

import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from src.core.config import get_settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)


class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def store(self, content: bytes, path: str) -> str:
        """Store content at the given path. Returns the full storage path."""
        pass

    @abstractmethod
    async def retrieve(self, path: str) -> bytes:
        """Retrieve content from the given path."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> None:
        """Delete content at the given path."""
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if a file exists at the given path."""
        pass

    @abstractmethod
    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get a URL to access the file (presigned for S3, file:// for local)."""
        pass


class LocalStorageBackend(StorageBackend):
    """Local filesystem storage backend for development."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info("local_storage_initialized", base_dir=str(base_dir))

    def _resolve_path(self, path: str) -> Path:
        """Resolve relative path to absolute, preventing directory traversal."""
        # Normalize and remove any leading slashes
        clean_path = path.lstrip("/").lstrip("\\")
        resolved = (self.base_dir / clean_path).resolve()
        
        # Security: ensure resolved path is within base_dir
        if not str(resolved).startswith(str(self.base_dir.resolve())):
            raise ValueError(f"Path traversal detected: {path}")
        
        return resolved

    async def store(self, content: bytes, path: str) -> str:
        """Store content to local filesystem."""
        file_path = self._resolve_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_path.write_bytes(content)
        logger.debug("file_stored", path=str(file_path), size=len(content))
        
        return str(file_path)

    async def retrieve(self, path: str) -> bytes:
        """Retrieve content from local filesystem."""
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        return file_path.read_bytes()

    async def delete(self, path: str) -> None:
        """Delete file from local filesystem."""
        file_path = self._resolve_path(path)
        
        if file_path.exists():
            file_path.unlink()
            logger.debug("file_deleted", path=str(file_path))
            
            # Clean up empty parent directories
            parent = file_path.parent
            while parent != self.base_dir and not any(parent.iterdir()):
                parent.rmdir()
                parent = parent.parent

    async def exists(self, path: str) -> bool:
        """Check if file exists on local filesystem."""
        file_path = self._resolve_path(path)
        return file_path.exists()

    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        """Get file:// URL for local files."""
        file_path = self._resolve_path(path)
        return f"file://{file_path}"


class S3StorageBackend(StorageBackend):
    """S3/MinIO storage backend for production.
    
    TODO: Implement when needed for production deployment.
    """

    def __init__(self, bucket: str, endpoint_url: Optional[str] = None):
        self.bucket = bucket
        self.endpoint_url = endpoint_url
        # Future: Initialize boto3 client here
        logger.info("s3_storage_initialized", bucket=bucket, endpoint=endpoint_url)

    async def store(self, content: bytes, path: str) -> str:
        raise NotImplementedError("S3 storage not yet implemented")

    async def retrieve(self, path: str) -> bytes:
        raise NotImplementedError("S3 storage not yet implemented")

    async def delete(self, path: str) -> None:
        raise NotImplementedError("S3 storage not yet implemented")

    async def exists(self, path: str) -> bool:
        raise NotImplementedError("S3 storage not yet implemented")

    async def get_url(self, path: str, expires_in: int = 3600) -> str:
        raise NotImplementedError("S3 storage not yet implemented")


class StorageService:
    """High-level storage service with backend abstraction.
    
    Provides convenience methods for common storage patterns.
    """

    def __init__(self, backend: StorageBackend):
        self.backend = backend

    async def store_event_log_file(
        self,
        content: bytes,
        log_id: str,
        filename: str,
    ) -> str:
        """Store an uploaded event log file.
        
        Args:
            content: File content
            log_id: Event log ID (used as directory)
            filename: Original filename
            
        Returns:
            Storage path
        """
        path = f"{log_id}/{filename}"
        return await self.backend.store(content, path)

    async def retrieve_event_log_file(
        self,
        log_id: str,
        filename: str,
    ) -> bytes:
        """Retrieve an event log file."""
        path = f"{log_id}/{filename}"
        return await self.backend.retrieve(path)

    async def delete_event_log_files(self, log_id: str) -> None:
        """Delete all files for an event log.
        
        Note: For local backend, deletes the log directory.
        """
        # For local storage, we can walk the directory
        if isinstance(self.backend, LocalStorageBackend):
            log_dir = self.backend._resolve_path(log_id)
            if log_dir.exists() and log_dir.is_dir():
                import shutil
                shutil.rmtree(log_dir)
                logger.info("event_log_files_deleted", log_id=log_id)

    async def event_log_file_exists(
        self,
        log_id: str,
        filename: str,
    ) -> bool:
        """Check if an event log file exists."""
        path = f"{log_id}/{filename}"
        return await self.backend.exists(path)


def get_storage_service() -> StorageService:
    """Factory function to get configured storage service."""
    settings = get_settings()
    
    # Future: Check for S3 configuration
    # if settings.s3_bucket:
    #     backend = S3StorageBackend(settings.s3_bucket, settings.s3_endpoint)
    # else:
    backend = LocalStorageBackend(settings.upload_dir)
    
    return StorageService(backend)


# Singleton instance
storage_service = get_storage_service()
