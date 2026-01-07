"""Visualization Router - Graph Data for Frontend.

Endpoints returning structured data for React visualization libraries.

## Business Context
Visualization endpoints provide graph data for the Process Explorer UI:
- **DFG**: Directly-Follows Graph showing activity flow and frequencies
- **Petri Net**: Formal process model structure (places, transitions, arcs)
- **SVG Export**: Rendered images for download/embedding
- **Explorer Data**: All-in-one endpoint for the Process Explorer component

## Testing Instructions

### Prerequisites
1. Have a dataset in READY status (completed ingestion)
2. Optionally have a discovered process model

### Endpoints
- **DFG Data**: `GET /api/v1/visualization/{dataset_id}/dfg`
- **DFG with Timing**: `GET /api/v1/visualization/{dataset_id}/dfg?include_performance=true`
- **DFG SVG**: `GET /api/v1/visualization/{dataset_id}/dfg/svg`
- **Petri Net**: `GET /api/v1/visualization/models/{model_id}/petri`
- **Model SVG**: `GET /api/v1/visualization/models/{model_id}/svg`
- **Footprints**: `GET /api/v1/visualization/{dataset_id}/footprints`
- **Explorer Data**: `GET /api/v1/visualization/{dataset_id}/explorer-data`

### Common Errors
- **404**: Dataset or Model not found
- **409**: Dataset not ready (complete ingestion first)
- **400**: Model has no serialized data (rediscover)
"""

import time

from fastapi import APIRouter, Query, Response
from sqlalchemy import select

from src.api.dependencies import ReadDBSession, ServiceContainer
from src.features.process_mining.enums import ModelFormat
from src.features.process_mining.models import Dataset, DatasetStatus, ProcessModel
from src.features.process_mining.schemas import (
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
    TieredDFGAggregationInfo,
    TieredDFGResponse,
    VariantResponse,
)
from src.platform.core.exceptions import (
    BadRequestError,
    ConflictError,
    ModelNotFoundError,
    NotFoundError,
    ProcessingError,
)
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/visualization", tags=["Visualization"])

# =============================================================================
# DFG (Directly-Follows Graph)
# =============================================================================


