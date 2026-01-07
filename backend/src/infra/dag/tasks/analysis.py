"""Analysis DAG Task Nodes.

Pure business logic functions for process mining analysis tasks.
"""

import time
from typing import Any

import structlog

from src.infra.dag.registry import DAGContext, TaskResult, dag_task

logger = structlog.get_logger(__name__)


@dag_task("discover_model", timeout_seconds=900, max_retries=2)
async def discover_model(ctx: DAGContext, params: dict[str, Any]) -> TaskResult:
    """Discover a process model using PM4Py miners.

    Extracted from perform_discovery_task. Runs Alpha, Inductive, Heuristic,
    or ILP miners on event log data.

    Args:
        ctx: DAG context with dataset_id
        params: Task parameters (miner_type, model_name)

    Returns:
        TaskResult with model_id and quality metrics
    """
    start = time.perf_counter()
    dataset_id = ctx.dataset_id or params.get("dataset_id")
    miner_type = params.get("miner_type", "inductive")
    params.get("model_name")

    if not dataset_id:
        return TaskResult.fail("dataset_id is required")

    logger.info(
        "discover_model_started",
        dataset_id=dataset_id,
        miner_type=miner_type,
        run_id=ctx.run_id,
    )

    try:
        from src.features.process_mining.enums import MinerType
        from src.features.process_mining.services.mining import mining_service

        # Validate miner type
        try:
            _miner_enum = MinerType(miner_type)
        except ValueError:
            return TaskResult.fail(f"Invalid miner type: {miner_type}")

        # TODO: Fix this - mining_service.discover_from_dataset_id doesn't exist
        # Need to load Dataset object from DB first, then call mining_service.discover(dataset, miner_enum)
        # For now, this DAG task is non-functional and needs refactoring
        raise NotImplementedError(
            "DAG task discover_model needs refactoring: discover_from_dataset_id method doesn't exist. "
            "Need to load Dataset ORM object from database first, then call mining_service.discover(dataset, miner_type)"
        )

        # Serialize model
        serialized = mining_service.serialize_model(model_data)
        graph_json = mining_service.serialize_to_graph_json(model_data, model_format)

        # Compute quality metrics if possible
        fitness = None
        precision = None
        if model_format.value in ["petri_net", "process_tree"]:
            try:
                if model_format.value == "petri_net":
                    _net, _im, _fm = model_data
                else:
                    _net, _im, _fm = mining_service.tree_to_petri_net(model_data)

                # These are expensive operations - skip in DAG context for now
                # fitness_result = mining_service.evaluate_fitness(dataset_id, net, im, fm)
                # fitness = fitness_result.get("fitness")
                # precision = mining_service.evaluate_precision(dataset_id, net, im, fm)
            except Exception as e:
                logger.warning("quality_metrics_failed", error=str(e))

        # Store in context for downstream steps
        ctx.set("model_data", serialized)
        ctx.set("model_format", model_format.value)
        ctx.set("graph_json", graph_json)

        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "discover_model_completed",
            dataset_id=dataset_id,
            miner_type=miner_type,
            model_format=model_format.value,
            duration_ms=round(duration_ms, 2),
        )

        return TaskResult.ok(
            data={
                "dataset_id": dataset_id,
                "miner_type": miner_type,
                "model_format": model_format.value,
                "serialized_model": serialized,
                "graph_json": graph_json,
                "fitness": fitness,
                "precision": precision,
            },
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error("discover_model_failed", error=str(e), dataset_id=dataset_id, exc_info=True)
        return TaskResult.fail(str(e))


@dag_task("check_conformance", timeout_seconds=600, max_retries=2)
async def check_conformance(ctx: DAGContext, params: dict[str, Any]) -> TaskResult:
    """Perform conformance checking between event log and process model.

    Extracted from perform_conformance_task. Supports token replay and alignment.

    Args:
        ctx: DAG context with dataset_id, model_id
        params: Task parameters (method: token_replay or alignment)

    Returns:
        TaskResult with conformance metrics
    """
    start = time.perf_counter()
    dataset_id = ctx.dataset_id or params.get("dataset_id")
    model_id = ctx.model_id or params.get("model_id")
    method = params.get("method", "token_replay")

    if not dataset_id:
        return TaskResult.fail("dataset_id is required")
    if not model_id:
        return TaskResult.fail("model_id is required")

    logger.info(
        "check_conformance_started",
        dataset_id=dataset_id,
        model_id=model_id,
        method=method,
        run_id=ctx.run_id,
    )

    try:

        # TODO: Fix this - conformance_service.check_conformance_by_ids doesn't exist
        # Need to load Dataset and ProcessModel objects from DB first,
        # then call conformance_service.check_conformance(event_log, model, method)
        # For now, this DAG task is non-functional and needs refactoring
        raise NotImplementedError(
            "DAG task check_conformance needs refactoring: check_conformance_by_ids method doesn't exist. "
            "Need to load Dataset and ProcessModel ORM objects from database first, "
            "then call conformance_service.check_conformance(event_log, model, method)"
        )

        # Store in context
        ctx.set("conformance_result", conf_result)

        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "check_conformance_completed",
            dataset_id=dataset_id,
            model_id=model_id,
            fitness=conf_result.get("fitness"),
            duration_ms=round(duration_ms, 2),
        )

        return TaskResult.ok(
            data={
                "dataset_id": dataset_id,
                "model_id": model_id,
                "method": method,
                "fitness": conf_result.get("fitness"),
                "precision": conf_result.get("precision"),
                "is_conformant": conf_result.get("is_conformant"),
                "fitting_traces": conf_result.get("fitting_traces"),
                "total_traces": conf_result.get("total_traces"),
            },
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error("check_conformance_failed", error=str(e), exc_info=True)
        return TaskResult.fail(str(e))


@dag_task("compute_statistics", timeout_seconds=300, max_retries=3)
async def compute_statistics(ctx: DAGContext, params: dict[str, Any]) -> TaskResult:
    """Compute process statistics including DFG and variants.

    Extracted from perform_analysis_task. Computes various process metrics.

    Args:
        ctx: DAG context with dataset_id
        params: Task parameters (analysis_type: discovery, variants, statistics)

    Returns:
        TaskResult with computed statistics
    """
    start = time.perf_counter()
    dataset_id = ctx.dataset_id or params.get("dataset_id")
    analysis_type = params.get("analysis_type", "statistics")

    if not dataset_id:
        return TaskResult.fail("dataset_id is required")

    logger.info(
        "compute_statistics_started",
        dataset_id=dataset_id,
        analysis_type=analysis_type,
        run_id=ctx.run_id,
    )

    try:
        from src.features.process_mining.services.mining import mining_service

        result_data = {}

        if analysis_type == "discovery":
            dfg_data = mining_service.get_dfg_fast(dataset_id)
            result_data["dfg"] = dfg_data
            result_data["summary"] = {
                "nodes_count": len(dfg_data.get("nodes", [])),
                "edges_count": len(dfg_data.get("edges", [])),
                "start_activities": list(dfg_data.get("start_activities", {}).keys()),
                "end_activities": list(dfg_data.get("end_activities", {}).keys()),
            }

        elif analysis_type == "variants":
            variants_data = mining_service.get_variants_fast(dataset_id, top_n=50)
            result_data["variants"] = variants_data
            result_data["summary"] = {
                "total_variants": variants_data.get("total_variants", 0),
                "top_variant": variants_data.get("top_variants", [{}])[0]
                if variants_data.get("top_variants")
                else None,
            }

        else:
            stats = mining_service.get_statistics_fast(dataset_id)
            result_data["statistics"] = stats
            result_data["summary"] = stats

        # Store in context
        ctx.set("analysis_result", result_data)

        duration_ms = (time.perf_counter() - start) * 1000

        logger.info(
            "compute_statistics_completed",
            dataset_id=dataset_id,
            analysis_type=analysis_type,
            duration_ms=round(duration_ms, 2),
        )

        return TaskResult.ok(
            data={
                "dataset_id": dataset_id,
                "analysis_type": analysis_type,
                **result_data,
            },
            duration_ms=duration_ms,
        )

    except Exception as e:
        logger.error("compute_statistics_failed", error=str(e), dataset_id=dataset_id)
        return TaskResult.fail(str(e))
