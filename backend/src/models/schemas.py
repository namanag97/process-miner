"""Pydantic schemas for API request/response models.

Clean, React-optimized response shapes.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.core.enums import ConformanceMethod, MinerType, ModelFormat, SourceFormat


# =============================================================================
# Common
# =============================================================================


class PaginationParams(BaseModel):
    """Pagination parameters."""

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Base paginated response."""

    total: int
    page: int
    page_size: int
    pages: int


# =============================================================================
# Processes (Event Logs)
# =============================================================================


class ColumnMapping(BaseModel):
    """CSV column mapping for ingestion."""

    case_id: str = Field(..., description="Column name for case ID")
    activity: str = Field(..., description="Column name for activity")
    timestamp: str = Field(..., description="Column name for timestamp")
    resource: Optional[str] = Field(None, description="Column name for resource")


class ProcessUploadRequest(BaseModel):
    """Request for file upload with column mapping."""

    name: Optional[str] = None
    case_id_column: Optional[str] = None
    activity_column: Optional[str] = None
    timestamp_column: Optional[str] = None
    resource_column: Optional[str] = None


class ProcessResponse(BaseModel):
    """Process (event log) response."""

    id: str
    name: str
    source_format: str
    total_events: int
    total_cases: int
    total_activities: int
    activities: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ProcessListResponse(PaginatedResponse):
    """Paginated process list."""

    items: list[ProcessResponse]


class ProcessDetailResponse(ProcessResponse):
    """Detailed process response with statistics."""

    source_file: Optional[str]
    statistics: Optional[dict[str, Any]]
    updated_at: Optional[datetime]


class CaseResponse(BaseModel):
    """Case/trace response."""

    case_id: str
    event_count: int
    variant: Optional[str]
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_seconds: Optional[float]


class CaseListResponse(PaginatedResponse):
    """Paginated case list."""

    items: list[CaseResponse]


class EventResponse(BaseModel):
    """Event response."""

    id: str
    activity: str
    timestamp: datetime
    resource: Optional[str]
    attributes: Optional[dict[str, Any]]


class VariantResponse(BaseModel):
    """Process variant response."""

    variant_key: str
    activity_trace: str  # Human-readable: "A -> B -> C"
    case_count: int
    frequency_percent: float
    avg_duration_seconds: Optional[float]


class StatisticsResponse(BaseModel):
    """Process statistics response."""

    total_events: int
    total_cases: int
    total_activities: int
    total_variants: int
    activities: list[str]
    start_activities: dict[str, int]
    end_activities: dict[str, int]
    avg_case_duration_seconds: Optional[float]
    min_case_duration_seconds: Optional[float]
    max_case_duration_seconds: Optional[float]
    date_range: Optional[dict[str, datetime]]


class ColumnDetectionResponse(BaseModel):
    """Column detection result."""

    columns: list[str]
    suggestions: dict[str, Optional[str]]
    sample_rows: list[dict[str, Any]]
    row_count: int


# =============================================================================
# Discovery
# =============================================================================


class MinerInfo(BaseModel):
    """Mining algorithm information."""

    id: str
    name: str
    description: str
    output_format: str


class DiscoverRequest(BaseModel):
    """Request to discover a process model."""

    log_id: str
    miner_type: MinerType = MinerType.INDUCTIVE
    model_name: Optional[str] = None


class ModelResponse(BaseModel):
    """Process model response."""

    id: str
    name: str
    miner_type: str
    model_format: str
    log_id: Optional[str]
    fitness: Optional[float]
    precision: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class ModelListResponse(PaginatedResponse):
    """Paginated model list."""

    items: list[ModelResponse]


# =============================================================================
# Visualization
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


class DFGResponse(BaseModel):
    """DFG graph data for React visualization."""

    nodes: list[DFGNode]
    edges: list[DFGEdge]
    start_activities: dict[str, int]
    end_activities: dict[str, int]
    total_frequency: int


class PetriNetPlace(BaseModel):
    """Petri net place."""

    id: str
    name: str
    tokens: int = 0


class PetriNetTransition(BaseModel):
    """Petri net transition."""

    id: str
    name: str
    label: Optional[str]


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


# =============================================================================
# Conformance
# =============================================================================


class ConformanceCheckRequest(BaseModel):
    """Request for conformance checking."""

    log_id: str
    model_id: str
    method: ConformanceMethod = ConformanceMethod.TOKEN_REPLAY


