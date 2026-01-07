"""Dataset Ingestion Workflow.

Temporal workflow for the complete dataset ingestion lifecycle.

Features:
- Query handlers for real-time progress tracking (survives worker restarts)
- Heartbeat-based progress for long-running parsing
- Deterministic workflow IDs for idempotent starts

Workflow ID Pattern: f"ingest-dataset-{dataset_id}"
"""

from dataclasses import dataclass, field
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.platform.temporal.activities.types import (
        ComputeStatsInput,
        DetectColumnsInput,
        ParseToParquetInput,
        ValidateFileInput,
    )


@dataclass
class IngestionProgress:
    """Progress state that survives Temporal replays."""

    progress_percent: int = 0
    current_step: str = "initializing"
    total_events: int = 0
    total_cases: int = 0
    error_message: str | None = None
    details: dict = field(default_factory=dict)


@workflow.defn
class DatasetIngestionWorkflow:
    """Workflow for ingesting a dataset from upload to ready state.

    Parquet-Only Architecture:
    1. Validate file format (magic bytes)
    2. Parse CSV/XES with DuckDB to Parquet (stored in S3)
    3. Compute statistics and metadata (stored in PostgreSQL)

    Event data is stored ONLY in S3 Parquet - NOT duplicated in PostgreSQL.
    Analytics queries read directly from S3 Parquet via DuckDB.

    Query Progress:
        Use Temporal query to get real-time progress:
        ```python
        handle = client.get_workflow_handle(workflow_id)
        progress = await handle.query("get_progress")
        ```
    """

    def __init__(self) -> None:
        """Initialize workflow state for progress tracking."""
        self._state = IngestionProgress()

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler for progress - survives replays and worker restarts.

        Returns:
            dict with progress info:
                - progress: 0-100 percentage
                - current_step: Current activity name
                - total_events: Events processed so far
                - total_cases: Cases processed so far
                - error: Error message if failed
                - details: Additional step-specific details
        """
        return {
            "progress": self._state.progress_percent,
            "current_step": self._state.current_step,
            "total_events": self._state.total_events,
            "total_cases": self._state.total_cases,
            "error": self._state.error_message,
            "details": self._state.details,
        }

    @workflow.run
    async def run(
        self,
        dataset_id: str,
        storage_key: str,
        case_id_column: str,
        activity_column: str,
        timestamp_column: str,
        resource_column: str | None = None,
    ) -> dict:
        """Execute the dataset ingestion workflow.

        Args:
            dataset_id: UUID of the dataset
            storage_key: S3 key where file is stored
            case_id_column: Mapped case ID column name
            activity_column: Mapped activity column name
            timestamp_column: Mapped timestamp column name
            resource_column: Optional resource column name

        Returns:
            dict with ingestion results
        """
        # Import activities inside workflow
        from src.platform.temporal.activities.dataset import (
            compute_statistics_activity,
            parse_to_parquet_activity,
            validate_file_activity,
        )

        # Default retry policy
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        try:
            # Step 1: Validate file
            self._state.current_step = "validate_file"
            self._state.progress_percent = 5
            self._state.details = {"step": 1, "total_steps": 3}

            validate_result = await workflow.execute_activity(
                validate_file_activity,
                ValidateFileInput(dataset_id=dataset_id, storage_key=storage_key),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            if not validate_result.is_valid:
                self._state.error_message = validate_result.error_message
                self._state.current_step = "failed"
                return {
                    "dataset_id": dataset_id,
                    "status": "failed",
                    "error": validate_result.error_message,
                }

            self._state.progress_percent = 15

            # Step 2: Parse with DuckDB and write to S3 Parquet (long-running, with heartbeat)
            # NOTE: Events are stored ONLY in S3 Parquet - NOT in PostgreSQL
            self._state.current_step = "parse_to_parquet"
            self._state.details = {"step": 2, "total_steps": 3}

            parse_result = await workflow.execute_activity(
                parse_to_parquet_activity,
                ParseToParquetInput(
                    dataset_id=dataset_id,
                    storage_key=storage_key,
                    case_id_column=case_id_column,
                    activity_column=activity_column,
                    timestamp_column=timestamp_column,
                    resource_column=resource_column,
                ),
                start_to_close_timeout=timedelta(minutes=30),
                heartbeat_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )

            # Verify Parquet was written successfully (required for Parquet-Only architecture)
            if not parse_result.parquet_s3_key:
                self._state.error_message = "Failed to write events to S3 Parquet"
                self._state.current_step = "failed"
                return {
                    "dataset_id": dataset_id,
                    "status": "failed",
                    "error": "Failed to write events to S3 Parquet",
                }

            # Update progress with parsed stats
            self._state.progress_percent = 80
            self._state.total_events = parse_result.total_events
            self._state.total_cases = parse_result.total_cases

            # Step 3: Compute statistics (metadata stored in PostgreSQL only)
            self._state.current_step = "compute_statistics"
            self._state.details = {"step": 3, "total_steps": 3}

            stats_with_parquet = {
                **parse_result.statistics,
                "parquet_s3_key": parse_result.parquet_s3_key,
                "parquet_size_bytes": parse_result.parquet_size_bytes,
            }
            await workflow.execute_activity(
                compute_statistics_activity,
                ComputeStatsInput(
                    dataset_id=dataset_id,
                    statistics=stats_with_parquet,
                ),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            # Mark as completed
            self._state.progress_percent = 100
            self._state.current_step = "completed"

            return {
                "dataset_id": dataset_id,
                "status": "completed",
                "total_cases": parse_result.total_cases,
                "total_events": parse_result.total_events,
                "total_activities": parse_result.total_activities,
                "parquet_s3_key": parse_result.parquet_s3_key,
                "parquet_size_bytes": parse_result.parquet_size_bytes,
            }

        except Exception as e:
            self._state.error_message = str(e)
            self._state.current_step = "failed"
            raise


@dataclass
class ValidationProgress:
    """Progress state for validation workflow."""

    progress_percent: int = 0
    current_step: str = "initializing"
    error_message: str | None = None


@workflow.defn
class DatasetValidationWorkflow:
    """Workflow for validating and detecting columns in a dataset.

    Used for the first phase before column mapping.

    Workflow ID Pattern: f"validate-dataset-{dataset_id}"

    Query Progress:
        Use Temporal query to get real-time progress:
        ```python
        handle = client.get_workflow_handle(workflow_id)
        progress = await handle.query("get_progress")
        ```
    """

    def __init__(self) -> None:
        """Initialize workflow state for progress tracking."""
        self._state = ValidationProgress()

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler for progress - survives replays and worker restarts."""
        return {
            "progress": self._state.progress_percent,
            "current_step": self._state.current_step,
            "error": self._state.error_message,
        }

    @workflow.run
    async def run(self, dataset_id: str, storage_key: str) -> dict:
        """Execute validation workflow.

        Args:
            dataset_id: UUID of the dataset
            storage_key: S3 key where file is stored

        Returns:
            dict with validation results and detected columns
        """
        from src.platform.temporal.activities.dataset import (
            detect_columns_activity,
            validate_file_activity,
        )

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        try:
            # Step 1: Validate file
            self._state.current_step = "validate_file"
            self._state.progress_percent = 10

            validate_result = await workflow.execute_activity(
                validate_file_activity,
                ValidateFileInput(dataset_id=dataset_id, storage_key=storage_key),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            if not validate_result.is_valid:
                self._state.error_message = validate_result.error_message
                self._state.current_step = "failed"
                return {
                    "dataset_id": dataset_id,
                    "status": "failed",
                    "error": validate_result.error_message,
                }

            self._state.progress_percent = 40

            # Step 2: Download and detect columns
            self._state.current_step = "detect_columns"

            from src.platform.infrastructure.object_storage import get_storage_client

            storage_client = get_storage_client()
            file_obj = storage_client.download_fileobj("raw", storage_key)
            file_content = file_obj.read()

            detect_result = await workflow.execute_activity(
                detect_columns_activity,
                DetectColumnsInput(
                    dataset_id=dataset_id,
                    file_content=file_content,
                    filename=storage_key.split("/")[-1],
                ),
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 100
            self._state.current_step = "completed"

            return {
                "dataset_id": dataset_id,
                "status": "awaiting_mapping",
                "columns": detect_result.columns,
                "suggestions": detect_result.suggestions,
                "can_auto_map": detect_result.can_auto_map,
                "row_count": detect_result.row_count,
            }

        except Exception as e:
            self._state.error_message = str(e)
            self._state.current_step = "failed"
            raise
