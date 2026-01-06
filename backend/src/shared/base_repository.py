"""Base Repository - Generic Repository Implementation.

Provides a reusable base repository class to reduce boilerplate.
Extend this for entity-specific repositories.

Usage:
    class AnalysisRepository(BaseRepository[Analysis]):
        model_class = Analysis
        
        async def get_by_dataset(self, dataset_id: str) -> list[Analysis]:
            # Custom query method
            ...
"""

from typing import Any, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.database import Base

T = TypeVar("T", bound=Base)


class BaseRepository(Generic[T]):
    """Generic async repository with common CRUD operations.
    
    Subclasses must set `model_class` to the SQLAlchemy model.
    
    Example:
        class UserRepository(BaseRepository[User]):
            model_class = User
    """
    
    model_class: type[T]
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    @property
    def session(self) -> AsyncSession:
        """Access the database session."""
        return self._session
    
    # =========================================================================
    # Basic CRUD
    # =========================================================================
    
    async def get_by_id(self, id: str) -> T | None:
        """Get entity by ID."""
        return await self._session.get(self.model_class, id)
    
    async def get_by_id_or_raise(self, id: str) -> T:
        """Get entity by ID or raise if not found."""
        entity = await self.get_by_id(id)
        if entity is None:
            raise ValueError(f"{self.model_class.__name__} with id {id} not found")
        return entity
    
    async def save(self, entity: T) -> T:
        """Save (create or update) entity."""
        self._session.add(entity)
        await self._session.flush()
        await self._session.refresh(entity)
        return entity
    
    async def save_many(self, entities: list[T]) -> list[T]:
        """Save multiple entities."""
        self._session.add_all(entities)
        await self._session.flush()
        for entity in entities:
            await self._session.refresh(entity)
        return entities
    
    async def delete(self, id: str) -> bool:
        """Delete entity by ID. Returns True if deleted."""
        entity = await self.get_by_id(id)
        if entity:
            await self._session.delete(entity)
            await self._session.flush()
            return True
        return False
    
    async def delete_entity(self, entity: T) -> None:
        """Delete entity instance."""
        await self._session.delete(entity)
        await self._session.flush()
    
    # =========================================================================
    # Query Helpers
    # =========================================================================
    
    async def exists(self, id: str) -> bool:
        """Check if entity exists."""
        stmt = select(func.count()).where(self.model_class.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0
    
    async def count(self, **filters: Any) -> int:
        """Count entities with optional filters."""
        stmt = select(func.count()).select_from(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                stmt = stmt.where(getattr(self.model_class, key) == value)
        result = await self._session.execute(stmt)
        return result.scalar_one()
    
    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
        order_by: str | None = None,
        order_desc: bool = True,
        **filters: Any,
    ) -> tuple[list[T], int]:
        """List entities with pagination and filtering.
        
        Returns:
            Tuple of (items, total_count)
        """
        # Build base query
        stmt = select(self.model_class)
        count_stmt = select(func.count()).select_from(self.model_class)
        
        # Apply filters
        for key, value in filters.items():
            if value is not None and hasattr(self.model_class, key):
                stmt = stmt.where(getattr(self.model_class, key) == value)
                count_stmt = count_stmt.where(getattr(self.model_class, key) == value)
        
        # Get total count
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        
        # Apply ordering
        if order_by and hasattr(self.model_class, order_by):
            order_col = getattr(self.model_class, order_by)
            stmt = stmt.order_by(order_col.desc() if order_desc else order_col.asc())
        elif hasattr(self.model_class, "created_at"):
            stmt = stmt.order_by(self.model_class.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)
        
        # Execute
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total
    
    async def find_by(self, **filters: Any) -> list[T]:
        """Find all entities matching filters."""
        stmt = select(self.model_class)
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                stmt = stmt.where(getattr(self.model_class, key) == value)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())
    
    async def find_one_by(self, **filters: Any) -> T | None:
        """Find single entity matching filters."""
        entities = await self.find_by(**filters)
        return entities[0] if entities else None


class ReadOnlyRepository(Generic[T]):
    """Read-only repository for query-heavy operations.
    
    Use when you only need read access without mutations.
    """
    
    model_class: type[T]
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, id: str) -> T | None:
        """Get entity by ID."""
        return await self._session.get(self.model_class, id)
    
    async def exists(self, id: str) -> bool:
        """Check if entity exists."""
        stmt = select(func.count()).where(self.model_class.id == id)
        result = await self._session.execute(stmt)
        return result.scalar_one() > 0
    
    async def count(self) -> int:
        """Count all entities."""
        stmt = select(func.count()).select_from(self.model_class)
        result = await self._session.execute(stmt)
        return result.scalar_one()
    
    async def list_all(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[T], int]:
        """List entities with pagination."""
        # Count
        count_stmt = select(func.count()).select_from(self.model_class)
        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar_one()
        
        # Fetch
        stmt = select(self.model_class)
        if hasattr(self.model_class, "created_at"):
            stmt = stmt.order_by(self.model_class.created_at.desc())
        stmt = stmt.offset((page - 1) * page_size).limit(page_size)
        
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total
