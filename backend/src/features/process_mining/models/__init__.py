"""Feature Models - Process Mining Domain.

All process mining models consolidated in one location.
"""

# Enums
# Algorithm Registry
from src.features.process_mining.models.algorithm_registry import (
    Algorithm,
    AlgorithmParameter,
)

# Analysis models
from src.features.process_mining.models.analysis_models import (
    Analysis,
    AnalyticsCache,
    ConformanceResult,
)

# Cache Models
from src.features.process_mining.models.cache_models import (
    DFGCache,
    VariantCache,
)

# Dataset models
from src.features.process_mining.models.dataset import (
    Dataset,
    DatasetColumn,
    DatasetColumnMapping,
    DatasetMetadata,
)
from src.features.process_mining.models.enums import (
    AnalysisStatus,
    AnalysisType,
    DatasetStatus,
)

# Event models
from src.features.process_mining.models.events_models import ProcessCase, ProcessEvent

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

# Organizational Mining
from src.features.process_mining.models.organizational import (
    ActivityMapping,
    HierarchicalProcessModel,
    SocialNetwork,
)

# Predictions
from src.features.process_mining.models.prediction import (
    Prediction,
    PredictionModel,
    Recommendation,
)

# Process model
from src.features.process_mining.models.process_model_models import (
    GraphCache,
    ProcessModel,
    ProcessModelMetrics,
)

# Uploaded file
from src.features.process_mining.models.uploaded_file import UploadedFile

# Variant models
from src.features.process_mining.models.variants import ProcessVariant

__all__ = [
    # Lookup Tables
    "Activity",
    # Models - Organizational
    "ActivityMapping",
    # Algorithm Registry
    "Algorithm",
    "AlgorithmParameter",
    # Models - Analysis
    "Analysis",
    "AnalysisStatus",
    "AnalysisType",
    "AnalyticsCache",
    "ConformanceResult",
    # Cache Models
    "DFGCache",
    # Models - Dataset
    "Dataset",
    "DatasetColumn",
    "DatasetColumnMapping",
    "DatasetMetadata",
    # Enums
    "DatasetStatus",
    "E2ORelation",
    "GraphCache",
    "HierarchicalProcessModel",
    "O2ORelation",
    # OCEL 2.0
    "OCEL2Event",
    "OCEL2EventType",
    "OCEL2Object",
    "OCEL2ObjectType",
    # OCEL Models (Service Layer)
    "OCELLog",
    "OCELObjectType",
    "OCPetriNet",
    "ObjectAttributeChange",
    "Prediction",
    # Models - Prediction
    "PredictionModel",
    # Models - Events
    "ProcessCase",
    "ProcessEvent",
    # Models - Process Model
    "ProcessModel",
    "ProcessModelMetrics",
    "ProcessVariant",
    "Recommendation",
    "Resource",
    "SocialNetwork",
    "UploadedFile",
    "VariantCache",
    "get_or_create_activity",
    "get_or_create_resource",
]
