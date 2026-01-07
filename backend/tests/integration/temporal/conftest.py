"""Temporal Integration Test Fixtures.

Provides shared fixtures for Temporal workflow integration tests using
the Temporal SDK's WorkflowEnvironment for testing.
"""

from collections.abc import AsyncGenerator
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from src.infra.temporal.activities.analysis import (
    check_conformance_activity,
    compute_metrics_activity,
    load_event_log_activity,
    mine_model_activity,
)
from src.infra.temporal.activities.dataset import (
    bulk_copy_to_db_activity,
    compute_statistics_activity,
    detect_columns_activity,
    parse_to_parquet_activity,
    validate_file_activity,
)
from src.infra.temporal.config import get_temporal_config
from src.infra.temporal.workflows.analysis import (
    ConformanceCheckWorkflow,
    ProcessDiscoveryWorkflow,
)
from src.infra.temporal.workflows.ingestion import (
    DatasetIngestionWorkflow,
    DatasetValidationWorkflow,
)

# =============================================================================
# Test Data Fixtures
# =============================================================================


@dataclass
class TestDataset:
    """Test dataset metadata."""

    id: str
    storage_key: str
    case_id_column: str = "case_id"
    activity_column: str = "activity"
    timestamp_column: str = "timestamp"
    resource_column: str | None = "resource"


@pytest.fixture
def test_dataset() -> TestDataset:
    """Create a test dataset fixture."""
    return TestDataset(
        id=str(uuid4()),
        storage_key=f"test/{uuid4()}/test_log.csv",
    )


@pytest.fixture
def sample_csv_content() -> bytes:
    """Sample CSV content for testing."""
    return b"""case_id,activity,timestamp,resource
case_1,Start,2026-01-01 09:00:00,Alice
case_1,Process,2026-01-01 09:30:00,Bob
case_1,End,2026-01-01 10:00:00,Alice
case_2,Start,2026-01-01 10:00:00,Charlie
case_2,Process,2026-01-01 10:45:00,Alice
case_2,End,2026-01-01 11:00:00,Bob
case_3,Start,2026-01-01 11:00:00,Alice
case_3,Review,2026-01-01 11:30:00,Charlie
case_3,Process,2026-01-01 12:00:00,Bob
case_3,End,2026-01-01 12:30:00,Alice
"""


# =============================================================================
# Mock Storage Fixtures
# =============================================================================


@pytest.fixture
def mock_storage_client(sample_csv_content: bytes):
    """Mock S3/MinIO storage client."""
    mock_client = MagicMock()
    mock_client.download_fileobj.return_value = MagicMock(
        read=MagicMock(return_value=sample_csv_content)
    )
    mock_client.upload_fileobj.return_value = None

    with patch(
        "src.infra.temporal.activities.dataset.get_storage_client",
        return_value=mock_client,
    ):
        yield mock_client


# =============================================================================
# Mock Database Fixtures
# =============================================================================


@pytest.fixture
def mock_db_session():
    """Mock async database session."""
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar=MagicMock(return_value=1)))
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()

    # Context manager support
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    return mock_session


@pytest.fixture
def mock_session_factory(mock_db_session):
    """Mock session factory that returns mock session."""
    mock_factory = MagicMock()
    mock_factory.return_value = mock_db_session

    with (
        patch(
            "src.infra.temporal.activities.dataset.AsyncSessionLocal",
            mock_factory,
        ),
        patch(
            "src.infra.temporal.activities.analysis.AsyncSessionLocal",
            mock_factory,
        ),
    ):
        yield mock_factory


# =============================================================================
# Temporal Environment Fixtures
# =============================================================================


@pytest.fixture
async def temporal_env() -> AsyncGenerator[WorkflowEnvironment, None]:
    """Create Temporal test environment.

    Uses the time-skipping test server for faster tests.
    """
    async with await WorkflowEnvironment.start_time_skipping() as env:
        yield env


@pytest.fixture
async def temporal_client(temporal_env: WorkflowEnvironment) -> Client:
    """Get Temporal client from test environment."""
    return temporal_env.client


@pytest.fixture
async def ingestion_worker(
    temporal_env: WorkflowEnvironment,
    mock_storage_client,
    mock_session_factory,
) -> AsyncGenerator[Worker, None]:
    """Create worker for ingestion workflows with mocked dependencies."""
    config = get_temporal_config()

    async with Worker(
        temporal_env.client,
        task_queue=config.QUEUE_INGESTION,
        workflows=[DatasetIngestionWorkflow, DatasetValidationWorkflow],
        activities=[
            validate_file_activity,
            detect_columns_activity,
            parse_to_parquet_activity,
            bulk_copy_to_db_activity,
            compute_statistics_activity,
        ],
    ) as worker:
        yield worker


@pytest.fixture
async def analysis_worker(
    temporal_env: WorkflowEnvironment,
    mock_session_factory,
) -> AsyncGenerator[Worker, None]:
    """Create worker for analysis workflows with mocked dependencies."""
    config = get_temporal_config()

    async with Worker(
        temporal_env.client,
        task_queue=config.QUEUE_ANALYSIS,
        workflows=[ProcessDiscoveryWorkflow, ConformanceCheckWorkflow],
        activities=[
            load_event_log_activity,
            mine_model_activity,
            compute_metrics_activity,
            check_conformance_activity,
        ],
    ) as worker:
        yield worker


# =============================================================================
# Combined Worker Fixture
# =============================================================================


@pytest.fixture
async def all_workers(
    temporal_env: WorkflowEnvironment,
    mock_storage_client,
    mock_session_factory,
) -> AsyncGenerator[dict[str, Worker], None]:
    """Create all workers for full E2E tests."""
    config = get_temporal_config()

    async with (
        Worker(
            temporal_env.client,
            task_queue=config.QUEUE_INGESTION,
            workflows=[DatasetIngestionWorkflow, DatasetValidationWorkflow],
            activities=[
                validate_file_activity,
                detect_columns_activity,
                parse_to_parquet_activity,
                bulk_copy_to_db_activity,
                compute_statistics_activity,
            ],
        ) as ingestion_worker,
        Worker(
            temporal_env.client,
            task_queue=config.QUEUE_ANALYSIS,
            workflows=[ProcessDiscoveryWorkflow, ConformanceCheckWorkflow],
            activities=[
                load_event_log_activity,
                mine_model_activity,
                compute_metrics_activity,
                check_conformance_activity,
            ],
        ) as analysis_worker,
    ):
        yield {
            "ingestion": ingestion_worker,
            "analysis": analysis_worker,
        }


# =============================================================================
# Cleanup Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
async def cleanup_workflows(temporal_env: WorkflowEnvironment):
    """Auto-cleanup running workflows after each test."""
    yield
    # Cleanup happens automatically when WorkflowEnvironment context exits
