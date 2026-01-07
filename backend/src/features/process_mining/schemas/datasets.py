"""Datasets layer schemas.

Contains schemas for:
- Datasets and ingestion
- Events and Cases
- Column mapping and validation
- File upload handling
"""

import json
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.shared.base_schemas import ColumnMappingBase, CreatedAtMixin, IDMixin
from src.shared.schemas import PaginatedResponse

# =============================================================================
# Ingestion & Column Mapping
# =============================================================================


class ColumnMapping(ColumnMappingBase):
    """CSV column mapping for ingestion (alias for ColumnMappingBase)."""


class IngestRequest(ColumnMappingBase):
    """Request to trigger background ingestion with column mapping (alias for ColumnMappingBase)."""


class PresignedUploadRequest(BaseModel):
    """Request for presigned upload URL generation.

    Client requests a presigned URL, then uploads directly to S3/MinIO.
    Backend receives upload notification via webhook or polling.
    """

    filename: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Original filename",
        examples=["purchasing_logs_2024.csv"],
    )
    content_type: str = Field(
        default="text/csv",
        description="MIME type (text/csv, application/xml)",
        examples=["text/csv"],
    )
    file_size_bytes: int | None = Field(
        None, ge=1, description="Expected file size in bytes (for validation)", examples=[15728640]
    )
    project_id: str | None = Field(
        None, description="Optional project association", examples=["proj_123456789"]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "filename": "process_log.csv",
                "content_type": "text/csv",
                "file_size_bytes": 1024000,
                "project_id": "proj_abc123",
            }
        }
    )


class PresignedUploadResponse(BaseModel):
    """Response containing presigned upload URL and tracking info.

    Client should:
    1. PUT file to upload_url with Content-Type header
    2. Poll /datasets/{dataset_id} for validation status
    """

    upload_url: str = Field(..., description="Presigned PUT URL for direct S3 upload")
    storage_key: str = Field(..., description="S3 object key for tracking")
    dataset_id: str = Field(..., description="Dataset ID for status polling")
    expires_in: int = Field(..., description="URL expiration in seconds")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "upload_url": "https://s3.amazonaws.com/bucket/key?sig=...",
                "storage_key": "datasets/123/file.csv",
                "dataset_id": "ds_123456789",
                "expires_in": 3600,
            }
        }
    )


class DatasetUploadRequest(BaseModel):
    """Request for file upload with column mapping."""

    name: str | None = None
    case_id_column: str | None = None
    activity_column: str | None = None
    timestamp_column: str | None = None
    resource_column: str | None = None


# =============================================================================
# Datasets
# =============================================================================


class DatasetResponse(IDMixin, CreatedAtMixin, BaseModel):
    """Dataset response with optional detail fields."""

    name: str
    source_format: str
    total_events: int
    total_cases: int
    total_activities: int
    activities: list[str] = []
    source_file: str | None = None
    status: str = "ready"
    validation_job_id: str | None = None
    ingestion_job_id: str | None = None
    file_size_bytes: int | None = None
    # Detail fields (optional)
    statistics: dict[str, Any] | None = None
    updated_at: datetime | None = None
    error_message: str | None = None

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse activities_json to activities list."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "name",
                    "source_format",
                    "total_events",
                    "total_cases",
                    "total_activities",
                    "activities_json",
                    "created_at",
                    "source_file",
                    "status",
                    "validation_job_id",
                    "ingestion_job_id",
                    "file_size_bytes",
                    "statistics",
                    "updated_at",
                    "error_message",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            if data.get("activities_json"):
                try:
                    data["activities"] = json.loads(data["activities_json"])
                except (json.JSONDecodeError, TypeError):
                    data["activities"] = []
            elif "activities" not in data:
                data["activities"] = []
        return data

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "OrderToCash_2023",
                "source_format": "CSV",
                "total_events": 15420,
                "total_cases": 1250,
                "total_activities": 8,
                "activities": ["Receive Order", "Check Credit", "Ship Goods", "Send Invoice"],
                "created_at": "2023-10-27T10:00:00Z",
                "source_file": "o2c_logs.csv",
                "status": "ready",
                "file_size_bytes": 2048500,
            }
        },
    )


