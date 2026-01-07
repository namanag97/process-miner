"""Database setup - SQLAlchemy async with CQRS read/write separation.

Provides separate connection pools for read and write operations:
- Write pool: Primary database for transactional writes
- Read pool: Can use a replica for scalable reads (defaults to primary)

Usage:
    # In FastAPI dependencies
    WriteDBSession = Annotated[AsyncSession, Depends(get_write_session)]
    ReadDBSession = Annotated[AsyncSession, Depends(get_read_session)]
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.platform.core.config import get_settings
from src.platform.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

# =============================================================================
# Write Engine (Primary Database)
# =============================================================================

# Create async engine for writes (primary database)
write_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
)

# Write session factory
write_session_maker = async_sessionmaker(
    write_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# =============================================================================
# Read Engine (Replica or Primary)
# =============================================================================

# Read engine uses replica URL if configured, otherwise falls back to primary
read_database_url = settings.read_database_url or settings.database_url

read_engine = create_async_engine(
    read_database_url,
    echo=settings.debug,
    future=True,
    pool_pre_ping=True,
)

# Read session factory
read_session_maker = async_sessionmaker(
    read_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# =============================================================================
# Session Generators (for FastAPI dependency injection)
# =============================================================================


async def get_write_session() -> AsyncGenerator[AsyncSession, None]:
    """Get write database session for commands (transactional operations)."""
    async with write_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("write_session_committed")
        except Exception as e:
            await session.rollback()
            logger.warning("write_session_rollback", error=str(e), error_type=type(e).__name__)
            raise


async def get_read_session() -> AsyncGenerator[AsyncSession, None]:
    """Get read database session for queries (read-only operations)."""
    async with read_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("read_session_committed")
        except Exception as e:
            await session.rollback()
            logger.warning("read_session_rollback", error=str(e), error_type=type(e).__name__)
            raise


# Legacy alias for backward compatibility
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Legacy session getter - wraps write session for compatibility.

    Deprecated: Use get_write_session() or get_read_session() directly.
    """
    async for session in get_write_session():
        yield session


# =============================================================================
# Context Managers (for use outside of FastAPI)
# =============================================================================


@asynccontextmanager
async def get_write_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for write session (for Temporal activities, scripts)."""
    async with write_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("write_session_context_committed")
        except Exception as e:
            await session.rollback()
            logger.warning(
                "write_session_context_rollback", error=str(e), error_type=type(e).__name__
            )
            raise


@asynccontextmanager
async def get_read_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for read session (for Temporal activities, scripts)."""
    async with read_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("read_session_context_committed")
        except Exception as e:
            await session.rollback()
            logger.warning(
                "read_session_context_rollback", error=str(e), error_type=type(e).__name__
            )
            raise


# Legacy alias for backward compatibility
get_session_context = get_write_session_context


# =============================================================================
# Database Lifecycle
# =============================================================================


async def init_database() -> None:
    """Initialize database - create all tables."""
    # Import the shared Base to register all models
    import src.features.process_mining.models

    # Import all models to ensure they're registered with the Base
    import src.platform.models
    import src.platform.workflows.models  # noqa: F401 - Workflow, WorkflowTask
    from src.shared.database import Base

    logger.info("database_initializing", url=settings.database_url)
    async with write_engine.begin() as conn:
        # Create all tables (both platform and process mining use the same Base)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized")


async def close_database() -> None:
    """Close database connections."""
    logger.info("database_closing")
    await write_engine.dispose()
    await read_engine.dispose()
    logger.info("database_closed")


# =============================================================================
# Backward Compatibility
# =============================================================================

# Legacy exports for code that still uses old names
async_engine = write_engine  # Legacy alias
async_session_maker = write_session_maker  # Legacy alias
