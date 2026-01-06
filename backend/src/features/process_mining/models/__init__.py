"""Feature Models - Process Mining Domain.

Re-exports all process mining models from the feature modules.
"""

# =============================================================================
# Re-exports from new domain locations for backward compatibility
# =============================================================================

# Datasets Domain
from src.domains.datasets.models import (
    Dataset,
    DatasetColumn,
    DatasetColumnMapping,
    DatasetMetadata,
    DatasetStatus,
    UploadedFile,
)

# Analysis Domain
from src.domains.analysis.models import (
    Analysis,
    AnalysisStatus,
    AnalysisType,
    AnalyticsCache,
    ConformanceResult,
    GraphCache,
    ProcessCase,
    ProcessEvent,
    ProcessModel,
    ProcessModelMetrics,
)

# Predictions
from src.features.process_mining.models.prediction import (
    Prediction,
    PredictionModel,
    Recommendation,
)

# Workflows
from src.features.process_mining.models.workflow import (
    Workflow,
    WorkflowRun,
)

# Organizational Mining
from src.features.process_mining.models.organizational import (
    ActivityMapping,
    HierarchicalProcessModel,
    SocialNetwork,
)

# OCEL 2.0 models
from src.features.process_mining.models.ocel2 import (
    E2ORelation,
    O2ORelation,
    ObjectAttributeChange,
    OCEL2Event,
    OCEL2EventType,
    OCEL2Object,
    OCEL2ObjectType,
)

# Lookup tables for normalized values
from src.features.process_mining.models.lookup_tables import (
    Activity,
    Resource,
    get_or_create_activity,
    get_or_create_resource,
)

# OCEL Service Models
from src.features.process_mining.models.ocel import (
    OCELLog,
    OCELObjectType,
    OCPetriNet,
)

__all__ = [
    # Enums
    "DatasetStatus",
    "AnalysisType",
    "AnalysisStatus",
    # Models - Dataset
    "Dataset",
    "DatasetColumn",
    "DatasetColumnMapping",
    "DatasetMetadata",
    "UploadedFile",
    # Models - Events
    "ProcessCase",
    "ProcessEvent",
    # Models - Process Model
    "ProcessModel",
    "ProcessModelMetrics",
    "GraphCache",
    # Models - Analysis
    "Analysis",
    "ConformanceResult",
    "AnalyticsCache",
    # Models - Organizational
    "ActivityMapping",
    "SocialNetwork",
    "HierarchicalProcessModel",
    # Models - Prediction
    "PredictionModel",
    "Prediction",
    "Recommendation",
    # Models - Workflows
    "Workflow",
    "WorkflowRun",
    # OCEL 2.0
    "OCEL2Event",
    "OCEL2EventType",
    "OCEL2Object",
    "OCEL2ObjectType",
    "E2ORelation",
    "O2ORelation",
    "ObjectAttributeChange",
    # Lookup Tables
    "Activity",
    "Resource",
    "get_or_create_activity",
    "get_or_create_resource",
    # OCEL Models (Service Layer)
    "OCELLog",
    "OCELObjectType",
    "OCPetriNet",
]

