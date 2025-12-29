"""FastAPI dependencies - DB session, auth, etc."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import get_session


# Database session dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    async for session in get_session():
        yield session


# Type alias for dependency injection
DBSession = Annotated[AsyncSession, Depends(get_db)]
