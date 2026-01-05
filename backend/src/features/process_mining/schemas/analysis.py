"""Analysis layer schemas.

Contains schemas for:
- Discovery (Miners, Models, DFG)
- Conformance checking
- Workflows
- OCEL
- Prediction & Simulation
- Saved Analyses
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.features.process_mining.enums import ConformanceMethod, MinerType
from src.features.process_mining.schemas.datasets import (
    ActivityDetailResponse,
    StatisticsResponse,
    VariantResponse,
)
from src.shared.schemas import PaginatedResponse

# =============================================================================
# Analytics (Bottlenecks, Rework, Performance)
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

    dataset_id: str
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

    dataset_id: str
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

    dataset_id: str
    chains: list[ReworkChain]
    total_chains: int
    most_problematic_activity: str | None = None
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

    dataset_id: str
    min_seconds: float
    max_seconds: float
    avg_seconds: float
    median_seconds: float
    percentile_25_seconds: float
    percentile_75_seconds: float
    percentile_95_seconds: float


class ThroughputResponse(BaseModel):
    """Throughput metrics."""

    dataset_id: str
    total_cases: int
    completed_cases: int
    cases_per_day: float
    cases_per_week: float
    cases_per_month: float
    time_range_days: float


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

    dataset_id: str = Field(..., description="Dataset ID to mine")
    miner_type: MinerType = MinerType.INDUCTIVE
    model_name: str | None = None


class ModelResponse(BaseModel):
    """Process model response."""

    id: str
    name: str
    miner_type: str
    model_format: str
    dataset_id: str | None
    fitness: float | None
    precision: float | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


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


class ProcessExplorerDataResponse(BaseModel):
    """Unified response for Process Explorer frontend component.

    Combines DFG, variants, activities, and statistics in a single request.
    """

    dataset_id: str
    dfg: DFGResponse
    variants: list[VariantResponse]
    activities: list[ActivityDetailResponse]
    statistics: StatisticsResponse


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


# =============================================================================
# Conformance
# =============================================================================


class ConformanceCheckRequest(BaseModel):
    """Request for conformance checking."""

    dataset_id: str
    model_id: str
    method: ConformanceMethod = ConformanceMethod.TOKEN_REPLAY


class ConformanceResponse(BaseModel):
    """Conformance check result."""

    id: str
    dataset_id: str
    model_id: str
    fitness: float
    precision: float | None
    generalization: float | None = None  # FE expects this metric
    simplicity: float | None = None  # FE expects this metric
    method: str  # What method was requested
    algorithm_used: str  # What algorithm actually ran (may differ if fallback)
    fallback_reason: str | None = None  # Reason for fallback if different from method
    is_conformant: bool  # fitness >= 0.8
    fitting_traces: int
    total_traces: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviationDetail(BaseModel):
    """Structured deviation for conformance diagnostics."""

    case_id: str
    activity: str
    violation_type: str  # 'missing_activity' | 'wrong_order' | 'extra_activity'
    expected_after: str | None = None
    frequency: int = 1
    impact: str = "medium"  # 'low' | 'medium' | 'high'


class DiagnosticsResponse(BaseModel):
    """Detailed conformance diagnostics."""

    fitness: float
    precision: float | None
    generalization: float | None = None
    simplicity: float | None = None
    f_score: float | None = None  # Harmonic mean of fitness & precision
    total_traces: int
    fitting_traces: int
    non_fitting_traces: int
    fitness_ratio: float
    average_alignment_cost: float | None = None
    deviations: list[DeviationDetail] | None = None  # Structured deviations


class QualityMetricsResponse(BaseModel):
    """Full quality metrics for a process model.

    Contains all 4 quality dimensions from PM4py:
    - Fitness: How well the log fits the model
    - Precision: How much the model allows for behavior not in the log
    - Generalization: How well the model generalizes beyond observed behavior
    - Simplicity: How simple/understandable the model is
    """

    dataset_id: str
    model_id: str
    fitness: float
    precision: float | None = None
    generalization: float | None = None
    simplicity: float | None = None
    f_score: float | None = None  # Harmonic mean of fitness & precision


class ConformanceListResponse(PaginatedResponse):
    """Paginated conformance results list."""

    items: list[ConformanceResponse]


class DeviationResponse(BaseModel):
    """Conformance deviation detail."""

    case_id: str
    activity: str | None
    deviation_type: str
    details: str


class AlignmentMove(BaseModel):
    """Single move in an alignment sequence."""

    log_move: str | None = None
    model_move: str | None = None
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

    dataset_id: str
    model_id: str
    total_cases: int
    fitting_cases: int
    average_fitness: float
    case_alignments: list[CaseAlignmentResponse]


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
    schedule: str | None = None  # Cron expression


class WorkflowResponse(BaseModel):
    """Workflow response."""

    id: str
    name: str
    steps: list[WorkflowStep] = []
    schedule: str | None
    is_active: bool
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse steps_json to steps list."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in ["id", "name", "steps_json", "schedule", "is_active", "created_at"]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("steps_json"):
                try:
                    data["steps"] = json.loads(data["steps_json"])
                except (json.JSONDecodeError, TypeError):
                    data["steps"] = []
            elif "steps" not in data:
                data["steps"] = []
        return data

    model_config = ConfigDict(from_attributes=True)


class WorkflowRunRequest(BaseModel):
    """Request to run a workflow."""

    dataset_id: str | None = None
    params: dict[str, Any] = Field(default_factory=dict)


class WorkflowRunResponse(BaseModel):
    """Workflow run response."""

    id: str
    workflow_id: str
    dataset_id: str | None
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    error: str | None

    model_config = ConfigDict(from_attributes=True)


class WorkflowTemplate(BaseModel):
    """Pre-defined workflow template."""

    id: str
    name: str
    description: str
    steps: list[WorkflowStep]


# =============================================================================
# OCEL (Object-Centric Event Logs)
# =============================================================================


class OCELUploadRequest(BaseModel):
    """Request for OCEL file upload."""

    name: str | None = None


class OCELLogResponse(BaseModel):
    """OCEL log response."""

    id: str
    name: str
    source_file: str | None
    source_format: str
    total_events: int
    total_objects: int
    total_object_types: int
    object_types: list[str] = []
    activities: list[str] = []
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse metadata_json to object_types and activities."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "name",
                    "source_file",
                    "source_format",
                    "total_events",
                    "total_objects",
                    "total_object_types",
                    "metadata_json",
                    "created_at",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("metadata_json"):
                try:
                    metadata = json.loads(data["metadata_json"])
                    # object_types is extracted from objects_per_type keys (ORM storage format)
                    data["object_types"] = list(metadata.get("objects_per_type", {}).keys())
                    data["activities"] = metadata.get("activities", [])
                except (json.JSONDecodeError, TypeError):
                    data["object_types"] = []
                    data["activities"] = []
            else:
                if "object_types" not in data:
                    data["object_types"] = []
                if "activities" not in data:
                    data["activities"] = []
        return data

    model_config = ConfigDict(from_attributes=True)


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

    dataset_id: str
    total_events: int
    total_objects: int
    total_object_types: int
    total_activities: int
    object_types: list[str]
    activities: list[str]
    objects_per_type: dict[str, int]


class DiscoverOCPNRequest(BaseModel):
    """Request to discover Object-Centric Petri Net."""

    dataset_id: str
    model_name: str | None = None


class OCPetriNetResponse(BaseModel):
    """Object-Centric Petri Net response."""

    id: str
    dataset_id: str = ""
    name: str
    object_types: list[str] = []
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse object_types_json to object_types list."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in ["id", "dataset_id", "name", "object_types_json", "created_at"]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("object_types_json"):
                try:
                    data["object_types"] = json.loads(data["object_types_json"])
                except (json.JSONDecodeError, TypeError):
                    data["object_types"] = []
            elif "object_types" not in data:
                data["object_types"] = []
        return data

    model_config = ConfigDict(from_attributes=True)


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

    dataset_id: str
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
    label: str | None = None


class SocialNetworkResponse(BaseModel):
    """Social network response."""

    dataset_id: str
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
    first_activity: datetime | None
    last_activity: datetime | None


class ResourceWorkloadResponse(BaseModel):
    """Resource workload distribution."""

    dataset_id: str
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
    outcome_attribute: str | None = Field(
        None,
        description="Attribute to predict for outcome models",
    )


class PredictorResponse(BaseModel):
    """Prediction model response."""

    id: str
    dataset_id: str = ""
    target_type: str
    algorithm: str
    metrics: dict[str, Any] = {}
    trained_at: datetime | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse metrics_json."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "dataset_id",
                    "target_type",
                    "algorithm",
                    "metrics_json",
                    "trained_at",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("metrics_json"):
                try:
                    data["metrics"] = json.loads(data["metrics_json"])
                except (json.JSONDecodeError, TypeError):
                    data["metrics"] = {}
            elif "metrics" not in data:
                data["metrics"] = {}
        return data

    model_config = ConfigDict(from_attributes=True)


class PredictorListResponse(BaseModel):
    """List of prediction models."""

    dataset_id: str
    predictors: list[PredictorResponse]
    total: int


class PredictionRequest(BaseModel):
    """Request for a single prediction."""

    case_prefix: list[str] = Field(..., description="Activity sequence so far")
    case_attributes: dict[str, Any] | None = None


class PredictionResponse(BaseModel):
    """Prediction result."""

    predictor_id: str
    case_prefix: list[str]
    prediction: Any
    confidence: float | None
    alternatives: list[dict[str, Any]] | None = None


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
    stage: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse result_json to result dict."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "job_type",
                    "status",
                    "progress",
                    "stage",
                    "result_json",
                    "error",
                    "created_at",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("result_json"):
                try:
                    data["result"] = json.loads(data["result_json"])
                except (json.JSONDecodeError, TypeError):
                    data["result"] = None
            elif "result" not in data:
                data["result"] = None
        return data

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Simulation
# =============================================================================


class PlayOutRequest(BaseModel):
    """Request to generate synthetic log from model."""

    num_traces: int = Field(default=100, ge=1, le=10000)


class PlayOutResponse(BaseModel):
    """Play-out result."""

    model_id: str
    generated_dataset_id: str
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

    dataset_id: str
    scenario: str
    original_metrics: dict[str, float]
    simulated_metrics: dict[str, float]
    impact: dict[str, float]


# =============================================================================
# Analyses (Saved Process Analyses)
# =============================================================================


class AnalysisCreateRequest(BaseModel):
    """Request to create a new analysis."""

    name: str = Field(..., min_length=1, max_length=255)
    analysis_type: str = Field(
        ..., description="Type: discovery, conformance, variants, bottleneck"
    )
    config: dict[str, Any] = Field(default_factory=dict, description="Analysis configuration")


class AnalysisResponse(BaseModel):
    """Analysis response."""

    id: str
    dataset_id: str
    name: str
    analysis_type: str
    status: str
    config: dict[str, Any] | None = None
    result_summary: dict[str, Any] | None = None
    model_id: str | None = None
    created_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse config_json and result_summary_json."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "dataset_id",
                    "name",
                    "analysis_type",
                    "status",
                    "config_json",
                    "result_summary_json",
                    "model_id",
                    "created_at",
                    "completed_at",
                    "error_message",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("config_json"):
                try:
                    data["config"] = json.loads(data["config_json"])
                except (json.JSONDecodeError, TypeError):
                    data["config"] = None
            if data.get("result_summary_json"):
                try:
                    data["result_summary"] = json.loads(data["result_summary_json"])
                except (json.JSONDecodeError, TypeError):
                    data["result_summary"] = None
        return data

    model_config = ConfigDict(from_attributes=True)


class AnalysisListResponse(PaginatedResponse):
    """Paginated analysis list."""

    items: list[AnalysisResponse]


class AnalysisDetailResponse(AnalysisResponse):
    """Detailed analysis with full results."""

    dfg: DFGResponse | None = None
    variants: list[VariantResponse] | None = None
    statistics: StatisticsResponse | None = None


class UploadedFileResponse(BaseModel):
    """Uploaded file metadata response."""

    id: str
    filename: str
    storage_path: str
    size_bytes: int | None = None
    mime_type: str | None = None
    checksum: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# Misc Patterns (Performance)
# =============================================================================


class PatternResponse(BaseModel):
    """Frequent pattern/subsequence."""

    pattern: str
    frequency: int
    support: float


class PerformanceDashboardResponse(BaseModel):
    """Performance summary dashboard."""

    dataset_id: str
    cycle_time: CycleTimeResponse
    throughput: ThroughputResponse
    top_bottlenecks: list[BottleneckResponse]
    rework_summary: dict[str, Any]
