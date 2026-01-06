"""Datasets Domain Services.

Services for dataset lifecycle management:
- Ingestion pipeline (DuckDB-based parsing)
- Storage service (S3/MinIO)
- Validation service
- Metadata computation
- Event streaming for job progress
"""

from src.features.process_mining.ingestion.service import IngestionService
from src.features.process_mining.services.ingestion.stream import (
    EventStreamManager,
    EventType,
    event_stream_manager,
)

__all__ = [
    "IngestionService",
    "EventStreamManager",
    "EventType",
    "event_stream_manager",
]

