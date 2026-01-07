"""Database setup - SQLAlchemy async."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.platform.core.config import get_settings
from src.platform.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Create async engine
async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

# Session factory
async_session_maker = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("db_session_committed")
        except Exception as e:
            await session.rollback()
            logger.warning("db_session_rollback", error=str(e), error_type=type(e).__name__)
            raise


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database session (for use outside of FastAPI)."""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("db_session_context_committed")
        except Exception as e:
            await session.rollback()
            logger.warning("db_session_context_rollback", error=str(e), error_type=type(e).__name__)
            raise


async def init_database() -> None:
    """Initialize database - create all tables."""
    # Import the shared Base to register all models
    import src.features.process_mining.models

    # Import all models to ensure they're registered with the Base
    import src.platform.models
    import src.platform.workflows.models  # noqa: F401 - Workflow, WorkflowTask
    from src.shared.database import Base

    logger.info("database_initializing", url=settings.database_url)
    async with async_engine.begin() as conn:
        # Create all tables (both platform and process mining use the same Base)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized")


async def close_database() -> None:
    """Close database connections."""
    logger.info("database_closing")
    await async_engine.dispose()
    logger.info("database_closed")
