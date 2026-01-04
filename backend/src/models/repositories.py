"""Repository pattern abstraction for data access.

Provides clean separation between domain logic and data access with:
- Generic repository interface
- SQLAlchemy implementation
- Unit of Work pattern for transactions

Usage:
    # Get repository from dependency injection
    repo = SQLAlchemyDatasetRepository(session)

    # Use repository methods
    dataset = await repo.get_by_id("...")
    await repo.save(dataset)
"""

from abc import ABC, abstractmethod
from typing import Optional, Protocol, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")
ID = TypeVar("ID")


# =============================================================================
# Generic Repository Interface
# =============================================================================


class Repository(Protocol[T, ID]):
    """Generic repository interface for aggregate roots."""

    async def get_by_id(self, id: ID) -> T | None:
        """Get an entity by its ID."""
        ...

    async def save(self, entity: T) -> T:
        """Save (create or update) an entity."""
        ...

    async def delete(self, id: ID) -> bool:
        """Delete an entity by its ID."""
        ...

    async def exists(self, id: ID) -> bool:
        """Check if an entity exists."""
        ...


class ReadOnlyRepository(Protocol[T, ID]):
    """Read-only repository interface for query-heavy operations."""

    async def get_by_id(self, id: ID) -> T | None: ...

    async def exists(self, id: ID) -> bool: ...

    async def count(self) -> int: ...


# =============================================================================
# Event Log Repository
# =============================================================================


class DatasetRepository(ABC):
    """Repository interface for Dataset aggregate root."""

    @abstractmethod
    async def get_by_id(self, dataset_id: str) -> Optional["Dataset"]:
        """Get dataset by ID with all cases loaded."""

    @abstractmethod
    async def get_by_id_lightweight(self, dataset_id: str) -> Optional["Dataset"]:
        """Get dataset by ID without loading cases (for metadata only)."""

    @abstractmethod
    async def save(self, dataset: "Dataset") -> "Dataset":
        """Save dataset (create or update)."""

    @abstractmethod
    async def delete(self, dataset_id: str) -> bool:
        """Delete dataset and all associated data."""

    @abstractmethod
    async def exists(self, dataset_id: str) -> bool:
        """Check if dataset exists."""

    @abstractmethod
    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        source_format: str | None = None,
    ) -> tuple[list["Dataset"], int]:
        """List datasets with pagination. Returns (datasets, total_count)."""

    @abstractmethod
    async def count(self) -> int:
        """Count total datasets."""


