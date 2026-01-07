"""CQRS Bootstrap - Wire command and query buses with handlers.

This module initializes the CQRS infrastructure by:
1. Creating handler factories that receive dependencies
2. Providing FastAPI dependencies for command/query buses
3. Auto-registering handlers on startup

Usage:
    # In main.py startup
    from src.application.bootstrap import init_cqrs
    await init_cqrs()

    # In routes - inject the buses
    from src.application.bootstrap import CommandBusDep, QueryBusDep

    @router.post("/datasets")
    async def create_dataset(
        command_bus: CommandBusDep,
        ...
    ):
        return await command_bus.dispatch(CreateDatasetCommand(...))
"""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.commands.base import command_bus
from src.application.queries.base import query_bus
from src.infra.core.logging_config import get_logger
from src.infra.infrastructure.duckdb import DuckDBManager, duckdb_manager

logger = get_logger(__name__)


# =============================================================================
# Handler Factories - Create handlers with injected dependencies
# =============================================================================


class CommandHandlerFactory:
    """Factory for creating command handlers with dependencies.

    Handlers are created per-request with the appropriate database session.
    """

    def __init__(self, db: AsyncSession, event_store=None):
        self.db = db
        self.event_store = event_store

    def create_ingest_handler(self):
        from src.application.commands.ingest_dataset import IngestDatasetHandler
        return IngestDatasetHandler(self.db)

    def create_delete_handler(self):
        from src.application.commands.delete_dataset import DeleteDatasetHandler
        return DeleteDatasetHandler(self.db)

    def create_dataset_handler(self):
        from src.application.commands.dataset_commands import CreateDatasetHandler
        return CreateDatasetHandler(self.db, self.event_store)

    def create_mapping_handler(self):
        from src.application.commands.dataset_commands import UpdateMappingHandler
        return UpdateMappingHandler(self.db, self.event_store)

    def create_trigger_ingestion_handler(self):
        from src.application.commands.dataset_commands import TriggerIngestionHandler
        return TriggerIngestionHandler(self.db, self.event_store)


class QueryHandlerFactory:
    """Factory for creating query handlers with dependencies.

    Handlers are created per-request with database session and DuckDB connection.
    """

    def __init__(self, db: AsyncSession, duckdb: DuckDBManager):
        self.db = db
        self.duckdb = duckdb

    def create_bottlenecks_handler(self):
        from src.application.queries.analytics_queries import GetBottlenecksHandler
        return GetBottlenecksHandler(
            duckdb_conn=self.duckdb.get_connection(),
            db=self.db,
        )

    def create_cycle_time_handler(self):
        from src.application.queries.analytics_queries import GetCycleTimeHandler
        return GetCycleTimeHandler(
            duckdb_conn=self.duckdb.get_connection(),
            db=self.db,
        )

    def create_rework_handler(self):
        from src.application.queries.analytics_queries import GetReworkHandler
        return GetReworkHandler(
            duckdb_conn=self.duckdb.get_connection(),
            db=self.db,
        )

    def create_variants_handler(self):
        from src.application.queries.get_variants import GetVariantsHandler
        return GetVariantsHandler(
            duckdb_conn=self.duckdb.get_connection(),
            db=self.db,
        )


# =============================================================================
# Request-Scoped Bus Wrappers
# =============================================================================


class RequestScopedCommandBus:
    """Command bus wrapper that creates handlers per-request.

    This ensures each request gets a fresh handler with its own DB session.
    """

    def __init__(self, db: AsyncSession, event_store=None):
        self.db = db
        self._factory = CommandHandlerFactory(db, event_store)

    async def dispatch(self, command):
        """Dispatch command to appropriate handler."""
        from src.application.commands.dataset_commands import (
            CreateDatasetCommand,
            TriggerIngestionCommand,
            UpdateMappingCommand,
        )
        from src.application.commands.delete_dataset import DeleteDatasetCommand
        from src.application.commands.ingest_dataset import IngestDatasetCommand

        command_type = type(command).__name__

        logger.info(
            "command_dispatching",
            command_type=command_type,
            correlation_id=getattr(command, 'correlation_id', None),
        )

        # Route to appropriate handler
        if isinstance(command, IngestDatasetCommand):
            handler = self._factory.create_ingest_handler()
        elif isinstance(command, DeleteDatasetCommand):
            handler = self._factory.create_delete_handler()
        elif isinstance(command, CreateDatasetCommand):
            handler = self._factory.create_dataset_handler()
        elif isinstance(command, UpdateMappingCommand):
            handler = self._factory.create_mapping_handler()
        elif isinstance(command, TriggerIngestionCommand):
            handler = self._factory.create_trigger_ingestion_handler()
        else:
            raise ValueError(f"No handler for command: {command_type}")

        try:
            result = await handler.handle(command)
            logger.info("command_completed", command_type=command_type)
            return result
        except Exception as e:
            logger.error("command_failed", command_type=command_type, error=str(e))
            raise


