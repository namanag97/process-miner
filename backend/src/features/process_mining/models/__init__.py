"""Feature Models - Process Mining Domain.

Re-exports all process mining models from the feature orm.
"""

from src.features.process_mining.models.orm import (
    ActivityMapping,
    Analysis,
    AnalysisStatus,
    AnalysisType,
    AnalyticsCache,
    ConformanceResult,
    # Core models
    Dataset,
    # NEW: 4-Phase Upload Architecture Models
    DatasetColumn,
    DatasetColumnMapping,
    DatasetMetadata,
    # Enums
    DatasetStatus,
    GraphCache,
    # Hierarchical Mining
    HierarchicalProcessModel,
    # OCEL
    OCELLog,
    OCELObjectType,
    OCPetriNet,
    Prediction,
    PredictionModel,
    ProcessCase,
    ProcessEvent,
    ProcessModel,
    ProcessModelMetrics,
    Recommendation,
    SocialNetwork,
    UploadedFile,
    # Workflows
    Workflow,
    WorkflowRun,
)

# Lookup tables for normalized values
from src.features.process_mining.models.lookup_tables import (
    Activity,
    Resource,
    get_or_create_activity,
    get_or_create_resource,
)

__all__ = [
    # Enums
    "DatasetStatus",
    "AnalysisType",
    "AnalysisStatus",
    # Models
    "Dataset",
    "DatasetColumn",
    "DatasetColumnMapping",
    "DatasetMetadata",
    "UploadedFile",
    "Analysis",
    "ProcessCase",
    "ProcessEvent",
    "ProcessModel",
    "ProcessModelMetrics",
    "GraphCache",
    "ConformanceResult",
    "ActivityMapping",
    "AnalyticsCache",
    "SocialNetwork",
    "PredictionModel",
    "Prediction",
    "Recommendation",
    # Workflows
    "Workflow",
    "WorkflowRun",
    # OCEL
    "OCELLog",
    "OCELObjectType",
    "OCPetriNet",
    # Hierarchical Mining
    "HierarchicalProcessModel",
    # Lookup Tables
    "Activity",
    "Resource",
    "get_or_create_activity",
    "get_or_create_resource",
]
