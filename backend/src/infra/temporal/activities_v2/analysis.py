"""Analysis Activities v2 - Stateless and Idempotent.

Activities for process discovery and conformance checking.
Each activity is self-contained and can be retried safely.
"""

import time

import structlog
from temporalio import activity

from src.infra.temporal.activities_v2.types import (
    ConformanceResult,
    DiscoveryResult,
)

logger = structlog.get_logger(__name__)


# =============================================================================
# Event Log Activities
# =============================================================================


@activity.defn
async def load_event_log(dataset_id: str) -> dict:
    """Load and verify event log is ready for analysis.

    Idempotent - just reads data.

    Args:
        dataset_id: UUID of the dataset

    Returns:
        dict with is_ready, total_cases, total_events
    """
    logger.info("load_event_log_started", dataset_id=dataset_id)
    activity.heartbeat("loading_event_log")

    try:
        from sqlalchemy import func, select

        from src.features.process_mining.models import (
            Dataset,
            DatasetStatus,
            ProcessCase,
            ProcessEvent,
        )
        from src.infra.infrastructure.database import async_session_maker

        async with async_session_maker() as db:
            dataset = await db.get(Dataset, dataset_id)

            if not dataset:
                return {"is_ready": False, "error": "Dataset not found"}

            if dataset.status != DatasetStatus.READY.value:
                return {
                    "is_ready": False,
                    "error": f"Dataset status is {dataset.status}, expected READY",
                }

            # Get counts
            case_count = (
                await db.scalar(
                    select(func.count())
                    .select_from(ProcessCase)
                    .where(ProcessCase.dataset_id == dataset_id)
                )
                or 0
            )

            event_count = (
                await db.scalar(
                    select(func.count())
                    .select_from(ProcessEvent)
                    .join(ProcessCase)
                    .where(ProcessCase.dataset_id == dataset_id)
                )
                or 0
            )

            activity_count = (
                await db.scalar(
                    select(func.count(func.distinct(ProcessEvent.activity)))
                    .select_from(ProcessEvent)
                    .join(ProcessCase)
                    .where(ProcessCase.dataset_id == dataset_id)
                )
                or 0
            )

        logger.info(
            "load_event_log_completed",
            dataset_id=dataset_id,
            total_cases=case_count,
            total_events=event_count,
        )

        return {
            "is_ready": True,
            "total_cases": case_count,
            "total_events": event_count,
            "total_activities": activity_count,
        }

    except Exception as e:
        logger.error("load_event_log_failed", dataset_id=dataset_id, error=str(e))
        raise


# =============================================================================
# Process Discovery Activities
# =============================================================================


@activity.defn
async def discover_process_model(
    dataset_id: str, miner_type: str, parameters: dict | None = None
) -> DiscoveryResult:
    """Discover process model using specified mining algorithm.

    Long-running operation with heartbeats.

    Args:
        dataset_id: UUID of the dataset
        miner_type: Mining algorithm (alpha, inductive, heuristic, ilp)
        parameters: Algorithm-specific parameters (optional)
            - inductive/inductive_infrequent: noise_threshold (0.0-1.0)
            - heuristics: dependency_threshold (0.0-1.0), and_threshold (0.0-1.0)
            - ilp: alpha (0.0-1.0)
            - log_skeleton: noise_threshold (0.0-1.0)
            - transition_system: direction (forward/backward), window (1-10)

    Returns:
        DiscoveryResult with model_data and initial metrics
    """
    logger.info(
        "discover_process_model_started",
        dataset_id=dataset_id,
        miner_type=miner_type,
        parameters=parameters,
    )
    activity.heartbeat("starting_discovery")

    start_time = time.perf_counter()

    try:
        from sqlalchemy import select

        from src.features.process_mining.models import ProcessCase, ProcessEvent
        from src.infra.infrastructure.database import async_session_maker

        # Load event log data
        activity.heartbeat("loading_events")

        async with async_session_maker() as db:
            # Get all events for dataset
            result = await db.execute(
                select(ProcessEvent, ProcessCase.case_id)
                .join(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
                .order_by(ProcessCase.case_id, ProcessEvent.timestamp)
            )
            rows = result.all()

        # Convert to PM4Py format
        activity.heartbeat("converting_to_pm4py")

        events = []
        for event, case_id in rows:
            events.append(
                {
                    "case:concept:name": case_id,
                    "concept:name": event.activity,
                    "time:timestamp": event.timestamp,
                    "org:resource": event.resource,
                }
            )

        if not events:
            raise ValueError("No events found in dataset")

        # For now, return placeholder - actual PM4Py integration would go here
        activity.heartbeat(f"running_{miner_type}_miner")

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "discover_process_model_completed",
            dataset_id=dataset_id,
            miner_type=miner_type,
            duration_ms=round(duration_ms, 2),
        )

        return DiscoveryResult(
            model_data=b"<pnml></pnml>",  # Placeholder
            model_format="pnml",
            fitness=0.0,
            precision=0.0,
        )

    except Exception as e:
        logger.error(
            "discover_process_model_failed",
            dataset_id=dataset_id,
            miner_type=miner_type,
            error=str(e),
        )
        raise


