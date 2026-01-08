"""Discovery Router - Process Mining Algorithms.

Endpoints for discovering process models from event logs.
"""

import time

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func, select

from src.api.dependencies import CurrentUser, ReadDBSession, ServiceContainer
from src.features.process_mining.enums import MinerType
from src.features.process_mining.models import Dataset, DatasetStatus, ProcessModel
from src.features.process_mining.schemas import (
    DiscoverRequest,
    MinerInfo,
    ModelListResponse,
    ModelResponse,
)
from src.infra.core.exceptions import (
    DiscoveryError,
    InvalidInputError,
    ModelNotFoundError,
    ProcessNotFoundError,
)
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/discovery", tags=["Discovery"])


# =============================================================================
# Miners
# =============================================================================


@router.get("/miners", response_model=list[MinerInfo])
async def list_miners(container: ServiceContainer):
    """List available mining algorithms."""
    return [MinerInfo(**m) for m in container.discovery.get_available_miners()]


# =============================================================================
# Discover
# =============================================================================


@router.post("/discover")
async def discover_model(
    db: ReadDBSession,
    user: CurrentUser,
    container: ServiceContainer,
    request: DiscoverRequest,
    async_mode: bool = True,
):
    """Discover a process model from an event log."""

    logger.info(
        "discovery_started",
        dataset_id=request.dataset_id,
        miner_type=str(request.miner_type),
        async_mode=async_mode,
    )

    # Verify dataset exists and is ready
    query = select(Dataset).where(Dataset.id == request.dataset_id)
    event_log = (await db.execute(query)).scalar_one_or_none()

    if not event_log:
        raise ProcessNotFoundError(request.dataset_id)
    if event_log.status != DatasetStatus.READY.value:
        raise InvalidInputError(
            f"Dataset not ready (status: {event_log.status}). Complete ingestion first.",
            field="dataset_id",
        )
    if event_log.total_events == 0:
        raise InvalidInputError("Dataset has no events.", field="dataset_id")

    # Validate miner type
    try:
        miner_type = MinerType(request.miner_type)
    except ValueError:
        raise InvalidInputError(
            f"Invalid miner type: {request.miner_type}. Valid: {[m.value for m in MinerType]}",
            field="miner_type",
        )

    # Extract parameters dict from request if provided
    params_dict = None
    if request.parameters:
        params_dict = request.parameters.model_dump(exclude_none=True)

    # Async mode - offload to Temporal v2 workflow
    if async_mode:
        from temporalio.common import WorkflowIDReusePolicy
        from temporalio.exceptions import WorkflowAlreadyStartedError

        from src.infra.temporal.client import get_temporal_client
        from src.infra.temporal.config import get_temporal_config
        from src.infra.temporal.workflows_v2.analysis import ProcessDiscoveryWorkflowV2

        config = get_temporal_config()

        # Deterministic workflow ID
        workflow_id = f"discover-{request.dataset_id}-{miner_type.value}"

        try:
            client = await get_temporal_client()
            await client.start_workflow(
                ProcessDiscoveryWorkflowV2.run,
                args=[request.dataset_id, miner_type.value, request.model_name, params_dict],
                id=workflow_id,
                task_queue=config.QUEUE_ANALYSIS,
                id_reuse_policy=WorkflowIDReusePolicy.ALLOW_DUPLICATE_FAILED_ONLY,
            )
            logger.info("async_discovery_started", workflow_id=workflow_id, parameters=params_dict)
            return JSONResponse(
                status_code=202,
                content={
                    "workflow_id": workflow_id,
                    "status": "queued",
                    "message": "Discovery started. Use /api/v1/operations/{workflow_id} to check status.",
                    "poll_endpoint": f"/api/v1/operations/{workflow_id}",
                },
            )
        except WorkflowAlreadyStartedError:
            # Already running - return existing ID
            logger.info("discovery_workflow_already_running", workflow_id=workflow_id)
            return JSONResponse(
                status_code=202,
                content={
                    "workflow_id": workflow_id,
                    "status": "running",
                    "message": "Discovery already in progress.",
                    "poll_endpoint": f"/api/v1/operations/{workflow_id}",
                },
            )
        except Exception as e:
            # Temporal unavailable - fall back to sync mode
            logger.warning(
                "temporal_unavailable_falling_back_to_sync",
                error=str(e),
                dataset_id=request.dataset_id,
            )

    # Sync mode
    start_time = time.perf_counter()
    try:
        model_data, model_format = container.discovery.discover(event_log, miner_type, params_dict)
    except Exception as e:
        logger.error("discovery_failed", dataset_id=request.dataset_id, error=str(e), exc_info=True)
        raise DiscoveryError(f"Discovery failed: {e!s}", miner_type=miner_type.value)

    model_name = request.model_name or f"{event_log.name}_{miner_type.value}"
    serialized = container.discovery.serialize_model(model_data)
    graph_json = container.discovery.serialize_to_graph_json(model_data, model_format)
    graph_structure_json = __import__("json").dumps(graph_json) if graph_json else None

    fitness, precision = None, None
    if model_format.value in ["petri_net", "process_tree"]:
        try:
            net, im, fm = (
                model_data
                if model_format.value == "petri_net"
                else container.discovery.tree_to_petri_net(model_data)
            )
            fitness = container.discovery.evaluate_fitness(event_log, net, im, fm).get("fitness")
            precision = container.discovery.evaluate_precision(event_log, net, im, fm)
        except Exception as e:
            logger.warning("quality_metrics_failed", error=str(e))

    process_model = ProcessModel(
        name=model_name,
        dataset_id=event_log.id,
        miner_type=miner_type.value,
        model_type=model_format.value,
        model_format=model_format.value,
        serialized_model=serialized,
        graph_structure_json=graph_structure_json,
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
        fitness=fitness,
        duration_ms=round(duration_ms, 2),
    )

    return ModelResponse(
        id=process_model.id,
        name=process_model.name,
        miner_type=process_model.miner_type,
        model_format=process_model.model_format,
        dataset_id=process_model.dataset_id,
        fitness=process_model.fitness,
        precision=process_model.precision,
        created_at=process_model.created_at,
    )


