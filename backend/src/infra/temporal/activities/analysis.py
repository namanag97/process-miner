"""Analysis Activities.

Temporal activities for process mining analysis workflows.
Each activity is a discrete, retriable unit of work.
"""

import json

import structlog
from temporalio import activity

from src.infra.temporal.activities.types import (
    CheckConformanceInput,
    CheckConformanceOutput,
    ComputeMetricsInput,
    ComputeMetricsOutput,
    LoadEventLogInput,
    LoadEventLogOutput,
    MineModelInput,
    MineModelOutput,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Load Event Log Activity
# =============================================================================


@activity.defn
async def load_event_log_activity(input: LoadEventLogInput) -> LoadEventLogOutput:
    """Load dataset metadata from database.

    Verifies the dataset exists and is in READY state for analysis.

    Args:
        input: LoadEventLogInput with dataset_id

    Returns:
        LoadEventLogOutput with dataset info
    """
    logger.info(
        "load_event_log_activity_started",
        dataset_id=input.dataset_id,
    )

    try:
        from sqlalchemy import select

        from src.features.process_mining.models import Dataset, DatasetStatus
        from src.infra.infrastructure.database import async_session_maker

        async with async_session_maker() as db:
            result = await db.execute(select(Dataset).where(Dataset.id == input.dataset_id))
            dataset = result.scalar_one_or_none()

            if not dataset:
                raise ValueError(f"Dataset not found: {input.dataset_id}")

            if dataset.status != DatasetStatus.READY.value:
                raise ValueError(
                    f"Dataset {input.dataset_id} is not ready for analysis. "
                    f"Status: {dataset.status}"
                )

            logger.info(
                "load_event_log_activity_completed",
                dataset_id=input.dataset_id,
                total_cases=dataset.total_cases,
                total_events=dataset.total_events,
            )

            return LoadEventLogOutput(
                dataset_id=input.dataset_id,
                dataset_name=dataset.name,
                total_cases=dataset.total_cases or 0,
                total_events=dataset.total_events or 0,
                is_loaded=True,
            )

    except Exception as e:
        logger.error(
            "load_event_log_activity_failed",
            dataset_id=input.dataset_id,
            error=str(e),
        )
        raise


# =============================================================================
# Mine Model Activity
# =============================================================================


@activity.defn
async def mine_model_activity(input: MineModelInput) -> MineModelOutput:
    """Run process discovery algorithm.

    Executes PM4Py mining algorithms (Alpha, Inductive, Heuristic, ILP).
    This is a CPU-intensive operation with heartbeats.

    Args:
        input: MineModelInput with miner type and options

    Returns:
        MineModelOutput with model data
    """
    logger.info(
        "mine_model_activity_started",
        dataset_id=input.dataset_id,
        miner_type=input.miner_type,
    )

    try:
        from sqlalchemy import select

        from src.features.process_mining.enums import MinerType
        from src.features.process_mining.models import Dataset, ProcessModel
        from src.features.process_mining.services.mining import mining_service
        from src.infra.infrastructure.database import async_session_maker

        # Heartbeat at start
        activity.heartbeat("loading_dataset")

        async with async_session_maker() as db:
            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == input.dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {input.dataset_id}")

            # Heartbeat before mining
            activity.heartbeat("running_miner")

            # Validate miner type
            try:
                miner_enum = MinerType(input.miner_type)
            except ValueError:
                raise ValueError(f"Invalid miner type: {input.miner_type}")

            # Run discovery
            model_data, model_format = mining_service.discover(dataset, miner_enum)

            # Heartbeat after mining
            activity.heartbeat("serializing_model")

            # Serialize model
            serialized = mining_service.serialize_model(model_data)
            final_name = input.model_name or f"{dataset.name}_{input.miner_type}"

            # Convert to graph JSON
            graph_json = mining_service.serialize_to_graph_json(model_data, model_format)

            # Compute quality metrics if possible
            fitness = None
            precision = None
            if model_format.value in ["petri_net", "process_tree"]:
                try:
                    if model_format.value == "petri_net":
                        net, im, fm = model_data
                    else:
                        net, im, fm = mining_service.tree_to_petri_net(model_data)
                    fitness_result = mining_service.evaluate_fitness(dataset, net, im, fm)
                    fitness = fitness_result.get("fitness")
                    precision = mining_service.evaluate_precision(dataset, net, im, fm)
                except Exception as e:
                    logger.warning("quality_metrics_failed", error=str(e))

            # Save model to database
            process_model = ProcessModel(
                name=final_name,
                dataset_id=input.dataset_id,
                miner_type=input.miner_type,
                model_format=model_format.value,
                serialized_model=serialized,
                graph_structure_json=json.dumps(graph_json) if graph_json else None,
                fitness=fitness,
                precision=precision,
            )
            db.add(process_model)
            await db.commit()
            await db.refresh(process_model)

            logger.info(
                "mine_model_activity_completed",
                model_id=process_model.id,
                miner_type=input.miner_type,
                fitness=fitness,
                precision=precision,
            )

            return MineModelOutput(
                model_id=process_model.id,
                dataset_id=input.dataset_id,
                miner_type=input.miner_type,
                model_format=model_format.value,
                serialized_model=serialized,
                graph_json=graph_json,
                fitness=fitness,
                precision=precision,
            )

    except Exception as e:
        logger.error(
            "mine_model_activity_failed",
            dataset_id=input.dataset_id,
            miner_type=input.miner_type,
            error=str(e),
        )
        raise


# =============================================================================
# Compute Metrics Activity
# =============================================================================


@activity.defn
async def compute_metrics_activity(input: ComputeMetricsInput) -> ComputeMetricsOutput:
    """Compute quality metrics for a process model.

    Evaluates fitness, precision, generalization, and simplicity.

    Args:
        input: ComputeMetricsInput with model_id

    Returns:
        ComputeMetricsOutput with quality metrics
    """
    logger.info(
        "compute_metrics_activity_started",
        dataset_id=input.dataset_id,
        model_id=input.model_id,
    )

    try:
        from sqlalchemy import select

        from src.features.process_mining.models import Dataset, ProcessModel
        from src.features.process_mining.services.mining import mining_service
        from src.infra.infrastructure.database import async_session_maker

        async with async_session_maker() as db:
            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == input.dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {input.dataset_id}")

            # Load model
            result = await db.execute(select(ProcessModel).where(ProcessModel.id == input.model_id))
            model = result.scalar_one_or_none()
            if not model:
                raise ValueError(f"Model not found: {input.model_id}")

            # Deserialize model
            model_data = mining_service.deserialize_model(model.serialized_model)

            # Compute metrics
            fitness = None
            precision = None
            generalization = None
            simplicity = None

            if model.model_format in ["petri_net", "process_tree"]:
                try:
                    if model.model_format == "petri_net":
                        net, im, fm = model_data
                    else:
                        net, im, fm = mining_service.tree_to_petri_net(model_data)

                    fitness_result = mining_service.evaluate_fitness(dataset, net, im, fm)
                    fitness = fitness_result.get("fitness")
                    precision = mining_service.evaluate_precision(dataset, net, im, fm)
                except Exception as e:
                    logger.warning("metrics_computation_failed", error=str(e))

            # Update model with metrics
            if fitness is not None:
                model.fitness = fitness
            if precision is not None:
                model.precision = precision
            await db.commit()

            logger.info(
                "compute_metrics_activity_completed",
                model_id=input.model_id,
                fitness=fitness,
                precision=precision,
            )

            return ComputeMetricsOutput(
                model_id=input.model_id,
                fitness=fitness,
                precision=precision,
                generalization=generalization,
                simplicity=simplicity,
            )

    except Exception as e:
        logger.error(
            "compute_metrics_activity_failed",
            model_id=input.model_id,
            error=str(e),
        )
        raise


# =============================================================================
# Check Conformance Activity
# =============================================================================


@activity.defn
async def check_conformance_activity(input: CheckConformanceInput) -> CheckConformanceOutput:
    """Check conformance between event log and process model.

    Supports token replay and alignment-based conformance checking.

    Args:
        input: CheckConformanceInput with model and method

    Returns:
        CheckConformanceOutput with conformance results
    """
    logger.info(
        "check_conformance_activity_started",
        dataset_id=input.dataset_id,
        model_id=input.model_id,
        method=input.method,
    )

    try:
        from sqlalchemy import select

        from src.features.process_mining.models import (
            ConformanceResult,
            Dataset,
            ProcessModel,
        )
        from src.features.process_mining.services.conformance import conformance_service
        from src.infra.infrastructure.database import async_session_maker

        async with async_session_maker() as db:
            # Load dataset
            result = await db.execute(select(Dataset).where(Dataset.id == input.dataset_id))
            dataset = result.scalar_one_or_none()
            if not dataset:
                raise ValueError(f"Dataset not found: {input.dataset_id}")

            # Load model
            result = await db.execute(select(ProcessModel).where(ProcessModel.id == input.model_id))
            model = result.scalar_one_or_none()
            if not model:
                raise ValueError(f"Model not found: {input.model_id}")

            # Run conformance check
            conf_result = conformance_service.check_conformance(
                event_log=dataset,
                model=model,
                method=input.method,
            )

            # Create conformance record
            conformance_record = ConformanceResult(
                dataset_id=input.dataset_id,
                model_id=input.model_id,
                fitness=conf_result["fitness"],
                precision=conf_result.get("precision"),
                method=conf_result["method"],
                diagnostics_json=json.dumps(
                    {
                        "fitting_traces": conf_result["fitting_traces"],
                        "total_traces": conf_result["total_traces"],
                    }
                ),
            )
            db.add(conformance_record)
            await db.commit()
            await db.refresh(conformance_record)

            logger.info(
                "check_conformance_activity_completed",
                conformance_id=conformance_record.id,
                fitness=conf_result["fitness"],
            )

            return CheckConformanceOutput(
                conformance_id=conformance_record.id,
                dataset_id=input.dataset_id,
                model_id=input.model_id,
                fitness=conf_result["fitness"],
                precision=conf_result.get("precision"),
                is_conformant=conf_result["is_conformant"],
                fitting_traces=conf_result["fitting_traces"],
                total_traces=conf_result["total_traces"],
            )

    except Exception as e:
        logger.error(
            "check_conformance_activity_failed",
            dataset_id=input.dataset_id,
            model_id=input.model_id,
            error=str(e),
        )
        raise


__all__ = [
    "check_conformance_activity",
    "compute_metrics_activity",
    "load_event_log_activity",
    "mine_model_activity",
]
