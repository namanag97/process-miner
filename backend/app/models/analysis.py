from typing import Literal
from sqlmodel import SQLModel, Field

class NodePosition(SQLModel):
    """Position for React Flow node."""
    x: float
    y: float


class ActivityNodeData(SQLModel):
    """Data for activity node in process graph."""
    label: str
    frequency: int
    isStart: bool = False
    isEnd: bool = False
    avgDuration: float = 0
    maxFrequency: int = 0


class DFGNode(SQLModel):
    """Node in DFG for React Flow."""
    id: str
    type: str = "activityNode"
    position: NodePosition
    data: ActivityNodeData


class EdgeData(SQLModel):
    """Data for edge in process graph."""
    frequency: int
    avgDuration: float = 0


class DFGEdge(SQLModel):
    """Edge in DFG for React Flow."""
    id: str
    source: str
    target: str
    type: str = "processEdge"
    data: EdgeData


class DFGSummary(SQLModel):
    """Summary statistics for DFG."""
    totalCases: int
    totalEvents: int
    totalActivities: int
    totalVariants: int


class DFGResponse(SQLModel):
    """Complete DFG response in React Flow format."""
    nodes: list[DFGNode]
    edges: list[DFGEdge]
    summary: DFGSummary


class VariantItem(SQLModel):
    """A single process variant."""
    id: str
    sequence: list[str]
    trace_display: str
    case_count: int
    percentage: float
    avg_duration_ms: float
    is_happy_path: bool = False
    case_ids: list[str] = Field(default_factory=list)


class VariantsResponse(SQLModel):
    """Response with variant list."""
    total: int
    variants: list[VariantItem]


class ActivityStat(SQLModel):
    """Statistics for a single activity."""
    name: str
    frequency: int
    frequency_pct: float
    is_start: bool
    is_end: bool
    avg_duration_ms: float


class Deviation(SQLModel):
    """A detected process deviation."""
    type: Literal["rework", "skip", "unusual_path"]
    description: str
    affected_cases: list[str]
    frequency: int


class ProcessStats(SQLModel):
    """Overall process statistics."""
    total_cases: int
    total_events: int
    total_activities: int
    total_variants: int
    avg_case_duration_ms: float
    median_case_duration_ms: float
    start_activities: list[str]
    end_activities: list[str]
