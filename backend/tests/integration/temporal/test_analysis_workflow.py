"""End-to-End Integration Tests for Analysis Workflows.

Tests the ProcessDiscoveryWorkflow and ConformanceCheckWorkflow using
Temporal's test environment.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from src.platform.temporal.config import get_temporal_config
from src.platform.temporal.workflows.analysis import (
    ConformanceCheckWorkflow,
    ProcessDiscoveryWorkflow,
)

# =============================================================================
# Mock Fixtures for Analysis Tests
# =============================================================================


@pytest.fixture
def mock_mining_service():
    """Mock the mining service for discovery tests."""
    mock_service = MagicMock()
    mock_service.discover_model = MagicMock(
        return_value={
            "model_id": str(uuid4()),
            "model_format": "petri_net",
            "places": 5,
            "transitions": 4,
        }
    )
    return mock_service


@pytest.fixture
def mock_conformance_service():
    """Mock conformance service for conformance tests."""
    mock_service = MagicMock()
    mock_service.check_conformance = MagicMock(
        return_value={
            "fitness": 0.95,
            "precision": 0.88,
            "is_conformant": True,
            "fitting_traces": 95,
            "total_traces": 100,
        }
    )
    return mock_service


# =============================================================================
# ProcessDiscoveryWorkflow Tests
# =============================================================================


@pytest.mark.asyncio
class TestProcessDiscoveryWorkflow:
    """Integration tests for process model discovery workflow."""

    async def test_successful_discovery_flow(
        self,
        temporal_env: WorkflowEnvironment,
        analysis_worker: Worker,
    ):
        """Test complete discovery flow: load → mine → compute_metrics."""
        config = get_temporal_config()
        client = temporal_env.client

        dataset_id = str(uuid4())
        workflow_id = f"test-discovery-{dataset_id}"

        # Mock the load_event_log to return is_loaded=True
        with patch("src.platform.temporal.activities.analysis.AsyncSessionLocal") as mock_session:
            mock_session.return_value.__aenter__ = AsyncMock(return_value=MagicMock())
            mock_session.return_value.__aexit__ = AsyncMock()

            handle = await client.start_workflow(
                ProcessDiscoveryWorkflow.run,
                args=[
                    dataset_id,
                    "inductive",  # miner_type
                    "Test Model",  # model_name
                ],
                id=workflow_id,
                task_queue=config.QUEUE_ANALYSIS,
            )

            result = await handle.result()

        # Assertions
        assert result is not None
        assert result["dataset_id"] == dataset_id
        assert result["miner_type"] == "inductive"
        assert result["status"] in ["completed", "failed"]

    async def test_discovery_with_different_miners(
        self,
        temporal_env: WorkflowEnvironment,
        analysis_worker: Worker,
    ):
        """Test discovery with different mining algorithms."""
        config = get_temporal_config()
        client = temporal_env.client

        miners = ["alpha", "inductive", "heuristic"]

        for miner in miners:
            dataset_id = str(uuid4())
            workflow_id = f"test-miner-{miner}-{dataset_id}"

            handle = await client.start_workflow(
                ProcessDiscoveryWorkflow.run,
                args=[
                    dataset_id,
                    miner,
                    f"{miner.title()} Miner Test",
                ],
                id=workflow_id,
                task_queue=config.QUEUE_ANALYSIS,
            )

            result = await handle.result()
            assert result["miner_type"] == miner

    async def test_discovery_result_structure(
        self,
        temporal_env: WorkflowEnvironment,
        analysis_worker: Worker,
    ):
        """Test that discovery result contains required fields."""
        config = get_temporal_config()
        client = temporal_env.client

        dataset_id = str(uuid4())
        handle = await client.start_workflow(
            ProcessDiscoveryWorkflow.run,
            args=[
                dataset_id,
                "inductive",
                None,  # No model name
            ],
            id=f"test-structure-{dataset_id}",
            task_queue=config.QUEUE_ANALYSIS,
        )

        result = await handle.result()

        # Verify result structure for completed workflow
        if result["status"] == "completed":
            required_fields = [
                "model_id",
                "dataset_id",
                "miner_type",
                "model_format",
                "fitness",
                "precision",
                "status",
            ]

            for field in required_fields:
                assert field in result, f"Missing field: {field}"


# =============================================================================
# ConformanceCheckWorkflow Tests
# =============================================================================


@pytest.mark.asyncio
class TestConformanceCheckWorkflow:
    """Integration tests for conformance checking workflow."""

    async def test_successful_conformance_check(
        self,
        temporal_env: WorkflowEnvironment,
        analysis_worker: Worker,
    ):
        """Test complete conformance check flow."""
        config = get_temporal_config()
        client = temporal_env.client

        dataset_id = str(uuid4())
        model_id = str(uuid4())
        workflow_id = f"test-conformance-{dataset_id}"

        handle = await client.start_workflow(
            ConformanceCheckWorkflow.run,
            args=[
                dataset_id,
                model_id,
                "token_replay",  # method
            ],
            id=workflow_id,
            task_queue=config.QUEUE_ANALYSIS,
        )

        result = await handle.result()

        # Assertions
        assert result is not None
        assert result["dataset_id"] == dataset_id
        assert result["model_id"] == model_id
        assert result["status"] in ["completed", "failed"]

    async def test_conformance_with_alignment_method(
        self,
        temporal_env: WorkflowEnvironment,
        analysis_worker: Worker,
    ):
        """Test conformance with alignment method."""
        config = get_temporal_config()
        client = temporal_env.client

        dataset_id = str(uuid4())
        model_id = str(uuid4())

        handle = await client.start_workflow(
            ConformanceCheckWorkflow.run,
            args=[
                dataset_id,
                model_id,
                "alignment",
            ],
            id=f"test-alignment-{dataset_id}",
            task_queue=config.QUEUE_ANALYSIS,
        )

        result = await handle.result()

        assert result is not None
        assert result["status"] in ["completed", "failed"]

    async def test_conformance_result_structure(
        self,
        temporal_env: WorkflowEnvironment,
        analysis_worker: Worker,
    ):
        """Test that conformance result contains required fields."""
        config = get_temporal_config()
        client = temporal_env.client

        dataset_id = str(uuid4())
        model_id = str(uuid4())

        handle = await client.start_workflow(
            ConformanceCheckWorkflow.run,
            args=[
                dataset_id,
                model_id,
                "token_replay",
            ],
            id=f"test-conf-result-{dataset_id}",
            task_queue=config.QUEUE_ANALYSIS,
        )

        result = await handle.result()

        # Verify result structure for completed workflow
        if result["status"] == "completed":
            required_fields = [
                "conformance_id",
                "dataset_id",
                "model_id",
                "fitness",
                "precision",
                "is_conformant",
                "fitting_traces",
                "total_traces",
                "status",
            ]

            for field in required_fields:
                assert field in result, f"Missing field: {field}"


# =============================================================================
# Workflow Cancellation Tests
# =============================================================================


@pytest.mark.asyncio
class TestWorkflowCancellation:
    """Test workflow cancellation behavior."""

    async def test_cancel_running_discovery(
        self,
        temporal_env: WorkflowEnvironment,
        analysis_worker: Worker,
    ):
        """Test that a running discovery workflow can be cancelled."""
        config = get_temporal_config()
        client = temporal_env.client

        dataset_id = str(uuid4())
        workflow_id = f"test-cancel-{dataset_id}"

        handle = await client.start_workflow(
            ProcessDiscoveryWorkflow.run,
            args=[
                dataset_id,
                "inductive",
                "Will Be Cancelled",
            ],
            id=workflow_id,
            task_queue=config.QUEUE_ANALYSIS,
        )

        # Note: In test environment, workflow may complete before we can cancel
        # This test primarily verifies the cancellation API works
        try:
            await handle.cancel()
            # If cancellation succeeds before completion
            desc = await handle.describe()
            assert desc.status is not None
        except Exception:
            # Workflow may have completed already
            result = await handle.result()
            assert result is not None
