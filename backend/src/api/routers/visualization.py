"""Visualization Router - Graph Data for Frontend.

Endpoints returning structured data for React visualization libraries.
"""

import time

from fastapi import APIRouter, HTTPException, Query, Response
from sqlalchemy import select

from src.api.dependencies import DBSession
from src.core.enums import ModelFormat
from src.core.logging_config import get_logger
from src.models.orm import Dataset, ProcessModel
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

    # FIX: Validate dataset is ready for visualization
    from src.models.orm import DatasetStatus

    if event_log.status != DatasetStatus.READY.value:
        logger.warning("dataset_not_ready", log_id=log_id, status=event_log.status)
        raise HTTPException(
            status_code=409,
            detail=f"Dataset not ready (status: {event_log.status}). Complete ingestion first.",
        )

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

    initial_marking = [str(p.name) for p in im] if im else []
    final_marking = [str(p.name) for p in fm] if fm else []

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
        raise HTTPException(status_code=500, detail=f"Visualization failed: {e!s}")

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
    # BUG-060 FIX: Remove eager load of cases/events (OOM risk)
    # mining_service methods below use DuckDB path which is memory efficient
    query = select(Dataset).where(Dataset.id == log_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    # Discover DFG using efficient DuckDB path
    try:
        # BUG-060 FIX: Use mining_service.get_dfg_data which uses DuckDB
        dfg_data = mining_service.get_dfg_data(event_log)
        svg_bytes = mining_service.visualize_dfg(
            dfg_data["dfg"], dfg_data["start_activities"], dfg_data["end_activities"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Visualization failed: {e!s}")

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
    # BUG-060 FIX: Remove eager load (OOM risk)
    query = select(Dataset).where(Dataset.id == log_id)
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

    # BUG-060 FIX: Remove eager loading of cases/events (Severe OOM risk)
    # mining_service methods below (get_dfg_data, get_variants_fast, etc.)
    # all leverage DuckDB for vectorized/streaming calculation.
    query = select(Dataset).where(Dataset.id == log_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("log_not_found", log_id=log_id)
        raise HTTPException(status_code=404, detail=f"Event log not found: {log_id}")

    # FIX: Validate dataset is ready for visualization
    from src.models.orm import DatasetStatus

    if event_log.status != DatasetStatus.READY.value:
        logger.warning("dataset_not_ready", log_id=log_id, status=event_log.status)
        raise HTTPException(
            status_code=409,
            detail=f"Dataset not ready (status: {event_log.status}). Complete ingestion first.",
        )

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

    # BUG-060 FIX: Use vectorized variant computation (DuckDB) instead of ORM loop
    variants_data = mining_service.get_variants_fast(log_id, top_n=top_variants)

    variants = []
    for v in variants_data.get("top_variants", []):
        variant_key = v["variant_key"]

        # Build response with optional complexity
        complexity_score: float | None = None
        rework_count: int | None = None
        unique_activity_count: int | None = None

        if include_complexity:
            complexity = mining_service.calculate_variant_complexity(variant_key)
            complexity_score = complexity.get("complexity_score")
            rework_count = complexity.get("rework_count")
            unique_activity_count = complexity.get("unique_activity_count")

        variants.append(
            VariantResponse(
                variant_key=variant_key,
                activity_trace=variant_key,
                case_count=v["case_count"],
                frequency_percent=v["frequency_percent"],
                avg_duration_seconds=v.get("avg_duration_seconds"),
                complexity_score=complexity_score,
                rework_count=rework_count,
                unique_activity_count=unique_activity_count,
            )
        )

    # Get activities
    activities_data = mining_service.get_activity_statistics(event_log)
    activities = [ActivityDetailResponse(**a) for a in activities_data]

    # BUG-060 FIX: Use cached statistics if available, otherwise use DuckDB path
    start_activities = mining_service.get_start_activities(event_log)
    end_activities = mining_service.get_end_activities(event_log)
    case_stats = mining_service.get_case_statistics(event_log)
    # mining_service.get_variants uses DuckDB
    variants_stats = mining_service.get_variants(event_log)

    date_range = None
    if case_stats.get("start_time"):
        date_range = {"start": case_stats["start_time"], "end": case_stats["end_time"]}

    activities_list = json.loads(event_log.activities_json) if event_log.activities_json else []
    statistics = StatisticsResponse(
        total_events=event_log.total_events,
        total_cases=event_log.total_cases,
        total_activities=event_log.total_activities,
        total_variants=variants_stats.get("total_variants", 0),
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