@router.get("/{dataset_id}/dfg", response_model=DFGResponse)
async def get_dfg(
    db: ReadDBSession,
    container: ServiceContainer,
    dataset_id: str,
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
    logger.info("get_dfg_started", dataset_id=dataset_id, include_performance=include_performance)
    start_time = time.perf_counter()

    # BUG-038 FIX: Load only Dataset metadata, not cases (mining_service uses DuckDB path)
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("log_not_found", dataset_id=dataset_id)
        raise NotFoundError(resource='Dataset', resource_id=dataset_id)

    # FIX: Validate dataset is ready for visualization

    if event_log.status != DatasetStatus.READY.value:
        logger.warning("dataset_not_ready", dataset_id=dataset_id, status=event_log.status)
        raise ConflictError(
            message=f"Dataset not ready (status: {event_log.status}). Complete ingestion first."
        )

    # Get DFG data (discovery service uses efficient DuckDB path internally)
    if include_performance:
        dfg_data = container.discovery.get_dfg_data_with_performance(event_log)
    else:
        dfg_data = container.discovery.get_dfg_data(event_log)

    duration_ms = (time.perf_counter() - start_time) * 1000

    logger.info(
        "get_dfg_completed",
        dataset_id=dataset_id,
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
# Tiered DFG (Performance Optimization)
# =============================================================================


@router.get("/{dataset_id}/dfg/tiered", response_model=TieredDFGResponse)
async def get_tiered_dfg(
    db: ReadDBSession,
    container: ServiceContainer,
    dataset_id: str,
    max_nodes: int | None = Query(50, ge=1, le=10000, description="Maximum nodes to return (null for all)"),
    min_edge_frequency: int = Query(1, ge=1, description="Minimum edge frequency to include"),
    aggregate: bool = Query(True, description="Aggregate low-frequency nodes into 'Other' cluster"),
    include_performance: bool = Query(False, description="Include performance metrics on edges"),
):
    """
    Get tiered DFG data for progressive loading performance.

    This endpoint supports three typical configurations:
    - **Overview tier**: max_nodes=50, min_edge_frequency=100, aggregate=true
      Fast initial load with top activities and high-frequency paths
    - **Standard tier**: max_nodes=500, min_edge_frequency=10, aggregate=false
      Balanced view with most activities visible
    - **Detailed tier**: max_nodes=null, min_edge_frequency=1, aggregate=false
      Full graph with all nodes and edges

    The response includes metadata about the full graph size, allowing
    the frontend to show "X of Y nodes" and offer tier upgrades.

    ## Performance Benefits
    - Overview tier typically returns in <50ms for any graph size
    - Enables fast initial render with progressive enhancement
    - Reduces memory usage on frontend for large graphs
    """
    logger.info(
        "get_tiered_dfg_started",
        dataset_id=dataset_id,
        max_nodes=max_nodes,
        min_edge_frequency=min_edge_frequency,
        aggregate=aggregate,
        include_performance=include_performance,
    )
    start_time = time.perf_counter()

    # Load dataset metadata
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise NotFoundError(resource='Dataset', resource_id=dataset_id)

    if event_log.status != DatasetStatus.READY.value:
        raise ConflictError(
            message=f"Dataset not ready (status: {event_log.status}). Complete ingestion first."
        )

    # Get full DFG data
    if include_performance:
        dfg_data = container.discovery.get_dfg_data_with_performance(event_log)
    else:
        dfg_data = container.discovery.get_dfg_data(event_log)

    full_nodes = dfg_data["nodes"]
    full_edges = dfg_data["edges"]
    total_nodes = len(full_nodes)
    total_edges = len(full_edges)

    # Apply edge frequency filtering
    filtered_edges = [e for e in full_edges if e.get("frequency", 0) >= min_edge_frequency]

    # Get nodes connected by filtered edges
    connected_node_ids = set()
    for edge in filtered_edges:
        connected_node_ids.add(edge["source"])
        connected_node_ids.add(edge["target"])

    # Always include start/end nodes
    for node in full_nodes:
        if node.get("is_start") or node.get("is_end"):
            connected_node_ids.add(node["id"])

    # Filter nodes
    filtered_nodes = [n for n in full_nodes if n["id"] in connected_node_ids]

    # Apply max_nodes limit with optional aggregation
    is_aggregated = False
    aggregation_info = None

    if max_nodes is not None and len(filtered_nodes) > max_nodes:
        # Sort by frequency
        filtered_nodes.sort(key=lambda n: n.get("frequency", 0), reverse=True)

        # Separate start/end nodes (always keep)
        start_end_nodes = [n for n in filtered_nodes if n.get("is_start") or n.get("is_end")]
        other_nodes = [n for n in filtered_nodes if not n.get("is_start") and not n.get("is_end")]

        # Calculate available slots
        available_slots = max_nodes - len(start_end_nodes)
        if available_slots < 0:
            available_slots = 0

        # Take top N nodes
        top_nodes = other_nodes[:available_slots]
        excluded_nodes = other_nodes[available_slots:]

        if aggregate and excluded_nodes:
            is_aggregated = True
            # Create aggregated node
            aggregated_frequency = sum(n.get("frequency", 0) for n in excluded_nodes)
            aggregated_node = {
                "id": "__aggregated__",
                "name": f"Other ({len(excluded_nodes)} activities)",
                "frequency": aggregated_frequency,
                "is_start": False,
                "is_end": False,
            }

            filtered_nodes = start_end_nodes + top_nodes + [aggregated_node]

            # Update edges to point to aggregated node
            excluded_ids = {n["id"] for n in excluded_nodes}
            edge_map: dict[str, dict] = {}

            for edge in filtered_edges:
                source = edge["source"]
                target = edge["target"]

                if source in excluded_ids:
                    source = "__aggregated__"
                if target in excluded_ids:
                    target = "__aggregated__"

                # Skip self-loops on aggregated node
                if source == "__aggregated__" and target == "__aggregated__":
                    continue

                key = f"{source}-{target}"
                if key in edge_map:
                    # Merge edge frequencies
                    edge_map[key]["frequency"] += edge.get("frequency", 0)
                else:
                    edge_map[key] = {
                        **edge,
                        "source": source,
                        "target": target,
                    }

            filtered_edges = list(edge_map.values())

            aggregation_info = TieredDFGAggregationInfo(
                clustered_nodes=len(excluded_nodes),
                original_nodes=total_nodes,
            )
        else:
            filtered_nodes = start_end_nodes + top_nodes

    # Filter edges to only include connected nodes
    final_node_ids = {n["id"] for n in filtered_nodes}
    filtered_edges = [
        e for e in filtered_edges
        if e["source"] in final_node_ids and e["target"] in final_node_ids
    ]

    # Determine tier based on parameters
    if max_nodes and max_nodes <= 50:
        tier = "overview"
    elif max_nodes and max_nodes <= 500:
        tier = "standard"
    else:
        tier = "detailed"

    duration_ms = (time.perf_counter() - start_time) * 1000
    logger.info(
        "get_tiered_dfg_completed",
        dataset_id=dataset_id,
        tier=tier,
        returned_nodes=len(filtered_nodes),
        returned_edges=len(filtered_edges),
        total_nodes=total_nodes,
        total_edges=total_edges,
        is_aggregated=is_aggregated,
        duration_ms=round(duration_ms, 2),
    )

    return TieredDFGResponse(
        nodes=[DFGNode(**n) for n in filtered_nodes],
        edges=[DFGEdge(**e) for e in filtered_edges],
        tier=tier,
        total_nodes=total_nodes,
        total_edges=total_edges,
        is_aggregated=is_aggregated,
        aggregation_info=aggregation_info,
        start_activities=dfg_data["start_activities"],
        end_activities=dfg_data["end_activities"],
    )


# =============================================================================
# Petri Net
# =============================================================================


@router.get("/models/{model_id}/petri", response_model=PetriNetResponse)
async def get_petri_net(
    db: ReadDBSession,
    container: ServiceContainer,
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
        raise ModelNotFoundError(model_id=model_id)

    if not model.serialized_model:
        raise BadRequestError(message="Model has no data")

    # Deserialize model
    model_data = container.discovery.deserialize_model(model.serialized_model)

    # Convert to Petri net if needed
    model_format = ModelFormat(model.model_format)

    if model_format == ModelFormat.PETRI_NET:
        net, im, fm = model_data
    elif model_format == ModelFormat.PROCESS_TREE:
        net, im, fm = container.discovery.tree_to_petri_net(model_data)
    else:
        raise BadRequestError(
            message=f"Cannot extract Petri net from format: {model.model_format}"
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
    db: ReadDBSession,
    container: ServiceContainer,
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
        raise ModelNotFoundError(model_id=model_id)

    if not model.serialized_model:
        raise BadRequestError(message="Model has no data")

    # Deserialize and visualize
    model_data = container.discovery.deserialize_model(model.serialized_model)
    model_format = ModelFormat(model.model_format)

    try:
        svg_bytes = container.discovery.visualize_model(model_data, model_format)
    except Exception as e:
        logger.error(
            "model_svg_visualization_failed",
            model_id=model_id,
            model_format=model_format.value,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise ProcessingError(
            message=f"Model visualization failed for {model_id} (format: {model_format.value}): {e!s}"
        )

    return Response(
        content=svg_bytes,
        media_type="image/svg+xml",
    )


@router.get("/{dataset_id}/dfg/svg")
async def get_dfg_svg(
    db: ReadDBSession,
    container: ServiceContainer,
    dataset_id: str,
):
    """
    Get SVG visualization of DFG for an event log.

    Discovers DFG and returns SVG visualization.
    """
    # BUG-060 FIX: Remove eager load of cases/events (OOM risk)
    # mining_service methods below use DuckDB path which is memory efficient
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise NotFoundError(resource='Dataset', resource_id=dataset_id)

    # Discover DFG using efficient DuckDB path
    try:
        # BUG-060 FIX: Use discovery service get_dfg_data which uses DuckDB
        dfg_data = container.discovery.get_dfg_data(event_log)
        svg_bytes = container.discovery.visualize_dfg(
            dfg_data["dfg"], dfg_data["start_activities"], dfg_data["end_activities"]
        )
    except Exception as e:
        logger.error(
            "dfg_svg_visualization_failed",
            dataset_id=dataset_id,
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True,
        )
        raise ProcessingError(
            message=f"DFG visualization failed for dataset {dataset_id}: {e!s}"
        )

    return Response(
        content=svg_bytes,
        media_type="image/svg+xml",
    )


# =============================================================================
# Footprints
# =============================================================================


@router.get("/{dataset_id}/footprints")
async def get_footprints(
    db: ReadDBSession,
    container: ServiceContainer,
    dataset_id: str,
):
    """
    Get behavioral footprints for an event log.

    Shows sequence and parallel relations between activities.
    """
    # BUG-060 FIX: Remove eager load (OOM risk)
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        raise NotFoundError(resource='Dataset', resource_id=dataset_id)

    footprints = container.discovery.get_footprints(event_log)

    if "error" in footprints:
        logger.error(
            "get_footprints_computation_failed",
            dataset_id=dataset_id,
            error=footprints.get("error"),
        )
        raise ProcessingError(
            message=f"Footprint computation failed for dataset {dataset_id}: {footprints['error']}"
        )

    return footprints


# =============================================================================
# Unified Explorer Data
# =============================================================================


@router.get("/{dataset_id}/explorer-data", response_model=ProcessExplorerDataResponse)
async def get_explorer_data(
    db: ReadDBSession,
    container: ServiceContainer,
    dataset_id: str,
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
        dataset_id=dataset_id,
        include_performance=include_performance,
        include_complexity=include_complexity,
        top_variants=top_variants,
    )
    start_time = time.perf_counter()

    # BUG-060 FIX: Remove eager loading of cases/events (Severe OOM risk)
    # mining_service methods below (get_dfg_data, get_variants_fast, etc.)
    # all leverage DuckDB for vectorized/streaming calculation.
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()

    if not event_log:
        logger.warning("log_not_found", dataset_id=dataset_id)
        raise NotFoundError(resource='Dataset', resource_id=dataset_id)

    # FIX: Validate dataset is ready for visualization

    if event_log.status != DatasetStatus.READY.value:
        logger.warning("dataset_not_ready", dataset_id=dataset_id, status=event_log.status)
        raise ConflictError(
            message=
            f"Dataset not ready (status: {event_log.status}). Complete ingestion first.",
        )

    # Get DFG data
    if include_performance:
        dfg_data = container.discovery.get_dfg_data_with_performance(event_log)
    else:
        dfg_data = container.discovery.get_dfg_data(event_log)

    dfg_response = DFGResponse(
        nodes=[DFGNode(**n) for n in dfg_data["nodes"]],
        edges=[DFGEdge(**e) for e in dfg_data["edges"]],
        start_activities=dfg_data["start_activities"],
        end_activities=dfg_data["end_activities"],
        total_frequency=dfg_data["total_frequency"],
    )

    # BUG-060 FIX: Use vectorized variant computation (DuckDB) instead of ORM loop
    variants_data = container.discovery.get_variants_fast(dataset_id, top_n=top_variants)

    variants = []
    for v in variants_data.get("top_variants", []):
        variant_key = v["variant_key"]

        # Build response with optional complexity
        complexity_score: float | None = None
        rework_count: int | None = None
        unique_activity_count: int | None = None

        if include_complexity:
            complexity = container.discovery.calculate_variant_complexity(variant_key)
            complexity_score = complexity.get("complexity_score")
            rework_count = complexity.get("rework_count")
            unique_activity_count = complexity.get("unique_activity_count")

        variants.append(
            VariantResponse(
                variant_key=variant_key,
                activity_trace=variant_key,
                activities=variant_key.split(" → ")
                if variant_key
                else [],  # Parse activities from trace
                case_count=v["case_count"],
                frequency_percent=v["frequency_percent"],
                avg_duration_seconds=v.get("avg_duration_seconds"),
                complexity_score=complexity_score,
                rework_count=rework_count,
                unique_activity_count=unique_activity_count,
            )
        )

    # Get activities
    activities_data = container.discovery.get_activity_statistics(event_log)
    activities = [ActivityDetailResponse(**a) for a in activities_data]

    # BUG-060 FIX: Use cached statistics if available, otherwise use DuckDB path
    start_activities = container.discovery.get_start_activities(event_log)
    end_activities = container.discovery.get_end_activities(event_log)
    case_stats = container.discovery.get_case_statistics(event_log)
    # discovery service get_variants uses DuckDB
    variants_stats = container.discovery.get_variants(event_log)

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
        dataset_id=dataset_id,
        nodes_count=len(dfg_response.nodes),
        edges_count=len(dfg_response.edges),
        variants_count=len(variants),
        activities_count=len(activities),
        duration_ms=round(duration_ms, 2),
    )

    return ProcessExplorerDataResponse(
        dataset_id=dataset_id,
        dfg=dfg_response,
        variants=variants,
        activities=activities,
        statistics=statistics,
    )
