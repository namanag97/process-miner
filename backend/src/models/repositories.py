"""Repository pattern abstraction for data access.

Provides clean separation between domain logic and data access with:
- Generic repository interface
- SQLAlchemy implementation
- Unit of Work pattern for transactions

Usage:
    # Get repository from dependency injection
    repo = SQLAlchemyEventLogRepository(session)
    
    # Use repository methods
    log = await repo.get_by_id(ProcessId("..."))
    await repo.save(log)
"""

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Protocol, TypeVar
from uuid import uuid4

from sqlalchemy import select, func
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
    
    async def get_by_id(self, id: ID) -> Optional[T]:
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
    
    async def get_by_id(self, id: ID) -> Optional[T]:
        ...
    
    async def exists(self, id: ID) -> bool:
        ...
    
    async def count(self) -> int:
        ...


# =============================================================================
# Event Log Repository
# =============================================================================

class EventLogRepository(ABC):
    """Repository interface for EventLog aggregate root."""
    
    @abstractmethod
    async def get_by_id(self, log_id: str) -> Optional["EventLog"]:
        """Get event log by ID with all cases loaded."""
        pass
    
    @abstractmethod
    async def get_by_id_lightweight(self, log_id: str) -> Optional["EventLog"]:
        """Get event log by ID without loading cases (for metadata only)."""
        pass
    
    @abstractmethod
    async def save(self, log: "EventLog") -> "EventLog":
        """Save event log (create or update)."""
        pass
    
    @abstractmethod
    async def delete(self, log_id: str) -> bool:
        """Delete event log and all associated data."""
        pass
    
    @abstractmethod
    async def exists(self, log_id: str) -> bool:
        """Check if event log exists."""
        pass
    
    @abstractmethod
    async def list_all(
        self, 
        page: int = 1, 
        page_size: int = 20,
        source_format: Optional[str] = None,
    ) -> tuple[List["EventLog"], int]:
        """List event logs with pagination. Returns (logs, total_count)."""
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """Count total event logs."""
        pass


class SQLAlchemyEventLogRepository(EventLogRepository):
    """SQLAlchemy implementation of EventLogRepository."""
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, log_id: str) -> Optional["EventLog"]:
        from src.models.orm import Dataset
        
        result = await self._session.get(EventLog, log_id)
        return result
    
    async def get_by_id_lightweight(self, log_id: str) -> Optional["EventLog"]:
        from src.models.orm import Dataset
        
        # Use a query that doesn't eager load relationships
        stmt = select(EventLog).where(EventLog.id == log_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def save(self, log: "EventLog") -> "EventLog":
        self._session.add(log)
        await self._session.flush()
        await self._session.refresh(log)
        return log
    
    async def delete(self, log_id: str) -> bool:
        from src.models.orm import Dataset
        
        log = await self.get_by_id(log_id)
        if log:
            await self._session.delete(log)
            await self._session.flush()
            return True
        return False
    
    async def exists(self, log_id: str) -> bool:
        from src.models.orm import Dataset
        
        stmt = select(func.count()).where(EventLog.id == log_id)
        result = await self._session.execute(stmt)
        return result.scalar() > 0
    
    async def list_all(
        self, 
        page: int = 1, 
        page_size: int = 20,
        source_format: Optional[str] = None,
    ) -> tuple[List["EventLog"], int]:
        from src.models.orm import Dataset
        
        # Count query
        count_stmt = select(func.count()).select_from(EventLog)
        if source_format:
            count_stmt = count_stmt.where(EventLog.source_format == source_format)
        
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0
        
        # Data query
        stmt = select(EventLog).order_by(EventLog.created_at.desc())
        if source_format:
            stmt = stmt.where(EventLog.source_format == source_format)
        
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        result = await self._session.execute(stmt)
        logs = list(result.scalars().all())
        
        return logs, total
    
    async def count(self) -> int:
        from src.models.orm import Dataset
        
        stmt = select(func.count()).select_from(EventLog)
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
    async def list_all(self, page: int = 1, page_size: int = 20) -> tuple[List["Project"], int]:
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
        from src.models.orm import Project
        
        project = await self.get_by_id(project_id)
        if project:
            await self._session.delete(project)
            await self._session.flush()
            return True
        return False
    
    async def list_all(self, page: int = 1, page_size: int = 20) -> tuple[List["Project"], int]:
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
    async def get_by_log_id(self, log_id: str) -> List["ProcessModel"]:
        """Get all models for a given event log."""
        pass


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
    
    async def get_by_log_id(self, log_id: str) -> List["ProcessModel"]:
        from src.models.orm import ProcessModel
        
        stmt = (
            select(ProcessModel)
            .where(ProcessModel.log_id == log_id)
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
            log = await uow.event_logs.get_by_id(log_id)
            log.name = "Updated"
            await uow.event_logs.save(log)
            await uow.commit()
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
        self.event_logs = SQLAlchemyEventLogRepository(session)
        self.projects = SQLAlchemyProjectRepository(session)
        self.models = SQLAlchemyProcessModelRepository(session)
    
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
