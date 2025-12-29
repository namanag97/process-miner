"""Discovery Router - Process Mining Algorithms.

Endpoints for running mining algorithms and managing discovered models.
"""

import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from src.api.dependencies import DBSession
from src.core.enums import MinerType
from src.core.logging_config import get_logger
from src.models.orm import EventLog, ProcessCase, ProcessModel
from src.models.schemas import (
    DiscoverRequest,
    MinerInfo,
    ModelListResponse,
    ModelResponse,
)
from src.services.mining import mining_service

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


@router.post("/discover", response_model=ModelResponse)
async def discover_model(
    db: DBSession,
    request: DiscoverRequest,
):
    """
    Discover a process model from an event log.

    Runs the specified mining algorithm and stores the resulting model.
    """
    logger.info(
        "discovery_started",
        log_id=request.log_id,
        miner_type=str(request.miner_type),
        model_name=request.model_name,
    )
    start_time = time.perf_counter()

    # Load event log with cases and events
    query = (
        select(EventLog)
        .options(selectinload(EventLog.cases).selectinload(ProcessCase.events))
        .where(EventLog.id == request.log_id)
    )
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("log_not_found", log_id=request.log_id)
        raise HTTPException(status_code=404, detail=f"Event log not found: {request.log_id}")

    # Validate miner type
    try:
        miner_type = MinerType(request.miner_type)
    except ValueError:
        valid_types = [m.value for m in MinerType]
        logger.warning("invalid_miner_type", miner_type=str(request.miner_type))
        raise HTTPException(
            status_code=400,
            detail=f"Invalid miner type: {request.miner_type}. Valid types: {valid_types}",
        )

    # Run discovery
    try:
        model_data, model_format = mining_service.discover(event_log, miner_type)
    except Exception as e:
        logger.error("discovery_failed", log_id=request.log_id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Discovery failed: {str(e)}")

    # Create model name
    model_name = request.model_name or f"{event_log.name}_{miner_type.value}"

    # Serialize model
    serialized = mining_service.serialize_model(model_data)

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
        except Exception:
            pass  # Quality metrics are optional

    # Save model
    process_model = ProcessModel(
        name=model_name,
        log_id=event_log.id,
        miner_type=miner_type.value,
        model_format=model_format.value,
        serialized_model=serialized,
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
        log_id=process_model.log_id,
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
    log_id: Optional[str] = Query(None),
):
    """
    List discovered process models.

    Supports pagination and filtering by source log.
    """
    logger.debug("list_models", page=page, page_size=page_size, log_id=log_id)
    query = select(ProcessModel).order_by(ProcessModel.created_at.desc())

    if log_id:
        query = query.where(ProcessModel.log_id == log_id)

    # Count total
    count_query = select(func.count()).select_from(ProcessModel)
    if log_id:
        count_query = count_query.where(ProcessModel.log_id == log_id)

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
            log_id=m.log_id,
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
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    return ModelResponse(
        id=model.id,
        name=model.name,
        miner_type=model.miner_type,
        model_format=model.model_format,
        log_id=model.log_id,
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
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    await db.delete(model)
    await db.flush()
    logger.info("delete_model_completed", model_id=model_id)

    return {"status": "deleted", "id": model_id}
