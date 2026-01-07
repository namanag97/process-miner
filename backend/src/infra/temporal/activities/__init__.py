"""Temporal Activities Package - DEPRECATED (v1).

This module is deprecated in favor of activities_v2.
Use the new stateless, idempotent activities instead:
    from src.infra.temporal.activities_v2 import (
        validate_file,
        detect_columns,
        process_chunk,
        finalize_ingestion,
    )

Migration timeline:
- 2026-01-08: Deprecation notice added
- 2026-02-01: Target date for full migration to v2
- 2026-03-01: Scheduled removal of v1

Differences from v2:
- v1: Monolithic activities with AsyncJob writes
- v2: Stateless, idempotent, chunk-based processing

---

Original v1 Documentation (for migration reference):

Exports all activities for worker registration.

All activities publish real-time progress to Redis for SSE streaming.
Frontend can subscribe to progress via: GET /api/v1/operations/{workflow_id}/stream

Dataset Activities:
    - validate_file_activity: Magic byte verification
    - detect_columns_activity: Column parsing and AI suggestions
    - parse_to_parquet_activity: DuckDB CSV parsing with heartbeat
    - compute_statistics_activity: Metadata computation

Analysis Activities:
    - load_event_log_activity: Load dataset from database
    - mine_model_activity: Run PM4Py discovery algorithms
    - compute_metrics_activity: Quality metrics calculation
    - check_conformance_activity: Token replay/alignment

Progress Publishing:
    - publish_progress: Publish step progress
    - publish_step_started: Publish step started event
    - publish_step_completed: Publish step completed event
    - publish_step_failed: Publish step failed event
"""

import warnings

warnings.warn(
    "src.infra.temporal.activities (v1) is deprecated. "
    "Migrate to src.infra.temporal.activities_v2 for stateless, idempotent activities. "
    "Target removal date: 2026-03-01",
    DeprecationWarning,
    stacklevel=2,
)

from src.infra.temporal.activities.analysis import (
    check_conformance_activity,
    compute_metrics_activity,
    load_event_log_activity,
    mine_model_activity,
)
from src.infra.temporal.activities.dataset import (
    compute_statistics_activity,
    detect_columns_activity,
    parse_to_parquet_activity,
    validate_file_activity,
)
from src.infra.temporal.activities.types import (
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
    "check_conformance_activity",
    "compute_metrics_activity",
    "compute_statistics_activity",
    "detect_columns_activity",
    "load_event_log_activity",
    "mine_model_activity",
    "parse_to_parquet_activity",
    "validate_file_activity",
]