class DatasetListResponse(PaginatedResponse):
    """Paginated dataset list."""

    items: list[DatasetResponse]


class DatasetDetailResponse(DatasetResponse):
    """Detailed dataset response (alias for DatasetResponse)."""


# =============================================================================
# Cases & Events
# =============================================================================


class CaseResponse(BaseModel):
    """Case/trace response."""

    case_id: str
    event_count: int
    variant: str | None
    start_time: datetime | None
    end_time: datetime | None
    duration_seconds: float | None


class CaseListResponse(PaginatedResponse):
    """Paginated case list."""

    items: list[CaseResponse]


class EventResponse(BaseModel):
    """Event response."""

    id: str
    activity: str
    timestamp: datetime
    resource: str | None
    attributes: dict[str, Any] | None


class VariantResponse(BaseModel):
    """Process variant response with both trace string and parsed activities array."""

    variant_key: str
    activity_trace: str  # Human-readable: "A → B → C" (for display)
    activities: list[str]  # Pre-parsed array: ["A", "B", "C"] (for FE consumption)
    case_count: int
    frequency_percent: float
    avg_duration_seconds: float | None = None
    # Complexity metrics (optional, populated when requested)
    complexity_score: float | None = None
    rework_count: int | None = None
    unique_activity_count: int | None = None


# =============================================================================
# Statistics & Analysis Data (Foundation layer)
# =============================================================================


class ActivityDetailResponse(BaseModel):
    """Detailed activity statistics for process explorer."""

    activity: str
    frequency: int
    frequency_percent: float
    avg_duration_seconds: float | None = None
    min_duration_seconds: float | None = None
    max_duration_seconds: float | None = None
    is_start_activity: bool = False
    is_end_activity: bool = False
    position_avg: float | None = None  # Average position in trace (0=first, 1=last)
    resources: list[str] = []  # Resources that perform this activity


class StatisticsResponse(BaseModel):
    """Process statistics response."""

    total_events: int
    total_cases: int
    total_activities: int
    total_variants: int
    activities: list[str]
    start_activities: dict[str, int]
    end_activities: dict[str, int]
    avg_case_duration_seconds: float | None
    min_case_duration_seconds: float | None
    max_case_duration_seconds: float | None
    date_range: dict[str, datetime] | None


class DatasetStatisticsResponse(BaseModel):
    """Computed statistics from dataset_statistics table.

    These are pre-computed and cached for performance.
    """

    dataset_id: str
    # Volume metrics
    total_events: int
    total_cases: int
    total_activities: int
    total_variants: int
    total_resources: int | None = None
    # Time boundaries
    first_event_at: datetime | None = None
    last_event_at: datetime | None = None
    log_duration_seconds: int | None = Field(None, description="Total time span of the log")
    # Case duration statistics (in seconds)
    avg_case_duration: float | None = None
    median_case_duration: float | None = None
    min_case_duration: float | None = None
    max_case_duration: float | None = None
    stddev_case_duration: float | None = None
    # Case length statistics (number of events)
    avg_case_length: float | None = None
    min_case_length: int | None = None
    max_case_length: int | None = None
    # Variant analysis (for spaghetti detection)
    variant_coverage_80: int | None = Field(
        None, description="Number of variants covering 80% of cases"
    )
    unique_variant_ratio: float | None = Field(
        None, description="variants/cases - high value indicates spaghetti"
    )
    # Activity distribution
    activities: list[dict] | None = Field(
        None, description="Activity frequency list from activities_json"
    )
    # Computation metadata
    computed_at: datetime
    computation_time_ms: int | None = None

    model_config = ConfigDict(from_attributes=True)


