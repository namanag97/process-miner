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
import tempfile
from datetime import datetime
from typing import Any, Optional

from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Lazy import to avoid requiring DuckDB if not used
_duckdb = None


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
        duckdb = _get_duckdb()
        
        logger.info("duckdb_parse_started", size_bytes=len(file_content))
        
        # Create in-memory connection
        conn = duckdb.connect(":memory:")
        
        # Write content to temp file (DuckDB reads from file path)
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(file_content)
            temp_path = f.name
        
        try:
            # Build column selection
            resource_select = f'"{resource_col}"' if resource_col else "NULL"
            
            # Let DuckDB parse the CSV natively with automatic type detection
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
                    "start_time": stats[3],
                    "end_time": stats[4],
                    "activities": list(stats[5]) if stats[5] else [],
                    "total_resources": stats[6],
                },
                "events_arrow": arrow_table,
                "cases_arrow": case_stats,
            }
            
        finally:
            conn.close()
            # Clean up temp file
            import os
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
        
        conn = duckdb.connect(":memory:")
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(file_content)
            temp_path = f.name
        
        try:
            # Get schema from DuckDB's auto-detection
            schema_info = conn.execute(f"""
                DESCRIBE SELECT * FROM read_csv_auto('{temp_path}', delim='{delimiter}', header=true, sample_size={sample_rows})
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
                
                if any(x in name_lower for x in ["case", "trace", "id"]) and "BIGINT" in col_type or "VARCHAR" in col_type:
                    col_info["suggested_role"] = "case_id"
                    if not suggestions["case_id_column"]:
                        suggestions["case_id_column"] = col_name
                        
                elif any(x in name_lower for x in ["activity", "action", "event", "task"]):
                    col_info["suggested_role"] = "activity"
                    if not suggestions["activity_column"]:
                        suggestions["activity_column"] = col_name
                        
                elif any(x in name_lower for x in ["time", "date", "timestamp"]) or "TIMESTAMP" in col_type:
                    col_info["suggested_role"] = "timestamp"
                    if not suggestions["timestamp_column"]:
                        suggestions["timestamp_column"] = col_name
                        
                elif any(x in name_lower for x in ["resource", "user", "actor", "agent", "employee"]):
                    col_info["suggested_role"] = "resource"
                    if not suggestions["resource_column"]:
                        suggestions["resource_column"] = col_name
                
                columns.append(col_info)
            
            # Get row count
            row_count = conn.execute(f"""
                SELECT COUNT(*) FROM read_csv_auto('{temp_path}', delim='{delimiter}', header=true)
            """).fetchone()[0]
            
            return {
                "columns": columns,
                "suggestions": suggestions,
                "row_count": row_count,
                "delimiter": delimiter,
            }
            
        finally:
            conn.close()
            import os
            os.unlink(temp_path)
    
    def get_variants_fast(self, file_content: bytes, mapping: dict) -> list[dict]:
        """
        Extract process variants using DuckDB aggregation.
        
        Computes variants in SQL instead of Python loops.
        """
        duckdb = _get_duckdb()
        
        conn = duckdb.connect(":memory:")
        
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.csv', delete=False) as f:
            f.write(file_content)
            temp_path = f.name
        
        try:
            # Compute variants with case counts
            variants = conn.execute(f"""
                WITH case_variants AS (
                    SELECT 
                        "{mapping['case_id']}" as case_id,
                        STRING_AGG("{mapping['activity']}", ' -> ' ORDER BY "{mapping['timestamp']}") as variant
                    FROM read_csv_auto('{temp_path}', header=true)
                    GROUP BY "{mapping['case_id']}"
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
            conn.close()
            import os
            os.unlink(temp_path)


# Singleton instance
duckdb_ingestion_service = DuckDBIngestionService()
