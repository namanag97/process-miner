"""Quality Evaluation Workflow.

Temporal workflow for comprehensive process model quality evaluation.

Features:
- Query handlers for real-time progress tracking (survives worker restarts)
- Deterministic workflow IDs for idempotent starts

Workflow ID Pattern: f"quality-{model_id}-{dataset_id}"
"""

from dataclasses import dataclass
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.infra.temporal.activities.types import (
        LoadEventLogInput,
    )


@dataclass
class QualityProgress:
    """Progress state for quality evaluation workflow."""

    progress_percent: int = 0
    current_step: str = "initializing"
    error_message: str | None = None
    computed_metrics: list[str] | None = None


@workflow.defn
class QualityEvaluationWorkflow:
    """Workflow for computing all quality metrics on a process model.

    Steps:
    1. Load and verify dataset exists
    2. Compute fitness (token-based replay)
    3. Compute precision (ETC precision)
    4. Compute generalization (optional, can be slow)
    5. Compute simplicity (structural)
    6. Store/update results in process_model_metrics

    Query Progress:
        Use Temporal query to get real-time progress:
        ```python
        handle = client.get_workflow_handle(workflow_id)
        progress = await handle.query("get_progress")
        ```
    """

    def __init__(self) -> None:
        """Initialize workflow state for progress tracking."""
        self._state = QualityProgress()

    @workflow.query
    def get_progress(self) -> dict:
        """Query handler for progress - survives replays and worker restarts."""
        return {
            "progress": self._state.progress_percent,
            "current_step": self._state.current_step,
            "error": self._state.error_message,
            "computed_metrics": self._state.computed_metrics or [],
        }

    @workflow.run
    async def run(
        self,
        model_id: str,
        dataset_id: str,
        include_generalization: bool = False,
    ) -> dict:
        """Execute quality evaluation workflow.

        Args:
            model_id: UUID of the process model to evaluate
            dataset_id: UUID of the dataset to evaluate against
            include_generalization: Include generalization metric (can be slow)

        Returns:
            dict with computed metrics and timing
        """
        from src.infra.temporal.activities.analysis import (
            load_event_log_activity,
        )
        from src.infra.temporal.activities.quality import (
            compute_fitness_activity,
            compute_generalization_activity,
            compute_precision_activity,
            compute_simplicity_activity,
            store_quality_metrics_activity,
        )

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=60),
            backoff_coefficient=2.0,
            maximum_attempts=3,
        )

        results = {}
        self._state.computed_metrics = []

        try:
            # Step 1: Verify dataset is ready
            self._state.current_step = "load_event_log"
            self._state.progress_percent = 5

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
                    "model_id": model_id,
                    "dataset_id": dataset_id,
                    "status": "failed",
                    "error": "Dataset not ready",
                }

            self._state.progress_percent = 15

            # Step 2: Compute fitness
            self._state.current_step = "compute_fitness"
            try:
                fitness_result = await workflow.execute_activity(
                    compute_fitness_activity,
                    {"model_id": model_id, "dataset_id": dataset_id},
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=retry_policy,
                )
                results["fitness"] = fitness_result
                self._state.computed_metrics.append("fitness")
            except Exception as e:
                results["fitness"] = {"error": str(e)}

            self._state.progress_percent = 35

            # Step 3: Compute precision
            self._state.current_step = "compute_precision"
            try:
                precision_result = await workflow.execute_activity(
                    compute_precision_activity,
                    {"model_id": model_id, "dataset_id": dataset_id},
                    start_to_close_timeout=timedelta(minutes=10),
                    retry_policy=retry_policy,
                )
                results["precision"] = precision_result
                self._state.computed_metrics.append("precision")
            except Exception as e:
                results["precision"] = {"error": str(e)}

            self._state.progress_percent = 55

            # Step 4: Compute generalization (optional)
            if include_generalization:
                self._state.current_step = "compute_generalization"
                try:
                    gen_result = await workflow.execute_activity(
                        compute_generalization_activity,
                        {"model_id": model_id, "dataset_id": dataset_id},
                        start_to_close_timeout=timedelta(minutes=15),
                        retry_policy=retry_policy,
                    )
                    results["generalization"] = gen_result
                    self._state.computed_metrics.append("generalization")
                except Exception as e:
                    results["generalization"] = {"error": str(e)}
                self._state.progress_percent = 70

            # Step 5: Compute simplicity
            self._state.current_step = "compute_simplicity"
            try:
                simplicity_result = await workflow.execute_activity(
                    compute_simplicity_activity,
                    {"model_id": model_id},
                    start_to_close_timeout=timedelta(minutes=2),
                    retry_policy=retry_policy,
                )
                results["simplicity"] = simplicity_result
                self._state.computed_metrics.append("simplicity")
            except Exception as e:
                results["simplicity"] = {"error": str(e)}

            self._state.progress_percent = 85

            # Step 6: Store results
            self._state.current_step = "store_results"
            await workflow.execute_activity(
                store_quality_metrics_activity,
                {
                    "model_id": model_id,
                    "dataset_id": dataset_id,
                    "results": results,
                },
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )

            self._state.progress_percent = 100
            self._state.current_step = "completed"

            return {
                "model_id": model_id,
                "dataset_id": dataset_id,
                "status": "completed",
                "metrics": results,
            }

        except Exception as e:
            self._state.error_message = str(e)
            self._state.current_step = "failed"
            raise
