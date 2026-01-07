"""Quality Evaluation Workflow.

Temporal workflow for comprehensive process model quality evaluation.
"""

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from src.platform.temporal.activities.types import (
        LoadEventLogInput,
    )


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
    """

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
        from src.platform.temporal.activities.analysis import (
            load_event_log_activity,
        )
        from src.platform.temporal.activities.quality import (
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

        # Step 1: Verify dataset is ready
        load_result = await workflow.execute_activity(
            load_event_log_activity,
            LoadEventLogInput(dataset_id=dataset_id),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )

        if not load_result.is_loaded:
            return {
                "model_id": model_id,
                "dataset_id": dataset_id,
                "status": "failed",
                "error": "Dataset not ready",
            }

        # Step 2: Compute fitness
        try:
            fitness_result = await workflow.execute_activity(
                compute_fitness_activity,
                {"model_id": model_id, "dataset_id": dataset_id},
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy,
            )
            results["fitness"] = fitness_result
        except Exception as e:
            results["fitness"] = {"error": str(e)}

        # Step 3: Compute precision
        try:
            precision_result = await workflow.execute_activity(
                compute_precision_activity,
                {"model_id": model_id, "dataset_id": dataset_id},
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy,
            )
            results["precision"] = precision_result
        except Exception as e:
            results["precision"] = {"error": str(e)}

        # Step 4: Compute generalization (optional)
        if include_generalization:
            try:
                gen_result = await workflow.execute_activity(
                    compute_generalization_activity,
                    {"model_id": model_id, "dataset_id": dataset_id},
                    start_to_close_timeout=timedelta(minutes=15),
                    retry_policy=retry_policy,
                )
                results["generalization"] = gen_result
            except Exception as e:
                results["generalization"] = {"error": str(e)}

        # Step 5: Compute simplicity
        try:
            simplicity_result = await workflow.execute_activity(
                compute_simplicity_activity,
                {"model_id": model_id},
                start_to_close_timeout=timedelta(minutes=2),
                retry_policy=retry_policy,
            )
            results["simplicity"] = simplicity_result
        except Exception as e:
            results["simplicity"] = {"error": str(e)}

        # Step 6: Store results
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

        return {
            "model_id": model_id,
            "dataset_id": dataset_id,
            "status": "completed",
            "metrics": results,
        }
