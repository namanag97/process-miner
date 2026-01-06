"""Dataset Domain Enums.

Status enumerations for dataset lifecycle management.
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
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    AWAITING_MAPPING = "awaiting_mapping"
    MAPPED = "mapped"
    INGESTING = "ingesting"
    READY = "ready"
    ERROR = "error"
    ARCHIVED = "archived"
    UNSTRUCTURED = "unstructured"
    ANALYZING = "analyzing"
