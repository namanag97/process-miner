"""Dataset Ingestion Workflow.

Temporal workflow for the complete dataset ingestion lifecycle.
"""

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


@workflow.defn
class DatasetIngestionWorkflow:
    """Workflow for ingesting a dataset from upload to ready state.

    Parquet-Only Architecture:
    1. Validate file format (magic bytes)
    2. Parse CSV/XES with DuckDB to Parquet (stored in S3)
    3. Compute statistics and metadata (stored in PostgreSQL)

    Event data is stored ONLY in S3 Parquet - NOT duplicated in PostgreSQL.
    Analytics queries read directly from S3 Parquet via DuckDB.
    """

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

        # Step 1: Validate file
        validate_result = await workflow.execute_activity(
            validate_file_activity,
            ValidateFileInput(dataset_id=dataset_id, storage_key=storage_key),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )

        if not validate_result.is_valid:
            return {
                "dataset_id": dataset_id,
                "status": "failed",
                "error": validate_result.error_message,
            }

        # Step 2: Parse with DuckDB and write to S3 Parquet (long-running, with heartbeat)
        # NOTE: Events are stored ONLY in S3 Parquet - NOT in PostgreSQL
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
            return {
                "dataset_id": dataset_id,
                "status": "failed",
                "error": "Failed to write events to S3 Parquet",
            }

        # Step 3: Compute statistics (metadata stored in PostgreSQL only)
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

        return {
            "dataset_id": dataset_id,
            "status": "completed",
            "total_cases": parse_result.total_cases,
            "total_events": parse_result.total_events,
            "total_activities": parse_result.total_activities,
            "parquet_s3_key": parse_result.parquet_s3_key,
            "parquet_size_bytes": parse_result.parquet_size_bytes,
        }


@workflow.defn
class DatasetValidationWorkflow:
    """Workflow for validating and detecting columns in a dataset.

    Used for the first phase before column mapping.
    """

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

        # Step 1: Validate file
        validate_result = await workflow.execute_activity(
            validate_file_activity,
            ValidateFileInput(dataset_id=dataset_id, storage_key=storage_key),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )

        if not validate_result.is_valid:
            return {
                "dataset_id": dataset_id,
                "status": "failed",
                "error": validate_result.error_message,
            }

        # Step 2: Download and detect columns
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

        return {
            "dataset_id": dataset_id,
            "status": "awaiting_mapping",
            "columns": detect_result.columns,
            "suggestions": detect_result.suggestions,
            "can_auto_map": detect_result.can_auto_map,
            "row_count": detect_result.row_count,
        }
