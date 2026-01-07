"""EventLog Loader Service - High-Performance DataFrame Loading.

Uses DuckDB to query SQLite database directly and return pandas DataFrames
formatted for PM4py, avoiding the 4x data copying of ORM iteration.

Performance improvement:
  - Current: SQL → Dict → ORM Object → PM4Py Trace (4 copies)
  - New: SQL → Arrow → DataFrame → PM4Py (1-2 copies, 10x faster)
"""

from typing import Any

import pandas as pd
import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog

from src.platform.core.config import get_settings
from src.platform.core.logging_config import get_logger

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
                "DuckDB is required for high-performance loading. Install with: pip install duckdb"
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
        """Get DuckDB connection with SQLite attached."""
        duckdb = _get_duckdb()
        conn = duckdb.connect(":memory:")

        if self._sqlite_path:
            # Attach SQLite database as 'db'
            conn.execute(f"ATTACH '{self._sqlite_path}' AS db (TYPE SQLITE)")
        else:
            pass

        return conn

    def load_as_dataframe(
        self,
        dataset_id: str,
        include_attributes: bool = False,
        max_events: int = 500000,  # BUG-050 FIX: Default limit to prevent OOM
    ) -> pd.DataFrame:
        """
        Load dataset directly as pandas DataFrame via DuckDB.

        Note: This is synchronous because DuckDB operations are sync.

        Args:
            dataset_id: UUID of the dataset
            include_attributes: Whether to parse JSON attributes
            max_events: Maximum events to load (default 500K, set to 0 for no limit)
        """
        logger.info("dataset_loader_started", dataset_id=dataset_id, max_events=max_events)

        conn = self._get_connection()

        try:
            # BUG-050 FIX: Add LIMIT clause when max_events > 0
            limit_clause = f"LIMIT {max_events}" if max_events > 0 else ""

            # Query SQLite through DuckDB
            # BUG-032 FIX: Use parameterized query to prevent SQL injection
            query = f"""
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
                {limit_clause}
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

            # BUG-050: Warn if data was truncated
            if max_events > 0 and len(df) >= max_events:
                logger.warning(
                    "dataset_loader_truncated",
                    dataset_id=dataset_id,
                    loaded_events=len(df),
                    limit=max_events,
                )

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
            stats = conn.execute(
                """
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
            """,
                [dataset_id],
            ).fetchone()

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
            start_result = conn.execute(
                """
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
            """,
                [dataset_id],
            ).fetchall()

            # End activities - BUG-032 FIX: parameterized query
            end_result = conn.execute(
                """
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
            """,
                [dataset_id],
            ).fetchall()

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
            # Check if events exist first
            try:
                _ = conn.execute("SELECT COUNT(*) FROM db.process_events").fetchone()[0]
                _ = conn.execute(
                    "SELECT COUNT(*) FROM db.process_cases WHERE dataset_id=?", [dataset_id]
                ).fetchone()[0]
            except Exception:
                pass
            # DFG edges - BUG-032 FIX: parameterized query
            dfg_result = conn.execute(
                """
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
            """,
                [dataset_id],
            ).fetchall()

            dfg = {(row[0], row[1]): row[2] for row in dfg_result}

            # Get start/end activities
            start_activities, end_activities = self.load_start_end_activities(dataset_id)

            return dfg, start_activities, end_activities

        finally:
            conn.close()

    def load_variants(
        self,
        dataset_id: str,
        top_k: int | None = None,
    ) -> list[dict[str, Any]]:
        """
        Get process variants using optimized SQL aggregation on variant_key.

        Now uses the indexed `variant_key` column from `process_cases` instead of
        slowly re-aggregating thousands of events per case.

        Note: This is synchronous because DuckDB operations are sync.

        Args:
            dataset_id: UUID of the dataset
            top_k: Limit to top K variants (optional)

        Returns:
            List of variant dictionaries with trace, count, and percentage
        """
        conn = self._get_connection()

        try:
            # BUG-032 FIX: parameterized query
            # BUG-070 FIX: Validate top_k is a positive integer before using in query
            limit_clause = ""
            if top_k is not None:
                validated_limit = int(top_k)
                if validated_limit <= 0:
                    raise ValueError(f"top_k must be positive, got {validated_limit}")
                limit_clause = f"LIMIT {validated_limit}"

            # OPTIMIZED: Group by pre-computed variant_key (O(Cases)) instead of aggregating events (O(Events))
            query = f"""
                WITH variants_agg AS (
                    SELECT
                        variant_key,
                        COUNT(*) as case_count
                    FROM db.process_cases
                    WHERE dataset_id = ?
                      AND variant_key IS NOT NULL
                    GROUP BY variant_key
                    ORDER BY case_count DESC
                    {limit_clause}
                )
                SELECT
                    variant_key,
                    case_count,
                    ROUND(case_count * 100.0 / SUM(case_count) OVER (), 2) as frequency_percent
                FROM variants_agg
                ORDER BY case_count DESC
            """
            variants = conn.execute(query, [dataset_id]).fetchall()

            result = []
            for _i, row in enumerate(variants):
                # Parse variant key back to activity list if needed
                # variant_key format: "Activity A -> Activity B"
                v_key = row[0]
                if not v_key:
                    continue

                result.append(
                    {
                        "variant_key": v_key,  # Dictionary key (hash)
                        "activity_trace": v_key,  # Display string
                        "activities": v_key.split(" -> "),  # List for FE
                        "case_count": row[1],
                        "frequency_percent": row[2],
                    }
                )

            return result

        finally:
            conn.close()

    def _empty_dataframe(self) -> pd.DataFrame:
        """Return empty DataFrame with correct columns."""
        return pd.DataFrame(
            columns=[
                "case:concept:name",
                "concept:name",
                "time:timestamp",
                "org:resource",
            ]
        )


# Singleton instance
event_log_loader = EventLogLoader()
