"""Ingestion Module - Unified data ingestion.

Components:
- service.py: Main IngestionService (PM4Py based for XES/CSV)
- duckdb_parser.py: High-performance DuckDB parser for CSV
- unified.py: UnifiedIngestionService facade (routes to appropriate parser)
"""

from .duckdb_parser import DuckDBParser, duckdb_parser
from .service import IngestionService, ingestion_service
from .unified import UnifiedIngestionService, unified_ingestion_service

__all__ = [
    "DuckDBParser",
    "IngestionService",
    "UnifiedIngestionService",
    "duckdb_parser",
    "ingestion_service",
    "unified_ingestion_service",
]
