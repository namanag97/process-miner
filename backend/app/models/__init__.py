"""
Models package - Using SQLModel for unified ORM + Pydantic schemas.
"""

from .common import generate_uuid

from .user import (
    User,
    UserBase,
    UserResponse,
)

from .upload import (
    Upload,
    UploadBase,
    UploadResponse,
    ColumnMetadata,
)

from .mapping import (
    Mapping,
    MappingBase,
    MappingCreate,
    MappingResponse,
)

from .job import (
    Job,
    JobResponse,
    ProcessingRequest,
)

from .dataset import (
    Dataset,
    DatasetSummary,
)

from .analysis import (
    DFGNode,
    DFGEdge,
    DFGSummary,
    DFGResponse,
    NodePosition,
    ActivityNodeData,
    EdgeData,
    VariantItem,
    VariantsResponse,
    ActivityStat,
    Deviation,
    ProcessStats,
)

from .validation import (
    ValidationError,
    ValidationWarning,
    ValidationStats,
    ValidationResult,
)

from .error import ErrorResponse

from .organization import (
    Organization,
    OrganizationBase,
    OrganizationCreate,
    OrganizationResponse,
)

from .process import (
    Process,
    ProcessBase,
    ProcessCreate,
    ProcessUpdate,
    ProcessResponse,
    ProcessWithStats,
)

from .audit_log import (
    AuditLog,
    AuditLogCreate,
    AuditLogResponse,
    AuditLogFilter,
)

from .insight import (
    Insight,
    InsightCreate,
    InsightResponse,
    InsightSummary,
)

__all__ = [
    # Common
    "generate_uuid",
    # User
    "User",
    "UserBase",
    "UserResponse",
    # Upload
    "Upload",
    "UploadBase",
    "UploadResponse",
    "ColumnMetadata",
    # Mapping
    "Mapping",
    "MappingBase",
    "MappingCreate",
    "MappingResponse",
    # Job
    "Job",
    "JobResponse",
    "ProcessingRequest",
    # Dataset
    "Dataset",
    "DatasetSummary",
    # Analysis
    "DFGNode",
    "DFGEdge",
    "DFGSummary",
    "DFGResponse",
    "NodePosition",
    "ActivityNodeData",
    "EdgeData",
    "VariantItem",
    "VariantsResponse",
    "ActivityStat",
    "Deviation",
    "ProcessStats",
    # Validation
    "ValidationError",
    "ValidationWarning",
    "ValidationStats",
    "ValidationResult",
    # Error
    "ErrorResponse",
    # Organization
    "Organization",
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationResponse",
    # Process
    "Process",
    "ProcessBase",
    "ProcessCreate",
    "ProcessUpdate",
    "ProcessResponse",
    "ProcessWithStats",
    # AuditLog
    "AuditLog",
    "AuditLogCreate",
    "AuditLogResponse",
    "AuditLogFilter",
    # Insight
    "Insight",
    "InsightCreate",
    "InsightResponse",
    "InsightSummary",
]
