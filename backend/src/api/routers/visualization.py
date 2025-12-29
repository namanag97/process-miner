"""Visualization Router - Graph Data for Frontend.

Endpoints returning structured data for React visualization libraries.
"""

import time

from fastapi import APIRouter, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.api.dependencies import DBSession
from src.core.enums import ModelFormat
from src.core.logging_config import get_logger
from src.models.orm import EventLog, ProcessCase, ProcessModel
from src.models.schemas import (
    DFGEdge,
    DFGNode,
    DFGResponse,
    PetriNetArc,
    PetriNetPlace,
    PetriNetResponse,
    PetriNetTransition,
)
from src.services.mining import mining_service

logger = get_logger(__name__)

router = APIRouter(prefix="/visualization", tags=["Visualization"])


# =============================================================================
# DFG (Directly-Follows Graph)
# =============================================================================


@router.get("/{log_id}/dfg", response_model=DFGResponse)
async def get_dfg(
    db: DBSession,
    log_id: str,
):
    """
    Get Directly-Follows Graph data for visualization.

    Returns nodes (activities) and edges (transitions) with frequencies,
    optimized for rendering with React Flow, D3, or similar libraries.
    """
    logger.info("get_dfg_started", log_id=log_id)
    start_time = time.perf_counter()

    # Load event log
    query = (
        select(EventLog)
        .options(selectinload(EventLog.cases).selectinload(ProcessCase.events))
        .where(EventLog.id == log_id)
    )
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("log_not_found", log_id=log_id)
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    # Get DFG data
    dfg_data = mining_service.get_dfg_data(event_log)
    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "get_dfg_completed",
        log_id=log_id,
        nodes_count=len(dfg_data["nodes"]),
        edges_count=len(dfg_data["edges"]),
        duration_ms=round(duration_ms, 2),
    )

    return DFGResponse(
        nodes=[DFGNode(**n) for n in dfg_data["nodes"]],
        edges=[DFGEdge(**e) for e in dfg_data["edges"]],
        start_activities=dfg_data["start_activities"],
        end_activities=dfg_data["end_activities"],
        total_frequency=dfg_data["total_frequency"],
    )


# =============================================================================
# Petri Net
# =============================================================================


@router.get("/models/{model_id}/petri", response_model=PetriNetResponse)
async def get_petri_net(
    db: DBSession,
    model_id: str,
):
    """
    Get Petri net structure for visualization.

    Returns places, transitions, and arcs with initial/final markings.
    Works with models discovered using Alpha, Heuristics, or Inductive miners.
    """
    query = select(ProcessModel).where(ProcessModel.id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    if not model.serialized_model:
        raise HTTPException(status_code=400, detail="Model has no data")

    # Deserialize model
    model_data = mining_service.deserialize_model(model.serialized_model)

    # Convert to Petri net if needed
    model_format = ModelFormat(model.model_format)

    if model_format == ModelFormat.PETRI_NET:
        net, im, fm = model_data
    elif model_format == ModelFormat.PROCESS_TREE:
        net, im, fm = mining_service.tree_to_petri_net(model_data)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot extract Petri net from format: {model.model_format}",
        )

    # Extract structure
    places = [
        PetriNetPlace(
            id=str(p.name),
            name=str(p.name),
            tokens=im.get(p, 0) if im else 0,
        )
        for p in net.places
    ]

    transitions = [
        PetriNetTransition(
            id=str(t.name),
            name=str(t.name),
            label=t.label,
        )
        for t in net.transitions
    ]

    arcs = []
    for arc in net.arcs:
        arcs.append(PetriNetArc(
            source=str(arc.source.name),
            target=str(arc.target.name),
            weight=arc.weight if hasattr(arc, "weight") else 1,
        ))

    initial_marking = [str(p.name) for p in im.keys()] if im else []
    final_marking = [str(p.name) for p in fm.keys()] if fm else []

    return PetriNetResponse(
        places=places,
        transitions=transitions,
        arcs=arcs,
        initial_marking=initial_marking,
        final_marking=final_marking,
    )


# =============================================================================
# SVG Export
# =============================================================================


@router.get("/models/{model_id}/svg")
async def get_model_svg(
    db: DBSession,
    model_id: str,
):
    """
    Get SVG visualization of a process model.

    Returns an SVG image that can be displayed directly in the browser.
    """
    query = select(ProcessModel).where(ProcessModel.id == model_id)
    result = await db.execute(query)
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")

    if not model.serialized_model:
        raise HTTPException(status_code=400, detail="Model has no data")

    # Deserialize and visualize
    model_data = mining_service.deserialize_model(model.serialized_model)
    model_format = ModelFormat(model.model_format)

    try:
        svg_bytes = mining_service.visualize_model(model_data, model_format)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization failed: {str(e)}")

    return Response(
        content=svg_bytes,
        media_type="image/svg+xml",
    )


@router.get("/{log_id}/dfg/svg")
async def get_dfg_svg(
    db: DBSession,
    log_id: str,
):
    """
    Get SVG visualization of DFG for an event log.

    Discovers DFG and returns SVG visualization.
    """
    # Load event log
    query = (
        select(EventLog)
        .options(selectinload(EventLog.cases).selectinload(ProcessCase.events))
        .where(EventLog.id == log_id)
    )
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    # Discover DFG
    try:
        dfg, start_activities, end_activities = mining_service._discover_dfg(
            mining_service._to_pm4py_log(event_log)
        )
        svg_bytes = mining_service.visualize_dfg(dfg, start_activities, end_activities)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization failed: {str(e)}")

    return Response(
        content=svg_bytes,
        media_type="image/svg+xml",
    )


# =============================================================================
# Footprints
# =============================================================================


@router.get("/{log_id}/footprints")
async def get_footprints(
    db: DBSession,
    log_id: str,
):
    """
    Get behavioral footprints for an event log.

    Shows sequence and parallel relations between activities.
    """
    query = (
        select(EventLog)
        .options(selectinload(EventLog.cases).selectinload(ProcessCase.events))
        .where(EventLog.id == log_id)
    )
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    footprints = mining_service.get_footprints(event_log)

    if "error" in footprints:
        raise HTTPException(status_code=500, detail=footprints["error"])

    return footprints
