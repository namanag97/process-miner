"""Visualization Router - Graph Data for Frontend.

Endpoints returning structured data for React visualization libraries.
"""

import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.api.dependencies import DBSession
from src.core.enums import ModelFormat
from src.core.logging_config import get_logger
from src.models.orm import Dataset, ProcessCase, ProcessModel
from src.models.schemas import (
    ActivityDetailResponse,
    DFGEdge,
    DFGNode,
    DFGResponse,
    PetriNetArc,
    PetriNetPlace,
    PetriNetResponse,
    PetriNetTransition,
    ProcessExplorerDataResponse,
    StatisticsResponse,
    VariantResponse,
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
    include_performance: bool = Query(
        False, description="Include performance metrics (avg/min/max duration) for edges"
    ),
):
    """
    Get Directly-Follows Graph data for visualization.

    Returns nodes (activities) and edges (transitions) with frequencies,
    optimized for rendering with React Flow, D3, or similar libraries.

    When include_performance=true, edges include timing metrics:
    - avg_duration_seconds: Mean time between activities
    - min_duration_seconds: Minimum time between activities
    - max_duration_seconds: Maximum time between activities
    """
    logger.info("get_dfg_started", log_id=log_id, include_performance=include_performance)
    start_time = time.perf_counter()

    # BUG-038 FIX: Load only Dataset metadata, not cases (mining_service uses DuckDB path)
    query = select(Dataset).where(Dataset.id == log_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("log_not_found", log_id=log_id)
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    # Get DFG data (mining_service uses efficient DuckDB path internally)
    if include_performance:
        dfg_data = mining_service.get_dfg_data_with_performance(event_log)
    else:
        dfg_data = mining_service.get_dfg_data(event_log)

    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "get_dfg_completed",
        log_id=log_id,
        include_performance=include_performance,
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
        arcs.append(
            PetriNetArc(
                source=str(arc.source.name),
                target=str(arc.target.name),
                weight=arc.weight if hasattr(arc, "weight") else 1,
            )
        )

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
        select(Dataset)
        .options(selectinload(Dataset.cases).selectinload(ProcessCase.events))
        .where(Dataset.id == log_id)
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
        select(Dataset)
        .options(selectinload(Dataset.cases).selectinload(ProcessCase.events))
        .where(Dataset.id == log_id)
    )
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    footprints = mining_service.get_footprints(event_log)

    if "error" in footprints:
        raise HTTPException(status_code=500, detail=footprints["error"])

    return footprints


# =============================================================================
# Unified Explorer Data
# =============================================================================


@router.get("/{log_id}/explorer-data", response_model=ProcessExplorerDataResponse)
async def get_explorer_data(
    db: DBSession,
    log_id: str,
    include_performance: bool = Query(True, description="Include performance metrics in DFG edges"),
    include_complexity: bool = Query(True, description="Include complexity metrics in variants"),
    top_variants: int = Query(20, ge=1, le=100, description="Number of top variants to include"),
):
    """
    Get unified explorer data for the Process Explorer frontend component.

    Returns all data needed for the process explorer in a single request:
    - dfg: Directly-Follows Graph with nodes and edges
    - variants: Top process variants with optional complexity metrics
    - activities: Activity statistics with frequency and timing
    - statistics: Overall process statistics

    This endpoint is optimized for the frontend to reduce API calls.
    """
    import json

    logger.info(
        "get_explorer_data_started",
        log_id=log_id,
        include_performance=include_performance,
        include_complexity=include_complexity,
        top_variants=top_variants,
    )
    start_time = time.perf_counter()

    # Load event log with all related data
    query = (
        select(Dataset)
        .options(selectinload(Dataset.cases).selectinload(ProcessCase.events))
        .where(Dataset.id == log_id)
    )
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("log_not_found", log_id=log_id)
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    # Get DFG data
    if include_performance:
        dfg_data = mining_service.get_dfg_data_with_performance(event_log)
    else:
        dfg_data = mining_service.get_dfg_data(event_log)

    dfg_response = DFGResponse(
        nodes=[DFGNode(**n) for n in dfg_data["nodes"]],
        edges=[DFGEdge(**e) for e in dfg_data["edges"]],
        start_activities=dfg_data["start_activities"],
        end_activities=dfg_data["end_activities"],
        total_frequency=dfg_data["total_frequency"],
    )

    # Get variants
    variant_cases: dict[str, list[ProcessCase]] = {}
    for case in event_log.cases:
        key = case.variant_key or "unknown"
        if key not in variant_cases:
            variant_cases[key] = []
        variant_cases[key].append(case)

    total_cases = len(event_log.cases)
    sorted_variants = sorted(variant_cases.items(), key=lambda x: -len(x[1]))[:top_variants]

    variants = []
    for variant_key, cases in sorted_variants:
        durations = []
        for case in cases:
            if case.start_time and case.end_time:
                durations.append((case.end_time - case.start_time).total_seconds())

        avg_duration = sum(durations) / len(durations) if durations else None

        # Build response with optional complexity
        complexity_score: Optional[float] = None
        rework_count: Optional[int] = None
        unique_activity_count: Optional[int] = None

        if include_complexity:
            complexity = mining_service.calculate_variant_complexity(variant_key)
            complexity_score = complexity.get("complexity_score")
            rework_count = complexity.get("rework_count")
            unique_activity_count = complexity.get("unique_activity_count")

        variants.append(VariantResponse(
            variant_key=variant_key,
            activity_trace=variant_key,
            case_count=len(cases),
            frequency_percent=round(len(cases) / total_cases * 100, 2) if total_cases > 0 else 0.0,
            avg_duration_seconds=avg_duration,
            complexity_score=complexity_score,
            rework_count=rework_count,
            unique_activity_count=unique_activity_count,
        ))

    # Get activities
    activities_data = mining_service.get_activity_statistics(event_log)
    activities = [ActivityDetailResponse(**a) for a in activities_data]

    # Get statistics
    activities_list = json.loads(event_log.activities_json) if event_log.activities_json else []
    start_activities = mining_service.get_start_activities(event_log)
    end_activities = mining_service.get_end_activities(event_log)
    case_stats = mining_service.get_case_statistics(event_log)
    variants_data = mining_service.get_variants(event_log)

    date_range = None
    if event_log.cases:
        all_times = []
        for case in event_log.cases:
            if case.start_time:
                all_times.append(case.start_time)
            if case.end_time:
                all_times.append(case.end_time)
        if all_times:
            date_range = {"start": min(all_times), "end": max(all_times)}

    statistics = StatisticsResponse(
        total_events=event_log.total_events,
        total_cases=event_log.total_cases,
        total_activities=event_log.total_activities,
        total_variants=variants_data.get("total_variants", 0),
        activities=activities_list,
        start_activities=start_activities,
        end_activities=end_activities,
        avg_case_duration_seconds=case_stats.get("avg_duration_seconds"),
        min_case_duration_seconds=case_stats.get("min_duration_seconds"),
        max_case_duration_seconds=case_stats.get("max_duration_seconds"),
        date_range=date_range,
    )

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "get_explorer_data_completed",
        log_id=log_id,
        nodes_count=len(dfg_response.nodes),
        edges_count=len(dfg_response.edges),
        variants_count=len(variants),
        activities_count=len(activities),
        duration_ms=round(duration_ms, 2),
    )

    return ProcessExplorerDataResponse(
        log_id=log_id,
        dfg=dfg_response,
        variants=variants,
        activities=activities,
        statistics=statistics,
    )
