"""Discovery Router - Process Mining Algorithms.

Endpoints for running mining algorithms and managing discovered models.
"""

import time

from fastapi import APIRouter, Query
from sqlalchemy import func, select

from src.api.dependencies import CurrentUser, DBSession
from src.features.process_mining.enums import MinerType
from src.features.process_mining.models import Dataset, ProcessModel
from src.features.process_mining.schemas import (
    DiscoverRequest,
    MinerInfo,
    ModelListResponse,
    ModelResponse,
)
from src.features.process_mining.services.mining import mining_service
from src.platform.core.exceptions import (
    DiscoveryError,
    InvalidInputError,
    ModelNotFoundError,
    ProcessNotFoundError,
)
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/discovery", tags=["Discovery"])


# =============================================================================
# Miners
# =============================================================================


@router.get("/miners", response_model=list[MinerInfo])
async def list_miners():
    """
    List available mining algorithms.

    Returns information about each algorithm including its output format.
    """
    miners = mining_service.get_available_miners()
    return [MinerInfo(**m) for m in miners]


# =============================================================================
# Discover
# =============================================================================


@router.post("/discover")
async def discover_model(
    db: DBSession,
    user: CurrentUser,
    request: DiscoverRequest,
    async_mode: bool = True,  # BUG-019 FIX: Default to async to prevent API blocking
):
    """
    Discover a process model from an event log.

    BUG-019 FIX: Heavy mining is now offloaded to Celery by default.
    Set async_mode=False for synchronous execution (not recommended for large logs).

    Args:
        request: Discovery request with dataset_id, miner_type, model_name
        async_mode: If True (default), runs in background and returns job_id

    Returns:
        - If async_mode=True: {"job_id": "...", "status": "pending"}
        - If async_mode=False: ModelResponse with discovered model
    """
    logger.info(
        "discovery_started",
        dataset_id=request.dataset_id,
        miner_type=str(request.miner_type),
        model_name=request.model_name,
        async_mode=async_mode,
    )

    # Verify dataset exists
    query = select(Dataset).where(Dataset.id == request.dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("dataset_not_found", dataset_id=request.dataset_id)
        raise ProcessNotFoundError(request.dataset_id)

    # FIX: Validate dataset is ready for discovery (has completed ingestion)
    from src.features.process_mining.models import DatasetStatus

    if event_log.status != DatasetStatus.READY.value:
        logger.warning("dataset_not_ready", dataset_id=request.dataset_id, status=event_log.status)
        raise InvalidInputError(
            f"Dataset is not ready for discovery (status: {event_log.status}). "
            f"Please complete ingestion first via POST /datasets/{request.dataset_id}/ingest.",
            field="dataset_id",
        )

    if event_log.total_events == 0:
        logger.warning("dataset_empty", dataset_id=request.dataset_id)
        raise InvalidInputError(
            "Dataset has no events. Cannot discover a process model.",
            field="dataset_id",
        )

    # Validate miner type
    try:
        miner_type = MinerType(request.miner_type)
    except ValueError:
        valid_types = [m.value for m in MinerType]
        logger.warning("invalid_miner_type", miner_type=str(request.miner_type))
        raise InvalidInputError(
            f"Invalid miner type: {request.miner_type}. Valid types: {valid_types}",
            field="miner_type",
        )

    # BUG-019 FIX: Async mode - offload to Celery
    if async_mode:
        import json

        from src.platform.core.enums import EntityType, JobStatus, JobType
        from src.platform.infrastructure.tasks import perform_discovery_task
        from src.platform.models import AsyncJob

        # Create AsyncJob record first with job-centric fields
        async_job = AsyncJob(
            user_id=user.id,  # BUG-002 FIX: Use authenticated user instead of hardcoded "system"
            job_type=JobType.DISCOVERY.value,
            status=JobStatus.QUEUED.value,
            entity_type=EntityType.MODEL.value,
            # entity_id will be set when model is created
            parameters_json=json.dumps(
                {
                    "dataset_id": request.dataset_id,
                    "miner_type": miner_type.value,
                    "model_name": request.model_name,
                }
            ),
        )
        db.add(async_job)
        await db.flush()

        # BUG-006 FIX: Atomicity - commit job record before queuing Celery task
        # This ensures job exists in DB even if Celery fails
        await db.commit()

        try:
            # Queue Celery task
            task = perform_discovery_task.delay(
                dataset_id=request.dataset_id,
                miner_type=miner_type.value,
                model_name=request.model_name,
            )

            # Link task_id to job (best effort - job already committed)
            async_job.task_id = task.id
            await db.commit()
        except Exception as e:
            # If Celery fails, mark job as failed so it doesn't stay QUEUED forever
            logger.error("celery_task_failed", job_id=async_job.id, error=str(e))
            async_job.status = JobStatus.FAILED.value
            async_job.error_message = f"Failed to queue task: {e}"
            await db.commit()
            raise DiscoveryError(
                f"Failed to start discovery task: {e}", miner_type=miner_type.value
            )

        logger.info(
            "async_discovery_started",
            job_id=async_job.id,
            task_id=task.id,
            dataset_id=request.dataset_id,
        )

        # Return 202 Accepted with job_id
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=202,
            content={
                "job_id": async_job.id,
                "task_id": task.id,
                "status": "queued",
                "message": "Discovery started. Use /api/v1/jobs/{job_id} to check status.",
            },
        )

    # Sync mode (legacy, not recommended for large logs)
    start_time = time.perf_counter()

    try:
        model_data, model_format = mining_service.discover(event_log, miner_type)
    except Exception as e:
        logger.error("discovery_failed", dataset_id=request.dataset_id, error=str(e), exc_info=True)
        raise DiscoveryError(f"Discovery failed: {e!s}", miner_type=miner_type.value)

    # Create model name
    model_name = request.model_name or f"{event_log.name}_{miner_type.value}"

    # Serialize model (legacy pickle for backward compatibility)
    serialized = mining_service.serialize_model(model_data)

    # Generate graph JSON for frontend visualization (new architecture)
    graph_json = mining_service.serialize_to_graph_json(model_data, model_format)
    graph_structure_json = None
    if graph_json:
        import json as json_module

        graph_structure_json = json_module.dumps(graph_json)

    # Calculate quality metrics (fitness/precision) if possible
    fitness = None
    precision = None

    if model_format.value in ["petri_net", "process_tree"]:
        try:
            # Get Petri net for evaluation
            if model_format.value == "petri_net":
                net, im, fm = model_data
            else:
                net, im, fm = mining_service.tree_to_petri_net(model_data)

            fitness_result = mining_service.evaluate_fitness(event_log, net, im, fm)
            fitness = fitness_result.get("fitness")
            precision = mining_service.evaluate_precision(event_log, net, im, fm)
        except Exception as e:
            logger.warning(
                "quality_metrics_failed",
                dataset_id=event_log.id,
                error=str(e),
                exc_info=True,
            )
            # Quality metrics are optional - continue without them

    # Save model
    process_model = ProcessModel(
        name=model_name,
        dataset_id=event_log.id,  # BUG-001 FIX: Use dataset_id (ORM field name)
        miner_type=miner_type.value,
        model_format=model_format.value,
        serialized_model=serialized,
        graph_structure_json=graph_structure_json,  # NEW: Store graph JSON
        fitness=fitness,
        precision=precision,
    )
    db.add(process_model)
    await db.flush()
    await db.refresh(process_model)

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "discovery_completed",
        model_id=process_model.id,
        miner_type=miner_type.value,
        fitness=fitness,
        precision=precision,
        duration_ms=round(duration_ms, 2),
    )

    return ModelResponse(
        id=process_model.id,
        name=process_model.name,
        miner_type=process_model.miner_type,
        model_format=process_model.model_format,
        dataset_id=process_model.dataset_id,  # BUG-001 FIX
        fitness=process_model.fitness,
        precision=process_model.precision,
        created_at=process_model.created_at,
    )


