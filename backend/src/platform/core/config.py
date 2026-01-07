"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings

# Security: Known insecure default secrets that must not be used in production
INSECURE_SECRETS = frozenset(
    {
        "dev-secret-change-in-production",
        "change_me",
        "secret",
        "changeme",
        "",
    }
)


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # Application
    app_name: str = "Process Mining API"
    app_version: str = "1.0.0"
    debug: bool = True
    environment: str = "development"  # development, staging, production

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

    # Object Storage (S3/MinIO/Local)
    storage_type: str = "s3"  # "s3" or "local"
    s3_endpoint_url: str | None = None  # None = AWS S3, set URL for MinIO
    s3_access_key_id: str = "minioadmin"
    s3_secret_access_key: str = "minioadmin"
    s3_region: str = "us-east-1"
    s3_bucket_raw: str = "pm-raw-dev"
    s3_bucket_models: str = "pm-models-dev"
    s3_bucket_cache: str = "pm-cache-dev"
    s3_presigned_url_expiry: int = 3600  # 1 hour
    s3_max_file_size_bytes: int = 5 * 1024 * 1024 * 1024  # 5 GB default

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def redis_url(self) -> str:
        """Construct Redis URL from components."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        Path("./data/db").mkdir(parents=True, exist_ok=True)

    def validate_production_settings(self) -> None:
        """Validate settings for production deployment.

        Raises:
            SystemExit: If insecure settings are detected in production mode.
        """
        if self.debug:
            return  # Skip validation in debug/development mode

        # Check for insecure JWT secret
        if self.jwt_secret in INSECURE_SECRETS:
            raise SystemExit(
                "FATAL: jwt_secret is set to an insecure default. "
                "Set the JWT_SECRET environment variable for production."
            )

        # Require minimum secret length when auth is enabled
        if self.auth_enabled and len(self.jwt_secret) < 32:
            raise SystemExit(
                "FATAL: jwt_secret must be at least 32 characters for production. "
                f"Current length: {len(self.jwt_secret)}"
            )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    settings = Settings()
    settings.ensure_directories()
    settings.validate_production_settings()
    return settings
