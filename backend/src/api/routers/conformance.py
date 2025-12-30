"""Conformance Checking API Router.

Endpoints for checking conformance between event logs and process models.
"""

import json
import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_session
from src.core.enums import ConformanceMethod
from src.core.logging_config import get_logger
from src.models.orm import ConformanceResult, EventLog, ProcessModel
from src.models.schemas import (
    AlignmentDiagnosticsResponse,
    ConformanceCheckRequest,
    ConformanceListResponse,
    ConformanceResponse,
    DeviationResponse,
    DiagnosticsResponse,
)
from src.services.conformance import conformance_service

logger = get_logger(__name__)

router = APIRouter(prefix="/conformance", tags=["Conformance"])


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post("/check", response_model=ConformanceResponse)
async def check_conformance(
    request: ConformanceCheckRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Check conformance between an event log and a process model.

    Supports two methods:
    - `token_replay`: Fast, token-based replay (default)
    - `alignment`: More accurate, alignment-based (slower)

    Returns fitness, precision, and conformance status.
    """
    logger.info(
        "conformance_check_started",
        log_id=request.log_id,
        model_id=request.model_id,
        method=str(request.method),
    )
    start_time = time.perf_counter()

    # Get the event log with cases and events
    log_result = await session.execute(
        select(EventLog).where(EventLog.id == request.log_id)
    )
    event_log = log_result.scalar_one_or_none()

    if not event_log:
        logger.warning("log_not_found", log_id=request.log_id)
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get the process model
    model_result = await session.execute(
        select(ProcessModel).where(ProcessModel.id == request.model_id)
    )
    model = model_result.scalar_one_or_none()

    if not model:
        logger.warning("model_not_found", model_id=request.model_id)
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        logger.warning("model_no_data", model_id=request.model_id)
        raise HTTPException(
            status_code=400,
            detail="Process model has no serialized data - rediscover the model",
        )

    try:
        # Run conformance check
        result = conformance_service.check_conformance(
            event_log=event_log,
            model=model,
            method=request.method,
        )

        # Store result in database
        conformance_record = ConformanceResult(
            log_id=request.log_id,
            model_id=request.model_id,
            fitness=result["fitness"],
            precision=result.get("precision"),
            method=result["method"],
            diagnostics_json=json.dumps({
                "fitting_traces": result["fitting_traces"],
                "total_traces": result["total_traces"],
            }),
        )
        session.add(conformance_record)
        await session.commit()
        await session.refresh(conformance_record)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "conformance_check_completed",
            result_id=conformance_record.id,
            fitness=result["fitness"],
            is_conformant=result["is_conformant"],
            fitting_traces=result["fitting_traces"],
            total_traces=result["total_traces"],
            duration_ms=round(duration_ms, 2),
        )

        return ConformanceResponse(
            id=conformance_record.id,
            log_id=conformance_record.log_id,
            model_id=conformance_record.model_id,
            fitness=conformance_record.fitness,
            precision=conformance_record.precision,
            method=conformance_record.method,
            is_conformant=result["is_conformant"],
            fitting_traces=result["fitting_traces"],
            total_traces=result["total_traces"],
            created_at=conformance_record.created_at,
        )

    except Exception as e:
        logger.error(
            "conformance_check_failed",
            log_id=request.log_id,
            model_id=request.model_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Conformance check failed: {str(e)}",
        )


@router.get("/results", response_model=ConformanceListResponse)
async def list_conformance_results(
    log_id: Optional[str] = Query(None, description="Filter by event log ID"),
    model_id: Optional[str] = Query(None, description="Filter by model ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """
    List conformance check results.

    Optionally filter by log_id or model_id.
    """
    query = select(ConformanceResult)

    if log_id:
        query = query.where(ConformanceResult.log_id == log_id)
    if model_id:
        query = query.where(ConformanceResult.model_id == model_id)

    query = query.order_by(ConformanceResult.created_at.desc())

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    results = result.scalars().all()

    items = []
    for r in results:
        diagnostics = json.loads(r.diagnostics_json) if r.diagnostics_json else {}
        items.append(
            ConformanceResponse(
                id=r.id,
                log_id=r.log_id,
                model_id=r.model_id,
                fitness=r.fitness,
                precision=r.precision,
                method=r.method,
                is_conformant=r.fitness >= 0.8,
                fitting_traces=diagnostics.get("fitting_traces", 0),
                total_traces=diagnostics.get("total_traces", 0),
                created_at=r.created_at,
            )
        )

    return ConformanceListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/results/{result_id}", response_model=ConformanceResponse)
async def get_conformance_result(
    result_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific conformance check result.
    """
    result = await session.execute(
        select(ConformanceResult).where(ConformanceResult.id == result_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Conformance result not found")

    diagnostics = json.loads(record.diagnostics_json) if record.diagnostics_json else {}

    return ConformanceResponse(
        id=record.id,
        log_id=record.log_id,
        model_id=record.model_id,
        fitness=record.fitness,
        precision=record.precision,
        method=record.method,
        is_conformant=record.fitness >= 0.8,
        fitting_traces=diagnostics.get("fitting_traces", 0),
        total_traces=diagnostics.get("total_traces", 0),
        created_at=record.created_at,
    )


@router.delete("/results/{result_id}")
async def delete_conformance_result(
    result_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a conformance check result.
    """
    result = await session.execute(
        select(ConformanceResult).where(ConformanceResult.id == result_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Conformance result not found")

    await session.delete(record)
    await session.commit()

    return {"status": "deleted", "result_id": result_id}


@router.get("/diagnostics/{log_id}/{model_id}", response_model=DiagnosticsResponse)
async def get_conformance_diagnostics(
    log_id: str,
    model_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get detailed conformance diagnostics for a log-model pair.

    Returns trace-level analysis including deviations.
    """
    # Get the event log
    log_result = await session.execute(
        select(EventLog).where(EventLog.id == log_id)
    )
    event_log = log_result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get the process model
    model_result = await session.execute(
        select(ProcessModel).where(ProcessModel.id == model_id)
    )
    model = model_result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        raise HTTPException(
            status_code=400,
            detail="Process model has no serialized data",
        )

    try:
        # Get detailed diagnostics
        diagnostics = conformance_service.get_diagnostics(event_log, model)

        # Also get fitness/precision for completeness
        result = conformance_service.check_conformance(event_log, model)

        return DiagnosticsResponse(
            fitness=result["fitness"],
            precision=result.get("precision"),
            total_traces=diagnostics["total_traces"],
            fitting_traces=diagnostics["fitting_traces"],
            non_fitting_traces=diagnostics["non_fitting_traces"],
            fitness_ratio=diagnostics["fitness_ratio"],
            deviations=diagnostics["deviations"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get diagnostics: {str(e)}",
        )


@router.get("/deviations/{log_id}/{model_id}", response_model=list[DeviationResponse])
async def get_deviations(
    log_id: str,
    model_id: str,
    threshold: float = Query(0.8, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_session),
):
    """
    Detect and list specific deviations from the model.

    Returns case-level deviation information.
    """
    # Get the event log
    log_result = await session.execute(
        select(EventLog).where(EventLog.id == log_id)
    )
    event_log = log_result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get the process model
    model_result = await session.execute(
        select(ProcessModel).where(ProcessModel.id == model_id)
    )
    model = model_result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        raise HTTPException(
            status_code=400,
            detail="Process model has no serialized data",
        )

    try:
        deviations = conformance_service.detect_deviations(
            event_log, model, threshold
        )

        return [
            DeviationResponse(
                case_id=d["case_id"],
                activity=d.get("activity"),
                deviation_type=d["deviation_type"],
                details=d["details"],
            )
            for d in deviations[:100]  # Limit to 100 deviations
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect deviations: {str(e)}",
        )


@router.get("/alignments/{log_id}/{model_id}", response_model=AlignmentDiagnosticsResponse)
async def get_alignment_diagnostics(
    log_id: str,
    model_id: str,
    max_cases: int = Query(100, ge=1, le=1000, description="Max cases to include"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get detailed alignment diagnostics for a log-model pair.

    Uses PM4Py's alignment-based conformance checking to compute optimal
    alignments between traces and the process model. This provides:
    - Per-case fitness scores
    - Detailed alignment moves (sync, log-only, model-only)
    - Identification of deviating activities

    Note: This is computationally expensive for large logs. Use max_cases to limit.
    """
    logger.info(
        "alignment_diagnostics_started",
        log_id=log_id,
        model_id=model_id,
        max_cases=max_cases,
    )
    start_time = time.perf_counter()

    # Get the event log
    log_result = await session.execute(
        select(EventLog).where(EventLog.id == log_id)
    )
    event_log = log_result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get the process model
    model_result = await session.execute(
        select(ProcessModel).where(ProcessModel.id == model_id)
    )
    model = model_result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        raise HTTPException(
            status_code=400,
            detail="Process model has no serialized data",
        )

    try:
        # Get alignment diagnostics
        diagnostics = conformance_service.get_alignment_diagnostics(
            event_log, model, max_cases
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "alignment_diagnostics_completed",
            log_id=log_id,
            model_id=model_id,
            total_cases=diagnostics["total_cases"],
            fitting_cases=diagnostics["fitting_cases"],
            average_fitness=diagnostics["average_fitness"],
            duration_ms=round(duration_ms, 2),
        )

        return AlignmentDiagnosticsResponse(
            log_id=log_id,
            model_id=model_id,
            total_cases=diagnostics["total_cases"],
            fitting_cases=diagnostics["fitting_cases"],
            average_fitness=diagnostics["average_fitness"],
            case_alignments=diagnostics["case_alignments"],
        )

    except Exception as e:
        logger.error(
            "alignment_diagnostics_failed",
            log_id=log_id,
            model_id=model_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get alignment diagnostics: {str(e)}",
        )


@router.get("/methods")
async def list_conformance_methods():
    """
    List available conformance checking methods.
    """
    return [
        {
            "id": ConformanceMethod.TOKEN_REPLAY.value,
            "name": "Token Replay",
            "description": "Fast token-based replay conformance checking",
            "is_default": True,
        },
        {
            "id": ConformanceMethod.ALIGNMENT.value,
            "name": "Alignment",
            "description": "More accurate alignment-based conformance (slower)",
            "is_default": False,
        },
    ]
