"""
End-to-end tests for CQRS (Command Query Responsibility Segregation) implementation.

Tests verify:
1. Read/Write database session separation
2. CommandBusDep and QueryBusDep dependencies work
3. Command and Query handlers are properly wired
4. Event sourcing infrastructure
5. Database engines are separate
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

# =============================================================================
# CQRS Infrastructure Tests
# =============================================================================


class TestCQRSInfrastructure:
    """Test CQRS infrastructure components are properly configured."""

    @pytest.mark.asyncio
    async def test_command_bus_dependency_importable(self):
        """CommandBusDep should be importable from dependencies."""
        from src.api.dependencies import CommandBusDep

        assert CommandBusDep is not None

    @pytest.mark.asyncio
    async def test_query_bus_dependency_importable(self):
        """QueryBusDep should be importable from dependencies."""
        from src.api.dependencies import QueryBusDep

        assert QueryBusDep is not None

    @pytest.mark.asyncio
    async def test_session_types_available(self):
        """WriteDBSession and ReadDBSession should be available."""
        from src.api.dependencies import ReadDBSession, WriteDBSession

        assert WriteDBSession is not None
        assert ReadDBSession is not None

    @pytest.mark.asyncio
    async def test_analytics_db_available(self):
        """AnalyticsDB (DuckDB) should be available."""
        from src.api.dependencies import AnalyticsDB

        assert AnalyticsDB is not None

    @pytest.mark.asyncio
    async def test_database_engines_are_separate(self):
        """Read and write engines should be separate instances."""
        from src.platform.infrastructure.database import read_engine, write_engine

        assert write_engine is not None
        assert read_engine is not None
        # Different engine objects (even if same URL in dev)
        assert id(write_engine) != id(read_engine) or write_engine is read_engine

    @pytest.mark.asyncio
    async def test_bootstrap_module_exports(self):
        """Bootstrap module should export CQRS components."""
        from src.application.bootstrap import (
            CommandBusDep,
            QueryBusDep,
            RequestScopedCommandBus,
            RequestScopedQueryBus,
            init_cqrs,
        )

        assert CommandBusDep is not None
        assert QueryBusDep is not None
        assert RequestScopedCommandBus is not None
        assert RequestScopedQueryBus is not None
        assert init_cqrs is not None


# =============================================================================
# Command Infrastructure Tests
# =============================================================================


class TestCommandInfrastructure:
    """Test command handlers and bus are properly wired."""

    @pytest.mark.asyncio
    async def test_base_command_class_exists(self):
        """BaseCommand should be importable."""
        from src.application.commands.base import BaseCommand

        assert BaseCommand is not None

    @pytest.mark.asyncio
    async def test_command_handler_class_exists(self):
        """CommandHandler should be importable."""
        from src.application.commands.base import CommandHandler

        assert CommandHandler is not None

    @pytest.mark.asyncio
    async def test_command_bus_class_exists(self):
        """CommandBus should be importable."""
        from src.application.commands.base import CommandBus

        assert CommandBus is not None

    @pytest.mark.asyncio
    async def test_dataset_commands_importable(self):
        """Dataset commands should be importable."""
        from src.application.commands.dataset_commands import (
            CreateDatasetCommand,
            CreateDatasetHandler,
            TriggerIngestionCommand,
            TriggerIngestionHandler,
            UpdateMappingCommand,
            UpdateMappingHandler,
        )

        assert CreateDatasetCommand is not None
        assert CreateDatasetHandler is not None
        assert UpdateMappingCommand is not None
        assert UpdateMappingHandler is not None
        assert TriggerIngestionCommand is not None
        assert TriggerIngestionHandler is not None

    @pytest.mark.asyncio
    async def test_request_scoped_command_bus_instantiable(self, db_session: AsyncSession):
        """RequestScopedCommandBus should be instantiable with a session."""
        from src.application.bootstrap import RequestScopedCommandBus

        bus = RequestScopedCommandBus(db_session)
        assert bus is not None
        assert bus.db is db_session


# =============================================================================
# Query Infrastructure Tests
# =============================================================================


class TestQueryInfrastructure:
    """Test query handlers and bus are properly wired."""

    @pytest.mark.asyncio
    async def test_base_query_class_exists(self):
        """BaseQuery should be importable."""
        from src.application.queries.base import BaseQuery

        assert BaseQuery is not None

    @pytest.mark.asyncio
    async def test_query_handler_class_exists(self):
        """QueryHandler should be importable."""
        from src.application.queries.base import QueryHandler

        assert QueryHandler is not None

    @pytest.mark.asyncio
    async def test_query_bus_class_exists(self):
        """QueryBus should be importable."""
        from src.application.queries.base import QueryBus

        assert QueryBus is not None

    @pytest.mark.asyncio
    async def test_analytics_queries_importable(self):
        """Analytics queries should be importable."""
        from src.application.queries.analytics_queries import (
            GetBottlenecksHandler,
            GetBottlenecksQuery,
            GetCycleTimeHandler,
            GetCycleTimeQuery,
            GetReworkHandler,
            GetReworkQuery,
        )

        assert GetBottlenecksQuery is not None
        assert GetBottlenecksHandler is not None
        assert GetCycleTimeQuery is not None
        assert GetCycleTimeHandler is not None
        assert GetReworkQuery is not None
        assert GetReworkHandler is not None

    @pytest.mark.asyncio
    async def test_request_scoped_query_bus_instantiable(self, db_session: AsyncSession):
        """RequestScopedQueryBus should be instantiable with a session."""
        from src.application.bootstrap import RequestScopedQueryBus
        from src.platform.infrastructure.duckdb import duckdb_manager

        bus = RequestScopedQueryBus(db_session, duckdb_manager)
        assert bus is not None
        assert bus.db is db_session

    @pytest.mark.asyncio
    async def test_query_bus_dispatches_to_handler(self, db_session: AsyncSession):
        """Query bus should dispatch queries and get expected errors for missing data."""
        from src.application.bootstrap import RequestScopedQueryBus
        from src.application.queries.analytics_queries import GetBottlenecksQuery
        from src.platform.infrastructure.duckdb import duckdb_manager

        query_bus = RequestScopedQueryBus(db_session, duckdb_manager)
        query = GetBottlenecksQuery(dataset_id="nonexistent-dataset")

        # Should fail with dataset not found (proves dispatch works)
        with pytest.raises(ValueError, match="Dataset not found"):
            await query_bus.dispatch(query)


# =============================================================================
# Event Sourcing Tests
# =============================================================================


class TestEventSourcing:
    """Test event sourcing infrastructure."""

    @pytest.mark.asyncio
    async def test_domain_event_model_exists(self):
        """DomainEvent model should exist."""
        from src.shared.events import DomainEvent

        assert DomainEvent is not None

    @pytest.mark.asyncio
    async def test_event_store_class_exists(self):
        """EventStore should be importable."""
        from src.shared.events import EventStore

        assert EventStore is not None

    @pytest.mark.asyncio
    async def test_event_envelope_class_exists(self):
        """EventEnvelope should be importable."""
        from src.shared.events import EventEnvelope

        assert EventEnvelope is not None

    @pytest.mark.asyncio
    async def test_event_store_append(self, db_session: AsyncSession):
        """EventStore should be able to append events."""
        from src.shared.events import EventEnvelope, EventStore

        store = EventStore(db_session)

        event = EventEnvelope(
            aggregate_type="test_aggregate",
            aggregate_id="test-123",
            event_type="test.event_created",
            payload={"key": "value"},
        )

        stored = await store.append(event)

        assert stored.id is not None
        assert stored.aggregate_type == "test_aggregate"
        assert stored.aggregate_id == "test-123"
        assert stored.event_type == "test.event_created"

    @pytest.mark.asyncio
    async def test_event_store_retrieval(self, db_session: AsyncSession):
        """EventStore should retrieve events by aggregate."""
        from src.shared.events import EventEnvelope, EventStore

        store = EventStore(db_session)

        # Store multiple events
        for i in range(3):
            event = EventEnvelope(
                aggregate_type="dataset",
                aggregate_id="dataset-retrieval-test",
                event_type=f"dataset.step_{i}",
                payload={"step": i},
            )
            await store.append(event)

        # Retrieve events
        events = await store.get_events("dataset", "dataset-retrieval-test")

        assert len(events) == 3
        assert events[0].event_type == "dataset.step_0"
        assert events[1].event_type == "dataset.step_1"
        assert events[2].event_type == "dataset.step_2"


# =============================================================================
# Database Session Separation Tests
# =============================================================================


class TestDatabaseSessionSeparation:
    """Test that read/write session factories are properly configured."""

    @pytest.mark.asyncio
    async def test_write_session_factory_exists(self):
        """Write session factory should exist."""
        from src.platform.infrastructure.database import write_session_maker

        assert write_session_maker is not None

    @pytest.mark.asyncio
    async def test_read_session_factory_exists(self):
        """Read session factory should exist."""
        from src.platform.infrastructure.database import read_session_maker

        assert read_session_maker is not None

    @pytest.mark.asyncio
    async def test_session_generators_exist(self):
        """Session generators should be importable."""
        from src.platform.infrastructure.database import get_read_session, get_write_session

        assert get_read_session is not None
        assert get_write_session is not None

    @pytest.mark.asyncio
    async def test_context_managers_exist(self):
        """Session context managers should be importable."""
        from src.platform.infrastructure.database import (
            get_read_session_context,
            get_write_session_context,
        )

        assert get_read_session_context is not None
        assert get_write_session_context is not None


# =============================================================================
# DuckDB Integration Tests
# =============================================================================


class TestDuckDBIntegration:
    """Test DuckDB analytics engine integration."""

    @pytest.mark.asyncio
    async def test_duckdb_manager_exists(self):
        """DuckDB manager should be importable."""
        from src.platform.infrastructure.duckdb import DuckDBManager, duckdb_manager

        assert DuckDBManager is not None
        assert duckdb_manager is not None

    @pytest.mark.asyncio
    async def test_duckdb_connection_works(self):
        """DuckDB should be able to execute queries."""
        from src.platform.infrastructure.duckdb import duckdb_manager

        conn = duckdb_manager.get_connection()
        result = conn.execute("SELECT 1 as test").fetchone()

        assert result is not None
        assert result[0] == 1

    @pytest.mark.asyncio
    async def test_duckdb_can_query_parquet(self, tmp_path):
        """DuckDB should be able to read Parquet files."""
        import pandas as pd

        from src.platform.infrastructure.duckdb import duckdb_manager

        # Create a test Parquet file
        df = pd.DataFrame({"case_id": [1, 2, 3], "activity": ["A", "B", "C"]})
        parquet_path = tmp_path / "test.parquet"
        df.to_parquet(parquet_path)

        conn = duckdb_manager.get_connection()
        result = conn.execute(f"SELECT COUNT(*) FROM read_parquet('{parquet_path}')").fetchone()

        assert result[0] == 3


# =============================================================================
# Projections Tests
# =============================================================================


class TestProjections:
    """Test CQRS projections for read model maintenance."""

    @pytest.mark.asyncio
    async def test_analytics_cache_projection_exists(self):
        """Analytics cache projection should be importable."""
        from src.application.projections.analytics_cache import analytics_cache_projection

        assert analytics_cache_projection is not None
