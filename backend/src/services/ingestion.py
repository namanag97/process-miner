"""Ingestion Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.ingestion.

Example:
    # Legacy (still works):
    from src.services.ingestion import ingestion_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.ingestion import ingestion_service
"""

from src.features.process_mining.ingestion import (
    IngestionService,
    ingestion_service,
)

__all__ = [
    "IngestionService",
    "ingestion_service",
]
