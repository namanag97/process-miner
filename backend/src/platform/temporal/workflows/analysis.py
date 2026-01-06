"""Analysis Workflows.

Temporal workflows for process mining analysis operations.
"""

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


@workflow.defn
class ProcessDiscoveryWorkflow:
    """Workflow for process model discovery.

    Steps:
    1. Load and verify dataset
    2. Run discovery algorithm (Alpha, Inductive, Heuristic)
    3. Compute quality metrics
    """

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

        # Step 1: Load event log
        load_result = await workflow.execute_activity(
            load_event_log_activity,
            LoadEventLogInput(dataset_id=dataset_id),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )

        if not load_result.is_loaded:
            return {
                "dataset_id": dataset_id,
                "status": "failed",
                "error": "Dataset not ready",
            }

        # Step 2: Mine model (long-running, with heartbeat)
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

        # Step 3: Compute additional metrics if not already computed
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

        return {
            "model_id": mine_result.model_id,
            "dataset_id": dataset_id,
            "miner_type": miner_type,
            "model_format": mine_result.model_format,
            "fitness": fitness,
            "precision": precision,
            "status": "completed",
        }


@workflow.defn
class ConformanceCheckWorkflow:
    """Workflow for conformance checking.

    Steps:
    1. Load dataset and model
    2. Run conformance check (token replay or alignment)
    """

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

        # Step 1: Verify dataset is ready
        load_result = await workflow.execute_activity(
            load_event_log_activity,
            LoadEventLogInput(dataset_id=dataset_id),
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )

        if not load_result.is_loaded:
            return {
                "dataset_id": dataset_id,
                "model_id": model_id,
                "status": "failed",
                "error": "Dataset not ready",
            }

        # Step 2: Run conformance check
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