class ProcessVariantDetailResponse(BaseModel):
    """Enhanced process variant with all computed fields.

    Used when fetching variants from process_variants table.
    """

    id: str
    dataset_id: str
    variant_key: str = Field(..., description="Hash of the activity sequence")
    activity_sequence: list[str] = Field(..., description="Ordered list of activity names")
    activity_trace: str = Field(..., description="Human-readable: 'A → B → C'")
    case_count: int
    frequency_percent: float
    avg_duration_seconds: float | None = None
    # Complexity metrics
    length: int = Field(..., description="Number of activities in variant")
    has_loops: bool = Field(False, description="True if any activity repeats")
    unique_activity_count: int | None = None

    model_config = ConfigDict(from_attributes=True)


# =============================================================================
# File Parsing & Validation
# =============================================================================


class ColumnDetectionResponse(BaseModel):
    """Column detection result for the mapping UI."""

    dataset_id: str
    status: str = Field(..., description="Dataset status")
    columns: list["ColumnTypeInfo"]
    suggestions: dict[str, dict[str, Any]] = Field(
        default_factory=dict, description="Suggested mappings: {role: {column, confidence}}"
    )
    requires_user_input: bool = Field(
        False, description="True if auto-mapping confidence is below threshold"
    )


class ColumnTypeInfo(BaseModel):
    """Column type information with suggestion data."""

    name: str
    dtype: str = Field(..., description="Detected type: STRING, INTEGER, DATETIME, FLOAT")
    position: int = 0
    sample_values: list[Any] = []
    null_percentage: float = 0.0
    unique_count: int = 0
    # Suggestion for process mining role
    suggested_role: str | None = Field(None, description="case_id, activity, timestamp, resource")
    confidence: float | None = Field(None, ge=0.0, le=1.0, description="Confidence score")


class DataPreviewResponse(BaseModel):
    """Data preview for upload wizard Configure step."""

    dataset_id: str
    filename: str
    columns: list[ColumnTypeInfo]
    rows: list[dict[str, Any]]  # Preview rows (first 10-20)
    total_rows: int
    has_header: bool = True
    field_separator: str = ","
    encoding: str = "utf-8"


class SheetInfo(BaseModel):
    """Sheet information for Excel files."""

    name: str
    index: int
    row_count: int
    column_count: int


class SheetsResponse(BaseModel):
    """Available sheets in an Excel file."""

    dataset_id: str
    filename: str
    sheets: list[SheetInfo]


class ParseConfigRequest(BaseModel):
    """Request to apply parsing configuration."""

    has_header: bool = True
    field_separator: str = ","
    decimal_separator: str = "."
    thousand_separator: str = ","
    sheet_name: str | None = None  # For Excel files
    encoding: str = "utf-8"


# =============================================================================
# Filtering
# =============================================================================


class FilterConfig(BaseModel):
    """Single filter configuration."""

    type: str = Field(..., description="Filter type: time_range, variants_top_k, etc.")
    params: dict[str, Any] = Field(default_factory=dict, description="Filter parameters")


class FilterRequest(BaseModel):
    """Request to apply filters to an event log."""

    name: str | None = Field(None, description="Name for the filtered log")
    filters: list[FilterConfig] = Field(..., description="List of filters to apply")
    save_result: bool = Field(default=True, description="Whether to save the filtered log")


class FilterPreviewRequest(BaseModel):
    """Request to preview filter impact without saving."""

    filters: list[FilterConfig] = Field(..., description="List of filters to apply")


class FilterStatistics(BaseModel):
    """Statistics comparing original and filtered logs."""

    original_cases: int
    filtered_cases: int
    cases_removed: int
    cases_retained_pct: float
    original_events: int
    filtered_events: int
    events_removed: int
    events_retained_pct: float
    original_activities: int
    filtered_activities: int
    activities_removed: int


