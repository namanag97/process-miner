"""Pydantic schemas for API request/response models.

Clean, React-optimized response shapes.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from src.core.enums import ConformanceMethod, MinerType

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
# Projects
# =============================================================================


class ProjectCreateRequest(BaseModel):
    """Request to create a project."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=2000)
    tags: list[str] = Field(default_factory=list)


class ProjectUpdateRequest(BaseModel):
    """Request to update a project."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    tags: Optional[list[str]] = None


class ProjectResponse(BaseModel):
    """Project response."""

    id: str
    name: str
    description: Optional[str]
    tags: list[str]
    total_files: int
    total_analyses: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ProjectListResponse(PaginatedResponse):
    """Paginated project list."""

    items: list[ProjectResponse]


class ProjectDetailResponse(ProjectResponse):
    """Detailed project response with event logs."""

    event_logs: list["ProcessResponse"]


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
    source_file: Optional[str] = None  # FE expects this for display

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
    # Complexity metrics (optional, populated when requested)
    complexity_score: Optional[float] = None
    rework_count: Optional[int] = None
    unique_activity_count: Optional[int] = None


class ActivityDetailResponse(BaseModel):
    """Detailed activity statistics for process explorer."""

    activity: str
    frequency: int
    frequency_percent: float
    avg_duration_seconds: Optional[float] = None
    min_duration_seconds: Optional[float] = None
    max_duration_seconds: Optional[float] = None
    is_start_activity: bool = False
    is_end_activity: bool = False
    position_avg: Optional[float] = None  # Average position in trace (0=first, 1=last)
    resources: list[str] = []  # Resources that perform this activity


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
    # Performance metrics (optional, populated when include_performance=true)
    avg_duration_seconds: Optional[float] = None
    min_duration_seconds: Optional[float] = None
    max_duration_seconds: Optional[float] = None


class DFGResponse(BaseModel):
    """DFG graph data for React visualization."""

    nodes: list[DFGNode]
    edges: list[DFGEdge]
    start_activities: dict[str, int]
    end_activities: dict[str, int]
    total_frequency: int


class ProcessExplorerDataResponse(BaseModel):
    """Unified response for Process Explorer frontend component.

    Combines DFG, variants, activities, and statistics in a single request.
    """

    log_id: str
    dfg: DFGResponse
    variants: list["VariantResponse"]
    activities: list["ActivityDetailResponse"]
    statistics: "StatisticsResponse"


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
    generalization: Optional[float] = None  # FE expects this metric
    simplicity: Optional[float] = None  # FE expects this metric
    method: str
    is_conformant: bool  # fitness >= 0.8
    fitting_traces: int
    total_traces: int
    created_at: datetime

    class Config:
        from_attributes = True


class DeviationDetail(BaseModel):
    """Structured deviation for conformance diagnostics."""

    case_id: str
    activity: str
    violation_type: str  # 'missing_activity' | 'wrong_order' | 'extra_activity'
    expected_after: Optional[str] = None
    frequency: int = 1
    impact: str = "medium"  # 'low' | 'medium' | 'high'


class DiagnosticsResponse(BaseModel):
    """Detailed conformance diagnostics."""

    fitness: float
    precision: Optional[float]
    generalization: Optional[float] = None
    simplicity: Optional[float] = None
    total_traces: int
    fitting_traces: int
    non_fitting_traces: int
    fitness_ratio: float
    deviations: Optional[list[DeviationDetail]] = None  # Structured deviations


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


class OCDFGTypeGraph(BaseModel):
    """OC-DFG graph for a single object type."""

    object_type: str
    nodes: list[OCDFGNode]
    edges: list[OCDFGEdge]
    start_activities: list[str] = []
    end_activities: list[str] = []


class OCDFGResponse(BaseModel):
    """Object-Centric DFG response."""

    log_id: str
    object_types: list[str]
    activities: list[str]
    graphs_by_type: dict[str, OCDFGTypeGraph]
    total_events: int = 0
    total_objects: int = 0


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


class AlignmentMove(BaseModel):
    """Single move in an alignment sequence."""

    log_move: Optional[str] = None
    model_move: Optional[str] = None
    move_type: str  # 'sync', 'log_only', 'model_only'


class CaseAlignmentResponse(BaseModel):
    """Alignment result for a single case."""

    case_id: str
    fitness: float
    cost: int = 0
    alignment: list[AlignmentMove]
    is_fit: bool = True


class AlignmentDiagnosticsResponse(BaseModel):
    """Response for alignment diagnostics endpoint."""

    log_id: str
    model_id: str
    total_cases: int
    fitting_cases: int
    average_fitness: float
    case_alignments: list[CaseAlignmentResponse]


# =============================================================================
# Filtering
# =============================================================================


class FilterConfig(BaseModel):
    """Single filter configuration."""

    type: str = Field(..., description="Filter type: time_range, variants_top_k, etc.")
    params: dict[str, Any] = Field(default_factory=dict, description="Filter parameters")


class FilterRequest(BaseModel):
    """Request to apply filters to an event log."""

    name: Optional[str] = Field(None, description="Name for the filtered log")
    filters: list[FilterConfig] = Field(..., description="List of filters to apply")
    save_result: bool = Field(default=True, description="Whether to save the filtered log")


class FilterPreviewRequest(BaseModel):
    """Request to preview filter impact without saving."""

    filters: list[FilterConfig] = Field(..., description="List of filters to apply")


class FilterStatistics(BaseModel):
    """Statistics comparing original and filtered logs."""

    original_cases: int
    filtered_cases: int
    cases_removed: int
    cases_retained_pct: float
    original_events: int
    filtered_events: int
    events_removed: int
    events_retained_pct: float
    original_activities: int
    filtered_activities: int
    activities_removed: int


class FilterPreviewResponse(BaseModel):
    """Response for filter preview."""

    would_retain_cases: int
    would_retain_events: int
    statistics: FilterStatistics
    filters_applied: list[FilterConfig]


class FilteredLogResponse(BaseModel):
    """Response for a filtered log."""

    id: str
    name: str
    source_log_id: str
    is_filtered: bool = True
    filter_config: list[FilterConfig]
    total_events: int
    total_cases: int
    total_activities: int
    statistics: Optional[FilterStatistics]
    created_at: datetime

    class Config:
        from_attributes = True


class FilteredLogListResponse(BaseModel):
    """List of filtered logs derived from a source log."""

    source_log_id: str
    source_log_name: str
    filtered_logs: list[FilteredLogResponse]
    total: int


class FilterOptionsResponse(BaseModel):
    """Available filter options based on log contents."""

    activities: list[str]
    resources: list[str]
    start_activities: dict[str, int]
    end_activities: dict[str, int]
    total_variants: int
    time_range: dict[str, Optional[str]]
    case_size_range: dict[str, float]


class FilterTemplateResponse(BaseModel):
    """Pre-built filter template."""

    id: str
    name: str
    description: str
    filters: list[FilterConfig]


class FilterTemplateListResponse(BaseModel):
    """List of available filter templates."""

    templates: list[FilterTemplateResponse]


# =============================================================================
# Analytics
# =============================================================================


class BottleneckResponse(BaseModel):
    """Bottleneck detection result."""

    activity: str
    avg_waiting_time_seconds: float
    avg_service_time_seconds: float
    frequency: int
    is_bottleneck: bool
    severity: str  # 'low', 'medium', 'high'
    preceding_activities: list[str] = []
    following_activities: list[str] = []
    bottleneck_impact_score: float = 0.0  # 0-1 score based on wait time and frequency


class BottleneckListResponse(BaseModel):
    """List of detected bottlenecks."""

    log_id: str
    bottlenecks: list[BottleneckResponse]
    total_bottlenecks: int


class ReworkResponse(BaseModel):
    """Rework analysis result."""

    activity: str
    rework_count: int
    cases_with_rework: int
    rework_percentage: float


class ReworkListResponse(BaseModel):
    """Rework analysis results."""

    log_id: str
    rework_activities: list[ReworkResponse]
    total_rework_cases: int
    rework_percentage: float


class ReworkChain(BaseModel):
    """A chain of rework activities showing patterns of repeated work."""

    activity: str
    chain_length: int  # How many times it repeats in a row
    frequency: int  # How many cases have this chain
    avg_chain_duration_seconds: float = 0.0
    example_case_ids: list[str] = []  # Sample case IDs exhibiting this pattern


class ReworkChainListResponse(BaseModel):
    """Response for rework chain analysis."""

    log_id: str
    chains: list[ReworkChain]
    total_chains: int
    most_problematic_activity: Optional[str] = None
    cases_with_chains: int = 0
    chains_percentage: float = 0.0


class ServiceTimeResponse(BaseModel):
    """Service time per activity."""

    activity: str
    min_seconds: float
    max_seconds: float
    avg_seconds: float
    median_seconds: float
    std_dev_seconds: float


class CycleTimeResponse(BaseModel):
    """Cycle time statistics."""

    log_id: str
    min_seconds: float
    max_seconds: float
    avg_seconds: float
    median_seconds: float
    percentile_25_seconds: float
    percentile_75_seconds: float
    percentile_95_seconds: float


class ThroughputResponse(BaseModel):
    """Throughput metrics."""

    log_id: str
    total_cases: int
    completed_cases: int
    cases_per_day: float
    cases_per_week: float
    cases_per_month: float
    time_range_days: float


class PatternResponse(BaseModel):
    """Frequent pattern/subsequence."""

    pattern: str
    frequency: int
    support: float


class PerformanceDashboardResponse(BaseModel):
    """Performance summary dashboard."""

    log_id: str
    cycle_time: CycleTimeResponse
    throughput: ThroughputResponse
    top_bottlenecks: list[BottleneckResponse]
    rework_summary: dict[str, Any]


# =============================================================================
# Organizational Mining
# =============================================================================


class NetworkNode(BaseModel):
    """Node in a social network graph."""

    id: str
    label: str
    type: str = "resource"
    weight: float = 1.0


class NetworkEdge(BaseModel):
    """Edge in a social network graph."""

    source: str
    target: str
    weight: float
    label: Optional[str] = None


class SocialNetworkResponse(BaseModel):
    """Social network response."""

    log_id: str
    network_type: str
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]
    metrics: dict[str, Any]


class ResourceRoleResponse(BaseModel):
    """Discovered organizational role."""

    role_id: str
    resources: list[str]
    activities: list[str]


class ResourceProfileResponse(BaseModel):
    """Resource profile details."""

    resource: str
    total_events: int
    activities: dict[str, int]
    avg_processing_time_seconds: float
    first_activity: Optional[datetime]
    last_activity: Optional[datetime]


class ResourceWorkloadResponse(BaseModel):
    """Resource workload distribution."""

    log_id: str
    workload: dict[str, int]
    avg_events_per_resource: float


# =============================================================================
# Predictions
# =============================================================================


class TrainPredictorRequest(BaseModel):
    """Request to train a prediction model."""

    target_type: str = Field(
        ...,
        description="Prediction target: 'next_activity', 'remaining_time', 'outcome'",
    )
    algorithm: str = Field(
        default="random_forest",
        description="ML algorithm: 'random_forest', 'xgboost', 'gradient_boosting'",
    )
    outcome_attribute: Optional[str] = Field(
        None,
        description="Attribute to predict for outcome models",
    )


class PredictorResponse(BaseModel):
    """Prediction model response."""

    id: str
    log_id: str
    target_type: str
    algorithm: str
    metrics: dict[str, float]
    trained_at: datetime

    class Config:
        from_attributes = True


class PredictorListResponse(BaseModel):
    """List of prediction models."""

    log_id: str
    predictors: list[PredictorResponse]
    total: int


class PredictionRequest(BaseModel):
    """Request for a single prediction."""

    case_prefix: list[str] = Field(..., description="Activity sequence so far")
    case_attributes: Optional[dict[str, Any]] = None


class PredictionResponse(BaseModel):
    """Prediction result."""

    predictor_id: str
    case_prefix: list[str]
    prediction: Any
    confidence: Optional[float]
    alternatives: Optional[list[dict[str, Any]]] = None


class BatchPredictionRequest(BaseModel):
    """Request for batch predictions."""

    cases: list[PredictionRequest]


class BatchPredictionResponse(BaseModel):
    """Batch prediction results."""

    predictor_id: str
    predictions: list[PredictionResponse]


class JobStatusResponse(BaseModel):
    """Async job status."""

    id: str
    job_type: str
    status: str
    progress: int
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# =============================================================================
# Simulation
# =============================================================================


class PlayOutRequest(BaseModel):
    """Request to generate synthetic log from model."""

    num_traces: int = Field(default=100, ge=1, le=10000)


class PlayOutResponse(BaseModel):
    """Play-out result."""

    model_id: str
    generated_log_id: str
    traces_generated: int
    events_generated: int


class SimulationRequest(BaseModel):
    """What-if simulation request."""

    modifications: list[dict[str, Any]] = Field(
        ...,
        description="Modifications to simulate",
    )


class SimulationResponse(BaseModel):
    """Simulation result."""

    log_id: str
    scenario: str
    original_metrics: dict[str, float]
    simulated_metrics: dict[str, float]
    impact: dict[str, float]


# Rebuild models with forward references
ProcessExplorerDataResponse.model_rebuild()
