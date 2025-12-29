"""Application configuration management."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "Process Mining SaaS"
    app_version: str = "0.1.0"
    debug: bool = True

    # API
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:4200"]

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/db/process_mining.db"

    # File Storage
    upload_dir: Path = Path("./data/uploads")
    models_dir: Path = Path("./data/models")
    exports_dir: Path = Path("./data/exports")

    # Logging Configuration
    logs_dir: Path = Path("./data/logs")
    api_log_level: str = "INFO"
    log_request_body: bool = True
    log_response_body: bool = False

    # Auth (Mock)
    jwt_secret: str = "dev-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24  # 24 hours
    auth_enabled: bool = False  # Set to True to enable auth

    # Background Tasks
    max_workers: int = 4

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.exports_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        Path("./data/db").mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings
