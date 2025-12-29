"""Repository implementations for data access.

These repositories extend BaseRepository for common CRUD operations
and provide domain-specific methods and mapping.
"""

import json
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.entities import (
    ConformanceResult,
    EventLog,
    ProcessCase,
    ProcessEvent,
    ProcessModel,
)
from src.domain.value_objects import (
    ActivityName,
    MinerType,
    ModelFormat,
    ResourceId,
    Timestamp,
)
from src.infrastructure.persistence.base_repository import BaseRepository
from src.infrastructure.persistence.models import (
    ConformanceResultModel,
    EventLogModel,
    ProcessCaseModel,
    ProcessEventModel,
    ProcessModelModel,
)


class EventLogRepository(BaseRepository[EventLogModel, EventLog]):
    """Repository for EventLog aggregate persistence.
    
    Extends BaseRepository for basic CRUD, adding custom save logic
    for aggregate persistence and eager loading for get_by_id.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, EventLogModel)

    async def save(self, log: EventLog) -> None:
        """Save an event log with all its cases and events."""
        existing = await self.session.get(EventLogModel, str(log.id))

        if existing:
            # Update existing
            existing.name = log.name
            existing.source_file = log.source_file
            existing.total_cases = log.total_cases
            existing.total_events = log.total_events
            existing.metadata_json = json.dumps(log.metadata) if log.metadata else None
            existing.updated_at = datetime.utcnow()
        else:
            # Create new
            log_model = EventLogModel(
                id=str(log.id),
                name=log.name,
                source_file=log.source_file,
                total_cases=log.total_cases,
                total_events=log.total_events,
                metadata_json=json.dumps(log.metadata) if log.metadata else None,
                created_at=log.created_at,
            )
            self.session.add(log_model)

            # Add cases and events
            for case in log.cases:
                case_model = ProcessCaseModel(
                    id=str(case.id),
                    case_id=case.case_id,
                    log_id=str(log.id),
                    variant_key=case.variant_key,
                    attributes_json=json.dumps(case.attributes) if case.attributes else None,
                )
                self.session.add(case_model)

                for event in case.events:
                    event_model = ProcessEventModel(
                        id=str(event.id),
                        case_db_id=str(case.id),
                        case_id=event.case_id,
                        activity=str(event.activity),
                        timestamp=event.timestamp.value,
                        resource=str(event.resource) if event.resource else None,
                        attributes_json=json.dumps(event.attributes) if event.attributes else None,
                    )
                    self.session.add(event_model)

        await self.session.flush()

    async def get_by_id(self, log_id: UUID) -> Optional[EventLog]:
        """Get an event log by ID with all cases and events (eager loading)."""
        query = (
            select(self.model_class)
            .options(selectinload(EventLogModel.cases).selectinload(ProcessCaseModel.events))
            .where(self.model_class.id == str(log_id))
        )
        result = await self.session.execute(query)
        log_model = result.scalar_one_or_none()

        if not log_model:
            return None

        return self._to_domain(log_model)

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[EventLog]:
        """List all event logs without loading cases (summary view)."""
        query = (
            select(self.model_class)
            .order_by(self.model_class.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        log_models = result.scalars().all()

        logs = []
        for log_model in log_models:
            log = EventLog(
                id=UUID(log_model.id),
                name=log_model.name,
                source_file=log_model.source_file,
                created_at=log_model.created_at,
                metadata=json.loads(log_model.metadata_json) if log_model.metadata_json else {},
            )
            # Set counts without loading all cases
            log.metadata["total_cases"] = log_model.total_cases
            log.metadata["total_events"] = log_model.total_events
            logs.append(log)

        return logs

    def _to_domain(self, model: EventLogModel) -> EventLog:
        """Convert ORM model to domain entity."""
        log = EventLog(
            id=UUID(model.id),
            name=model.name,
            source_file=model.source_file,
            created_at=model.created_at,
            metadata=json.loads(model.metadata_json) if model.metadata_json else {},
        )

        for case_model in model.cases:
            case = ProcessCase(
                id=UUID(case_model.id),
                case_id=case_model.case_id,
                attributes=json.loads(case_model.attributes_json)
                if case_model.attributes_json
                else {},
            )

            for event_model in case_model.events:
                event = ProcessEvent(
                    id=UUID(event_model.id),
                    case_id=event_model.case_id,
                    activity=ActivityName(event_model.activity),
                    timestamp=Timestamp(event_model.timestamp),
                    resource=ResourceId(event_model.resource) if event_model.resource else None,
                    attributes=json.loads(event_model.attributes_json)
                    if event_model.attributes_json
                    else {},
                )
                case.events.append(event)

            log.cases.append(case)

        return log


class ProcessModelRepository(BaseRepository[ProcessModelModel, ProcessModel]):
    """Repository for ProcessModel persistence.
    
    Extends BaseRepository, overriding save for custom update logic.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, ProcessModelModel)

    async def save(self, model: ProcessModel) -> None:
        """Save a process model."""
        existing = await self.session.get(ProcessModelModel, str(model.id))

        if existing:
            existing.name = model.name
            existing.format = model.format.value
            existing.miner_type = model.miner_type.value if model.miner_type else None
            existing.serialized_data = model.serialized
            existing.metadata_json = json.dumps(model.metadata) if model.metadata else None
        else:
            model_orm = ProcessModelModel(
                id=str(model.id),
                name=model.name,
                format=model.format.value,
                miner_type=model.miner_type.value if model.miner_type else None,
                source_log_id=str(model.source_log_id) if model.source_log_id else None,
                serialized_data=model.serialized,
                metadata_json=json.dumps(model.metadata) if model.metadata else None,
                created_at=model.created_at,
            )
            self.session.add(model_orm)

        await self.session.flush()

    async def get_by_id(self, model_id: UUID) -> Optional[ProcessModel]:
        """Get a process model by ID."""
        model_orm = await self.session.get(self.model_class, str(model_id))
        return self._to_domain(model_orm) if model_orm else None

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[ProcessModel]:
        """List all process models."""
        query = (
            select(self.model_class)
            .order_by(self.model_class.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: ProcessModelModel) -> ProcessModel:
        """Convert ORM model to domain entity."""
        return ProcessModel(
            id=UUID(model.id),
            name=model.name,
            format=ModelFormat(model.format),
            miner_type=MinerType(model.miner_type) if model.miner_type else None,
            source_log_id=UUID(model.source_log_id) if model.source_log_id else None,
            serialized=model.serialized_data,
            created_at=model.created_at,
            metadata=json.loads(model.metadata_json) if model.metadata_json else {},
        )


class ConformanceResultRepository(BaseRepository[ConformanceResultModel, ConformanceResult]):
    """Repository for ConformanceResult persistence.
    
    Extends BaseRepository with domain-specific query methods.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, ConformanceResultModel)

    async def save(self, result: ConformanceResult) -> None:
        """Save a conformance result."""
        result_orm = ConformanceResultModel(
            id=str(result.id),
            log_id=str(result.log_id),
            model_id=str(result.model_id),
            fitness=result.fitness,
            precision=result.precision,
            generalization=result.generalization,
            simplicity=result.simplicity,
            deviations_json=json.dumps(result.deviations) if result.deviations else None,
            created_at=result.created_at,
        )
        self.session.add(result_orm)
        await self.session.flush()

    async def get_by_id(self, result_id: UUID) -> Optional[ConformanceResult]:
        """Get a conformance result by ID."""
        result_orm = await self.session.get(self.model_class, str(result_id))
        return self._to_domain(result_orm) if result_orm else None

    async def get_by_log_and_model(
        self, log_id: UUID, model_id: UUID
    ) -> Optional[ConformanceResult]:
        """Get conformance result for a specific log and model pair."""
        query = (
            select(self.model_class)
            .where(
                self.model_class.log_id == str(log_id),
                self.model_class.model_id == str(model_id),
            )
            .order_by(self.model_class.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        result_orm = result.scalar_one_or_none()
        return self._to_domain(result_orm) if result_orm else None

    def _to_domain(self, model: ConformanceResultModel) -> ConformanceResult:
        """Convert ORM model to domain entity."""
        return ConformanceResult(
            id=UUID(model.id),
            log_id=UUID(model.log_id),
            model_id=UUID(model.model_id),
            fitness=model.fitness,
            precision=model.precision,
            generalization=model.generalization,
            simplicity=model.simplicity,
            deviations=json.loads(model.deviations_json) if model.deviations_json else [],
            created_at=model.created_at,
        )
