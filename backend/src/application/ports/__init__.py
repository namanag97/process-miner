"""Port interfaces for application layer.

These abstract interfaces define contracts that infrastructure must implement,
enabling the application layer to remain independent of infrastructure details.
This follows the Ports & Adapters (Hexagonal) architecture pattern.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, BinaryIO, Callable, Dict, List, Optional
from uuid import UUID

from src.domain.events import DomainEvent

# =============================================================================
# File Storage Port
# =============================================================================


class FileStoragePort(ABC):
    """Abstract interface for file storage operations."""

    @abstractmethod
    async def upload_log(
        self,
        file: BinaryIO,
        filename: str,
        log_id: Optional[UUID] = None,
    ) -> str:
        """Upload an event log file. Returns the stored file path."""
        ...

    @abstractmethod
    async def upload_log_bytes(
        self,
        content: bytes,
        filename: str,
        log_id: Optional[UUID] = None,
    ) -> str:
        """Upload event log from bytes."""
        ...

    @abstractmethod
    async def get_log_path(self, log_id: UUID, extension: str = ".csv") -> Optional[Path]:
        """Get the path to a stored log file."""
        ...

    @abstractmethod
    async def read_log(self, log_id: UUID, extension: str = ".csv") -> Optional[bytes]:
        """Read a stored log file."""
        ...

    @abstractmethod
    async def delete_log(self, log_id: UUID) -> bool:
        """Delete a stored log file."""
        ...

    @abstractmethod
    async def save_model(self, model_id: UUID, data: bytes, format: str) -> str:
        """Save a process model to file storage."""
        ...

    @abstractmethod
    async def get_model(self, model_id: UUID, format: str) -> Optional[bytes]:
        """Read a stored process model."""
        ...

    @abstractmethod
    async def save_export(self, export_id: UUID, data: bytes, filename: str) -> str:
        """Save an export file."""
        ...

    @abstractmethod
    async def get_export(self, export_id: UUID, extension: str = ".png") -> Optional[bytes]:
        """Read an export file."""
        ...


# =============================================================================
# Event Bus Port
# =============================================================================


class EventBusPort(ABC):
    """Abstract interface for domain event publishing/subscribing."""

    @abstractmethod
    def subscribe(self, topic: str, handler: Callable) -> None:
        """Subscribe a handler to a topic."""
        ...

    @abstractmethod
    def unsubscribe(self, topic: str, handler: Callable) -> None:
        """Unsubscribe a handler from a topic."""
        ...

    @abstractmethod
    async def publish(self, event: DomainEvent, topic: Optional[str] = None) -> None:
        """Publish a domain event to a topic."""
        ...

    @abstractmethod
    async def publish_all(self, events: List[DomainEvent]) -> None:
        """Publish multiple events."""
        ...


# =============================================================================
# Task Queue Port
# =============================================================================


class TaskQueuePort(ABC):
    """Abstract interface for background task queue."""

    @abstractmethod
    def register_handler(self, job_type: str, handler: Callable) -> None:
        """Register a handler for a job type."""
        ...

    @abstractmethod
    async def enqueue(self, job_type: str, payload: Dict[str, Any]) -> UUID:
        """Add a job to the queue. Returns job ID."""
        ...

    @abstractmethod
    def get_job(self, job_id: UUID) -> Optional[Any]:
        """Get job status by ID."""
        ...

    @abstractmethod
    async def start(self) -> None:
        """Start the background worker."""
        ...

    @abstractmethod
    async def stop(self) -> None:
        """Stop the background worker."""
        ...
