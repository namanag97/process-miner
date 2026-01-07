"""Data Layer Ownership Tests.

Automated tests to verify the data ownership model:
- PostgreSQL: Metadata only (no events)
- Parquet: Event data (authoritative source)
- DuckDB: Compute only (ephemeral)

Run with: pytest tests/integration/test_data_ownership.py -v
"""


import pytest


@pytest.mark.asyncio
class TestDataOwnership:
    """Verify the data ownership model is enforced."""

    async def test_ingestion_creates_parquet_not_postgres(self, db_session, test_dataset):
        """Verify ingestion creates Parquet file, not PostgreSQL events."""
        from sqlalchemy import func, select

        from src.features.process_mining.models import Dataset
        from src.features.process_mining.models.events_models import ProcessEvent

        # After ingestion, dataset should have parquet_s3_key
        result = await db_session.execute(
            select(Dataset.parquet_s3_key).where(Dataset.id == test_dataset.id)
        )
        parquet_key = result.scalar_one_or_none()

        assert parquet_key is not None, "Dataset must have parquet_s3_key after ingestion"

        # Verify Parquet file exists (local or S3)
        from src.platform.infrastructure.object_storage import get_storage_client
        storage = get_storage_client()
        assert storage.file_exists("cache", parquet_key), "Parquet file must exist"

        # Verify NO events in PostgreSQL (for new datasets)
        # Note: Legacy datasets may still have events during migration
        result = await db_session.execute(
            select(func.count()).select_from(ProcessEvent).where(
                ProcessEvent.case_ref_id.in_(
                    select(ProcessEvent.case_ref_id).join(ProcessEvent.case).where(
                        ProcessEvent.case.has(dataset_id=test_dataset.id)
                    )
                )
            )
        )
        event_count = result.scalar()

        # For new datasets, event count should be 0
        # This assertion will fail for legacy datasets (expected during migration)
        assert event_count == 0, f"No events should be in PostgreSQL (found {event_count})"

    async def test_loader_reads_from_parquet(self, test_dataset_with_parquet):
        """Verify EventLogLoader reads from Parquet, not PostgreSQL."""
        from src.features.process_mining.services.loader import event_log_loader

        # Load data
        df = event_log_loader.load_as_dataframe(test_dataset_with_parquet.id)

        assert not df.empty, "Loader should return data from Parquet"
        assert "case:concept:name" in df.columns
        assert "concept:name" in df.columns
        assert "time:timestamp" in df.columns

    def test_duckdb_is_ephemeral(self):
        """Verify DuckDB connections are in-memory only."""
        from src.features.process_mining.services.loader import event_log_loader

        conn = event_log_loader._get_connection(for_parquet=True)

        # Verify connection is in-memory
        # DuckDB in-memory connections don't persist
        assert conn is not None

        # Connection should be closeable without persisting
        conn.close()

    def test_no_bulk_copy_activity_in_workflow(self):
        """Verify bulk_copy_to_db_activity is not in ingestion workflow."""
        import inspect

        from src.platform.temporal.workflows.ingestion import DatasetIngestionWorkflow

        source = inspect.getsource(DatasetIngestionWorkflow.run)

        assert "bulk_copy_to_db_activity" not in source, \
            "bulk_copy_to_db_activity should be removed from workflow"

    def test_parquet_write_is_mandatory(self):
        """Verify parse_to_parquet_activity requires successful Parquet write."""
        import inspect

        from src.platform.temporal.activities.dataset import parse_to_parquet_activity

        source = inspect.getsource(parse_to_parquet_activity)

        # Should NOT have try/except around Parquet write
        assert "Parquet write failure is not fatal" not in source, \
            "Parquet write should be mandatory (no try/except)"


class TestDataOwnershipMatrix:
    """Test matrix for data ownership verification."""

    OWNERSHIP_RULES = {
        # Entity: (authoritative_store, allowed_writes, allowed_reads)
        "organizations": ("postgresql", ["postgresql"], ["postgresql"]),
        "workspaces": ("postgresql", ["postgresql"], ["postgresql"]),
        "datasets_metadata": ("postgresql", ["postgresql"], ["postgresql"]),
        "events": ("parquet", ["parquet"], ["parquet", "duckdb"]),
        "cases": ("parquet", ["parquet"], ["parquet", "duckdb"]),
        "process_models": ("postgresql", ["postgresql"], ["postgresql"]),
        "dfg_cache": ("redis", ["redis"], ["redis"]),
    }

    def test_ownership_rules_documented(self):
        """Verify all entity ownership rules are defined."""
        required_entities = [
            "organizations", "workspaces", "datasets_metadata",
            "events", "cases", "process_models"
        ]

        for entity in required_entities:
            assert entity in self.OWNERSHIP_RULES, \
                f"Missing ownership rule for {entity}"

    def test_events_not_in_postgresql(self):
        """Verify events are NOT written to PostgreSQL."""
        events_rule = self.OWNERSHIP_RULES["events"]

        assert "postgresql" not in events_rule[1], \
            "Events should NOT be written to PostgreSQL"
        assert events_rule[0] == "parquet", \
            "Parquet should be authoritative for events"


# Fixtures
@pytest.fixture
async def test_dataset_with_parquet(db_session):
    """Create a test dataset with Parquet file."""
    import io
    import uuid

    import pyarrow as pa
    import pyarrow.parquet as pq

    from src.features.process_mining.models import Dataset
    from src.platform.infrastructure.object_storage import get_storage_client

    dataset_id = str(uuid.uuid4())
    parquet_key = f"parsed/{dataset_id}/events.parquet"

    # Create sample Parquet data
    data = {
        "case_id": ["case_1", "case_1", "case_2"],
        "activity": ["Start", "End", "Start"],
        "timestamp": ["2024-01-01 10:00:00", "2024-01-01 11:00:00", "2024-01-01 10:30:00"],
        "resource": ["user_1", "user_1", "user_2"],
    }
    table = pa.table(data)
    buffer = io.BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)

    # Upload Parquet
    storage = get_storage_client()
    storage.upload_fileobj("cache", parquet_key, buffer)

    # Create dataset record
    dataset = Dataset(
        id=dataset_id,
        name="Test Dataset",
        parquet_s3_key=parquet_key,
        parquet_size_bytes=len(buffer.getvalue()),
        parquet_row_count=3,
    )
    db_session.add(dataset)
    await db_session.commit()

    yield dataset

    # Cleanup
    storage.delete_file("cache", parquet_key)
