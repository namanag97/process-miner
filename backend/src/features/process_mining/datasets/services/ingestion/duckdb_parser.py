"""DuckDB Vectorized Parser - DEPRECATED MODULE.

This module is deprecated. Use the canonical location instead:
    from src.features.process_mining.ingestion.duckdb_parser import duckdb_parser

Scheduled for removal: 2026-01-21
"""

import warnings

warnings.warn(
    "src.features.process_mining.datasets.services.ingestion.duckdb_parser is deprecated. "
    "Use src.features.process_mining.ingestion.duckdb_parser instead. "
    "Scheduled for removal: 2026-01-21",
    DeprecationWarning,
    stacklevel=2,
)

# Re-export from canonical location for backwards compatibility
from src.features.process_mining.ingestion.duckdb_parser import (
    DuckDBParser,
    duckdb_parser,
    _sanitize_column_name,
    _sanitize_delimiter,
    _get_duckdb,
)

__all__ = [
    "DuckDBParser",
    "duckdb_parser",
    "_sanitize_column_name",
    "_sanitize_delimiter",
    "_get_duckdb",
]

