"""Service Protocols - Structural Typing for Services.

Defines interfaces using Python Protocols for structural (duck) typing.
Any class implementing these methods is valid - no inheritance required.

Benefits:
- Maximum flexibility in implementations
- Easy mocking for tests
- Clear contracts without coupling
- Runtime type checking with @runtime_checkable

Usage:
    def process_data(service: Ingestable):
        # Works with any class that has an ingest() method
        return service.ingest(data, mapping)
"""

from datetime import datetime
from typing import Any, Protocol, runtime_checkable

from sqlalchemy.ext.asyncio import AsyncSession


# =============================================================================
# Data Ingestion Protocols
# =============================================================================


@runtime_checkable
class Ingestable(Protocol):
    """Protocol for services that can ingest data files."""
    
    async def ingest_file(
        self,
        session: AsyncSession,
        file_content: bytes,
        filename: str,
        name: str | None = None,
        case_id_col: str | None = None,
        activity_col: str | None = None,
        timestamp_col: str | None = None,
        resource_col: str | None = None,
    ) -> Any:
        """Ingest a file and create a dataset."""
        ...


@runtime_checkable
class ColumnDetectable(Protocol):
    """Protocol for services that can detect column types."""
    
    def detect_columns(
        self,
        file_content: bytes,
        delimiter: str = ",",
    ) -> dict[str, Any]:
        """Detect column types and suggest mappings."""
        ...


# =============================================================================
# Export Protocols
# =============================================================================


@runtime_checkable
class Exportable(Protocol):
    """Protocol for services that can export data."""
    
    async def export(
        self,
        session: AsyncSession,
        dataset_id: str,
        format: str,
    ) -> bytes:
        """Export dataset to specified format."""
        ...


# =============================================================================
# Analysis Protocols
# =============================================================================


@runtime_checkable
class Analyzable(Protocol):
    """Protocol for services that can analyze datasets."""
    
    async def analyze(
        self,
        session: AsyncSession,
        dataset_id: str,
        **options: Any,
    ) -> dict[str, Any]:
        """Run analysis on a dataset."""
        ...


@runtime_checkable
class Discoverable(Protocol):
    """Protocol for process discovery services."""
    
    async def discover_model(
        self,
        session: AsyncSession,
        dataset_id: str,
        algorithm: str = "inductive",
        **params: Any,
    ) -> Any:
        """Discover process model from event log."""
        ...


@runtime_checkable
class ConformanceCheckable(Protocol):
    """Protocol for conformance checking services."""
    
    async def check_conformance(
        self,
        session: AsyncSession,
        dataset_id: str,
        model_id: str,
        **options: Any,
    ) -> dict[str, Any]:
        """Check conformance between log and model."""
        ...


# =============================================================================
# Filtering Protocols
# =============================================================================


@runtime_checkable
class Filterable(Protocol):
    """Protocol for services that can filter event logs."""
    
    async def apply_filter(
        self,
        session: AsyncSession,
        dataset_id: str,
        filter_config: dict[str, Any],
    ) -> Any:
        """Apply filter to create filtered dataset."""
        ...


# =============================================================================
# Prediction Protocols
# =============================================================================


@runtime_checkable
class Predictable(Protocol):
    """Protocol for predictive analytics services."""
    
    async def predict(
        self,
        session: AsyncSession,
        dataset_id: str,
        prediction_type: str,
        **params: Any,
    ) -> dict[str, Any]:
        """Generate predictions for cases."""
        ...


# =============================================================================
# Storage Protocols
# =============================================================================


@runtime_checkable
class FileStorable(Protocol):
    """Protocol for file storage services."""
    
    async def store(self, key: str, content: bytes) -> str:
        """Store file and return storage path."""
        ...
    
    async def retrieve(self, key: str) -> bytes:
        """Retrieve file content by key."""
        ...
    
    async def delete(self, key: str) -> bool:
        """Delete file by key."""
        ...


@runtime_checkable
class PresignedUrlGenerator(Protocol):
    """Protocol for presigned URL generation."""
    
    async def generate_upload_url(
        self,
        key: str,
        content_type: str,
        expires_in: int = 3600,
    ) -> str:
        """Generate presigned upload URL."""
        ...
    
    async def generate_download_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        """Generate presigned download URL."""
        ...


# =============================================================================
# Job/Task Protocols
# =============================================================================


@runtime_checkable
class JobTrackable(Protocol):
    """Protocol for job tracking services."""
    
    async def create_job(
        self,
        session: AsyncSession,
        job_type: str,
        entity_type: str | None = None,
        entity_id: str | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> Any:
        """Create and track an async job."""
        ...
    
    async def update_progress(
        self,
        session: AsyncSession,
        job_id: str,
        progress: int,
        stage: str | None = None,
    ) -> None:
        """Update job progress."""
        ...
    
    async def complete_job(
        self,
        session: AsyncSession,
        job_id: str,
        result: dict[str, Any] | None = None,
    ) -> None:
        """Mark job as completed."""
        ...
    
    async def fail_job(
        self,
        session: AsyncSession,
        job_id: str,
        error: str,
    ) -> None:
        """Mark job as failed."""
        ...


# =============================================================================
# Repository Protocols
# =============================================================================


@runtime_checkable
class Repository(Protocol):
    """Generic repository protocol."""
    
    async def get_by_id(self, id: str) -> Any | None:
        """Get entity by ID."""
        ...
    
    async def save(self, entity: Any) -> Any:
        """Save (create or update) entity."""
        ...
    
    async def delete(self, id: str) -> bool:
        """Delete entity by ID."""
        ...
    
    async def exists(self, id: str) -> bool:
        """Check if entity exists."""
        ...


@runtime_checkable
class PaginatedRepository(Protocol):
    """Repository with pagination support."""
    
    async def list_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        **filters: Any,
    ) -> tuple[list[Any], int]:
        """List entities with pagination. Returns (items, total_count)."""
        ...
