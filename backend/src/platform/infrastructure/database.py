"""Database setup - SQLAlchemy async with CQRS support.

Provides separate connection pools for write and read operations:
- Write pool: Lower concurrency, transactional writes to PostgreSQL
- Read pool: Higher concurrency, read-heavy operations

Usage:
    # For write operations (commands)
    @router.post("/datasets")
    async def create(db: AsyncSession = Depends(get_write_session)):
        ...
    
    # For read operations (queries)
    @router.get("/datasets")
    async def list(db: AsyncSession = Depends(get_read_session)):
        ...
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.platform.core.config import get_settings
from src.platform.core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)


# =============================================================================
# CQRS: Separate Write and Read Engines
# =============================================================================

def _is_sqlite(url: str) -> bool:
    """Check if database URL is SQLite (doesn't support pooling)."""
    return url.startswith("sqlite")


# WRITE engine - PostgreSQL primary (or SQLite in dev)
# Lower pool size, optimized for transactional writes
_write_pool_class = NullPool if _is_sqlite(settings.database_url) else None
write_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
    poolclass=_write_pool_class,
    **(
        {}
        if _is_sqlite(settings.database_url)
        else {
            "pool_size": settings.write_pool_size,
            "max_overflow": settings.write_pool_max_overflow,
        }
    ),
)

# READ engine - PostgreSQL replica or same as write
# Higher pool size, optimized for read-heavy operations
_read_db_url = settings.read_database_url or settings.database_url
_read_pool_class = NullPool if _is_sqlite(_read_db_url) else None
read_engine = create_async_engine(
    _read_db_url,
    echo=settings.debug,
    future=True,
    poolclass=_read_pool_class,
    **(
        {}
        if _is_sqlite(_read_db_url)
        else {
            "pool_size": settings.read_pool_size,
            "max_overflow": settings.read_pool_max_overflow,
        }
    ),
)

# Log CQRS configuration
logger.info(
    "cqrs_database_engines_created",
    write_url=settings.database_url.split("@")[-1] if "@" in settings.database_url else "local",
    read_url=_read_db_url.split("@")[-1] if "@" in _read_db_url else "local",
    separate_read_db=settings.read_database_url is not None,
)


# =============================================================================
# Session Factories
# =============================================================================

# Write session factory
write_session_maker = async_sessionmaker(
    write_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Read session factory
read_session_maker = async_sessionmaker(
    read_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Backward compatibility: default session uses write engine
async_engine = write_engine
async_session_maker = write_session_maker


# =============================================================================
# CQRS Dependencies
# =============================================================================

async def get_write_session() -> AsyncGenerator[AsyncSession, None]:
    """Get write-optimized database session for commands.
    
    Use for: POST, PUT, PATCH, DELETE operations.
    """
    async with write_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("write_session_committed")
        except Exception as e:
            await session.rollback()
            logger.warning(
                "write_session_rollback",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise


async def get_read_session() -> AsyncGenerator[AsyncSession, None]:
    """Get read-optimized database session for queries.
    
    Use for: GET operations (metadata queries).
    Note: For analytics, use DuckDB via get_analytics_db().
    """
    async with read_session_maker() as session:
        try:
            yield session
            # Read sessions don't need commit (no mutations)
        except Exception as e:
            logger.warning(
                "read_session_error",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise


# Backward compatibility
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session (backward compatibility).
    
    Prefer get_write_session() or get_read_session() for new code.
    """
    async for session in get_write_session():
        yield session


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for database session (for use outside of FastAPI)."""
    async with write_session_maker() as session:
        try:
            yield session
            await session.commit()
            logger.debug("db_session_context_committed")
        except Exception as e:
            await session.rollback()
            logger.warning(
                "db_session_context_rollback",
                error=str(e),
                error_type=type(e).__name__,
            )
            raise


@asynccontextmanager
async def get_write_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for write session (outside FastAPI)."""
    async with write_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise


@asynccontextmanager
async def get_read_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Context manager for read session (outside FastAPI)."""
    async with read_session_maker() as session:
        yield session


# =============================================================================
# Database Lifecycle
# =============================================================================

async def init_database() -> None:
    """Initialize database - create all tables."""
    # Import the shared Base to register all models
    import src.features.process_mining.models
    import src.platform.models
    import src.platform.workflows.models  # noqa: F401 - Workflow, WorkflowTask
    from src.shared.database import Base

    logger.info("database_initializing", url=settings.database_url)
    async with write_engine.begin() as conn:
        # Create all tables (both platform and process mining use the same Base)
        await conn.run_sync(Base.metadata.create_all)
    logger.info("database_initialized")


async def close_database() -> None:
    """Close all database connections."""
    logger.info("database_closing")
    await write_engine.dispose()
    if settings.read_database_url:
        await read_engine.dispose()
    logger.info("database_closed")