class SQLAlchemyDatasetRepository(DatasetRepository):
    """SQLAlchemy implementation of DatasetRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, dataset_id: str) -> Optional["Dataset"]:
        from src.models.orm import Dataset

        return await self._session.get(Dataset, dataset_id)

    async def get_by_id_lightweight(self, dataset_id: str) -> Optional["Dataset"]:
        from src.models.orm import Dataset

        # Use a query that doesn't eager load relationships
        stmt = select(Dataset).where(Dataset.id == dataset_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, dataset: "Dataset") -> "Dataset":
        self._session.add(dataset)
        await self._session.flush()
        await self._session.refresh(dataset)
        return dataset

    async def delete(self, dataset_id: str) -> bool:
        dataset = await self.get_by_id(dataset_id)
        if dataset:
            await self._session.delete(dataset)
            await self._session.flush()
            return True
        return False

    async def exists(self, dataset_id: str) -> bool:
        from src.models.orm import Dataset

        stmt = select(func.count()).where(Dataset.id == dataset_id)
        result = await self._session.execute(stmt)
        return result.scalar() > 0

    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        source_format: str | None = None,
    ) -> tuple[list["Dataset"], int]:
        from src.models.orm import Dataset

        # Count query
        count_stmt = select(func.count()).select_from(Dataset)
        if source_format:
            count_stmt = count_stmt.where(Dataset.source_format == source_format)

        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Data query
        stmt = select(Dataset).order_by(Dataset.created_at.desc())
        if source_format:
            stmt = stmt.where(Dataset.source_format == source_format)

        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(stmt)
        datasets = list(result.scalars().all())

        return datasets, total

    async def count(self) -> int:
        from src.models.orm import Dataset

        stmt = select(func.count()).select_from(Dataset)
        result = await self._session.execute(stmt)
        return result.scalar() or 0


# =============================================================================
# Project Repository
# =============================================================================


class ProjectRepository(ABC):
    """Repository interface for Project aggregate root."""

    @abstractmethod
    async def get_by_id(self, project_id: str) -> Optional["Project"]:
        pass

    @abstractmethod
    async def save(self, project: "Project") -> "Project":
        pass

    @abstractmethod
    async def delete(self, project_id: str) -> bool:
        pass

    @abstractmethod
    async def list_all(self, page: int = 1, page_size: int = 20) -> tuple[list["Project"], int]:
        pass


class SQLAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy implementation of ProjectRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, project_id: str) -> Optional["Project"]:
        from src.models.orm import Project

        return await self._session.get(Project, project_id)

    async def save(self, project: "Project") -> "Project":
        self._session.add(project)
        await self._session.flush()
        await self._session.refresh(project)
        return project

    async def delete(self, project_id: str) -> bool:
        project = await self.get_by_id(project_id)
        if project:
            await self._session.delete(project)
            await self._session.flush()
            return True
        return False

    async def list_all(self, page: int = 1, page_size: int = 20) -> tuple[list["Project"], int]:
        from src.models.orm import Project

        # Count
        count_stmt = select(func.count()).select_from(Project)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Data
        stmt = (
            select(Project)
            .order_by(Project.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(stmt)
        projects = list(result.scalars().all())

        return projects, total


# =============================================================================
# Process Model Repository
# =============================================================================


class ProcessModelRepository(ABC):
    """Repository interface for ProcessModel."""

    @abstractmethod
    async def get_by_id(self, model_id: str) -> Optional["ProcessModel"]:
        pass

    @abstractmethod
    async def save(self, model: "ProcessModel") -> "ProcessModel":
        pass

    @abstractmethod
    async def get_by_dataset_id(self, dataset_id: str) -> list["ProcessModel"]:
        """Get all models for a given dataset."""


class SQLAlchemyProcessModelRepository(ProcessModelRepository):
    """SQLAlchemy implementation."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, model_id: str) -> Optional["ProcessModel"]:
        from src.models.orm import ProcessModel

        return await self._session.get(ProcessModel, model_id)

    async def save(self, model: "ProcessModel") -> "ProcessModel":
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return model

    async def get_by_dataset_id(self, dataset_id: str) -> list["ProcessModel"]:
        from src.models.orm import ProcessModel

        stmt = (
            select(ProcessModel)
            .where(ProcessModel.dataset_id == dataset_id)
            .order_by(ProcessModel.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


# =============================================================================
# Unit of Work
# =============================================================================


class UnitOfWork:
    """Unit of Work pattern for managing transactions across repositories.

    Usage:
        async with UnitOfWork(session) as uow:
            dataset = await uow.datasets.get_by_id(dataset_id)
            dataset.name = "Updated"
            await uow.datasets.save(dataset)
            await uow.commit()
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        self.datasets = SQLAlchemyDatasetRepository(session)
        self.projects = SQLAlchemyProjectRepository(session)
        self.models = SQLAlchemyProcessModelRepository(session)
        self.jobs = SQLAlchemyAsyncJobRepository(session)

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type:
            await self.rollback()
        else:
            await self.commit()

    async def commit(self) -> None:
        """Commit the current transaction."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Rollback the current transaction."""
        await self._session.rollback()


# =============================================================================
# Async Job Repository
# =============================================================================


class AsyncJobRepository(ABC):
    """Repository interface for AsyncJob."""

    @abstractmethod
    async def get_by_id(self, job_id: str) -> Optional["AsyncJob"]:
        pass

    @abstractmethod
    async def get_by_task_id(self, task_id: str) -> Optional["AsyncJob"]:
        """Get job by Celery task ID."""

    @abstractmethod
    async def save(self, job: "AsyncJob") -> "AsyncJob":
        pass

    @abstractmethod
    async def delete(self, job_id: str) -> bool:
        pass

    @abstractmethod
    async def update_progress(self, job_id: str, progress: int, stage: str | None = None) -> bool:
        """Update job progress and stage."""

    @abstractmethod
    async def complete(
        self, job_id: str, result: dict | None = None, entity_id: str | None = None
    ) -> bool:
        """Mark job as completed with result."""

    @abstractmethod
    async def fail(self, job_id: str, error: str) -> bool:
        """Mark job as failed with error."""

    @abstractmethod
    async def list_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        job_type: str | None = None,
        status: str | None = None,
        entity_id: str | None = None,
    ) -> tuple[list["AsyncJob"], int]:
        """List jobs for a user with filtering and pagination."""

    @abstractmethod
    async def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list["AsyncJob"]:
        """List all jobs for a specific entity."""


class SQLAlchemyAsyncJobRepository(AsyncJobRepository):
    """SQLAlchemy implementation of AsyncJobRepository."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, job_id: str) -> Optional["AsyncJob"]:
        from src.models.orm import AsyncJob

        return await self._session.get(AsyncJob, job_id)

    async def get_by_task_id(self, task_id: str) -> Optional["AsyncJob"]:
        from src.models.orm import AsyncJob

        stmt = select(AsyncJob).where(AsyncJob.task_id == task_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def save(self, job: "AsyncJob") -> "AsyncJob":
        self._session.add(job)
        await self._session.flush()
        await self._session.refresh(job)
        return job

    async def delete(self, job_id: str) -> bool:
        job = await self.get_by_id(job_id)
        if job:
            await self._session.delete(job)
            await self._session.flush()
            return True
        return False

    async def update_progress(self, job_id: str, progress: int, stage: str | None = None) -> bool:
        from datetime import datetime

        from src.models.orm import JobStatus

        job = await self.get_by_id(job_id)
        if not job:
            return False

        job.progress = min(max(progress, 0), 100)  # Clamp 0-100
        if stage:
            job.stage = stage
        job.updated_at = datetime.utcnow()

        # Auto-transition to RUNNING if not already
        if job.status == JobStatus.PENDING.value and progress > 0:
            job.status = JobStatus.RUNNING.value
            job.started_at = datetime.utcnow()

        await self._session.flush()
        return True

    async def complete(
        self, job_id: str, result: dict | None = None, entity_id: str | None = None
    ) -> bool:
        import json
        from datetime import datetime

        from src.models.orm import JobStatus

        job = await self.get_by_id(job_id)
        if not job:
            return False

        job.status = JobStatus.COMPLETED.value
        job.progress = 100
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

        if result:
            job.result_json = json.dumps(result)
        if entity_id:
            job.entity_id = entity_id

        await self._session.flush()
        return True

    async def fail(self, job_id: str, error: str) -> bool:
        from datetime import datetime

        from src.models.orm import JobStatus

        job = await self.get_by_id(job_id)
        if not job:
            return False

        job.status = JobStatus.FAILED.value
        job.error = error
        job.completed_at = datetime.utcnow()
        job.updated_at = datetime.utcnow()

        await self._session.flush()
        return True

    async def list_by_user(
        self,
        user_id: str,
        page: int = 1,
        page_size: int = 20,
        job_type: str | None = None,
        status: str | None = None,
        entity_id: str | None = None,
    ) -> tuple[list["AsyncJob"], int]:
        from src.models.orm import AsyncJob

        # Build filter conditions
        conditions = [AsyncJob.user_id == user_id]
        if job_type:
            conditions.append(AsyncJob.job_type == job_type)
        if status:
            conditions.append(AsyncJob.status == status)
        if entity_id:
            conditions.append(AsyncJob.entity_id == entity_id)

        # Count query
        count_stmt = select(func.count()).select_from(AsyncJob).where(*conditions)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        # Data query
        stmt = (
            select(AsyncJob)
            .where(*conditions)
            .order_by(AsyncJob.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self._session.execute(stmt)
        jobs = list(result.scalars().all())

        return jobs, total

    async def list_by_entity(
        self,
        entity_type: str,
        entity_id: str,
    ) -> list["AsyncJob"]:
        from src.models.orm import AsyncJob

        stmt = (
            select(AsyncJob)
            .where(AsyncJob.entity_type == entity_type, AsyncJob.entity_id == entity_id)
            .order_by(AsyncJob.created_at.desc())
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
