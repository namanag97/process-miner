"""Repository Pattern - Abstract data access interfaces.

Repositories provide a clean interface for loading and persisting aggregates.
These are pure interfaces that belong in the domain layer.

Implementations (SQLAlchemy, etc.) belong in the infrastructure layer.
"""

from abc import ABC, abstractmethod

from src.domain.entities import DatasetAggregate

# =============================================================================
# Repository Interfaces (Domain Layer - Pure Abstractions)
# =============================================================================


class DatasetRepository(ABC):
    """Abstract repository for Dataset aggregates."""

    @abstractmethod
    async def get(self, dataset_id: str) -> DatasetAggregate | None:
        """Load an aggregate by ID.

        Returns None if not found.
        """

    @abstractmethod
    async def get_many(self, dataset_ids: list[str]) -> list[DatasetAggregate]:
        """Load multiple aggregates by ID."""

    @abstractmethod
    async def save(self, aggregate: DatasetAggregate) -> None:
        """Persist an aggregate and its cases/events."""

    @abstractmethod
    async def delete(self, dataset_id: str) -> bool:
        """Delete an aggregate. Returns True if deleted."""

    @abstractmethod
    async def exists(self, dataset_id: str) -> bool:
        """Check if an aggregate exists."""


class ProcessModelRepository(ABC):
    """Abstract repository for ProcessModel aggregates."""

    @abstractmethod
    async def get(self, model_id: str) -> dict | None:
        """Load a model by ID."""

    @abstractmethod
    async def get_by_dataset(self, dataset_id: str) -> list[dict]:
        """Get all models for a dataset."""

    @abstractmethod
    async def save(self, model: dict) -> None:
        """Persist a model."""

    @abstractmethod
    async def delete(self, model_id: str) -> bool:
        """Delete a model."""
