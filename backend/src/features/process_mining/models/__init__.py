"""Feature Models - Process Mining Domain.

All process mining models consolidated in one location.
"""

# Enums
from src.features.process_mining.models.enums import (
    AnalysisStatus,
    AnalysisType,
    DatasetStatus,
)

# Dataset models
from src.features.process_mining.models.dataset import (
    Dataset,
    DatasetColumn,
    DatasetColumnMapping,
    DatasetMetadata,
)

# Uploaded file
from src.features.process_mining.models.uploaded_file import UploadedFile

# Event models
from src.features.process_mining.models.events_models import ProcessCase, ProcessEvent

# Variant models
from src.features.process_mining.models.variants import ProcessVariant

# Analysis models
from src.features.process_mining.models.analysis_models import (
    Analysis,
    AnalyticsCache,
    ConformanceResult,
)

# Process model
from src.features.process_mining.models.process_model_models import (
    GraphCache,
    ProcessModel,
    ProcessModelMetrics,
)

# Predictions
from src.features.process_mining.models.prediction import (
    Prediction,
    PredictionModel,
    Recommendation,
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
    "ProcessVariant",
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
