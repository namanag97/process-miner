"""Process Mining Feature Enums.

Status and type enumerations for process mining domain models.
"""

from enum import Enum


class DatasetStatus(str, Enum):
    """Dataset lifecycle states.
    
    4-Phase Flow:
    1. PENDING → File upload initiated (presigned URL generated)
    2. UPLOADED → File stored in S3, awaiting validation
    3. VALIDATING → Background job validating file
    4. AWAITING_MAPPING → Validation passed, needs column mapping
    5. MAPPED → Column mapping confirmed, ready for ingestion
    6. INGESTING → Background job parsing and storing events
    7. READY → Dataset ready for analysis
    
    Error/Archive states:
    - ERROR → Any phase failed
    - ARCHIVED → Dataset archived by user
    - UNSTRUCTURED → Legacy: file stored without parsing
    - ANALYZING → Legacy: analysis in progress
    """

    PENDING = "pending"
    UPLOADED = "uploaded"  # NEW: File in S3, awaiting validation job
    VALIDATING = "validating"
    AWAITING_MAPPING = "awaiting_mapping"
    MAPPED = "mapped"  # NEW: Mapping confirmed, ready for ingestion
    INGESTING = "ingesting"
    READY = "ready"
    ERROR = "error"
    ARCHIVED = "archived"
    UNSTRUCTURED = "unstructured"
    ANALYZING = "analyzing"


class AnalysisType(str, Enum):
    """Types of process analyses."""

    DISCOVERY = "discovery"
    CONFORMANCE = "conformance"
    ENHANCEMENT = "enhancement"
    VARIANTS = "variants"
    BOTTLENECK = "bottleneck"


class AnalysisStatus(str, Enum):
    """Analysis job lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
