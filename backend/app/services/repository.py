"""
Generic repository pattern for CRUD operations.

Reduces boilerplate in routers by providing common database operations
with proper error handling and dependency injection.
"""

from typing import TypeVar, Generic, Type, Optional, Sequence
from sqlmodel import SQLModel, select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Depends

from ..database import get_db


T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    """
    Generic repository providing common CRUD operations.
    
    Usage:
        repo = BaseRepository(Upload, db)
        upload = await repo.get_or_404("abc-123")
    """
    
    def __init__(self, model: Type[T], db: AsyncSession):
        self.model = model
        self.db = db
    
    async def get(self, id: str) -> Optional[T]:
        """Get a record by ID, returns None if not found."""
        result = await self.db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_404(self, id: str) -> T:
        """Get a record by ID, raises 404 if not found."""
        obj = await self.get(id)
        if not obj:
            raise HTTPException(
                status_code=404,
                detail=f"{self.model.__name__} not found"
            )
        return obj
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[T]:
        """Get all records with pagination."""
        result = await self.db.execute(
            select(self.model).offset(offset).limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_field(self, field_name: str, value: str) -> Sequence[T]:
        """Get records by a specific field value."""
        field = getattr(self.model, field_name)
        result = await self.db.execute(
            select(self.model).where(field == value)
        )
        return result.scalars().all()
    
    async def create(self, obj: T) -> T:
        """Create a new record."""
        self.db.add(obj)
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def update(self, obj: T) -> T:
        """Update an existing record."""
        await self.db.commit()
        await self.db.refresh(obj)
        return obj
    
    async def delete(self, obj: T) -> None:
        """Delete a record."""
        await self.db.delete(obj)
        await self.db.commit()
    
    async def delete_by_id(self, id: str) -> bool:
        """Delete a record by ID, returns True if deleted."""
        obj = await self.get(id)
        if obj:
            await self.delete(obj)
            return True
        return False


# =============================================================================
# Dependency Injection Factories
# =============================================================================

def get_repository(model: Type[T]):
    """
    Factory to create repository dependencies.
    
    Usage:
        @router.get("/{upload_id}")
        async def get_upload(
            upload_id: str,
            repo: BaseRepository[Upload] = Depends(get_repository(Upload))
        ):
            return await repo.get_or_404(upload_id)
    """
    async def _get_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[T]:
        return BaseRepository(model, db)
    return _get_repo
