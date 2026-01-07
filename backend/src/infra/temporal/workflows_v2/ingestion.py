"""Dataset Ingestion Workflow v2 - Temporal Native.

Key improvements over v1:
- Deterministic workflow ID from dataset_id (enables idempotent starts)
- Query handlers for progress (survives worker restarts and replays)
- Chunk-based parsing (workflow orchestrates chunks, not single 30-min activity)
- No AsyncJob creation - updates business entities directly
- Proper compensation on failure

Workflow ID Pattern: f"ingest-dataset-{dataset_id}"
"""

from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.infra.temporal.activities_v2.types import (
        ChunkInfo,
        ColumnMapping,
        IngestionResult,
        ValidationResult,
    )


@dataclass
class IngestionProgress:
    """Progress state that survives replays."""

    progress_percent: int = 0
    current_step: str = "initializing"
    total_chunks: int = 0
    processed_chunks: int = 0
    total_events: int = 0
    total_cases: int = 0
    error_message: str | None = None


@workflow.defn
class DatasetIngestionWorkflowV2:
    """Temporal-native ingestion workflow.

    Steps:
    1. Validate file format (fast, <2 min)
    2. Get chunk list for parallel processing
    3. Process each chunk (workflow orchestrates, activities are short)
    4. Finalize ingestion (compute stats, update status)

    Progress is tracked via query handler and survives worker failures.
    """

    def __init__(self) -> None:
        self._state = IngestionProgress()

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler for progress - survives replays.

        Frontend polls this via Temporal query, not database.
        """
        return {
            "progress": self._state.progress_percent,
            "current_step": self._state.current_step,
            "total_chunks": self._state.total_chunks,
            "processed_chunks": self._state.processed_chunks,
            "total_events": self._state.total_events,
            "total_cases": self._state.total_cases,
            "error": self._state.error_message,
        }

    @workflow.run
    async def run(
        self,
        dataset_id: str,
        storage_key: str,
        mapping: dict,
    ) -> dict:
        """Execute ingestion with chunk-level granularity.

        Args:
            dataset_id: UUID of the dataset
            storage_key: S3 key where file is stored
            mapping: Column mapping dict with case_id, activity, timestamp, resource

        Returns:
            dict with ingestion results
        """
        # Import activities inside workflow (Temporal requirement)
        from src.infra.temporal.activities_v2.ingestion import (
            finalize_ingestion,
            get_chunk_list,
            process_chunk,
            update_dataset_status,
            validate_file,
        )

        # Default retry policy for all activities
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        try:
            # Step 1: Validate file (fast, <2 min)
            self._state.current_step = "validate_file"
            validation: ValidationResult = await workflow.execute_activity(
                validate_file,
                args=[dataset_id, storage_key],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            if not validation.is_valid:
                self._state.error_message = validation.error_message
                self._state.current_step = "failed"

                # Update dataset status to error
                await workflow.execute_activity(
                    update_dataset_status,
                    args=[dataset_id, "error", validation.error_message],
                    start_to_close_timeout=timedelta(minutes=1),
                    retry_policy=retry_policy,
                )

                return {
                    "status": "failed",
                    "dataset_id": dataset_id,
                    "error": validation.error_message,
                }

            self._state.progress_percent = 10

            # Step 2: Get chunk list (fast, <1 min)
            self._state.current_step = "get_chunk_list"
            chunks: list[ChunkInfo] = await workflow.execute_activity(
                get_chunk_list,
                args=[dataset_id, storage_key, validation.file_size_bytes],
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )

            self._state.total_chunks = len(chunks)
            self._state.progress_percent = 15

            # Step 3: Process each chunk (workflow orchestrates, survives replays)
            # If worker dies mid-processing, Temporal replays and skips completed chunks
            self._state.current_step = "processing_chunks"

            chunk_results = []
            for i, chunk in enumerate(chunks):
                result = await workflow.execute_activity(
                    process_chunk,
                    args=[dataset_id, chunk, ColumnMapping(**mapping)],
                    start_to_close_timeout=timedelta(minutes=5),
                    heartbeat_timeout=timedelta(seconds=30),
                    retry_policy=retry_policy,
                )

                chunk_results.append(result)
                self._state.processed_chunks = i + 1
                self._state.total_events += result.get("events_processed", 0)
                self._state.total_cases += result.get("cases_processed", 0)
                # Progress: 15-85% based on chunks
                self._state.progress_percent = 15 + int((i + 1) / len(chunks) * 70)

            # Step 4: Finalize (fast, <2 min)
            self._state.current_step = "finalize"
            final_result: IngestionResult = await workflow.execute_activity(
                finalize_ingestion,
                args=[dataset_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 100
            self._state.current_step = "completed"
            self._state.total_cases = final_result.total_cases
            self._state.total_events = final_result.total_events

            return {
                "status": "completed",
                "dataset_id": dataset_id,
                "total_cases": final_result.total_cases,
                "total_events": final_result.total_events,
                "total_activities": final_result.total_activities,
                "chunks_processed": len(chunks),
            }

        except Exception as e:
            self._state.error_message = str(e)
            self._state.current_step = "failed"

            # Update dataset status to error
            try:
                await workflow.execute_activity(
                    update_dataset_status,
                    args=[dataset_id, "error", str(e)],
                    start_to_close_timeout=timedelta(minutes=1),
                )
            except Exception:
                pass  # Best effort

            raise


@workflow.defn
class DatasetValidationWorkflowV2:
    """Validation-only workflow for column detection phase.

    Used before column mapping is confirmed.
    Workflow ID Pattern: f"validate-dataset-{dataset_id}"
    """

    def __init__(self) -> None:
        self._progress = 0
        self._current_step = "initializing"

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler for progress."""
        return {
            "progress": self._progress,
            "current_step": self._current_step,
        }

    @workflow.run
    async def run(self, dataset_id: str, storage_key: str) -> dict:
        """Execute validation workflow.

        Returns detected columns and AI suggestions for mapping.
        """
        from src.infra.temporal.activities_v2.ingestion import (
            detect_columns,
            validate_file,
        )

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        # Step 1: Validate file
        self._current_step = "validate_file"
        validation = await workflow.execute_activity(
            validate_file,
            args=[dataset_id, storage_key],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )

        if not validation.is_valid:
            return {
                "status": "failed",
                "dataset_id": dataset_id,
                "error": validation.error_message,
            }

        self._progress = 50

        # Step 2: Detect columns
        self._current_step = "detect_columns"
        detection = await workflow.execute_activity(
            detect_columns,
            args=[dataset_id, storage_key],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )

        self._progress = 100
        self._current_step = "completed"

        return {
            "status": "awaiting_mapping",
            "dataset_id": dataset_id,
            "columns": detection.columns,
            "suggestions": detection.suggestions,
            "row_count": detection.row_count,
            "can_auto_map": detection.can_auto_map,
        }
