from typing import Any
from collections import defaultdict

from ...models import (
    DFGNode, DFGEdge, DFGResponse, DFGSummary, NodePosition, ActivityNodeData, EdgeData,
    VariantItem, VariantsResponse
)

def transform_dfg_for_react_flow(
    dfg_data: dict[str, Any],
    stats: dict[str, Any],
) -> DFGResponse:
    """
    Transform PM4Py DFG output to React Flow format.
    """
    dfg = dfg_data["dfg"]
    start_activities = dfg_data["start_activities"]
    end_activities = dfg_data["end_activities"]
    performance_dfg = dfg_data.get("performance_dfg", {})
    
    # Collect all activity names
    activities: set[str] = set()
    for (source, target) in dfg.keys():
        activities.add(source)
        activities.add(target)
    for act in start_activities:
        activities.add(act)
    for act in end_activities:
        activities.add(act)
    
    # Calculate activity frequencies
    activity_freq: dict[str, int] = defaultdict(int)
    for (source, target), freq in dfg.items():
        activity_freq[source] += freq
        activity_freq[target] += freq
    
    max_frequency = max(activity_freq.values()) if activity_freq else 1
    
    # Simple layout: arrange activities in layers
    # Start activities on left, end on right, others in middle
    start_set = set(start_activities.keys())
    end_set = set(end_activities.keys())
    middle = activities - start_set - end_set
    
    # Position calculation
    x_spacing = 250
    y_spacing = 100
    
    positions: dict[str, tuple[float, float]] = {}
    
    # Position start activities
    start_list = sorted(start_set)
    for i, act in enumerate(start_list):
        positions[act] = (0, i * y_spacing)
    
    # Position middle activities
    middle_list = sorted(middle)
    for i, act in enumerate(middle_list):
        positions[act] = (x_spacing, i * y_spacing)
    
    # Position end activities
    end_list = sorted(end_set)
    for i, act in enumerate(end_list):
        positions[act] = (x_spacing * 2, i * y_spacing)
    
    # Create nodes
    nodes: list[DFGNode] = []
    for act in activities:
        x, y = positions.get(act, (x_spacing, 0))
        freq = activity_freq.get(act, 0)
        
        nodes.append(DFGNode(
            id=_to_node_id(act),
            type="activityNode",
            position=NodePosition(x=x, y=y),
            data=ActivityNodeData(
                label=act,
                frequency=freq,
                isStart=act in start_set,
                isEnd=act in end_set,
                avgDuration=0,  # Would need event-level timing
                maxFrequency=max_frequency,
            ),
        ))
    
    # Create edges
    edges: list[DFGEdge] = []
    for (source, target), freq in dfg.items():
        # Get duration from performance DFG
        duration = 0
        perf_key = (source, target)
        if perf_key in performance_dfg:
            perf_data = performance_dfg[perf_key]
            # Performance DFG returns dict with 'mean' key
            if isinstance(perf_data, dict):
                duration = perf_data.get("mean", 0) * 1000  # Convert to ms
            else:
                duration = float(perf_data) * 1000
        
        edges.append(DFGEdge(
            id=f"e-{_to_node_id(source)}-{_to_node_id(target)}",
            source=_to_node_id(source),
            target=_to_node_id(target),
            type="processEdge",
            data=EdgeData(
                frequency=freq,
                avgDuration=duration,
            ),
        ))
    
    return DFGResponse(
        nodes=nodes,
        edges=edges,
        summary=DFGSummary(
            totalCases=stats["total_cases"],
            totalEvents=stats["total_events"],
            totalActivities=stats["total_activities"],
            totalVariants=stats["total_variants"],
        ),
    )


def transform_variants(variants_data: list[dict]) -> VariantsResponse:
    """
    Transform variant data to response format.
    """
    items = []
    happy_path_set = False
    
    for v in variants_data:
        is_happy = not happy_path_set and v["case_count"] > 0
        if is_happy:
            happy_path_set = True
        
        items.append(VariantItem(
            id=v["id"],
            sequence=v["sequence"],
            trace_display=" -> ".join(v["sequence"]),
            case_count=v["case_count"],
            percentage=round(v["percentage"], 2),
            avg_duration_ms=v["avg_duration_ms"],
            is_happy_path=is_happy,
            case_ids=v["case_ids"],
        ))
    
    return VariantsResponse(
        total=len(items),
        variants=items,
    )


def _to_node_id(activity_name: str) -> str:
    """Convert activity name to a valid React Flow node ID."""
    # Replace spaces and special chars with underscores
    return activity_name.lower().replace(" ", "_").replace("-", "_")
