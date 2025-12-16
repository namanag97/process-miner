"""
Configuration management using Pydantic Settings.

Loads configuration from environment variables and .env file.
"""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False  # Default to False for production safety

    # CORS
    frontend_url: str = "http://localhost:3000"

    # Storage
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 100

    # Database
    database_url: str = "sqlite+aiosqlite:///./process_miner.db"

    # Optional: Redis for async job processing
    redis_url: str | None = None

    @property
    def upload_path(self) -> Path:
        """Get upload directory as Path, creating if needed."""
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def max_file_size_bytes(self) -> int:
        """Max file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Using lru_cache ensures settings are only loaded once.
    """
    return Settings()