class ConformanceResponse(BaseModel):
    """Conformance check result."""

    id: str
    log_id: str
    model_id: str
    fitness: float
    precision: Optional[float]
    method: str
    is_conformant: bool  # fitness >= 0.8
    fitting_traces: int
    total_traces: int
    created_at: datetime

    class Config:
        from_attributes = True


class DiagnosticsResponse(BaseModel):
    """Detailed conformance diagnostics."""

    fitness: float
    precision: Optional[float]
    total_traces: int
    fitting_traces: int
    non_fitting_traces: int
    fitness_ratio: float
    deviations: Optional[list[dict[str, Any]]]


# =============================================================================
# Workflows
# =============================================================================


class WorkflowStep(BaseModel):
    """Workflow step definition."""

    name: str
    type: str  # ingest, discover, check_conformance, export
    params: dict[str, Any] = Field(default_factory=dict)


class WorkflowCreateRequest(BaseModel):
    """Request to create a workflow."""

    name: str
    steps: list[WorkflowStep]
    schedule: Optional[str] = None  # Cron expression


class WorkflowResponse(BaseModel):
    """Workflow response."""

    id: str
    name: str
    steps: list[WorkflowStep]
    schedule: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class WorkflowRunRequest(BaseModel):
    """Request to run a workflow."""

    log_id: Optional[str] = None
    params: dict[str, Any] = Field(default_factory=dict)


class WorkflowRunResponse(BaseModel):
    """Workflow run response."""

    id: str
    workflow_id: str
    log_id: Optional[str]
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error: Optional[str]

    class Config:
        from_attributes = True


class WorkflowTemplate(BaseModel):
    """Pre-defined workflow template."""

    id: str
    name: str
    description: str
    steps: list[WorkflowStep]


# =============================================================================
# Error Response
# =============================================================================


class ErrorResponse(BaseModel):
    """API error response (RFC 7807 inspired)."""

    type: str = "error"
    title: str
    status: int
    detail: str
    instance: Optional[str] = None


# =============================================================================
# OCEL (Object-Centric Event Logs)
# =============================================================================


class OCELUploadRequest(BaseModel):
    """Request for OCEL file upload."""

    name: Optional[str] = None


class OCELLogResponse(BaseModel):
    """OCEL log response."""

    id: str
    name: str
    source_file: Optional[str]
    source_format: str
    total_events: int
    total_objects: int
    total_object_types: int
    object_types: list[str]
    activities: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OCELLogListResponse(BaseModel):
    """List of OCEL logs."""

    logs: list[OCELLogResponse]
    total: int


class OCELObjectTypeResponse(BaseModel):
    """Object type in an OCEL."""

    name: str
    object_count: int
    attributes: list[str] = []


class OCELStatisticsResponse(BaseModel):
    """OCEL statistics response."""

    log_id: str
    total_events: int
    total_objects: int
    total_object_types: int
    total_activities: int
    object_types: list[str]
    activities: list[str]
    objects_per_type: dict[str, int]


class DiscoverOCPNRequest(BaseModel):
    """Request to discover Object-Centric Petri Net."""

    log_id: str
    model_name: Optional[str] = None


class OCPetriNetResponse(BaseModel):
    """Object-Centric Petri Net response."""

    id: str
    log_id: str
    name: str
    object_types: list[str]
    created_at: datetime

    class Config:
        from_attributes = True


class OCDFGNode(BaseModel):
    """Object-Centric DFG node."""

    id: str
    name: str
    object_type: str
    frequency: int = 0


class OCDFGEdge(BaseModel):
    """Object-Centric DFG edge."""

    source: str
    target: str
    object_type: str
    frequency: int


class OCDFGResponse(BaseModel):
    """Object-Centric DFG response."""

    object_types: list[str]
    activities: list[str]
    graphs_by_type: dict[str, Any]


class FlattenedLogInfo(BaseModel):
    """Info about a flattened OCEL."""

    object_type: str
    case_count: int
    event_count: int


class ObjectGraphNode(BaseModel):
    """Node in object interaction graph."""

    id: str
    object_type: str


class ObjectGraphEdge(BaseModel):
    """Edge in object interaction graph."""

    source: str
    target: str
    relationship: str = ""


class ObjectGraphResponse(BaseModel):
    """Object interaction graph response."""

    nodes: list[ObjectGraphNode]
    edges: list[ObjectGraphEdge]


# =============================================================================
# Conformance (additional schemas)
# =============================================================================


class ConformanceListResponse(PaginatedResponse):
    """Paginated conformance results list."""

    items: list[ConformanceResponse]


class DeviationResponse(BaseModel):
    """Conformance deviation detail."""

    case_id: str
    activity: Optional[str]
    deviation_type: str
    details: str
