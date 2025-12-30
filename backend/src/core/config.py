"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "Process Mining API"
    app_version: str = "1.0.0"
    debug: bool = True

    # API
    api_prefix: str = "/api/v1"
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:4200",
        "http://localhost:5173",
        "http://localhost:8080",
        "http://127.0.0.1:4200",
        "*",  # Allow all origins in development
    ]

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/db/process_mining.db"

    # File Storage
    upload_dir: Path = Path("./data/uploads")
    models_dir: Path = Path("./data/models")

    # Auth (disabled by default for development)
    auth_enabled: bool = False
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60 * 24

    # Logging
    log_level: str = "DEBUG"  # DEBUG, INFO, WARNING, ERROR
    log_json: bool = False  # Force JSON output even in dev

    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Celery Configuration
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"

    # Cache Configuration
    cache_enabled: bool = True
    cache_default_ttl: int = 3600  # 1 hour

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        Path("./data/db").mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    return settings
