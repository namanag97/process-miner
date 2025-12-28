"""Local file storage service (S3-compatible interface)."""

from pathlib import Path
from typing import Optional, BinaryIO
from uuid import UUID, uuid4
import aiofiles
import aiofiles.os
import shutil

from src.config import get_settings


class FileStorage:
    """
    Local file storage with S3-like interface.
    Stores files in organized directories by type.
    """
    
    def __init__(self):
        self.settings = get_settings()
    
    async def upload_log(
        self,
        file: BinaryIO,
        filename: str,
        log_id: Optional[UUID] = None,
    ) -> str:
        """
        Upload an event log file.
        Returns the stored file path.
        """
        log_id = log_id or uuid4()
        extension = Path(filename).suffix.lower()
        stored_filename = f"{log_id}{extension}"
        file_path = self.settings.upload_dir / stored_filename
        
        # Ensure directory exists
        await aiofiles.os.makedirs(self.settings.upload_dir, exist_ok=True)
        
        # Write file
        async with aiofiles.open(file_path, "wb") as f:
            content = file.read()
            await f.write(content)
        
        return str(file_path)
    
    async def upload_log_bytes(
        self,
        content: bytes,
        filename: str,
        log_id: Optional[UUID] = None,
    ) -> str:
        """Upload event log from bytes."""
        log_id = log_id or uuid4()
        extension = Path(filename).suffix.lower()
        stored_filename = f"{log_id}{extension}"
        file_path = self.settings.upload_dir / stored_filename
        
        await aiofiles.os.makedirs(self.settings.upload_dir, exist_ok=True)
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)
        
        return str(file_path)
    
    async def get_log_path(self, log_id: UUID, extension: str = ".csv") -> Optional[Path]:
        """Get the path to a stored log file."""
        file_path = self.settings.upload_dir / f"{log_id}{extension}"
        if await aiofiles.os.path.exists(file_path):
            return file_path
        
        # Try other common extensions
        for ext in [".csv", ".xes", ".parquet"]:
            file_path = self.settings.upload_dir / f"{log_id}{ext}"
            if await aiofiles.os.path.exists(file_path):
                return file_path
        
        return None
    
    async def read_log(self, log_id: UUID, extension: str = ".csv") -> Optional[bytes]:
        """Read a stored log file."""
        file_path = await self.get_log_path(log_id, extension)
        if not file_path:
            return None
        
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()
    
    async def delete_log(self, log_id: UUID) -> bool:
        """Delete a stored log file."""
        for ext in [".csv", ".xes", ".parquet"]:
            file_path = self.settings.upload_dir / f"{log_id}{ext}"
            if await aiofiles.os.path.exists(file_path):
                await aiofiles.os.remove(file_path)
                return True
        return False
    
    async def save_model(
        self,
        model_id: UUID,
        data: bytes,
        format: str,
    ) -> str:
        """Save a process model to file storage."""
        extension = self._get_model_extension(format)
        filename = f"{model_id}{extension}"
        file_path = self.settings.models_dir / filename
        
        await aiofiles.os.makedirs(self.settings.models_dir, exist_ok=True)
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)
        
        return str(file_path)
    
    async def get_model(self, model_id: UUID, format: str) -> Optional[bytes]:
        """Read a stored process model."""
        extension = self._get_model_extension(format)
        file_path = self.settings.models_dir / f"{model_id}{extension}"
        
        if not await aiofiles.os.path.exists(file_path):
            return None
        
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()
    
    async def save_export(
        self,
        export_id: UUID,
        data: bytes,
        filename: str,
    ) -> str:
        """Save an export file."""
        extension = Path(filename).suffix.lower()
        stored_filename = f"{export_id}{extension}"
        file_path = self.settings.exports_dir / stored_filename
        
        await aiofiles.os.makedirs(self.settings.exports_dir, exist_ok=True)
        
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)
        
        return str(file_path)
    
    async def get_export(self, export_id: UUID, extension: str = ".png") -> Optional[bytes]:
        """Read an export file."""
        file_path = self.settings.exports_dir / f"{export_id}{extension}"
        
        if not await aiofiles.os.path.exists(file_path):
            return None
        
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()
    
    def _get_model_extension(self, format: str) -> str:
        """Get file extension for model format."""
        extensions = {
            "petri_net": ".pnml",
            "bpmn": ".bpmn",
            "process_tree": ".ptml",
            "dfg": ".json",
        }
        return extensions.get(format, ".pnml")


# Singleton instance
file_storage = FileStorage()
