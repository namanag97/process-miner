"""Temporal Activities v2 - Stateless and Idempotent.

Activities follow these rules:
1. Single responsibility, <5 min execution
2. Idempotent: same input → same result (use upserts, check before insert)
3. No AsyncJob writes—update business entities directly
4. Return value contains next-step data, not status updates
5. Heartbeat for operations >30 seconds

Usage:
    from src.platform.temporal.activities_v2 import (
        validate_file,
        get_chunk_list,
        process_chunk,
        finalize_ingestion,
    )
"""

from src.platform.temporal.activities_v2.types import (
    ChunkInfo,
    ColumnMapping,
    ValidationResult,
    ColumnDetectionResult,
    ChunkProcessResult,
    IngestionResult,
    EventLogInfo,
    DiscoveryResult,
    ConformanceResult,
    ModelMetrics,
)

# Ingestion activities
from src.platform.temporal.activities_v2.ingestion import (
    validate_file,
    detect_columns,
    get_chunk_list,
    process_chunk,
    finalize_ingestion,
    update_dataset_status,
)

# Analysis activities
from src.platform.temporal.activities_v2.analysis import (
    load_event_log,
    discover_process_model,
    compute_model_metrics,
    save_process_model,
    load_process_model,
    check_conformance,
    save_conformance_result,
)

__all__ = [
    # Types
    "ChunkInfo",
    "ColumnMapping",
    "ValidationResult",
    "ColumnDetectionResult",
    "ChunkProcessResult",
    "IngestionResult",
    "EventLogInfo",
    "DiscoveryResult",
    "ConformanceResult",
    "ModelMetrics",
    # Ingestion activities
    "validate_file",
    "detect_columns",
    "get_chunk_list",
    "process_chunk",
    "finalize_ingestion",
    "update_dataset_status",
    # Analysis activities
    "load_event_log",
    "discover_process_model",
    "compute_model_metrics",
    "save_process_model",
    "load_process_model",
    "check_conformance",
    "save_conformance_result",
]
