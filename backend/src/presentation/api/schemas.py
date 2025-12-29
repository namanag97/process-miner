"""Shared API Response Schemas.

This module consolidates common Pydantic models used across multiple routers
to reduce code duplication. Import these models instead of redefining them.
"""

from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field


# =============================================================================
# GENERIC PAGINATION
# =============================================================================

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated list response.
    
    Use with type parameter: PaginatedResponse[ProcessResponse]
    """
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# COMMON RESPONSE MODELS
# =============================================================================


class VariantResponse(BaseModel):
    """Process variant response - shared between logs and processes routers."""
    
    variant_hash: str = Field(description="MD5 hash of activity trace")
    activity_trace: str = Field(description="Human-readable activity sequence")
    activities: List[str]
    length: int
    case_count: int
    frequency_percent: float
    avg_duration_seconds: Optional[float] = None
    median_duration_seconds: Optional[float] = None
    is_happy_path: bool = False
    rank: int


class QualityIssueResponse(BaseModel):
    """Single quality issue detected in a log or process."""
    
    issue_type: str
    message: str
    severity: str  # "low", "medium", "high"
    affected_rows: int
    column: Optional[str] = None


class QualityReportResponse(BaseModel):
    """Quality assessment report for event logs/processes."""
    
    process_id: str = Field(alias="log_id", serialization_alias="process_id")
    completeness_score: float
    validity_score: float
    overall_score: float
    is_valid: bool
    issues: List[QualityIssueResponse]
    
    class Config:
        populate_by_name = True


class StatisticsResponse(BaseModel):
    """Unified statistics response for processes/logs."""
    
    process_id: str = Field(alias="log_id", serialization_alias="process_id")
    process_type: str = "traditional"
    event_count: int
    case_count: int
    activity_count: int
    variant_count: int
    resource_count: int
    date_range_start: Optional[str] = None
    date_range_end: Optional[str] = None
    avg_case_duration_seconds: Optional[float] = None
    median_case_duration_seconds: Optional[float] = None
    min_case_duration_seconds: Optional[float] = None
    max_case_duration_seconds: Optional[float] = None
    activities: List[str] = []
    start_activities: Dict[str, int] = {}
    end_activities: Dict[str, int] = {}
    # OCPM-specific
    object_types: List[str] = []
    objects_per_type: Dict[str, int] = {}
    
    class Config:
        populate_by_name = True


class UploadResponse(BaseModel):
    """Response from file upload."""
    
    id: str
    name: str
    process_type: str = "traditional"
    total_events: int
    total_cases: int
    object_types: List[str] = []
    validation: Dict[str, Any] = {}
    _links: Dict[str, Dict[str, str]] = {}


class ColumnDetectionResponse(BaseModel):
    """Column detection for CSV upload."""
    
    columns: List[str]
    suggestions: Dict[str, Optional[str]]
    sample_rows: List[Dict[str, Any]]


class FilePreviewResponse(BaseModel):
    """File preview before ingestion."""
    
    filename: str
    file_format: str
    process_type: str = "traditional"
    columns: List[str]
    column_types: Dict[str, str]
    suggestions: Dict[str, Optional[str]]
    sample_rows: List[Dict[str, Any]]
    row_count: int
    estimated_case_count: int
    estimated_event_count: int
    detected_object_types: List[str] = []


class CaseResponse(BaseModel):
    """Single case/trace information."""
    
    case_id: str
    event_count: int
    variant: str
    duration_seconds: Optional[float] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None


# =============================================================================
# UPDATE REQUEST MODELS
# =============================================================================


class UpdateRequest(BaseModel):
    """Request for updating process/log metadata."""
    
    name: Optional[str] = None
    description: Optional[str] = None


# =============================================================================
# HYPERMEDIA LINKS HELPER
# =============================================================================


def build_links(resource_id: str, base_url: str = "/api/v1/processes") -> Dict[str, Dict[str, str]]:
    """Build hypermedia links for a resource."""
    return {
        "self": {"href": f"{base_url}/{resource_id}"},
        "statistics": {"href": f"{base_url}/{resource_id}/statistics"},
        "quality": {"href": f"{base_url}/{resource_id}/quality"},
        "variants": {"href": f"{base_url}/{resource_id}/variants"},
        "activities": {"href": f"{base_url}/{resource_id}/activities"},
        "cases": {"href": f"{base_url}/{resource_id}/cases"},
        "discovery": {"href": f"{base_url}/{resource_id}/discovery", "method": "POST"},
        "dfg": {"href": f"{base_url}/{resource_id}/dfg"},
        "object_types": {"href": f"{base_url}/{resource_id}/object-types"},
    }