# =============================================================================
# Models
# =============================================================================


@router.get("/models", response_model=ModelListResponse)
async def list_models(
    db: ReadDBSession,
    user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    dataset_id: str | None = Query(None),
):
    """List discovered process models."""
    query = select(ProcessModel).order_by(ProcessModel.created_at.desc())
    if dataset_id:
        query = query.where(ProcessModel.dataset_id == dataset_id)

    count_query = select(func.count()).select_from(ProcessModel)
    if dataset_id:
        count_query = count_query.where(ProcessModel.dataset_id == dataset_id)
    total = await db.scalar(count_query) or 0

    models = (
        (await db.execute(query.offset((page - 1) * page_size).limit(page_size))).scalars().all()
    )
    items = [
        ModelResponse(
            id=m.id,
            name=m.name,
            miner_type=m.miner_type,
            model_format=m.model_format,
            dataset_id=m.dataset_id,
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
async def get_model(db: ReadDBSession, user: CurrentUser, model_id: str):
    """Get details of a discovered process model."""
    model = (
        await db.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    ).scalar_one_or_none()
    if not model:
        raise ModelNotFoundError(model_id)
    return ModelResponse(
        id=model.id,
        name=model.name,
        miner_type=model.miner_type,
        model_format=model.model_format,
        dataset_id=model.dataset_id,
        fitness=model.fitness,
        precision=model.precision,
        created_at=model.created_at,
    )


@router.delete("/models/{model_id}")
async def delete_model(db: ReadDBSession, user: CurrentUser, model_id: str):
    """Delete a discovered process model.

    Requires DATASET_UPDATE permission on the model's dataset.
    """
    from src.infra.core.permissions import Permission
    from src.infra.users.services import require_dataset_permission

    model = (
        await db.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    ).scalar_one_or_none()
    if not model:
        raise ModelNotFoundError(model_id)

    # Verify user has permission to modify the dataset this model belongs to
    await require_dataset_permission(db, model.dataset_id, user, Permission.DATASET_UPDATE)

    await db.delete(model)
    await db.flush()
    logger.info("delete_model_completed", model_id=model_id, user_id=user.id)
    return {"status": "deleted", "id": model_id}


# =============================================================================
# Variants (convenience endpoint - delegates to analytics)
# =============================================================================


@router.get("/variants/{dataset_id}")
async def get_variants(
    db: ReadDBSession,
    user: CurrentUser,
    dataset_id: str,
    top_n: int = Query(20, ge=1, le=100, description="Number of top variants to return"),
):
    """Get process variants (unique activity sequences) for a dataset.

    This is a convenience endpoint that delegates to the analytics variants query.
    Variants are computed from the Parquet file using DuckDB for OLAP performance.

    Returns the top N most frequent variants with:
    - Activity sequence
    - Case count
    - Percentage of total cases
    """
    from src.application.queries.get_variants import GetVariantsHandler, GetVariantsQuery
    from src.infra.infrastructure.duckdb import DuckDBManager

    logger.info("get_variants", dataset_id=dataset_id, user_id=user.id, top_n=top_n)

    # Verify dataset exists and is ready
    query = select(Dataset).where(Dataset.id == dataset_id)
    dataset = (await db.execute(query)).scalar_one_or_none()

    if not dataset:
        raise ProcessNotFoundError(dataset_id)
    if dataset.status != DatasetStatus.READY.value:
        raise InvalidInputError(
            f"Dataset not ready (status: {dataset.status}). Complete ingestion first.",
            field="dataset_id",
        )

    # Execute variants query using DuckDB
    duckdb_manager = DuckDBManager()
    handler = GetVariantsHandler(db, duckdb_manager)
    variants_query = GetVariantsQuery(dataset_id=dataset_id, top_n=top_n)

    result = await handler.handle(variants_query)

    return {
        "dataset_id": result.dataset_id,
        "variants": [
            {
                "variant_id": v.variant_id,
                "activities": v.activities,
                "case_count": v.case_count,
                "percentage": v.percentage,
            }
            for v in result.variants
        ],
        "total_variants": result.total_variants,
        "total_cases": result.total_cases,
    }
