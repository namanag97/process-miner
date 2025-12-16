"""
Database configuration using SQLModel with async support.
"""

from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from .config import get_settings

# Get settings
settings = get_settings()

# Create async engine with configuration from settings
engine = create_async_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},  # Needed for SQLite
    echo=settings.debug,  # Log SQL queries in debug mode
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def create_db_tables():
    """Create all database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_db():
    """Dependency to get DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
