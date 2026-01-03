"""DuckDB Vectorized Ingestion Service.

High-performance CSV/data parsing using DuckDB for 10-100x speedup
over native Python loops on large files.

Key features:
- Columnar processing (vectorized operations)
- Zero-copy Arrow interop for PM4Py integration
- Automatic type detection
- Memory-efficient streaming for large files
"""

import io
import os
import re
import tempfile
from datetime import datetime
from typing import Any, Optional

from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Lazy import to avoid requiring DuckDB if not used
_duckdb = None

# BUG-056 FIX: Strict column name validation pattern
# Only allow alphanumeric, underscores, colons (for PM4Py standard names like "case:concept:name")
VALID_COLUMN_PATTERN = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_:.\-\s]*$')
MAX_COLUMN_LENGTH = 128


def _sanitize_column_name(col: str, param_name: str = "column") -> str:
    """Validate and sanitize column name to prevent SQL injection.
    
    BUG-056 FIX: Prevents SQL injection via malicious column names.
    
    Args:
        col: Column name to validate
        param_name: Parameter name for error message
        
    Returns:
        The validated column name
        
    Raises:
        ValueError: If column name is invalid
    """
    if not col:
        raise ValueError(f"Empty {param_name} name")
    
    if len(col) > MAX_COLUMN_LENGTH:
        raise ValueError(f"{param_name} name too long: {len(col)} > {MAX_COLUMN_LENGTH}")
    
    if not VALID_COLUMN_PATTERN.match(col):
        raise ValueError(
            f"Invalid {param_name} name '{col}'. "
            f"Only alphanumeric characters, underscores, colons, dots, and hyphens are allowed."
        )
    
    return col


def _sanitize_delimiter(delim: str) -> str:
    """Validate delimiter to prevent SQL injection.
    
    Args:
        delim: Delimiter character
        
    Returns:
        Validated delimiter
        
    Raises:
        ValueError: If delimiter is invalid
    """
    # Only allow single common delimiters
    allowed = {",", ";", "\t", "|", " "}
    if delim not in allowed:
        raise ValueError(f"Invalid delimiter '{delim}'. Allowed: {allowed}")
    return delim


def _get_duckdb():
    """Lazy load DuckDB."""
    global _duckdb
    if _duckdb is None:
        try:
            import duckdb
            _duckdb = duckdb
        except ImportError:
            raise ImportError(
                "DuckDB is required for vectorized ingestion. "
                "Install with: pip install duckdb"
            )
    return _duckdb