class RequestScopedQueryBus:
    """Query bus wrapper that creates handlers per-request.

    This ensures each request gets fresh handlers with proper dependencies.
    """

    def __init__(self, db: AsyncSession, duckdb: DuckDBManager):
        self.db = db
        self.duckdb = duckdb
        self._factory = QueryHandlerFactory(db, duckdb)

    async def dispatch(self, query):
        """Dispatch query to appropriate handler."""
        from src.application.queries.analytics_queries import (
            GetBottlenecksQuery,
            GetCycleTimeQuery,
            GetReworkQuery,
            GetVariantsQuery,
        )

        query_type = type(query).__name__

        logger.debug("query_dispatching", query_type=query_type)

        # Route to appropriate handler
        if isinstance(query, GetBottlenecksQuery):
            handler = self._factory.create_bottlenecks_handler()
        elif isinstance(query, GetCycleTimeQuery):
            handler = self._factory.create_cycle_time_handler()
        elif isinstance(query, GetReworkQuery):
            handler = self._factory.create_rework_handler()
        elif isinstance(query, GetVariantsQuery):
            handler = self._factory.create_variants_handler()
        else:
            raise ValueError(f"No handler for query: {query_type}")

        try:
            result = await handler.handle(query)
            logger.debug("query_completed", query_type=query_type)
            return result
        except Exception as e:
            logger.error("query_failed", query_type=query_type, error=str(e))
            raise


# =============================================================================
# FastAPI Dependencies
# =============================================================================


async def get_command_bus() -> AsyncGenerator[RequestScopedCommandBus, None]:
    """Get request-scoped command bus."""
    from src.infra.infrastructure.database import get_write_session
    from src.shared.events import EventStore

    async for session in get_write_session():
        event_store = EventStore(session)
        yield RequestScopedCommandBus(session, event_store)


async def get_query_bus() -> AsyncGenerator[RequestScopedQueryBus, None]:
    """Get request-scoped query bus."""
    from src.infra.infrastructure.database import get_read_session

    async for session in get_read_session():
        yield RequestScopedQueryBus(session, duckdb_manager)


# Type aliases for dependency injection
CommandBusDep = Annotated[RequestScopedCommandBus, Depends(get_command_bus)]
QueryBusDep = Annotated[RequestScopedQueryBus, Depends(get_query_bus)]


# =============================================================================
# Initialization
# =============================================================================


async def init_cqrs() -> None:
    """Initialize CQRS infrastructure.

    Called during application startup to:
    1. Verify DuckDB connection
    2. Initialize projections
    3. Log CQRS readiness
    """
    logger.info("cqrs_initializing")

    # Verify DuckDB is ready
    try:
        conn = duckdb_manager.get_connection()
        conn.execute("SELECT 1").fetchone()
        logger.info("duckdb_ready")
    except Exception as e:
        logger.error("duckdb_init_failed", error=str(e))
        raise

    # Initialize projections (they auto-register event handlers)
    from src.application.projections.analytics_cache import analytics_cache_projection
    _ = analytics_cache_projection  # Ensure it's loaded

    logger.info("cqrs_initialized", status="ready")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "CommandBusDep",
    "QueryBusDep",
    "RequestScopedCommandBus",
    "RequestScopedQueryBus",
    "command_bus",
    "init_cqrs",
    "query_bus",
]
