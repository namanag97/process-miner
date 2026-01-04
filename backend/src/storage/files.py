"""File storage operations."""

from src.core.config import get_settings


async def save_upload(
    content: bytes,
    filename: str,
    log_id: str,
) -> str:
    """Save uploaded file to storage."""
    settings = get_settings()
    log_dir = settings.upload_dir / log_id
    log_dir.mkdir(parents=True, exist_ok=True)

    file_path = log_dir / filename
    file_path.write_bytes(content)

    return str(file_path)


async def get_upload(
    log_id: str,
    filename: str,
) -> bytes | None:
    """Retrieve uploaded file from storage."""
    settings = get_settings()
    file_path = settings.upload_dir / log_id / filename

    if file_path.exists():
        return file_path.read_bytes()
    return None


async def delete_upload(log_id: str) -> bool:
    """Delete all files for an event log."""
    import shutil

    settings = get_settings()
    log_dir = settings.upload_dir / log_id

    if log_dir.exists():
        shutil.rmtree(log_dir)
        return True
    return False
