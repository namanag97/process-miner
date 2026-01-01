"""Repository Pattern - Abstract data access.

Repositories provide a clean interface for loading and persisting aggregates,
hiding the complexity of ORM operations and eager loading strategies.

Key Benefits:
- Aggregate loading is optimized (eager loading of cases and events)
- Testing is simplified (mock repositories)
- Domain layer stays free of ORM concerns
"""

from abc import ABC, abstractmethod
from typing import List, Optional, TYPE_CHECKING
import json

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import (
    EventLogAggregate,
    ProcessCase,
    ProcessEvent,
)
from src.domain.value_objects import CaseId
from src.core.logging_config import get_logger

if TYPE_CHECKING:
    from src.models.orm import EventLog as ORMEventLog

logger = get_logger(__name__)


# =============================================================================
# Repository Interfaces
# =============================================================================

class EventLogRepository(ABC):
    """Abstract repository for EventLog aggregates."""
    
    @abstractmethod
    async def get(self, log_id: str) -> Optional[EventLogAggregate]:
        """Load an aggregate by ID.
        
        Returns None if not found.
        """
        pass
    
    @abstractmethod
    async def get_many(self, log_ids: List[str]) -> List[EventLogAggregate]:
        """Load multiple aggregates by ID."""
        pass
    
    @abstractmethod
    async def save(self, aggregate: EventLogAggregate) -> None:
        """Persist an aggregate and its cases/events."""
        pass
    
    @abstractmethod
    async def delete(self, log_id: str) -> bool:
        """Delete an aggregate. Returns True if deleted."""
        pass
    
    @abstractmethod
    async def exists(self, log_id: str) -> bool:
        """Check if an aggregate exists."""
        pass


class ProcessModelRepository(ABC):
    """Abstract repository for ProcessModel aggregates."""
    
    @abstractmethod
    async def get(self, model_id: str) -> Optional[dict]:
        """Load a model by ID."""
        pass
    
    @abstractmethod
    async def get_by_log(self, log_id: str) -> List[dict]:
        """Get all models for a log."""
        pass
    
    @abstractmethod
    async def save(self, model: dict) -> None:
        """Persist a model."""
        pass
    
    @abstractmethod
    async def delete(self, model_id: str) -> bool:
        """Delete a model."""
        pass


# =============================================================================
# SQLAlchemy Implementations
# =============================================================================

class SQLAlchemyEventLogRepository(EventLogRepository):
    """SQLAlchemy implementation of EventLogRepository.
    
    Optimized for:
    - Eager loading of cases and events
    - Efficient batch operations
    - Proper transaction management
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get(self, log_id: str) -> Optional[EventLogAggregate]:
        """Load aggregate with eager loading of cases and events."""
        from src.models.orm import EventLog as ORMEventLog, ProcessCase as ORMCase
        
        stmt = (
            select(ORMEventLog)
            .options(
                selectinload(ORMEventLog.cases).selectinload(ORMCase.events)
            )
            .where(ORMEventLog.id == log_id)
        )
        
        result = await self._session.execute(stmt)
        orm_log = result.scalar_one_or_none()
        
        if not orm_log:
            return None
        
        return self._to_domain(orm_log)
    
    async def get_many(self, log_ids: List[str]) -> List[EventLogAggregate]:
        """Load multiple aggregates efficiently."""
        from src.models.orm import EventLog as ORMEventLog, ProcessCase as ORMCase
        
        if not log_ids:
            return []
        
        stmt = (
            select(ORMEventLog)
            .options(
                selectinload(ORMEventLog.cases).selectinload(ORMCase.events)
            )
            .where(ORMEventLog.id.in_(log_ids))
        )
        
        result = await self._session.execute(stmt)
        orm_logs = result.scalars().all()
        
        return [self._to_domain(orm_log) for orm_log in orm_logs]
    
    async def save(self, aggregate: EventLogAggregate) -> None:
        """Persist aggregate - UPDATE not implemented yet (MVP)."""
        # For MVP, we don't update existing logs through this path
        # The existing upload flow handles creation
        logger.warning("repository_save_not_implemented", log_id=aggregate.id)
    
    async def delete(self, log_id: str) -> bool:
        """Delete aggregate and all related entities."""
        from src.models.orm import EventLog as ORMEventLog
        
        stmt = select(ORMEventLog).where(ORMEventLog.id == log_id)
        result = await self._session.execute(stmt)
        orm_log = result.scalar_one_or_none()
        
        if not orm_log:
            return False
        
        await self._session.delete(orm_log)
        return True
    
    async def exists(self, log_id: str) -> bool:
        """Check if log exists."""
        from src.models.orm import EventLog as ORMEventLog
        
        stmt = select(ORMEventLog.id).where(ORMEventLog.id == log_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None
    
    def _to_domain(self, orm_log: "ORMEventLog") -> EventLogAggregate:
        """Convert ORM model to domain aggregate."""
        cases = []
        
        for orm_case in orm_log.cases:
            events = []
            for orm_event in orm_case.events:
                # Parse attributes JSON if present
                attributes = {}
                if orm_event.attributes_json:
                    try:
                        attributes = json.loads(orm_event.attributes_json)
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                events.append(ProcessEvent(
                    id=orm_event.id,
                    activity=orm_event.activity,
                    timestamp=orm_event.timestamp,
                    resource=orm_event.resource,
                    attributes=attributes,
                ))
            
            cases.append(ProcessCase(
                case_id=CaseId(orm_case.case_id),
                events=events,
            ))
        
        return EventLogAggregate(
            id=orm_log.id,
            name=orm_log.name or "Untitled",
            cases=cases,
            source_format=orm_log.source_format or "csv",
            source_file=orm_log.source_file,
            created_at=orm_log.created_at,
        )


# =============================================================================
# Factory Function
# =============================================================================

def create_event_log_repository(session: AsyncSession) -> EventLogRepository:
    """Factory function to create the appropriate repository."""
    return SQLAlchemyEventLogRepository(session)
