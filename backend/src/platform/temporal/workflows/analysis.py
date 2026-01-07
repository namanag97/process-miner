"""Analysis Workflows.

Temporal workflows for process mining analysis operations.

Features:
- Query handlers for real-time progress tracking (survives worker restarts)
- Deterministic workflow IDs for idempotent starts

Workflow ID Patterns:
- Discovery: f"discover-{dataset_id}-{miner_type}"
- Conformance: f"conformance-{dataset_id}-{model_id}"
"""

from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.platform.temporal.activities.types import (
        CheckConformanceInput,
        ComputeMetricsInput,
        LoadEventLogInput,
        MineModelInput,
    )


@dataclass
class AnalysisProgress:
    """Progress state for analysis workflows."""

    progress_percent: int = 0
    current_step: str = "initializing"
    error_message: str | None = None
    details: dict | None = None


@workflow.defn
class ProcessDiscoveryWorkflow:
    """Workflow for process model discovery.

    Steps:
    1. Load and verify dataset
    2. Run discovery algorithm (Alpha, Inductive, Heuristic)
    3. Compute quality metrics

    Query Progress:
        Use Temporal query to get real-time progress:
        ```python
        handle = client.get_workflow_handle(workflow_id)
        progress = await handle.query("get_progress")
        ```
    """

    def __init__(self) -> None:
        """Initialize workflow state for progress tracking."""
        self._state = AnalysisProgress()

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler for progress - survives replays and worker restarts."""
        return {
            "progress": self._state.progress_percent,
            "current_step": self._state.current_step,
            "error": self._state.error_message,
            "details": self._state.details,
        }

    @workflow.run
    async def run(
        self,
        dataset_id: str,
        miner_type: str,
        model_name: str | None = None,
    ) -> dict:
        """Execute process discovery workflow.

        Args:
            dataset_id: UUID of the dataset to analyze
            miner_type: Mining algorithm (alpha, inductive, heuristic, ilp)
            model_name: Optional name for the discovered model

        Returns:
            dict with model data and metrics
        """
        from src.platform.temporal.activities.analysis import (
            compute_metrics_activity,
            load_event_log_activity,
            mine_model_activity,
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
            self._state.progress_percent = 10
            self._state.details = {"miner_type": miner_type}

            load_result = await workflow.execute_activity(
                load_event_log_activity,
                LoadEventLogInput(dataset_id=dataset_id),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            if not load_result.is_loaded:
                self._state.error_message = "Dataset not ready"
                self._state.current_step = "failed"
                return {
                    "dataset_id": dataset_id,
                    "status": "failed",
                    "error": "Dataset not ready",
                }

            self._state.progress_percent = 20

            # Step 2: Mine model (long-running, with heartbeat)
            self._state.current_step = "mine_model"
            self._state.details = {"miner_type": miner_type, "step": 2, "total_steps": 3}

            mine_result = await workflow.execute_activity(
                mine_model_activity,
                MineModelInput(
                    dataset_id=dataset_id,
                    miner_type=miner_type,
                    model_name=model_name,
                ),
                start_to_close_timeout=timedelta(minutes=15),
                heartbeat_timeout=timedelta(seconds=60),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 70

            # Step 3: Compute additional metrics if not already computed
            self._state.current_step = "compute_metrics"
            self._state.details = {"step": 3, "total_steps": 3}

            if mine_result.fitness is None:
                metrics_result = await workflow.execute_activity(
                    compute_metrics_activity,
                    ComputeMetricsInput(
                        dataset_id=dataset_id,
                        model_id=mine_result.model_id,
                    ),
                    start_to_close_timeout=timedelta(minutes=5),
                    retry_policy=retry_policy,
                )
                fitness = metrics_result.fitness
                precision = metrics_result.precision
            else:
                fitness = mine_result.fitness
                precision = mine_result.precision

            self._state.progress_percent = 100
            self._state.current_step = "completed"

            return {
                "model_id": mine_result.model_id,
                "dataset_id": dataset_id,
                "miner_type": miner_type,
                "model_format": mine_result.model_format,
                "fitness": fitness,
                "precision": precision,
                "status": "completed",
            }

        except Exception as e:
            self._state.error_message = str(e)
            self._state.current_step = "failed"
            raise


@workflow.defn
class ConformanceCheckWorkflow:
    """Workflow for conformance checking.

    Steps:
    1. Load dataset and model
    2. Run conformance check (token replay or alignment)

    Query Progress:
        Use Temporal query to get real-time progress:
        ```python
        handle = client.get_workflow_handle(workflow_id)
        progress = await handle.query("get_progress")
        ```
    """

    def __init__(self) -> None:
        """Initialize workflow state for progress tracking."""
        self._state = AnalysisProgress()

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler for progress - survives replays and worker restarts."""
        return {
            "progress": self._state.progress_percent,
            "current_step": self._state.current_step,
            "error": self._state.error_message,
            "details": self._state.details,
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
        from src.platform.temporal.activities.analysis import (
            check_conformance_activity,
            load_event_log_activity,
        )

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        try:
            # Step 1: Verify dataset is ready
            self._state.current_step = "load_event_log"
            self._state.progress_percent = 10
            self._state.details = {"method": method}

            load_result = await workflow.execute_activity(
                load_event_log_activity,
                LoadEventLogInput(dataset_id=dataset_id),
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=retry_policy,
            )

            if not load_result.is_loaded:
                self._state.error_message = "Dataset not ready"
                self._state.current_step = "failed"
                return {
                    "dataset_id": dataset_id,
                    "model_id": model_id,
                    "status": "failed",
                    "error": "Dataset not ready",
                }

            self._state.progress_percent = 30

            # Step 2: Run conformance check
            self._state.current_step = "check_conformance"
            self._state.details = {"method": method, "step": 2, "total_steps": 2}

            conf_result = await workflow.execute_activity(
                check_conformance_activity,
                CheckConformanceInput(
                    dataset_id=dataset_id,
                    model_id=model_id,
                    method=method,
                ),
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 100
            self._state.current_step = "completed"

            return {
                "conformance_id": conf_result.conformance_id,
                "dataset_id": dataset_id,
                "model_id": model_id,
                "fitness": conf_result.fitness,
                "precision": conf_result.precision,
                "is_conformant": conf_result.is_conformant,
                "fitting_traces": conf_result.fitting_traces,
                "total_traces": conf_result.total_traces,
                "status": "completed",
            }

        except Exception as e:
            self._state.error_message = str(e)
            self._state.current_step = "failed"
            raise
