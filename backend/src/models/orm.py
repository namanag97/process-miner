"""ORM Models - Re-export shim for backwards compatibility.

All models are now organized by layer:
- Platform: src.platform.models (Organization, Workspace, User, Project, AsyncJob, ErrorLog)
- Features: src.features.process_mining.models (Dataset, Analysis, ProcessCase, etc.)
- Shared: src.shared.database (Base)

This file re-exports all models for backwards compatibility.
New code should import from the appropriate layer directly.
"""

# Re-export Base from shared
from src.shared.database import Base

# Re-export Platform models
from src.platform.models import (
    Organization,
    Workspace,
    User,
    WorkspaceMember,
    Project,
    AsyncJob,
    ErrorLog,
)

# Re-export Feature models
from src.features.process_mining.models import (
    # Enums
    DatasetStatus,
    AnalysisType,
    AnalysisStatus,
    # Core models
    Dataset,
    UploadedFile,
    Analysis,
    ProcessCase,
    ProcessEvent,
    ProcessModel,
    ProcessModelMetrics,
    GraphCache,
    ConformanceResult,
    ActivityMapping,
    AnalyticsCache,
    SocialNetwork,
    PredictionModel,
    Prediction,
    Recommendation,
    # Workflows
    Workflow,
    WorkflowRun,
    # OCEL
    OCELLog,
    OCELObjectType,
    OCPetriNet,
    # Hierarchical Mining
    HierarchicalProcessModel,
)

# Also import JobStatus for compatibility (used in the old orm.py)
from src.platform.core.enums import JobStatus

__all__ = [
    # Base
    "Base",
    # Platform
    "Organization",
    "Workspace",
    "User",
    "WorkspaceMember",
    "Project",
    "AsyncJob",
    "ErrorLog",
    # Feature enums
    "DatasetStatus",
    "AnalysisType",
    "AnalysisStatus",
    "JobStatus",
    # Feature models
    "Dataset",
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
]
