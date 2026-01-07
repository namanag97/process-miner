"""EventLog Loader Service - Parquet-First DataFrame Loading.

Uses DuckDB to query S3 Parquet files directly and return pandas DataFrames
formatted for PM4py.

Data Flow:
  - Events stored ONLY in S3 Parquet (not PostgreSQL)
  - Metadata (parquet_s3_key) stored in PostgreSQL datasets table
  - DuckDB reads Parquet from S3 → Arrow → DataFrame → PM4Py

This eliminates the dual-write anti-pattern and establishes clear data ownership.
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
    Parquet-First event log loading for PM4py.

    Reads events from Parquet files (the authoritative source) via DuckDB.
    Supports both:
    - S3/MinIO: For production/staging
    - Local filesystem: For MVP/local development (storage_type="local")
    
    Metadata (parquet_s3_key) is fetched from PostgreSQL datasets table.
    """

    def __init__(self):
        # Check storage configuration
        self._storage_type = getattr(settings, "storage_type", "s3")
        self._is_local = self._storage_type == "local"
        
        if self._is_local:
            # Local file storage for MVP
            from pathlib import Path
            self._local_base_path = Path("./data/storage/pm-cache-dev")
            logger.info("loader_using_local_storage", base_path=str(self._local_base_path))
        else:
            # S3/MinIO configuration
            self._s3_endpoint = getattr(settings, "S3_ENDPOINT", None) or getattr(settings, "s3_endpoint_url", None)
            self._s3_region = getattr(settings, "AWS_REGION", None) or getattr(settings, "s3_region", "us-east-1")
            self._s3_access_key = getattr(settings, "AWS_ACCESS_KEY_ID", None) or getattr(settings, "s3_access_key_id", None)
            self._s3_secret_key = getattr(settings, "AWS_SECRET_ACCESS_KEY", None) or getattr(settings, "s3_secret_access_key", None)
            self._s3_bucket = getattr(settings, "CACHE_BUCKET", None) or "pm-cache-dev"

        # Legacy: Keep SQLite path for backwards compatibility during migration
        db_url = settings.database_url
        if "sqlite" in db_url:
            self._sqlite_path = db_url.split("///")[-1]
        else:
            self._sqlite_path = None

    def _get_connection(self, for_parquet: bool = False):
        """Get DuckDB connection configured for Parquet reading."""
        duckdb = _get_duckdb()
        conn = duckdb.connect(":memory:")

        if for_parquet and not self._is_local:
            # Configure for S3/MinIO Parquet reading
            conn.execute("INSTALL httpfs; LOAD httpfs;")
            if self._s3_endpoint:
                # Extract hostname from endpoint URL
                endpoint = self._s3_endpoint.replace("http://", "").replace("https://", "")
                conn.execute(f"SET s3_endpoint='{endpoint}';")
                conn.execute("SET s3_url_style='path';")
                conn.execute("SET s3_use_ssl=false;")
            if self._s3_region:
                conn.execute(f"SET s3_region='{self._s3_region}';")
            if self._s3_access_key and self._s3_secret_key:
                conn.execute(f"SET s3_access_key_id='{self._s3_access_key}';")
                conn.execute(f"SET s3_secret_access_key='{self._s3_secret_key}';")
        elif self._sqlite_path:
            # Legacy: Attach SQLite for backwards compatibility
            conn.execute(f"ATTACH '{self._sqlite_path}' AS db (TYPE SQLITE)")

        return conn

    def _get_parquet_path(self, dataset_id: str) -> str | None:
        """Get Parquet path from dataset metadata."""
        # Import here to avoid circular imports
        from sqlalchemy import select
        from src.features.process_mining.models import Dataset
        from src.shared.database import sync_session_maker

        with sync_session_maker() as session:
            result = session.execute(
                select(Dataset.parquet_s3_key).where(Dataset.id == dataset_id)
            )
            row = result.fetchone()
            return row[0] if row else None

    def _build_parquet_url(self, parquet_key: str) -> str:
        """Build Parquet URL for DuckDB to read."""
        if self._is_local:
            # Local filesystem - return absolute path
            from pathlib import Path
            local_path = self._local_base_path / parquet_key
            return str(local_path.absolute())
        else:
            # S3/MinIO
            return f"s3://{self._s3_bucket}/{parquet_key}"

    def load_as_dataframe(
        self,
        dataset_id: str,
        include_attributes: bool = False,
        max_events: int = 500000,
    ) -> pd.DataFrame:
        """
        Load dataset from S3 Parquet as pandas DataFrame via DuckDB.

        This is the Parquet-First approach: reads directly from S3, no PostgreSQL events.

        Args:
            dataset_id: UUID of the dataset
            include_attributes: Whether to parse JSON attributes
            max_events: Maximum events to load (default 500K, set to 0 for no limit)
        """
        logger.info("dataset_loader_started", dataset_id=dataset_id, max_events=max_events)

        # Get Parquet path from metadata
        parquet_key = self._get_parquet_path(dataset_id)
        if not parquet_key:
            logger.warning("dataset_loader_no_parquet", dataset_id=dataset_id)
            # Fallback to legacy PostgreSQL loading during migration
            return self._load_from_sqlite_legacy(dataset_id, max_events)

        conn = self._get_connection(for_parquet=True)

        try:
            parquet_url = self._build_parquet_url(parquet_key)
            limit_clause = f"LIMIT {max_events}" if max_events > 0 else ""

            # Query Parquet directly via DuckDB
            query = f"""
                SELECT
                    case_id AS "case:concept:name",
                    activity AS "concept:name",
                    timestamp AS "time:timestamp",
                    resource AS "org:resource"
                FROM read_parquet('{parquet_url}')
                ORDER BY case_id, timestamp
                {limit_clause}
            """

            # Execute and get Arrow table (zero-copy)
            import pyarrow as pa
            arrow_result = conn.execute(query).arrow()

            if isinstance(arrow_result, pa.RecordBatchReader):
                arrow_table = arrow_result.read_all()
            else:
                arrow_table = arrow_result

            df = arrow_table.to_pandas()

            if df.empty:
                logger.warning("dataset_loader_empty", dataset_id=dataset_id)
                return self._empty_dataframe()

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
                source="parquet",
            )

            return df

        except Exception as e:
            logger.error(
                "dataset_loader_parquet_failed",
                dataset_id=dataset_id,
                parquet_key=parquet_key,
                error=str(e),
            )
            # Fallback to legacy loading during migration
            logger.info("dataset_loader_fallback_to_sqlite", dataset_id=dataset_id)
            return self._load_from_sqlite_legacy(dataset_id, max_events)
        finally:
            conn.close()

    def _load_from_sqlite_legacy(self, dataset_id: str, max_events: int) -> pd.DataFrame:
        """Legacy loader for datasets still in PostgreSQL (migration fallback)."""
        if not self._sqlite_path:
            logger.warning("dataset_loader_no_sqlite", dataset_id=dataset_id)
            return self._empty_dataframe()

        conn = self._get_connection(for_parquet=False)

        try:
            limit_clause = f"LIMIT {max_events}" if max_events > 0 else ""

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

            import pyarrow as pa
            arrow_result = conn.execute(query, [dataset_id]).arrow()

            if isinstance(arrow_result, pa.RecordBatchReader):
                arrow_table = arrow_result.read_all()
            else:
                arrow_table = arrow_result

            df = arrow_table.to_pandas()

            if df.empty:
                return self._empty_dataframe()

            if "time:timestamp" in df.columns:
                df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

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
                source="sqlite_legacy",
            )

            return df

        finally:
            conn.close()

    def load_as_pm4py_log(self, dataset_id: str) -> PM4PyLog:
        """
        Load dataset and convert to PM4Py EventLog object.

        Args:
            dataset_id: UUID of the dataset

        Returns:
            PM4Py EventLog object
        """
        df = self.load_as_dataframe(dataset_id)

        if df.empty:
            return PM4PyLog()

        return pm4py.convert_to_event_log(df)

    def load_statistics(self, dataset_id: str) -> dict[str, Any]:
        """
        Load dataset statistics from S3 Parquet.

        Args:
            dataset_id: UUID of the dataset

        Returns:
            Dictionary with statistics
        """
        parquet_key = self._get_parquet_path(dataset_id)
        if not parquet_key:
            return self._load_statistics_legacy(dataset_id)

        conn = self._get_connection(for_parquet=True)

        try:
            parquet_url = self._build_parquet_url(parquet_key)

            stats = conn.execute(
                f"""
                SELECT
                    COUNT(*) as total_events,
                    COUNT(DISTINCT case_id) as total_cases,
                    COUNT(DISTINCT activity) as total_activities,
                    COUNT(DISTINCT resource) FILTER (WHERE resource IS NOT NULL) as total_resources,
                    MIN(timestamp) as start_time,
                    MAX(timestamp) as end_time,
                    LIST(DISTINCT activity ORDER BY activity) as activities
                FROM read_parquet('{parquet_url}')
            """
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

        except Exception as e:
            logger.warning("stats_parquet_failed", dataset_id=dataset_id, error=str(e))
            return self._load_statistics_legacy(dataset_id)
        finally:
            conn.close()

    def _load_statistics_legacy(self, dataset_id: str) -> dict[str, Any]:
        """Legacy statistics loader for SQLite."""
        if not self._sqlite_path:
            return {"total_events": 0, "total_cases": 0, "total_activities": 0}

        conn = self._get_connection(for_parquet=False)

        try:
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
        """Get start and end activities with frequencies."""
        parquet_key = self._get_parquet_path(dataset_id)
        if not parquet_key:
            return self._load_start_end_legacy(dataset_id)

        conn = self._get_connection(for_parquet=True)

        try:
            parquet_url = self._build_parquet_url(parquet_key)

            start_result = conn.execute(
                f"""
                WITH first_events AS (
                    SELECT
                        case_id,
                        activity,
                        ROW_NUMBER() OVER (PARTITION BY case_id ORDER BY timestamp) as rn
                    FROM read_parquet('{parquet_url}')
                )
                SELECT activity, COUNT(*) as freq
                FROM first_events
                WHERE rn = 1
                GROUP BY activity
                ORDER BY freq DESC
            """
            ).fetchall()

            end_result = conn.execute(
                f"""
                WITH last_events AS (
                    SELECT
                        case_id,
                        activity,
                        ROW_NUMBER() OVER (PARTITION BY case_id ORDER BY timestamp DESC) as rn
                    FROM read_parquet('{parquet_url}')
                )
                SELECT activity, COUNT(*) as freq
                FROM last_events
                WHERE rn = 1
                GROUP BY activity
                ORDER BY freq DESC
            """
            ).fetchall()

            start_activities = {row[0]: row[1] for row in start_result}
            end_activities = {row[0]: row[1] for row in end_result}

            return start_activities, end_activities

        except Exception as e:
            logger.warning("start_end_parquet_failed", dataset_id=dataset_id, error=str(e))
            return self._load_start_end_legacy(dataset_id)
        finally:
            conn.close()

    def _load_start_end_legacy(self, dataset_id: str) -> tuple[dict[str, int], dict[str, int]]:
        """Legacy start/end loader for SQLite."""
        if not self._sqlite_path:
            return {}, {}

        conn = self._get_connection(for_parquet=False)

        try:
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

            return (
                {row[0]: row[1] for row in start_result},
                {row[0]: row[1] for row in end_result},
            )

        finally:
            conn.close()

    def load_dfg(self, dataset_id: str) -> tuple[dict, dict[str, int], dict[str, int]]:
        """
        Compute Directly-Follows Graph from S3 Parquet.

        Returns:
            Tuple of (dfg, start_activities, end_activities)
        """
        parquet_key = self._get_parquet_path(dataset_id)
        if not parquet_key:
            return self._load_dfg_legacy(dataset_id)

        conn = self._get_connection(for_parquet=True)

        try:
            parquet_url = self._build_parquet_url(parquet_key)

            dfg_result = conn.execute(
                f"""
                WITH ordered_events AS (
                    SELECT
                        case_id,
                        activity,
                        timestamp,
                        LEAD(activity) OVER (
                            PARTITION BY case_id
                            ORDER BY timestamp
                        ) as next_activity
                    FROM read_parquet('{parquet_url}')
                )
                SELECT activity, next_activity, COUNT(*) as freq
                FROM ordered_events
                WHERE next_activity IS NOT NULL
                GROUP BY activity, next_activity
                ORDER BY freq DESC
            """
            ).fetchall()

            dfg = {(row[0], row[1]): row[2] for row in dfg_result}
            start_activities, end_activities = self.load_start_end_activities(dataset_id)

            return dfg, start_activities, end_activities

        except Exception as e:
            logger.warning("dfg_parquet_failed", dataset_id=dataset_id, error=str(e))
            return self._load_dfg_legacy(dataset_id)
        finally:
            conn.close()

    def _load_dfg_legacy(self, dataset_id: str) -> tuple[dict, dict[str, int], dict[str, int]]:
        """Legacy DFG loader for SQLite."""
        if not self._sqlite_path:
            return {}, {}, {}

        conn = self._get_connection(for_parquet=False)

        try:
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
        Get process variants from S3 Parquet.

        Args:
            dataset_id: UUID of the dataset
            top_k: Limit to top K variants (optional)

        Returns:
            List of variant dictionaries with trace, count, and percentage
        """
        parquet_key = self._get_parquet_path(dataset_id)
        if not parquet_key:
            return self._load_variants_legacy(dataset_id, top_k)

        conn = self._get_connection(for_parquet=True)

        try:
            parquet_url = self._build_parquet_url(parquet_key)

            limit_clause = ""
            if top_k is not None:
                validated_limit = int(top_k)
                if validated_limit <= 0:
                    raise ValueError(f"top_k must be positive, got {validated_limit}")
                limit_clause = f"LIMIT {validated_limit}"

            query = f"""
                WITH case_variants AS (
                    SELECT
                        case_id,
                        STRING_AGG(activity, ' -> ' ORDER BY timestamp) as variant_key
                    FROM read_parquet('{parquet_url}')
                    GROUP BY case_id
                ),
                variants_agg AS (
                    SELECT
                        variant_key,
                        COUNT(*) as case_count
                    FROM case_variants
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
            variants = conn.execute(query).fetchall()

            result = []
            for row in variants:
                v_key = row[0]
                if not v_key:
                    continue

                result.append(
                    {
                        "variant_key": v_key,
                        "activity_trace": v_key,
                        "activities": v_key.split(" -> "),
                        "case_count": row[1],
                        "frequency_percent": row[2],
                    }
                )

            return result

        except Exception as e:
            logger.warning("variants_parquet_failed", dataset_id=dataset_id, error=str(e))
            return self._load_variants_legacy(dataset_id, top_k)
        finally:
            conn.close()

    def _load_variants_legacy(self, dataset_id: str, top_k: int | None) -> list[dict[str, Any]]:
        """Legacy variants loader for SQLite."""
        if not self._sqlite_path:
            return []

        conn = self._get_connection(for_parquet=False)

        try:
            limit_clause = ""
            if top_k is not None:
                validated_limit = int(top_k)
                if validated_limit <= 0:
                    raise ValueError(f"top_k must be positive, got {validated_limit}")
                limit_clause = f"LIMIT {validated_limit}"

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
            for row in variants:
                v_key = row[0]
                if not v_key:
                    continue

                result.append(
                    {
                        "variant_key": v_key,
                        "activity_trace": v_key,
                        "activities": v_key.split(" -> "),
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