class FilterPreviewResponse(BaseModel):
    """Response for filter preview."""

    would_retain_cases: int
    would_retain_events: int
    statistics: FilterStatistics
    filters_applied: list[FilterConfig]


class FilteredLogResponse(BaseModel):
    """Response for a filtered log."""

    id: str
    name: str
    source_dataset_id: str = ""
    is_filtered: bool = True
    filter_config: list[FilterConfig] = []
    total_events: int
    total_cases: int
    total_activities: int
    statistics: FilterStatistics | None = None
    created_at: datetime

    @model_validator(mode="before")
    @classmethod
    def parse_json_fields(cls, data: Any) -> Any:
        """Auto-parse filter_config_json and filter_stats_json."""
        if hasattr(data, "__dict__"):
            data = {
                k: getattr(data, k)
                for k in [
                    "id",
                    "name",
                    "source_dataset_id",
                    "is_filtered",
                    "filter_config_json",
                    "filter_stats_json",
                    "total_events",
                    "total_cases",
                    "total_activities",
                    "created_at",
                ]
                if hasattr(data, k)
            }
        if isinstance(data, dict):
            # No longer need to map - using source_dataset_id directly
            if data.get("filter_config_json"):
                try:
                    config_list = json.loads(data["filter_config_json"])
                    data["filter_config"] = [FilterConfig(**c) for c in config_list]
                except (json.JSONDecodeError, TypeError):
                    data["filter_config"] = []
            elif "filter_config" not in data:
                data["filter_config"] = []
            if data.get("filter_stats_json"):
                try:
                    stats_dict = json.loads(data["filter_stats_json"])
                    data["statistics"] = FilterStatistics(**stats_dict)
                except (json.JSONDecodeError, TypeError):
                    data["statistics"] = None
        return data

    model_config = ConfigDict(from_attributes=True)


class FilteredLogListResponse(BaseModel):
    """List of filtered logs derived from a source log."""

    source_dataset_id: str
    source_dataset_name: str
    filtered_logs: list[FilteredLogResponse]
    total: int


class FilterOptionsResponse(BaseModel):
    """Available filter options based on log contents."""

    activities: list[str]
    resources: list[str]
    start_activities: dict[str, int]
    end_activities: dict[str, int]
    total_variants: int
    time_range: dict[str, str | None]
    case_size_range: dict[str, float]


class FilterTemplateResponse(BaseModel):
    """Pre-built filter template."""

    id: str
    name: str
    description: str
    filters: list[FilterConfig]


class FilterTemplateListResponse(BaseModel):
    """List of available filter templates."""

    templates: list[FilterTemplateResponse]


# =============================================================================
# Export
# =============================================================================


class ExportRequest(BaseModel):
    """Export request."""

    format: str = Field("csv", pattern=r"^(csv|xes|parquet)$")
    include_metadata: bool = Field(True, description="Include dataset metadata")


class DownloadResponse(BaseModel):
    """Download URL response."""

    download_url: str
    filename: str
    expires_in: int = 3600


# =============================================================================
# Column Mapping
# =============================================================================


class MappingResponse(BaseModel):
    """Current mapping response."""

    dataset_id: str
    case_id_column: str
    activity_column: str
    timestamp_column: str
    resource_column: str | None = None
    timestamp_format: str | None = None
    additional_columns: list[str] = []
    auto_mapped: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MappingUpdateRequest(BaseModel):
    """Update mapping request."""

    case_id_column: str = Field(..., description="Column for case ID")
    activity_column: str = Field(..., description="Column for activity")
    timestamp_column: str = Field(..., description="Column for timestamp")
    resource_column: str | None = Field(None, description="Column for resource")
    timestamp_format: str | None = Field(None, description="Timestamp format")
    additional_columns: list[str] = Field(default_factory=list)


class PreviewResponse(BaseModel):
    """Preview response with sample mapped data."""

    dataset_id: str
    sample_events: list[dict]
    total_rows: int
    parse_errors: list[str] = []
