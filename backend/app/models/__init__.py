"""
Models package - Unified imports for database models and schemas.

Database tables are defined in db.py.
Pydantic schemas (API models) are defined in schemas.py.
"""

# Database models (table=True)
from .db import (
    # Utility
    generate_uuid,
    # Enums
    UploadStatus,
    JobStatus,
    # Tables
    Organization,
    User,
    Process,
    Upload,
    Mapping,
    Job,
    Dataset,
    AuditLog,
    Insight,
)

# Pydantic schemas (request/response models)
from .schemas import (
    # Organization
    OrganizationBase,
    OrganizationCreate,
    OrganizationResponse,
    # User
    UserBase,
    UserResponse,
    # Process
    ProcessBase,
    ProcessCreate,
    ProcessUpdate,
    ProcessResponse,
    ProcessWithStats,
    # Upload
    UploadBase,
    ColumnMetadata,
    UploadResponse,
    # Mapping
    MappingBase,
    MappingCreate,
    MappingResponse,
    # Job
    JobResponse,
    ProcessingRequest,
    # Dataset
    DatasetSummary,
    # Analysis
    NodePosition,
    ActivityNodeData,
    DFGNode,
    EdgeData,
    DFGEdge,
    DFGSummary,
    DFGResponse,
    VariantItem,
    VariantsResponse,
    ActivityStat,
    Deviation,
    ProcessStats,
    # Validation
    ValidationError,
    ValidationWarning,
    ValidationStats,
    ValidationResult,
    # Audit Log
    AuditLogCreate,
    AuditLogResponse,
    AuditLogFilter,
    # Insight
    InsightCreate,
    InsightResponse,
    InsightSummary,
    # Error
    ErrorResponse,
)

__all__ = [
    # Utility
    "generate_uuid",
    # Enums
    "UploadStatus",
    "JobStatus",
    # Database Tables
    "Organization",
    "User",
    "Process",
    "Upload",
    "Mapping",
    "Job",
    "Dataset",
    "AuditLog",
    "Insight",
    # Organization Schemas
    "OrganizationBase",
    "OrganizationCreate",
    "OrganizationResponse",
    # User Schemas
    "UserBase",
    "UserResponse",
    # Process Schemas
    "ProcessBase",
    "ProcessCreate",
    "ProcessUpdate",
    "ProcessResponse",
    "ProcessWithStats",
    # Upload Schemas
    "UploadBase",
    "ColumnMetadata",
    "UploadResponse",
    # Mapping Schemas
    "MappingBase",
    "MappingCreate",
    "MappingResponse",
    # Job Schemas
    "JobResponse",
    "ProcessingRequest",
    # Dataset Schemas
    "DatasetSummary",
    # Analysis Schemas
    "NodePosition",
    "ActivityNodeData",
    "DFGNode",
    "EdgeData",
    "DFGEdge",
    "DFGSummary",
    "DFGResponse",
    "VariantItem",
    "VariantsResponse",
    "ActivityStat",
    "Deviation",
    "ProcessStats",
    # Validation Schemas
    "ValidationError",
    "ValidationWarning",
    "ValidationStats",
    "ValidationResult",
    # Audit Log Schemas
    "AuditLogCreate",
    "AuditLogResponse",
    "AuditLogFilter",
    # Insight Schemas
    "InsightCreate",
    "InsightResponse",
    "InsightSummary",
    # Error
    "ErrorResponse",
]
