"""Data Ingestion Service - DEPRECATED MODULE.

This module is deprecated. Use the canonical location instead:
    from src.features.process_mining.ingestion.service import IngestionService

Scheduled for removal: 2026-01-22
"""

import warnings

warnings.warn(
    "src.features.process_mining.datasets.services.ingestion.service is deprecated. "
    "Use src.features.process_mining.ingestion.service instead. "
    "Scheduled for removal: 2026-01-22",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from canonical location for backwards compatibility
from src.features.process_mining.ingestion.service import (  # noqa: E402
    IngestionService,
    get_ingestion_service,
    ingestion_service,
)

__all__ = [
    "IngestionService",
    "get_ingestion_service",
    "ingestion_service",
]