@activity.defn
async def compute_model_metrics(dataset_id: str, model_data: bytes) -> dict:
    """Compute quality metrics for a process model.

    Args:
        dataset_id: UUID of the dataset
        model_data: Serialized model (PNML)

    Returns:
        dict with fitness, precision, generalization, simplicity
    """
    logger.info("compute_model_metrics_started", dataset_id=dataset_id)
    activity.heartbeat("computing_metrics")

    # Placeholder - actual metrics computation would go here
    return {"fitness": 0.0, "precision": 0.0}


@activity.defn
async def save_process_model(
    dataset_id: str,
    model_name: str,
    model_data: bytes,
    metrics: dict,
) -> str:
    """Save process model to database.

    Idempotent via upsert on (dataset_id, model_name).

    Args:
        dataset_id: UUID of the dataset
        model_name: Name for the model
        model_data: Serialized model
        metrics: Quality metrics

    Returns:
        model_id (UUID string)
    """
    logger.info("save_process_model_started", dataset_id=dataset_id, model_name=model_name)

    try:
        from uuid import uuid4

        from sqlalchemy import select

        from src.features.process_mining.models import ProcessModel
        from src.infra.infrastructure.database import async_session_maker

        async with async_session_maker() as db:
            # Check for existing model with same name
            existing = await db.execute(
                select(ProcessModel).where(
                    ProcessModel.dataset_id == dataset_id,
                    ProcessModel.name == model_name,
                )
            )
            model = existing.scalar_one_or_none()

            if model:
                # Update existing
                model.serialized_model = (
                    model_data.decode("utf-8") if isinstance(model_data, bytes) else model_data
                )
                model.fitness = metrics.get("fitness")
                model.precision = metrics.get("precision")
                model_id = model.id
            else:
                # Create new
                model_id = str(uuid4())
                model = ProcessModel(
                    id=model_id,
                    dataset_id=dataset_id,
                    name=model_name,
                    serialized_model=model_data.decode("utf-8")
                    if isinstance(model_data, bytes)
                    else model_data,
                    fitness=metrics.get("fitness"),
                    precision=metrics.get("precision"),
                )
                db.add(model)

            await db.commit()

        logger.info("save_process_model_completed", model_id=model_id)
        return model_id

    except Exception as e:
        logger.error("save_process_model_failed", dataset_id=dataset_id, error=str(e))
        raise


@activity.defn
async def load_process_model(model_id: str) -> dict:
    """Load process model from database.

    Idempotent - just reads data.

    Args:
        model_id: UUID of the process model

    Returns:
        dict with model_data and metadata
    """
    logger.info("load_process_model_started", model_id=model_id)

    try:
        from src.features.process_mining.models import ProcessModel
        from src.infra.infrastructure.database import async_session_maker

        async with async_session_maker() as db:
            model = await db.get(ProcessModel, model_id)

            if not model:
                raise ValueError(f"Process model not found: {model_id}")

            return {
                "model_id": model.id,
                "model_data": model.serialized_model.encode("utf-8")
                if model.serialized_model
                else b"",
                "model_format": "pnml",
                "name": model.name,
            }

    except Exception as e:
        logger.error("load_process_model_failed", model_id=model_id, error=str(e))
        raise


# =============================================================================
# Conformance Checking Activities
# =============================================================================


@activity.defn
async def check_conformance(
    dataset_id: str,
    model_data: dict,
    method: str,
) -> ConformanceResult:
    """Run conformance checking between event log and model.

    Args:
        dataset_id: UUID of the dataset
        model_data: dict with model_data bytes and format
        method: Conformance method (token_replay or alignment)

    Returns:
        ConformanceResult with fitness, precision, etc.
    """
    logger.info(
        "check_conformance_started",
        dataset_id=dataset_id,
        method=method,
    )
    activity.heartbeat("starting_conformance_check")

    start_time = time.perf_counter()

    try:
        from sqlalchemy import select

        from src.features.process_mining.models import ProcessCase, ProcessEvent
        from src.infra.infrastructure.database import async_session_maker

        # Load event log
        activity.heartbeat("loading_events")

        async with async_session_maker() as db:
            result = await db.execute(
                select(ProcessEvent, ProcessCase.case_id)
                .join(ProcessCase)
                .where(ProcessCase.dataset_id == dataset_id)
                .order_by(ProcessCase.case_id, ProcessEvent.timestamp)
            )
            rows = result.all()

        total_traces = len({case_id for _, case_id in rows})

        duration_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "check_conformance_completed",
            dataset_id=dataset_id,
            duration_ms=round(duration_ms, 2),
        )

        # Placeholder - actual conformance checking would go here
        return ConformanceResult(
            fitness=0.0,
            precision=0.0,
            is_conformant=False,
            fitting_traces=0,
            total_traces=total_traces,
            deviations=[],
        )

    except Exception as e:
        logger.error("check_conformance_failed", dataset_id=dataset_id, error=str(e))
        raise


@activity.defn
async def save_conformance_result(
    dataset_id: str,
    model_id: str,
    result: ConformanceResult,
) -> str:
    """Save conformance result to database.

    Idempotent via upsert on (dataset_id, model_id).

    Args:
        dataset_id: UUID of the dataset
        model_id: UUID of the process model
        result: ConformanceResult

    Returns:
        conformance_id (UUID string)
    """
    logger.info(
        "save_conformance_result_started",
        dataset_id=dataset_id,
        model_id=model_id,
    )

    # Placeholder - actual save would go here
    from uuid import uuid4

    conformance_id = str(uuid4())

    logger.info("save_conformance_result_completed", conformance_id=conformance_id)
    return conformance_id
