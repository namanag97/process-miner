"""Feature Models - Process Mining Domain.

Re-exports all process mining models from the feature modules.
"""

# Enums
from src.features.process_mining.models.enums import (
    AnalysisStatus,
    AnalysisType,
    DatasetStatus,
)

# Core models - Dataset
from src.features.process_mining.models.dataset import (
    Dataset,
    DatasetColumn,
    DatasetColumnMapping,
    DatasetMetadata,
    UploadedFile,
)

# Events
from src.features.process_mining.models.events import (
    ProcessCase,
    ProcessEvent,
)

# Process Models
from src.features.process_mining.models.process_model import (
    GraphCache,
    ProcessModel,
    ProcessModelMetrics,
)

# Analysis
from src.features.process_mining.models.analysis import (
    Analysis,
    AnalyticsCache,
    ConformanceResult,
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

# OCEL
from src.features.process_mining.models.ocel2 import (
    OCELLog,
    OCELObjectType,
    OCPetriNet,
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
    # OCEL
    "OCELLog",
    "OCELObjectType",
    "OCPetriNet",
    # Lookup Tables
    "Activity",
    "Resource",
    "get_or_create_activity",
    "get_or_create_resource",
]
