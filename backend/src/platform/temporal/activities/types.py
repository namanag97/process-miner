"""Temporal Activity Types.

Dataclasses for activity inputs and outputs, providing type safety
for workflow-to-activity communication.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


# =============================================================================
# Dataset Activities Types
# =============================================================================


@dataclass
class ValidateFileInput:
    """Input for validate_file_activity."""

    dataset_id: str
    storage_key: str


@dataclass
class ValidateFileOutput:
    """Output from validate_file_activity."""

    dataset_id: str
    is_valid: bool
    file_format: str  # "csv" or "xes"
    file_size_bytes: int
    error_message: str | None = None


@dataclass
class DetectColumnsInput:
    """Input for detect_columns_activity."""

    dataset_id: str
    file_content: bytes
    filename: str


@dataclass
class DetectColumnsOutput:
    """Output from detect_columns_activity."""

    dataset_id: str
    columns: list[dict[str, Any]]
    suggestions: dict[str, Any]
    row_count: int
    can_auto_map: bool = False


@dataclass
class ParseToParquetInput:
    """Input for parse_to_parquet_activity."""

    dataset_id: str
    storage_key: str
    case_id_column: str
    activity_column: str
    timestamp_column: str
    resource_column: str | None = None
    timestamp_format: str | None = None


@dataclass
class ParseToParquetOutput:
    """Output from parse_to_parquet_activity."""

    dataset_id: str
    total_cases: int
    total_events: int
    total_activities: int
    cases_data: list[dict[str, Any]] = field(default_factory=list)
    events_data: list[dict[str, Any]] = field(default_factory=list)
    statistics: dict[str, Any] = field(default_factory=dict)


@dataclass
class BulkCopyInput:
    """Input for bulk_copy_to_db_activity."""

    dataset_id: str
    cases_data: list[dict[str, Any]]
    events_data: list[dict[str, Any]]
    batch_size: int = 5000


@dataclass
class BulkCopyOutput:
    """Output from bulk_copy_to_db_activity."""

    dataset_id: str
    cases_inserted: int
    events_inserted: int
    duration_ms: float


@dataclass
class ComputeStatsInput:
    """Input for compute_statistics_activity."""

    dataset_id: str
    statistics: dict[str, Any]


@dataclass
class ComputeStatsOutput:
    """Output from compute_statistics_activity."""

    dataset_id: str
    total_events: int
    total_cases: int
    total_activities: int
    total_variants: int
    first_event_at: datetime | None = None
    last_event_at: datetime | None = None
    avg_case_duration: float | None = None


# =============================================================================
# Analysis Activities Types
# =============================================================================


@dataclass
class LoadEventLogInput:
    """Input for load_event_log_activity."""

    dataset_id: str


@dataclass
class LoadEventLogOutput:
    """Output from load_event_log_activity."""

    dataset_id: str
    dataset_name: str
    total_cases: int
    total_events: int
    is_loaded: bool = True


@dataclass
class MineModelInput:
    """Input for mine_model_activity."""

    dataset_id: str
    miner_type: str  # "alpha", "inductive", "heuristic", "ilp"
    model_name: str | None = None


@dataclass
class MineModelOutput:
    """Output from mine_model_activity."""

    model_id: str
    dataset_id: str
    miner_type: str
    model_format: str
    serialized_model: str
    graph_json: dict[str, Any] | None = None
    fitness: float | None = None
    precision: float | None = None


@dataclass
class ComputeMetricsInput:
    """Input for compute_metrics_activity."""

    dataset_id: str
    model_id: str


@dataclass
class ComputeMetricsOutput:
    """Output from compute_metrics_activity."""

    model_id: str
    fitness: float | None = None
    precision: float | None = None
    generalization: float | None = None
    simplicity: float | None = None


@dataclass
class CheckConformanceInput:
    """Input for check_conformance_activity."""

    dataset_id: str
    model_id: str
    method: str = "token_replay"  # "token_replay" or "alignment"


@dataclass
class CheckConformanceOutput:
    """Output from check_conformance_activity."""

    conformance_id: str
    dataset_id: str
    model_id: str
    fitness: float
    precision: float | None = None
    is_conformant: bool = False
    fitting_traces: int = 0
    total_traces: int = 0
