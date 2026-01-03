"""EventLog Loader Service - High-Performance DataFrame Loading.

Uses DuckDB to query SQLite database directly and return pandas DataFrames
formatted for PM4py, avoiding the 4x data copying of ORM iteration.

Performance improvement:
  - Current: SQL → Dict → ORM Object → PM4Py Trace (4 copies)
  - New: SQL → Arrow → DataFrame → PM4Py (1-2 copies, 10x faster)
"""

from typing import Any, Optional

import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog

from src.core.config import get_settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

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
                "DuckDB is required for high-performance loading. "
                "Install with: pip install duckdb"
            )
    return _duckdb


class EventLogLoader:
    """
    High-performance event log loading for PM4py.
    
    Uses DuckDB to query the SQLite database directly and return
    pandas DataFrames in PM4py format, bypassing slow ORM iteration.
    """

    def __init__(self):
        # Extract SQLite path from async URL
        # "sqlite+aiosqlite:///./data/db/process_mining.db" -> "./data/db/process_mining.db"
        db_url = settings.database_url
        if "sqlite" in db_url:
            # Handle both relative and absolute paths
            self._sqlite_path = db_url.split("///")[-1]
        else:
            self._sqlite_path = None
            logger.warning("event_log_loader_non_sqlite", database_url=db_url)

    def _get_connection(self):
        """Get DuckDB connection with SQLite attached.

        IMPORTANT: This reads directly from the SQLite file on disk, bypassing
        SQLAlchemy's transaction buffer. Any uncommitted SQLAlchemy changes will
        NOT be visible to DuckDB queries.

        To avoid "transactional ghosting" issues:
        - Ensure all SQLAlchemy changes are committed before using this loader
        - FastAPI endpoints auto-commit via get_db() dependency
        - For manual usage, call session.commit() before loading
        """
        duckdb = _get_duckdb()
        conn = duckdb.connect(":memory:")

        if self._sqlite_path:
            # Attach SQLite database as 'db'
            conn.execute(f"ATTACH '{self._sqlite_path}' AS db (TYPE SQLITE)")

        return conn

    def load_as_dataframe(
        self,
        dataset_id: str,
        include_attributes: bool = False,
    ) -> pd.DataFrame:
        """
        Load dataset directly as pandas DataFrame via DuckDB.

        Note: This is synchronous because DuckDB operations are sync.

        Args:
            dataset_id: UUID of the dataset
            include_attributes: Whether to parse JSON attributes
        """
        logger.info("dataset_loader_started", dataset_id=dataset_id)

        conn = self._get_connection()
        
        try:
            # Query SQLite through DuckDB
            # BUG-032 FIX: Use parameterized query to prevent SQL injection
            query = """
                SELECT 
                    pc.case_id AS "case:concept:name",
                    pe.activity AS "concept:name",
                    pe.timestamp AS "time:timestamp",
                    pe.resource AS "org:resource"
                FROM db.process_events pe
                INNER JOIN db.process_cases pc 
                    ON pe.case_ref_id = pc.id
                WHERE pc.dataset_id = ?
                ORDER BY pc.case_id, pe.timestamp
            """
            
            # Execute and get Arrow table (zero-copy)
            arrow_result = conn.execute(query, [dataset_id]).arrow()
            
            # Handle newer DuckDB/PyArrow where arrow() returns a RecordBatchReader
            import pyarrow as pa
            if isinstance(arrow_result, pa.RecordBatchReader):
                arrow_table = arrow_result.read_all()
            else:
                arrow_table = arrow_result
            
            # Convert to pandas DataFrame
            df = arrow_table.to_pandas()
            
            if df.empty:
                logger.warning("dataset_loader_empty", dataset_id=dataset_id)
                return self._empty_dataframe()
            
            # Ensure timestamp is datetime
            if "time:timestamp" in df.columns:
                df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])
            
            # Format for PM4py
            df = pm4py.format_dataframe(
                df,
                case_id="case:concept:name",
                activity_key="concept:name",
                timestamp_key="time:timestamp",
            )
            
            logger.info(
                "dataset_loader_completed",
                dataset_id=dataset_id,
                total_events=len(df),
                total_cases=df["case:concept:name"].nunique(),
            )
            
            return df
            
        finally:
            conn.close()

    def load_as_pm4py_log(self, dataset_id: str) -> PM4PyLog:
        """
        Load dataset and convert to PM4Py EventLog object.

        Note: This is synchronous because DuckDB operations are sync.

        Args:
            dataset_id: UUID of the dataset

        Returns:
            PM4Py EventLog object
        """
        df = self.load_as_dataframe(dataset_id)

        if df.empty:
            return PM4PyLog()

        # Convert DataFrame to EventLog
        return pm4py.convert_to_event_log(df)

    def load_statistics(self, dataset_id: str) -> dict[str, Any]:
        """
        Load dataset statistics using SQL aggregation.

        Note: This is synchronous because DuckDB operations are sync.

        Args:
            dataset_id: UUID of the dataset

        Returns:
            Dictionary with statistics
        """
        conn = self._get_connection()
        
        try:
            # BUG-032 FIX: Use parameterized query
            stats = conn.execute("""
                WITH events AS (
                    SELECT 
                        pc.case_id,
                        pe.activity,
                        pe.timestamp,
                        pe.resource
                    FROM db.process_events pe
                    INNER JOIN db.process_cases pc 
                        ON pe.case_ref_id = pc.id
                    WHERE pc.dataset_id = ?
                )
                SELECT
                    COUNT(*) as total_events,
                    COUNT(DISTINCT case_id) as total_cases,
                    COUNT(DISTINCT activity) as total_activities,
                    COUNT(DISTINCT resource) FILTER (WHERE resource IS NOT NULL) as total_resources,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time,
                    LIST(DISTINCT activity ORDER BY activity) as activities
                FROM events
            """, [dataset_id]).fetchone()
            
            return {
                "total_events": stats[0],
                "total_cases": stats[1],
                "total_activities": stats[2],
                "total_resources": stats[3],
                "start_time": stats[4].isoformat() if stats[4] else None,
                "end_time": stats[5].isoformat() if stats[5] else None,
                "activities": list(stats[6]) if stats[6] else [],
            }
            
        finally:
            conn.close()

    def load_start_end_activities(self, dataset_id: str) -> tuple[dict[str, int], dict[str, int]]:
        """
        Get start and end activities with frequencies using SQL.

        Note: This is synchronous because DuckDB operations are sync.

        Args:
            dataset_id: UUID of the dataset

        Returns:
            Tuple of (start_activities, end_activities) dictionaries
        """
        conn = self._get_connection()
        
        try:
            # Start activities - BUG-032 FIX: parameterized query
            start_result = conn.execute("""
                WITH first_events AS (
                    SELECT 
                        pc.case_id,
                        pe.activity,
                        ROW_NUMBER() OVER (PARTITION BY pc.case_id ORDER BY pe.timestamp) as rn
                    FROM db.process_events pe
                    INNER JOIN db.process_cases pc 
                        ON pe.case_ref_id = pc.id
                    WHERE pc.dataset_id = ?
                )
                SELECT activity, COUNT(*) as freq
                FROM first_events
                WHERE rn = 1
                GROUP BY activity
                ORDER BY freq DESC
            """, [dataset_id]).fetchall()
            
            # End activities - BUG-032 FIX: parameterized query
            end_result = conn.execute("""
                WITH last_events AS (
                    SELECT 
                        pc.case_id,
                        pe.activity,
                        ROW_NUMBER() OVER (PARTITION BY pc.case_id ORDER BY pe.timestamp DESC) as rn
                    FROM db.process_events pe
                    INNER JOIN db.process_cases pc 
                        ON pe.case_ref_id = pc.id
                    WHERE pc.dataset_id = ?
                )
                SELECT activity, COUNT(*) as freq
                FROM last_events
                WHERE rn = 1
                GROUP BY activity
                ORDER BY freq DESC
            """, [dataset_id]).fetchall()
            
            start_activities = {row[0]: row[1] for row in start_result}
            end_activities = {row[0]: row[1] for row in end_result}
            
            return start_activities, end_activities
            
        finally:
            conn.close()

    def load_dfg(self, dataset_id: str) -> tuple[dict, dict[str, int], dict[str, int]]:
        """
        Compute Directly-Follows Graph using SQL.

        Note: This is synchronous because DuckDB operations are sync.

        Args:
            dataset_id: UUID of the dataset

        Returns:
            Tuple of (dfg, start_activities, end_activities)
            where dfg is {(source, target): frequency}
        """
        conn = self._get_connection()

        try:
            # DFG edges - BUG-032 FIX: parameterized query
            dfg_result = conn.execute("""
                WITH ordered_events AS (
                    SELECT
                        pc.case_id,
                        pe.activity,
                        pe.timestamp,
                        LEAD(pe.activity) OVER (
                            PARTITION BY pc.case_id
                            ORDER BY pe.timestamp
                        ) as next_activity
                    FROM db.process_events pe
                    INNER JOIN db.process_cases pc
                        ON pe.case_ref_id = pc.id
                    WHERE pc.dataset_id = ?
                )
                SELECT activity, next_activity, COUNT(*) as freq
                FROM ordered_events
                WHERE next_activity IS NOT NULL
                GROUP BY activity, next_activity
                ORDER BY freq DESC
            """, [dataset_id]).fetchall()

            dfg = {(row[0], row[1]): row[2] for row in dfg_result}

            # Get start/end activities
            start_activities, end_activities = self.load_start_end_activities(dataset_id)

            return dfg, start_activities, end_activities

        finally:
            conn.close()

    def load_variants(
        self,
        dataset_id: str,
        top_k: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """
        Get process variants using SQL aggregation.

        Note: This is synchronous because DuckDB operations are sync.

        Args:
            dataset_id: UUID of the dataset
            top_k: Limit to top K variants (optional)

        Returns:
            List of variant dictionaries with trace, count, and percentage
        """
        conn = self._get_connection()
        
        try:
            # BUG-032 FIX: parameterized query (limit_clause handled separately as it's an int)
            limit_clause = f"LIMIT {int(top_k)}" if top_k else ""
            
            # Note: limit_clause is safe as we cast top_k to int above
            query = f"""
                WITH case_variants AS (
                    SELECT 
                        pc.case_id,
                        STRING_AGG(pe.activity, ' -> ' ORDER BY pe.timestamp) as variant
                    FROM db.process_events pe
                    INNER JOIN db.process_cases pc 
                        ON pe.case_ref_id = pc.id
                    WHERE pc.dataset_id = ?
                    GROUP BY pc.case_id
                )
                SELECT 
                    variant,
                    COUNT(*) as case_count,
                    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as frequency_percent
                FROM case_variants
                GROUP BY variant
                ORDER BY case_count DESC
                {limit_clause}
            """
            variants = conn.execute(query, [dataset_id]).fetchall()
            
            return [
                {
                    "variant_key": f"v{i}",
                    "activity_trace": row[0],
                    "activities": row[0].split(" -> "),
                    "case_count": row[1],
                    "frequency_percent": row[2],
                }
                for i, row in enumerate(variants)
            ]
            
        finally:
            conn.close()

    def _empty_dataframe(self) -> pd.DataFrame:
        """Return empty DataFrame with correct columns."""
        return pd.DataFrame(columns=[
            "case:concept:name",
            "concept:name", 
            "time:timestamp",
            "org:resource",
        ])


# Singleton instance
event_log_loader = EventLogLoader()
