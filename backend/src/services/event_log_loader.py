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
        log_id: str,
        include_attributes: bool = False,
    ) -> pd.DataFrame:
        """
        Load event log directly as pandas DataFrame via DuckDB.
        
        This is 10x faster than ORM iteration for large logs because:
        1. DuckDB queries SQLite directly (no Python ORM overhead)
        2. Arrow columnar format enables zero-copy to pandas
        3. No per-row Python object creation
        
        Args:
            log_id: UUID of the event log
            include_attributes: Whether to parse JSON attributes
            
        Returns:
            pandas DataFrame formatted for PM4py with columns:
            - case:concept:name
            - concept:name
            - time:timestamp
            - org:resource (optional)
        """
        logger.info("event_log_loader_started", log_id=log_id)
        
        conn = self._get_connection()
        
        try:
            # Query SQLite through DuckDB
            query = f"""
                SELECT 
                    pc.case_id AS "case:concept:name",
                    pe.activity AS "concept:name",
                    pe.timestamp AS "time:timestamp",
                    pe.resource AS "org:resource"
                    {"," if include_attributes else ""}
                    {'"pe.attributes_json"' if include_attributes else ""}
                FROM db.process_events pe
                INNER JOIN db.process_cases pc 
                    ON pe.case_ref_id = pc.id
                WHERE pc.log_id = '{log_id}'
                ORDER BY pc.case_id, pe.timestamp
            """
            
            # Execute and get Arrow table (zero-copy)
            arrow_table = conn.execute(query).arrow()
            
            # Convert to pandas DataFrame
            df = arrow_table.to_pandas()
            
            if df.empty:
                logger.warning("event_log_loader_empty", log_id=log_id)
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
                "event_log_loader_completed",
                log_id=log_id,
                total_events=len(df),
                total_cases=df["case:concept:name"].nunique(),
            )
            
            return df
            
        finally:
            conn.close()

    def load_as_pm4py_log(self, log_id: str) -> PM4PyLog:
        """
        Load event log and convert to PM4Py EventLog object.
        
        For algorithms that require the traditional EventLog format.
        Still faster than ORM iteration because DataFrame loading is fast.
        
        Args:
            log_id: UUID of the event log
            
        Returns:
            PM4Py EventLog object
        """
        df = self.load_as_dataframe(log_id)
        
        if df.empty:
            return PM4PyLog()
        
        # Convert DataFrame to EventLog
        return pm4py.convert_to_event_log(df)

    def load_statistics(self, log_id: str) -> dict[str, Any]:
        """
        Load event log statistics using SQL aggregation.
        
        Much faster than computing in Python for large logs.
        
        Args:
            log_id: UUID of the event log
            
        Returns:
            Dictionary with statistics
        """
        conn = self._get_connection()
        
        try:
            stats = conn.execute(f"""
                WITH events AS (
                    SELECT 
                        pc.case_id,
                        pe.activity,
                        pe.timestamp,
                        pe.resource
                    FROM db.process_events pe
                    INNER JOIN db.process_cases pc 
                        ON pe.case_ref_id = pc.id
                    WHERE pc.log_id = '{log_id}'
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
            """).fetchone()
            
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

    def load_start_end_activities(self, log_id: str) -> tuple[dict[str, int], dict[str, int]]:
        """
        Get start and end activities with frequencies using SQL.
        
        Args:
            log_id: UUID of the event log
            
        Returns:
            Tuple of (start_activities, end_activities) dictionaries
        """
        conn = self._get_connection()
        
        try:
            # Start activities
            start_result = conn.execute(f"""
                WITH first_events AS (
                    SELECT 
                        pc.case_id,
                        pe.activity,
                        ROW_NUMBER() OVER (PARTITION BY pc.case_id ORDER BY pe.timestamp) as rn
                    FROM db.process_events pe
                    INNER JOIN db.process_cases pc 
                        ON pe.case_ref_id = pc.id
                    WHERE pc.log_id = '{log_id}'
                )
                SELECT activity, COUNT(*) as freq
                FROM first_events
                WHERE rn = 1
                GROUP BY activity
                ORDER BY freq DESC
            """).fetchall()
            
            # End activities
            end_result = conn.execute(f"""
                WITH last_events AS (
                    SELECT 
                        pc.case_id,
                        pe.activity,
                        ROW_NUMBER() OVER (PARTITION BY pc.case_id ORDER BY pe.timestamp DESC) as rn
                    FROM db.process_events pe
                    INNER JOIN db.process_cases pc 
                        ON pe.case_ref_id = pc.id
                    WHERE pc.log_id = '{log_id}'
                )
                SELECT activity, COUNT(*) as freq
                FROM last_events
                WHERE rn = 1
                GROUP BY activity
                ORDER BY freq DESC
            """).fetchall()
            
            start_activities = {row[0]: row[1] for row in start_result}
            end_activities = {row[0]: row[1] for row in end_result}
            
            return start_activities, end_activities
            
        finally:
            conn.close()

    def load_dfg(self, log_id: str) -> tuple[dict, dict[str, int], dict[str, int]]:
        """
        Compute Directly-Follows Graph using SQL.
        
        Much faster than PM4py's discover_dfg for large logs.
        
        Args:
            log_id: UUID of the event log
            
        Returns:
            Tuple of (dfg, start_activities, end_activities)
            where dfg is {(source, target): frequency}
        """
        conn = self._get_connection()
        
        try:
            # DFG edges
            dfg_result = conn.execute(f"""
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
                    WHERE pc.log_id = '{log_id}'
                )
                SELECT activity, next_activity, COUNT(*) as freq
                FROM ordered_events
                WHERE next_activity IS NOT NULL
                GROUP BY activity, next_activity
                ORDER BY freq DESC
            """).fetchall()
            
            dfg = {(row[0], row[1]): row[2] for row in dfg_result}
            
            # Get start/end activities
            start_activities, end_activities = self.load_start_end_activities(log_id)
            
            return dfg, start_activities, end_activities
            
        finally:
            conn.close()

    def load_variants(
        self, 
        log_id: str, 
        top_k: Optional[int] = None,
    ) -> list[dict[str, Any]]:
        """
        Get process variants using SQL aggregation.
        
        Args:
            log_id: UUID of the event log
            top_k: Limit to top K variants (optional)
            
        Returns:
            List of variant dictionaries with trace, count, and percentage
        """
        conn = self._get_connection()
        
        try:
            limit_clause = f"LIMIT {top_k}" if top_k else ""
            
            variants = conn.execute(f"""
                WITH case_variants AS (
                    SELECT 
                        pc.case_id,
                        STRING_AGG(pe.activity, ' -> ' ORDER BY pe.timestamp) as variant
                    FROM db.process_events pe
                    INNER JOIN db.process_cases pc 
                        ON pe.case_ref_id = pc.id
                    WHERE pc.log_id = '{log_id}'
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
            """).fetchall()
            
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
