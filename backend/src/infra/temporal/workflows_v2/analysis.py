"""Analysis Workflows v2 - Temporal Native.

Process discovery and conformance checking workflows with:
- Deterministic workflow IDs
- Query handlers for progress
- Proper chunking for large datasets

Workflow ID Patterns:
- Discovery: f"discover-{dataset_id}-{miner_type}"
- Conformance: f"conformance-{dataset_id}-{model_id}"
"""

from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.infra.temporal.activities_v2.types import (
        ConformanceResult,
        DiscoveryResult,
    )


@dataclass
class AnalysisProgress:
    """Progress state for analysis workflows."""

    progress_percent: int = 0
    current_step: str = "initializing"
    error_message: str | None = None


@workflow.defn
class ProcessDiscoveryWorkflowV2:
    """Process model discovery workflow.

    Discovers process models using various mining algorithms.
    Updates business entities (ProcessModel) directly.

    Workflow ID: f"discover-{dataset_id}-{miner_type}"
    """

    def __init__(self) -> None:
        self._state = AnalysisProgress()

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler for progress."""
        return {
            "progress": self._state.progress_percent,
            "current_step": self._state.current_step,
            "error": self._state.error_message,
        }

    @workflow.run
    async def run(
        self,
        dataset_id: str,
        miner_type: str,
        model_name: str | None = None,
        parameters: dict | None = None,
    ) -> dict:
        """Execute process discovery workflow.

        Args:
            dataset_id: UUID of the dataset to analyze
            miner_type: Mining algorithm (alpha, inductive, heuristic, ilp)
            model_name: Optional name for the discovered model
            parameters: Algorithm-specific parameters (optional)
                - inductive/inductive_infrequent: noise_threshold (0.0-1.0)
                - heuristics: dependency_threshold (0.0-1.0), and_threshold (0.0-1.0)
                - ilp: alpha (0.0-1.0)
                - log_skeleton: noise_threshold (0.0-1.0)
                - transition_system: direction (forward/backward), window (1-10)

        Returns:
            dict with model data and metrics
        """
        from src.infra.temporal.activities_v2.analysis import (
            compute_model_metrics,
            discover_process_model,
            load_event_log,
            save_process_model,
        )

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        try:
            # Step 1: Load and verify event log
            self._state.current_step = "load_event_log"
            log_info = await workflow.execute_activity(
                load_event_log,
                args=[dataset_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            if not log_info.get("is_ready"):
                self._state.error_message = "Dataset not ready"
                return {"status": "failed", "error": "Dataset not ready"}

            self._state.progress_percent = 20

            # Step 2: Discover process model (with optional parameters)
            self._state.current_step = "discover_model"
            discovery: DiscoveryResult = await workflow.execute_activity(
                discover_process_model,
                args=[dataset_id, miner_type, parameters or {}],
                start_to_close_timeout=timedelta(minutes=15),
                heartbeat_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 70

            # Step 3: Compute metrics
            self._state.current_step = "compute_metrics"
            metrics = await workflow.execute_activity(
                compute_model_metrics,
                args=[dataset_id, discovery.model_data],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 90

            # Step 4: Save model to database
            self._state.current_step = "save_model"
            model_id = await workflow.execute_activity(
                save_process_model,
                args=[
                    dataset_id,
                    model_name or f"Model_{miner_type}",
                    discovery.model_data,
                    metrics,
                ],
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 100
            self._state.current_step = "completed"

            return {
                "status": "completed",
                "model_id": model_id,
                "dataset_id": dataset_id,
                "miner_type": miner_type,
                "fitness": metrics.get("fitness"),
                "precision": metrics.get("precision"),
            }

        except Exception as e:
            self._state.error_message = str(e)
            self._state.current_step = "failed"
            raise


@workflow.defn
class ConformanceCheckWorkflowV2:
    """Conformance checking workflow.

    Checks how well a process model fits the event log.

    Workflow ID: f"conformance-{dataset_id}-{model_id}"
    """

    def __init__(self) -> None:
        self._state = AnalysisProgress()

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler for progress."""
        return {
            "progress": self._state.progress_percent,
            "current_step": self._state.current_step,
            "error": self._state.error_message,
        }

    @workflow.run
    async def run(
        self,
        dataset_id: str,
        model_id: str,
        method: str = "token_replay",
    ) -> dict:
        """Execute conformance checking workflow.

        Args:
            dataset_id: UUID of the dataset
            model_id: UUID of the process model
            method: Conformance method (token_replay or alignment)

        Returns:
            dict with conformance results
        """
        from src.infra.temporal.activities_v2.analysis import (
            check_conformance,
            load_event_log,
            load_process_model,
            save_conformance_result,
        )

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        try:
            # Step 1: Load event log
            self._state.current_step = "load_event_log"
            log_info = await workflow.execute_activity(
                load_event_log,
                args=[dataset_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            if not log_info.get("is_ready"):
                return {"status": "failed", "error": "Dataset not ready"}

            self._state.progress_percent = 20

            # Step 2: Load process model
            self._state.current_step = "load_model"
            model_data = await workflow.execute_activity(
                load_process_model,
                args=[model_id],
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 30

            # Step 3: Run conformance check
            self._state.current_step = "check_conformance"
            result: ConformanceResult = await workflow.execute_activity(
                check_conformance,
                args=[dataset_id, model_data, method],
                start_to_close_timeout=timedelta(minutes=10),
                heartbeat_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 90

            # Step 4: Save result
            self._state.current_step = "save_result"
            conformance_id = await workflow.execute_activity(
                save_conformance_result,
                args=[dataset_id, model_id, result],
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 100
            self._state.current_step = "completed"

            return {
                "status": "completed",
                "conformance_id": conformance_id,
                "dataset_id": dataset_id,
                "model_id": model_id,
                "fitness": result.fitness,
                "precision": result.precision,
                "is_conformant": result.is_conformant,
                "fitting_traces": result.fitting_traces,
                "total_traces": result.total_traces,
            }

        except Exception as e:
            self._state.error_message = str(e)
            self._state.current_step = "failed"
            raise
