"""SQLAlchemy Repository Implementations.

Infrastructure layer implementations of the domain repository interfaces.
This is where all ORM and database-specific code lives.
"""

import contextlib
import json
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.logging_config import get_logger
from src.domain.entities import (
    DatasetAggregate,
    ProcessCase,
    ProcessEvent,
)
from src.domain.repositories import DatasetRepository
from src.domain.value_objects import CaseId

if TYPE_CHECKING:
    from src.models.orm import Dataset as ORMDataset

logger = get_logger(__name__)


# =============================================================================
# SQLAlchemy Implementations
# =============================================================================


class SQLAlchemyDatasetRepository(DatasetRepository):
    """SQLAlchemy implementation of DatasetRepository.

    Optimized for:
    - Eager loading of cases and events
    - Efficient batch operations
    - Proper transaction management
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get(self, dataset_id: str) -> DatasetAggregate | None:
        """Load aggregate with eager loading of cases and events."""
        from src.models.orm import Dataset as ORMDataset
        from src.models.orm import ProcessCase as ORMCase

        stmt = (
            select(ORMDataset)
            .options(selectinload(ORMDataset.cases).selectinload(ORMCase.events))
            .where(ORMDataset.id == dataset_id)
        )

        result = await self._session.execute(stmt)
        orm_log = result.scalar_one_or_none()

        if not orm_log:
            return None

        return self._to_domain(orm_log)

    async def get_many(self, dataset_ids: list[str]) -> list[DatasetAggregate]:
        """Load multiple aggregates efficiently."""
        from src.models.orm import Dataset as ORMDataset
        from src.models.orm import ProcessCase as ORMCase

        if not dataset_ids:
            return []

        stmt = (
            select(ORMDataset)
            .options(selectinload(ORMDataset.cases).selectinload(ORMCase.events))
            .where(ORMDataset.id.in_(dataset_ids))
        )

        result = await self._session.execute(stmt)
        orm_logs = result.scalars().all()

        return [self._to_domain(orm_log) for orm_log in orm_logs]

    async def save(self, aggregate: DatasetAggregate) -> None:
        """Persist aggregate - UPDATE not implemented yet (MVP)."""
        # For MVP, we don't update existing logs through this path
        # The existing upload flow handles creation
        logger.warning("repository_save_not_implemented", dataset_id=aggregate.id)

    async def delete(self, dataset_id: str) -> bool:
        """Delete aggregate and all related entities."""
        from src.models.orm import Dataset as ORMDataset

        stmt = select(ORMDataset).where(ORMDataset.id == dataset_id)
        result = await self._session.execute(stmt)
        orm_log = result.scalar_one_or_none()

        if not orm_log:
            return False

        await self._session.delete(orm_log)
        return True

    async def exists(self, dataset_id: str) -> bool:
        """Check if dataset exists."""
        from src.models.orm import Dataset as ORMDataset

        stmt = select(ORMDataset.id).where(ORMDataset.id == dataset_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none() is not None

    def _to_domain(self, orm_log: "ORMDataset") -> DatasetAggregate:
        """Convert ORM model to domain aggregate."""
        cases = []

        for orm_case in orm_log.cases:
            events = []
            for orm_event in orm_case.events:
                # Parse attributes JSON if present
                attributes = {}
                if orm_event.attributes_json:
                    with contextlib.suppress(json.JSONDecodeError, TypeError):
                        attributes = json.loads(orm_event.attributes_json)

                events.append(
                    ProcessEvent(
                        id=orm_event.id,
                        activity=orm_event.activity,
                        timestamp=orm_event.timestamp,
                        resource=orm_event.resource,
                        attributes=attributes,
                    )
                )

            cases.append(
                ProcessCase(
                    case_id=CaseId(orm_case.case_id),
                    events=events,
                )
            )

        return DatasetAggregate(
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


def create_dataset_repository(session: AsyncSession) -> DatasetRepository:
    """Factory function to create the appropriate repository."""
    return SQLAlchemyDatasetRepository(session)
