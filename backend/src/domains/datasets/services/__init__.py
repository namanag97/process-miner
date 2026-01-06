"""Datasets Domain Services.

Dataset management and ingestion services.
"""

# Re-export from process_mining for backward compatibility
from src.features.process_mining.ingestion import (
    IngestionService,
    ingestion_service,
)

__all__ = [
    "IngestionService",
    "ingestion_service",
]
