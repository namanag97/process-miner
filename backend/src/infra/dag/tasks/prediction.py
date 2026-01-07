"""Prediction DAG Task Nodes.

Pure business logic functions for ML prediction model training.
"""

import time
from typing import Any

import structlog

from src.infra.dag.registry import DAGContext, TaskResult, dag_task

logger = structlog.get_logger(__name__)


@dag_task("train_predictor", timeout_seconds=1800, max_retries=2)
async def train_predictor(ctx: DAGContext, params: dict[str, Any]) -> TaskResult:
    """Train an ML prediction model.

    Extracted from train_prediction_model_task. Supports:
    - next_activity: Predict the next activity in a trace
    - remaining_time: Predict time until process completion

    Args:
        ctx: DAG context with dataset_id
        params: Task parameters (target_type, algorithm)

    Returns:
        TaskResult with model_id and metrics
    """
    start = time.perf_counter()
    dataset_id = ctx.dataset_id or params.get("dataset_id")
    target_type = params.get("target_type", "next_activity")
    algorithm = params.get("algorithm", "random_forest")

    if not dataset_id:
        return TaskResult.fail("dataset_id is required")

    logger.info(
        "train_predictor_started",
        dataset_id=dataset_id,
        target_type=target_type,
        algorithm=algorithm,
        run_id=ctx.run_id,
    )

    try:
        from src.features.process_mining.services.loader import event_log_loader
        from src.features.process_mining.services.prediction import prediction_service

        # Convert to PM4Py log
        pm4py_log = event_log_loader.load_as_pm4py_log(dataset_id)

        # Train model based on target type
        if target_type == "next_activity":
            model_info = prediction_service.train_next_activity_model(
                pm4py_log=pm4py_log,
                algorithm=algorithm,
            )
        elif target_type == "remaining_time":
            model_info = prediction_service.train_remaining_time_model(
                pm4py_log=pm4py_log,
                algorithm=algorithm,
            )
        else:
            return TaskResult.fail(f"Unknown target type: {target_type}")

        # Store in context
        ctx.set("model_binary", model_info.get("model_binary"))
        ctx.set("model_metrics", model_info.get("metrics", {}))

        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "train_predictor_completed",
            dataset_id=dataset_id,
            target_type=target_type,
            algorithm=algorithm,
            duration_ms=round(duration_ms, 2),
        )

        return TaskResult.ok(
            data={
                "dataset_id": dataset_id,
                "target_type": target_type,
                "algorithm": algorithm,
                "metrics": model_info.get("metrics", {}),
                "model_binary": model_info.get("model_binary"),
            },
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error(
            "train_predictor_failed",
            error=str(e),
            dataset_id=dataset_id,
            exc_info=True,
        )
        return TaskResult.fail(str(e))
