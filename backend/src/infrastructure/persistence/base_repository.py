"""Base Repository - Generic repository pattern for DRY CRUD operations."""

from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

# Type variables for generic repository
ModelType = TypeVar("ModelType")
DomainType = TypeVar("DomainType")


class BaseRepository(Generic[ModelType, DomainType]):
    """
    Generic base repository providing common CRUD operations.
    
    Subclasses should implement:
    - _to_domain(model) -> domain entity conversion
    - _to_model(entity) -> ORM model conversion (optional, for custom save logic)
    """

    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        self.session = session
        self.model_class = model_class

    async def get_by_id(self, entity_id: UUID) -> Optional[ModelType]:
        """Get entity by ID."""
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.id == str(entity_id))
        )
        return result.scalar_one_or_none()

    async def list_all(
        self, limit: int = 100, offset: int = 0
    ) -> List[ModelType]:
        """List all entities with pagination."""
        result = await self.session.execute(
            select(self.model_class).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def save(self, model: ModelType) -> ModelType:
        """Save or update an entity."""
        self.session.add(model)
        await self.session.flush()
        return model

    async def delete(self, entity_id: UUID) -> bool:
        """Delete entity by ID. Returns True if deleted."""
        result = await self.session.execute(
            delete(self.model_class).where(self.model_class.id == str(entity_id))
        )
        await self.session.flush()
        return result.rowcount > 0

    async def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists."""
        result = await self.session.execute(
            select(self.model_class.id).where(self.model_class.id == str(entity_id))
        )
        return result.scalar_one_or_none() is not None
