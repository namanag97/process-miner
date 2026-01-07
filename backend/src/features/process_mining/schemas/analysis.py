"""Analysis layer schemas - Barrel file for backward compatibility.

This module re-exports all analysis schemas from their domain-specific modules.
All new code should import directly from the specific modules.

Schema organization:
- analytics: Bottleneck, rework, performance metrics
- discovery: Mining algorithms and process models
- visualization: DFG, Petri nets, graph structures
- conformance: Conformance checking and alignment
- ocel: Object-centric event logs (OCEL 2.0)
- organizational: Social networks and resources
- predictions: ML-based predictions
- simulation: Play-out and what-if analysis
- analyses: Saved analysis state and patterns
"""

# Analytics - Bottleneck, Rework, Performance
# Analyses (Saved state)
from src.features.process_mining.schemas.analyses import (
    AnalysisCreateRequest,
    AnalysisDetailResponse,
    AnalysisListResponse,
    AnalysisResponse,
    JobStatusResponse,
    PatternResponse,
    PerformanceDashboardResponse,
    UploadedFileResponse,
)
from src.features.process_mining.schemas.analytics import (
    BottleneckListResponse,
    BottleneckResponse,
    CycleTimeResponse,
    ReworkChain,
    ReworkChainListResponse,
    ReworkListResponse,
    ReworkResponse,
    ServiceTimeResponse,
    ThroughputResponse,
    VariantListResponse,
)

# Conformance - Checking and Alignment
from src.features.process_mining.schemas.conformance import (
    AlignmentDiagnosticsResponse,
    AlignmentMove,
    CaseAlignmentResponse,
    ConformanceCheckRequest,
    ConformanceListResponse,
    ConformanceResponse,
    DeviationDetail,
    DeviationResponse,
    DiagnosticsResponse,
    QualityMetricsResponse,
)

# Discovery - Miners and Models
from src.features.process_mining.schemas.discovery import (
    DiscoverRequest,
    MinerInfo,
    ModelListResponse,
    ModelResponse,
)

# OCEL - Object-Centric Event Logs
from src.features.process_mining.schemas.ocel import (
    DiscoverOCPNRequest,
    FlattenedLogInfo,
    ObjectGraphEdge,
    ObjectGraphNode,
    ObjectGraphResponse,
    OCDFGEdge,
    OCDFGNode,
    OCDFGResponse,
    OCDFGTypeGraph,
    OCELLogListResponse,
    OCELLogResponse,
    OCELObjectTypeResponse,
    OCELStatisticsResponse,
    OCELUploadRequest,
    OCPetriNetResponse,
)

# Organizational Mining
from src.features.process_mining.schemas.organizational import (
    NetworkEdge,
    NetworkNode,
    ResourceProfileResponse,
    ResourceRoleResponse,
    ResourceWorkloadResponse,
    SocialNetworkResponse,
)

# Predictions
from src.features.process_mining.schemas.predictions import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    PredictionRequest,
    PredictionResponse,
    PredictorListResponse,
    PredictorResponse,
    TrainPredictorRequest,
)

# Simulation
from src.features.process_mining.schemas.simulation import (
    PlayOutRequest,
    PlayOutResponse,
    SimulationRequest,
    SimulationResponse,
)

# Visualization - DFG, Petri Nets
from src.features.process_mining.schemas.visualization import (
    DFGEdge,
    DFGNode,
    DFGResponse,
    PetriNetArc,
    PetriNetPlace,
    PetriNetResponse,
    PetriNetTransition,
    ProcessExplorerDataResponse,
    TieredDFGAggregationInfo,
    TieredDFGResponse,
)

# Workflows (legacy - superceded by DAGs)
from src.features.process_mining.schemas.workflows import (
    WorkflowCreateRequest,
    WorkflowResponse,
    WorkflowRunRequest,
    WorkflowRunResponse,
    WorkflowStep,
    WorkflowTemplate,
)

__all__ = [
    "AlignmentDiagnosticsResponse",
    "AlignmentMove",
    # Analyses
    "AnalysisCreateRequest",
    "AnalysisDetailResponse",
    "AnalysisListResponse",
    "AnalysisResponse",
    "BatchPredictionRequest",
    "BatchPredictionResponse",
    "BottleneckListResponse",
    # Analytics
    "BottleneckResponse",
    "CaseAlignmentResponse",
    # Conformance
    "ConformanceCheckRequest",
    "ConformanceListResponse",
    "ConformanceResponse",
    "CycleTimeResponse",
    "DFGEdge",
    # Visualization
    "DFGNode",
    "DFGResponse",
    "DeviationDetail",
    "DeviationResponse",
    "DiagnosticsResponse",
    "DiscoverOCPNRequest",
    "DiscoverRequest",
    "FlattenedLogInfo",
    "JobStatusResponse",
    # Discovery
    "MinerInfo",
    "ModelListResponse",
    "ModelResponse",
    "NetworkEdge",
    # Organizational
    "NetworkNode",
    "OCDFGEdge",
    "OCDFGNode",
    "OCDFGResponse",
    "OCDFGTypeGraph",
    "OCELLogListResponse",
    "OCELLogResponse",
    "OCELObjectTypeResponse",
    "OCELStatisticsResponse",
    # OCEL
    "OCELUploadRequest",
    "OCPetriNetResponse",
    "ObjectGraphEdge",
    "ObjectGraphNode",
    "ObjectGraphResponse",
    "PatternResponse",
    "PerformanceDashboardResponse",
    "PetriNetArc",
    "PetriNetPlace",
    "PetriNetResponse",
    "PetriNetTransition",
    # Simulation
    "PlayOutRequest",
    "PlayOutResponse",
    "PredictionRequest",
    "PredictionResponse",
    "PredictorListResponse",
    "PredictorResponse",
    "ProcessExplorerDataResponse",
    "QualityMetricsResponse",
    "ResourceProfileResponse",
    "ResourceRoleResponse",
    "ResourceWorkloadResponse",
    "ReworkChain",
    "ReworkChainListResponse",
    "ReworkListResponse",
    "ReworkResponse",
    "ServiceTimeResponse",
    "SimulationRequest",
    "SimulationResponse",
    "SocialNetworkResponse",
    "ThroughputResponse",
    "TieredDFGAggregationInfo",
    "TieredDFGResponse",
    # Predictions
    "TrainPredictorRequest",
    "UploadedFileResponse",
    "VariantListResponse",
    "WorkflowCreateRequest",
    "WorkflowResponse",
    "WorkflowRunRequest",
    "WorkflowRunResponse",
    # Workflows (legacy)
    "WorkflowStep",
    "WorkflowTemplate",
]