# =============================================================================
# Models
# =============================================================================


@router.get("/models", response_model=ModelListResponse)
async def list_models(
    db: DBSession,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    dataset_id: str | None = Query(None),
):
    """
    List discovered process models.

    Supports pagination and filtering by source dataset.
    """
    logger.debug("list_models", page=page, page_size=page_size, dataset_id=dataset_id)
    query = select(ProcessModel).order_by(ProcessModel.created_at.desc())

    if dataset_id:
        query = query.where(ProcessModel.dataset_id == dataset_id)

    # Count total
    count_query = select(func.count()).select_from(ProcessModel)
    if dataset_id:
        count_query = count_query.where(ProcessModel.dataset_id == dataset_id)

    total = await db.scalar(count_query) or 0

    # Paginate
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    result = await db.execute(query)
    models = result.scalars().all()

    items = [
        ModelResponse(
            id=m.id,
            name=m.name,
            miner_type=m.miner_type,
            model_format=m.model_format,
            dataset_id=m.dataset_id,  # BUG-059 FIX
            fitness=m.fitness,
            precision=m.precision,
            created_at=m.created_at,
        )
        for m in models
    ]

    return ModelListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/models/{model_id}", response_model=ModelResponse)
async def get_model(
    db: DBSession,
    model_id: str,
):
    """
    Get details of a discovered process model.
    """
    query = select(ProcessModel).where(ProcessModel.id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise ModelNotFoundError(model_id)

    return ModelResponse(
        id=model.id,
        name=model.name,
        miner_type=model.miner_type,
        model_format=model.model_format,
        dataset_id=model.dataset_id,  # BUG-059 FIX
        fitness=model.fitness,
        precision=model.precision,
        created_at=model.created_at,
    )


@router.delete("/models/{model_id}")
async def delete_model(
    db: DBSession,
    model_id: str,
):
    """
    Delete a discovered process model.
    """
    logger.info("delete_model_started", model_id=model_id)
    query = select(ProcessModel).where(ProcessModel.id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        logger.warning("model_not_found", model_id=model_id)
        raise ModelNotFoundError(model_id)

    await db.delete(model)
    await db.flush()
    logger.info("delete_model_completed", model_id=model_id)

    return {"status": "deleted", "id": model_id}
