"""Temporal Activities Package.

Exports all activities for worker registration.

Dataset Activities:
    - validate_file_activity: Magic byte verification
    - detect_columns_activity: Column parsing and AI suggestions
    - parse_to_parquet_activity: DuckDB CSV parsing with heartbeat
    - bulk_copy_to_db_activity: Batch insert to PostgreSQL
    - compute_statistics_activity: Metadata computation

Analysis Activities:
    - load_event_log_activity: Load dataset from database
    - mine_model_activity: Run PM4Py discovery algorithms
    - compute_metrics_activity: Quality metrics calculation
    - check_conformance_activity: Token replay/alignment
"""

from src.platform.temporal.activities.analysis import (
    check_conformance_activity,
    compute_metrics_activity,
    load_event_log_activity,
    mine_model_activity,
)
from src.platform.temporal.activities.dataset import (
    bulk_copy_to_db_activity,
    compute_statistics_activity,
    detect_columns_activity,
    parse_to_parquet_activity,
    validate_file_activity,
)
from src.platform.temporal.activities.types import (
    BulkCopyInput,
    BulkCopyOutput,
    CheckConformanceInput,
    CheckConformanceOutput,
    ComputeMetricsInput,
    ComputeMetricsOutput,
    ComputeStatsInput,
    ComputeStatsOutput,
    DetectColumnsInput,
    DetectColumnsOutput,
    LoadEventLogInput,
    LoadEventLogOutput,
    MineModelInput,
    MineModelOutput,
    ParseToParquetInput,
    ParseToParquetOutput,
    ValidateFileInput,
    ValidateFileOutput,
)

# All dataset activities
DATASET_ACTIVITIES = [
    validate_file_activity,
    detect_columns_activity,
    parse_to_parquet_activity,
    bulk_copy_to_db_activity,
    compute_statistics_activity,
]

# All analysis activities
ANALYSIS_ACTIVITIES = [
    load_event_log_activity,
    mine_model_activity,
    compute_metrics_activity,
    check_conformance_activity,
]

# Combined list for worker registration
ALL_ACTIVITIES = DATASET_ACTIVITIES + ANALYSIS_ACTIVITIES

__all__ = [
    "ALL_ACTIVITIES",
    "ANALYSIS_ACTIVITIES",
    "DATASET_ACTIVITIES",
    "BulkCopyInput",
    "BulkCopyOutput",
    "CheckConformanceInput",
    "CheckConformanceOutput",
    "ComputeMetricsInput",
    "ComputeMetricsOutput",
    "ComputeStatsInput",
    "ComputeStatsOutput",
    "DetectColumnsInput",
    "DetectColumnsOutput",
    "LoadEventLogInput",
    "LoadEventLogOutput",
    "MineModelInput",
    "MineModelOutput",
    "ParseToParquetInput",
    "ParseToParquetOutput",
    "ValidateFileInput",
    "ValidateFileOutput",
    "bulk_copy_to_db_activity",
    "check_conformance_activity",
    "compute_metrics_activity",
    "compute_statistics_activity",
    "detect_columns_activity",
    "load_event_log_activity",
    "mine_model_activity",
    "parse_to_parquet_activity",
    "validate_file_activity",
]
