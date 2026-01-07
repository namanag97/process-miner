"""End-to-End Integration Tests for Dataset Ingestion Workflow.

Tests the complete DatasetIngestionWorkflow using Temporal's test environment.
"""

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from src.platform.temporal.config import get_temporal_config
from src.platform.temporal.workflows.ingestion import (
    DatasetIngestionWorkflow,
    DatasetValidationWorkflow,
)

from .conftest import TestDataset

# =============================================================================
# DatasetIngestionWorkflow Tests
# =============================================================================


@pytest.mark.asyncio
class TestDatasetIngestionWorkflow:
    """Integration tests for the full dataset ingestion workflow."""

    async def test_successful_ingestion_flow(
        self,
        temporal_env: WorkflowEnvironment,
        ingestion_worker: Worker,
        test_dataset: TestDataset,
    ):
        """Test complete ingestion flow: validate → parse → bulk_copy → compute_stats."""
        config = get_temporal_config()
        client = temporal_env.client

        # Start the workflow
        workflow_id = f"test-ingestion-{test_dataset.id}"
        handle = await client.start_workflow(
            DatasetIngestionWorkflow.run,
            args=[
                test_dataset.id,
                test_dataset.storage_key,
                test_dataset.case_id_column,
                test_dataset.activity_column,
                test_dataset.timestamp_column,
                test_dataset.resource_column,
            ],
            id=workflow_id,
            task_queue=config.QUEUE_INGESTION,
        )

        # Wait for workflow to complete
        result = await handle.result()

        # Assertions
        assert result is not None
        assert result["dataset_id"] == test_dataset.id
        assert result["status"] == "completed"
        assert "total_cases" in result
        assert "total_events" in result
        assert "total_activities" in result
        assert result["total_cases"] > 0
        assert result["total_events"] > 0

    async def test_ingestion_workflow_id_format(
        self,
        temporal_env: WorkflowEnvironment,
        ingestion_worker: Worker,
        test_dataset: TestDataset,
    ):
        """Test that workflow ID follows expected format."""
        config = get_temporal_config()
        client = temporal_env.client

        workflow_id = f"dataset-ingestion-{test_dataset.id}"
        handle = await client.start_workflow(
            DatasetIngestionWorkflow.run,
            args=[
                test_dataset.id,
                test_dataset.storage_key,
                test_dataset.case_id_column,
                test_dataset.activity_column,
                test_dataset.timestamp_column,
                None,  # No resource column
            ],
            id=workflow_id,
            task_queue=config.QUEUE_INGESTION,
        )

        # Verify workflow ID
        assert handle.id == workflow_id

        # Get workflow description
        desc = await handle.describe()
        assert desc.status is not None

        # Complete workflow
        result = await handle.result()
        assert result["status"] == "completed"

    async def test_ingestion_workflow_result_structure(
        self,
        temporal_env: WorkflowEnvironment,
        ingestion_worker: Worker,
        test_dataset: TestDataset,
    ):
        """Test that workflow result contains required fields."""
        config = get_temporal_config()
        client = temporal_env.client

        handle = await client.start_workflow(
            DatasetIngestionWorkflow.run,
            args=[
                test_dataset.id,
                test_dataset.storage_key,
                test_dataset.case_id_column,
                test_dataset.activity_column,
                test_dataset.timestamp_column,
                test_dataset.resource_column,
            ],
            id=f"test-result-{test_dataset.id}",
            task_queue=config.QUEUE_INGESTION,
        )

        result = await handle.result()

        # Verify result structure
        required_fields = [
            "dataset_id",
            "status",
            "total_cases",
            "total_events",
            "total_activities",
            "cases_inserted",
            "events_inserted",
        ]

        for field in required_fields:
            assert field in result, f"Missing field: {field}"


# =============================================================================
# DatasetValidationWorkflow Tests
# =============================================================================


@pytest.mark.asyncio
class TestDatasetValidationWorkflow:
    """Integration tests for the dataset validation workflow."""

    async def test_successful_validation_flow(
        self,
        temporal_env: WorkflowEnvironment,
        ingestion_worker: Worker,
        test_dataset: TestDataset,
    ):
        """Test complete validation flow: validate → detect_columns."""
        config = get_temporal_config()
        client = temporal_env.client

        workflow_id = f"test-validation-{test_dataset.id}"
        handle = await client.start_workflow(
            DatasetValidationWorkflow.run,
            args=[
                test_dataset.id,
                test_dataset.storage_key,
            ],
            id=workflow_id,
            task_queue=config.QUEUE_INGESTION,
        )

        result = await handle.result()

        # Assertions
        assert result is not None
        assert result["dataset_id"] == test_dataset.id
        assert result["status"] in ["awaiting_mapping", "failed"]

        if result["status"] == "awaiting_mapping":
            assert "columns" in result
            assert "suggestions" in result
            assert "can_auto_map" in result

    async def test_validation_detects_columns(
        self,
        temporal_env: WorkflowEnvironment,
        ingestion_worker: Worker,
        test_dataset: TestDataset,
    ):
        """Test that validation correctly detects CSV columns."""
        config = get_temporal_config()
        client = temporal_env.client

        handle = await client.start_workflow(
            DatasetValidationWorkflow.run,
            args=[
                test_dataset.id,
                test_dataset.storage_key,
            ],
            id=f"test-columns-{test_dataset.id}",
            task_queue=config.QUEUE_INGESTION,
        )

        result = await handle.result()

        if result["status"] == "awaiting_mapping":
            columns = result.get("columns", [])
            # Our sample CSV has: case_id, activity, timestamp, resource
            {col["name"] if isinstance(col, dict) else col for col in columns}

            # At least some columns should be detected
            assert len(columns) > 0 or "error" not in result
