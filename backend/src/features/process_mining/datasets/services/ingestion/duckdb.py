"""DuckDB Ingestion Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.ingestion.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.ingestion.duckdb import duckdb_ingestion_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.ingestion import duckdb_parser
"""

from src.features.process_mining.ingestion.duckdb_parser import (
    DuckDBParser as DuckDBIngestionService,
)
from src.features.process_mining.ingestion.duckdb_parser import (
    duckdb_parser as duckdb_ingestion_service,
)

__all__ = [
    "DuckDBIngestionService",
    "duckdb_ingestion_service",
]
