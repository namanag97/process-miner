"""Temporal Activities v2 - Stateless and Idempotent.

Activities follow these rules:
1. Single responsibility, <5 min execution
2. Idempotent: same input → same result (use upserts, check before insert)
3. No AsyncJob writes—update business entities directly
4. Return value contains next-step data, not status updates
5. Heartbeat for operations >30 seconds

Usage:
    from src.infra.temporal.activities_v2 import (
        validate_file,
        get_chunk_list,
        process_chunk,
        finalize_ingestion,
    )
"""

# Analysis activities
from src.infra.temporal.activities_v2.analysis import (
    check_conformance,
    compute_model_metrics,
    discover_process_model,
    load_event_log,
    load_process_model,
    save_conformance_result,
    save_process_model,
)

# Ingestion activities
from src.infra.temporal.activities_v2.ingestion import (
    detect_columns,
    finalize_ingestion,
    get_chunk_list,
    process_chunk,
    update_dataset_status,
    validate_file,
)
from src.infra.temporal.activities_v2.types import (
    ChunkInfo,
    ChunkProcessResult,
    ColumnDetectionResult,
    ColumnMapping,
    ConformanceResult,
    DiscoveryResult,
    EventLogInfo,
    IngestionResult,
    ModelMetrics,
    ValidationResult,
)

__all__ = [
    # Types
    "ChunkInfo",
    "ChunkProcessResult",
    "ColumnDetectionResult",
    "ColumnMapping",
    "ConformanceResult",
    "DiscoveryResult",
    "EventLogInfo",
    "IngestionResult",
    "ModelMetrics",
    "ValidationResult",
    "check_conformance",
    "compute_model_metrics",
    "detect_columns",
    "discover_process_model",
    "finalize_ingestion",
    "get_chunk_list",
    # Analysis activities
    "load_event_log",
    "load_process_model",
    "process_chunk",
    "save_conformance_result",
    "save_process_model",
    "update_dataset_status",
    # Ingestion activities
    "validate_file",
]
