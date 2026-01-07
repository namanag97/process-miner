"""Visualization schemas - DFG, Petri nets, and graph structures.

Contains schemas for:
- Directly-Follows Graph (DFG) visualization
- Petri net representation
- Process Explorer unified response
"""

from pydantic import BaseModel

from src.features.process_mining.schemas.datasets import (
    ActivityDetailResponse,
    StatisticsResponse,
    VariantResponse,
)

# =============================================================================
# Directly-Follows Graph (DFG)
# =============================================================================


class DFGNode(BaseModel):
    """DFG node for visualization."""

    id: str
    name: str
    frequency: int
    is_start: bool = False
    is_end: bool = False


class DFGEdge(BaseModel):
    """DFG edge for visualization."""

    source: str
    target: str
    frequency: int
    probability: float
    # Performance metrics (optional, populated when include_performance=true)
    avg_duration_seconds: float | None = None
    min_duration_seconds: float | None = None
    max_duration_seconds: float | None = None


class DFGResponse(BaseModel):
    """DFG graph data for React visualization."""

    nodes: list[DFGNode]
    edges: list[DFGEdge]
    start_activities: dict[str, int]
    end_activities: dict[str, int]
    total_frequency: int


class TieredDFGAggregationInfo(BaseModel):
    """Information about aggregated nodes in tiered graph."""

    clustered_nodes: int
    original_nodes: int


class TieredDFGResponse(BaseModel):
    """Tiered DFG response for progressive loading.

    Supports three tiers:
    - overview: Max 50 nodes, high-frequency edges only
    - standard: Max 500 nodes, moderate edge filtering
    - detailed: Full graph with all nodes and edges

    This enables fast initial rendering with progressive detail enhancement.
    """

    nodes: list[DFGNode]
    edges: list[DFGEdge]
    tier: str  # "overview", "standard", or "detailed"
    total_nodes: int  # Total nodes in full graph
    total_edges: int  # Total edges in full graph
    is_aggregated: bool  # True if nodes were aggregated
    aggregation_info: TieredDFGAggregationInfo | None = None
    start_activities: dict[str, int]
    end_activities: dict[str, int]


class ProcessExplorerDataResponse(BaseModel):
    """Unified response for Process Explorer frontend component.

    Combines DFG, variants, activities, and statistics in a single request.
    """

    dataset_id: str
    dfg: DFGResponse
    variants: list[VariantResponse]
    activities: list[ActivityDetailResponse]
    statistics: StatisticsResponse


# =============================================================================
# Petri Net
# =============================================================================


class PetriNetPlace(BaseModel):
    """Petri net place."""

    id: str
    name: str
    tokens: int = 0


class PetriNetTransition(BaseModel):
    """Petri net transition."""

    id: str
    name: str
    label: str | None


class PetriNetArc(BaseModel):
    """Petri net arc."""

    source: str
    target: str
    weight: int = 1


class PetriNetResponse(BaseModel):
    """Petri net structure for visualization."""

    places: list[PetriNetPlace]
    transitions: list[PetriNetTransition]
    arcs: list[PetriNetArc]
    initial_marking: list[str]
    final_marking: list[str]