class DuckDBIngestionService:
    """High-performance data ingestion using DuckDB."""

    def _get_manager(self):
        """Get the DuckDB manager instance."""
        from src.infrastructure.duckdb import duckdb_manager
        return duckdb_manager

    def parse_csv_fast(
        self,
        file_content: bytes,
        case_id_col: str = "case_id",
        activity_col: str = "activity",
        timestamp_col: str = "timestamp",
        resource_col: Optional[str] = None,
        delimiter: str = ",",
    ) -> dict[str, Any]:
        """
        Parse CSV using DuckDB for vectorized performance.

        Returns:
            Dictionary with parsed data and statistics.
        """
        # BUG-056 FIX: Sanitize ALL user-controlled inputs before SQL construction
        case_id_col = _sanitize_column_name(case_id_col, "case_id_column")
        activity_col = _sanitize_column_name(activity_col, "activity_column")
        timestamp_col = _sanitize_column_name(timestamp_col, "timestamp_column")
        if resource_col:
            resource_col = _sanitize_column_name(resource_col, "resource_column")
        delimiter = _sanitize_delimiter(delimiter)
        
        duckdb_manager = self._get_manager()
        
        logger.info("duckdb_parse_started", size_bytes=len(file_content))
        
        temp_path = None
        conn = None
        try:
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
                f.write(file_content)
                temp_path = f.name

            # Build column selection (now safe after sanitization)
            resource_select = f'"{resource_col}"' if resource_col else "NULL"

            conn = duckdb_manager.get_connection()
            conn.execute(f"""
                CREATE TABLE events AS
                SELECT
                    "{case_id_col}"::VARCHAR as case_id,
                    "{activity_col}"::VARCHAR as activity,
                    "{timestamp_col}"::TIMESTAMP as timestamp,
                    {resource_select}::VARCHAR as resource,
                    ROW_NUMBER() OVER () as row_num
                FROM read_csv_auto('{temp_path}', delim='{delimiter}', header=true)
                WHERE "{case_id_col}" IS NOT NULL
                  AND "{activity_col}" IS NOT NULL
                  AND "{timestamp_col}" IS NOT NULL
            """)

            # Get aggregate statistics in SQL (not Python!)
            stats = conn.execute("""
                SELECT
                    COUNT(DISTINCT case_id) as total_cases,
                    COUNT(*) as total_events,
                    COUNT(DISTINCT activity) as total_activities,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time,
                    LIST(DISTINCT activity ORDER BY activity) as activities,
                    COUNT(DISTINCT resource) FILTER (WHERE resource IS NOT NULL) as total_resources
                FROM events
            """).fetchone()

            # Get events as Arrow table for zero-copy conversion
            arrow_table = conn.execute("""
                SELECT case_id, activity, timestamp, resource
                FROM events
                ORDER BY case_id, timestamp
            """).arrow()

            import pyarrow as pa
            if isinstance(arrow_table, pa.RecordBatchReader):
                arrow_table = arrow_table.read_all()

            # Get case-level aggregates
            case_stats = conn.execute("""
                SELECT
                    case_id,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time,
                    COUNT(*) as event_count,
                    STRING_AGG(activity, ' -> ' ORDER BY timestamp) as variant
                FROM events
                GROUP BY case_id
            """).arrow()

            if isinstance(case_stats, pa.RecordBatchReader):
                case_stats = case_stats.read_all()

            logger.info(
                "duckdb_parse_completed",
                total_cases=stats[0],
                total_events=stats[1],
                total_activities=stats[2],
            )

            return {
                "statistics": {
                    "total_cases": stats[0],
                    "total_events": stats[1],
                    "total_activities": stats[2],
                    "start_time": stats[3].isoformat() if stats[3] else None,
                    "end_time": stats[4].isoformat() if stats[4] else None,
                    "activities": list(stats[5]) if stats[5] else [],
                    "total_resources": stats[6],
                },
                "events_arrow": arrow_table,
                "cases_arrow": case_stats,
            }
        finally:
            # Clean up resources
            if conn:
                conn.close()
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def arrow_to_pm4py(self, arrow_table) -> Any:
        """
        Convert Arrow table to PM4Py EventLog.
        
        Uses direct pandas conversion for zero-copy performance.
        """
        import pm4py
        from pm4py.objects.conversion.log import converter
        
        # Arrow -> Pandas (zero-copy where possible)
        df = arrow_table.to_pandas()
        
        # Rename to PM4Py standard columns
        df = df.rename(columns={
            "case_id": "case:concept:name",
            "activity": "concept:name",
            "timestamp": "time:timestamp",
            "resource": "org:resource",
        })
        
        # Convert to EventLog
        log = converter.apply(df, variant=converter.Variants.TO_EVENT_LOG)
        
        return log
    
    def detect_columns_fast(
        self,
        file_content: bytes,
        delimiter: str = ",",
        sample_rows: int = 100,
    ) -> dict[str, Any]:
        """
        Detect column types using DuckDB's inference.

        Much faster than Python-based detection for large files.
        """
        duckdb = _get_duckdb()

        conn = None
        temp_path = None
        try:
            conn = duckdb.connect(":memory:")

            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
                f.write(file_content)
                temp_path = f.name

            # BUG-056b FIX: Sanitize delimiter to prevent injection
            safe_delimiter = _sanitize_delimiter(delimiter)
            
            # Get schema from DuckDB's auto-detection using safe file path and delimiter
            # Note: temp_path is controlled, not user input
            schema_info = conn.execute(f"""
                DESCRIBE SELECT * FROM read_csv_auto('{temp_path}', delim='{safe_delimiter}', header=true, sample_size={int(sample_rows)})
            """).fetchall()

            # Analyze each column
            columns = []
            suggestions = {
                "case_id_column": None,
                "activity_column": None,
                "timestamp_column": None,
                "resource_column": None,
            }

            for col_name, col_type, *_ in schema_info:
                col_info = {
                    "name": col_name,
                    "detected_type": col_type,
                    "suggested_role": None,
                }

                # Heuristic detection based on column name and type
                name_lower = col_name.lower()

                if any(x in name_lower for x in ["case", "trace"]) or (name_lower == "id" and ("BIGINT" in col_type or "VARCHAR" in col_type)):
                    col_info["suggested_role"] = "case_id"
                    if not suggestions["case_id_column"]:
                        suggestions["case_id_column"] = col_name

                elif any(x in name_lower for x in ["activity", "action", "event", "task"]):
                    col_info["suggested_role"] = "activity"
                    if not suggestions["activity_column"]:
                        suggestions["activity_column"] = col_name

                elif any(x in name_lower for x in ["time", "date", "stamp"]) or "TIMESTAMP" in col_type:
                    col_info["suggested_role"] = "timestamp"
                    if not suggestions["timestamp_column"]:
                        suggestions["timestamp_column"] = col_name

                elif any(x in name_lower for x in ["resource", "user", "actor", "agent", "employee"]):
                    col_info["suggested_role"] = "resource"
                    if not suggestions["resource_column"]:
                        suggestions["resource_column"] = col_name

                columns.append(col_info)

            # Get row count using sanitized delimiter
            row_count = conn.execute(f"""
                SELECT COUNT(*) FROM read_csv_auto('{temp_path}', delim='{safe_delimiter}', header=true)
            """).fetchone()[0]

            return {
                "columns": columns,
                "suggestions": suggestions,
                "row_count": row_count,
                "delimiter": delimiter,
            }
        finally:
            # Clean up resources
            if conn:
                conn.close()
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)
    
    def get_variants_fast(self, file_content: bytes, mapping: dict) -> list[dict]:
        """
        Extract process variants using DuckDB aggregation.

        Computes variants in SQL instead of Python loops.
        """
        duckdb = _get_duckdb()

        conn = None
        temp_path = None
        try:
            conn = duckdb.connect(":memory:")

            with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
                f.write(file_content)
                temp_path = f.name

            # BUG-056b FIX: Sanitize column names from mapping
            case_col = _sanitize_column_name(mapping['case_id'], 'case_id')
            activity_col = _sanitize_column_name(mapping['activity'], 'activity')
            timestamp_col = _sanitize_column_name(mapping['timestamp'], 'timestamp')
            
            # Compute variants with case counts using sanitized column names
            variants = conn.execute(f"""
                WITH case_variants AS (
                    SELECT
                        "{case_col}" as case_id,
                        STRING_AGG("{activity_col}", ' -> ' ORDER BY "{timestamp_col}") as variant
                    FROM read_csv_auto('{temp_path}', header=true)
                    GROUP BY "{case_col}"
                )
                SELECT
                    variant,
                    COUNT(*) as case_count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as frequency_percent
                FROM case_variants
                GROUP BY variant
                ORDER BY case_count DESC
                LIMIT 100
            """).fetchall()

            return [
                {
                    "variant": v[0],
                    "case_count": v[1],
                    "frequency_percent": v[2],
                }
                for v in variants
            ]
        finally:
            # Clean up resources
            if conn:
                conn.close()
            if temp_path and os.path.exists(temp_path):
                os.unlink(temp_path)


# Singleton instance
duckdb_ingestion_service = DuckDBIngestionService()
