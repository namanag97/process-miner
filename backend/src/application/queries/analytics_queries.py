"""Analytics Query Handlers for CQRS.

Query handlers for analytics read operations.
All handlers use DuckDB to read from Parquet files - never PostgreSQL.

Usage:
    result = await query_bus.execute(
        GetBottlenecksQuery(dataset_id="...", limit=10)
    )
"""

from dataclasses import dataclass
from typing import Any

import duckdb
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.queries import BaseQuery, QueryHandler

# =============================================================================
# Queries
# =============================================================================


@dataclass
class GetBottlenecksQuery(BaseQuery):
    """Get process bottlenecks based on waiting times."""

    dataset_id: str
    limit: int = 10

    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("Dataset ID is required")


@dataclass
class GetCycleTimeQuery(BaseQuery):
    """Get cycle time (case duration) statistics."""

    dataset_id: str

    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("Dataset ID is required")


@dataclass
class GetReworkQuery(BaseQuery):
    """Get rework analysis - repeated activities."""

    dataset_id: str

    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("Dataset ID is required")


@dataclass
class GetVariantsQuery(BaseQuery):
    """Get process variants (unique activity sequences)."""

    dataset_id: str
    min_frequency: int = 1

    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("Dataset ID is required")


@dataclass
class GetThroughputQuery(BaseQuery):
    """Get throughput statistics."""

    dataset_id: str

    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("Dataset ID is required")


@dataclass
class GetDFGQuery(BaseQuery):
    """Get Directly-Follows Graph data."""

    dataset_id: str

    def validate(self) -> None:
        if not self.dataset_id:
            raise ValueError("Dataset ID is required")


# =============================================================================
# Result Types
# =============================================================================


@dataclass
class BottleneckResult:
    """Single bottleneck item."""

    activity: str
    avg_wait_time_seconds: float
    median_wait_time_seconds: float
    max_wait_time_seconds: float
    occurrence_count: int


@dataclass
class BottlenecksResult:
    """Bottleneck analysis result."""

    bottlenecks: list[BottleneckResult]
    total_activities: int


@dataclass
class CycleTimeResult:
    """Cycle time statistics."""

    mean_seconds: float
    median_seconds: float
    min_seconds: float
    max_seconds: float
    std_seconds: float
    total_cases: int


@dataclass
class ReworkItem:
    """Single rework pattern."""

    activity: str
    repeat_count: int
    case_count: int
    percentage: float


@dataclass
class ReworkResult:
    """Rework analysis result."""

    rework_patterns: list[ReworkItem]
    total_cases_with_rework: int
    rework_rate: float


@dataclass
class VariantItem:
    """Single process variant."""

    variant_id: int
    activities: list[str]
    case_count: int
    percentage: float


@dataclass
class VariantsResult:
    """Variants analysis result."""

    variants: list[VariantItem]
    total_variants: int
    total_cases: int


@dataclass
class ThroughputResult:
    """Throughput statistics result."""

    total_cases: int
    completed_cases: int
    cases_per_day: float
    cases_per_week: float
    cases_per_month: float
    time_range_days: float


# =============================================================================
# Query Handlers
# =============================================================================


class AnalyticsQueryHandlerBase(QueryHandler):
    """Base class for analytics query handlers.

    Provides common functionality for Parquet/DuckDB queries.
    Uses isolated DuckDB connections for thread-safe concurrent execution.
    """

    def __init__(
        self,
        duckdb_manager: Any = None,  # DuckDBManager for isolated connections
        duckdb_conn: duckdb.DuckDBPyConnection | None = None,  # Legacy, deprecated
        db: AsyncSession | None = None,
        cache: Any | None = None,
    ):
        # Support both new (duckdb_manager) and legacy (duckdb_conn) patterns
        super().__init__(duckdb_conn=duckdb_conn, cache=cache)
        self.db = db  # For metadata lookups only
        self._duckdb_manager = duckdb_manager

    def get_isolated_connection(self):
        """Get an isolated DuckDB connection for thread-safe query execution.

        Returns a context manager that yields a fresh connection.
        """
        if self._duckdb_manager is not None:
            return self._duckdb_manager.get_isolated_connection()
        # Fallback for legacy code - use shared connection (not thread-safe)
        from contextlib import contextmanager
        @contextmanager
        def legacy_conn():
            yield self.duckdb
        return legacy_conn()

    async def get_parquet_path(self, dataset_id: str) -> str:
        """Get Parquet file path for a dataset.

        Looks up in PostgreSQL metadata, but reads data from Parquet.
        """
        if not self.db:
            raise ValueError("Database session required for metadata lookup")

        from src.features.process_mining.models import Dataset
        from src.infra.core.config import get_settings

        result = await self.db.execute(
            select(Dataset.parquet_s3_key).where(Dataset.id == dataset_id)
        )
        parquet_key = result.scalar_one_or_none()

        if not parquet_key:
            raise ValueError(f"Dataset not found or no Parquet file: {dataset_id}")

        settings = get_settings()

        # Resolve to full path (local or S3)
        if settings.storage_type == "local":
            return f"./data/storage/{settings.s3_bucket_cache}/{parquet_key}"
        # S3 path
        endpoint = settings.s3_endpoint_url or "s3://"
        return f"{endpoint}/{settings.s3_bucket_cache}/{parquet_key}"


class GetBottlenecksHandler(AnalyticsQueryHandlerBase):
    """Handler for GetBottlenecksQuery.

    Queries Parquet via DuckDB to find activities with high wait times.
    """

    async def handle(self, query: GetBottlenecksQuery) -> BottlenecksResult:
        # Check cache first
        cached = await self.get_cached(query)
        if cached:
            return cached

        parquet_path = await self.get_parquet_path(query.dataset_id)

        # Use isolated connection for thread-safe concurrent execution
        with self.get_isolated_connection() as conn:
            # Single optimized query - reads Parquet once, computes both bottlenecks and totals
            sql = f"""
                WITH raw_data AS (
                    SELECT
                        "case:concept:name" as case_id,
                        "concept:name" as activity,
                        "time:timestamp" as ts
                    FROM read_parquet('{parquet_path}')
                ),
                events_with_lag AS (
                    SELECT
                        case_id,
                        activity,
                        ts,
                        LAG(ts) OVER (PARTITION BY case_id ORDER BY ts) as prev_ts
                    FROM raw_data
                ),
                wait_times AS (
                    SELECT
                        activity,
                        EXTRACT(EPOCH FROM (ts - prev_ts)) as wait_seconds
                    FROM events_with_lag
                    WHERE prev_ts IS NOT NULL
                ),
                bottleneck_stats AS (
                    SELECT
                        activity,
                        AVG(wait_seconds) as avg_wait,
                        MEDIAN(wait_seconds) as median_wait,
                        MAX(wait_seconds) as max_wait,
                        COUNT(*) as occurrences
                    FROM wait_times
                    GROUP BY activity
                    ORDER BY avg_wait DESC
                    LIMIT {query.limit}
                ),
                total_activities AS (
                    SELECT COUNT(DISTINCT activity) as cnt FROM raw_data
                )
                SELECT
                    b.activity, b.avg_wait, b.median_wait, b.max_wait, b.occurrences,
                    t.cnt as total_activities
                FROM bottleneck_stats b, total_activities t
            """

            rows = conn.execute(sql).fetchall()

        total_activities = rows[0][5] if rows else 0
        bottlenecks = [
            BottleneckResult(
                activity=row[0],
                avg_wait_time_seconds=row[1] or 0,
                median_wait_time_seconds=row[2] or 0,
                max_wait_time_seconds=row[3] or 0,
                occurrence_count=row[4],
            )
            for row in rows
        ]

        response = BottlenecksResult(
            bottlenecks=bottlenecks,
            total_activities=total_activities or 0,
        )

        # Cache result
        await self.set_cached(query, response, ttl=3600)

        return response


class GetCycleTimeHandler(AnalyticsQueryHandlerBase):
    """Handler for GetCycleTimeQuery.

    Computes case duration statistics from Parquet.
    """

    async def handle(self, query: GetCycleTimeQuery) -> CycleTimeResult:
        cached = await self.get_cached(query)
        if cached:
            return cached

        parquet_path = await self.get_parquet_path(query.dataset_id)

        # Use isolated connection for thread-safe concurrent execution
        with self.get_isolated_connection() as conn:
            sql = f"""
                WITH case_times AS (
                    SELECT
                        "case:concept:name" as case_id,
                        MIN("time:timestamp") as start_time,
                        MAX("time:timestamp") as end_time
                    FROM read_parquet('{parquet_path}')
                    GROUP BY "case:concept:name"
                ),
                durations AS (
                    SELECT
                        EXTRACT(EPOCH FROM (end_time - start_time)) as duration_seconds
                    FROM case_times
                )
                SELECT
                    AVG(duration_seconds) as mean_dur,
                    MEDIAN(duration_seconds) as median_dur,
                    MIN(duration_seconds) as min_dur,
                    MAX(duration_seconds) as max_dur,
                    STDDEV(duration_seconds) as std_dur,
                    COUNT(*) as total_cases
                FROM durations
            """

            row = conn.execute(sql).fetchone()

        if row:
            result = CycleTimeResult(
                mean_seconds=row[0] or 0,
                median_seconds=row[1] or 0,
                min_seconds=row[2] or 0,
                max_seconds=row[3] or 0,
                std_seconds=row[4] or 0,
                total_cases=row[5] or 0,
            )
        else:
            result = CycleTimeResult(
                mean_seconds=0,
                median_seconds=0,
                min_seconds=0,
                max_seconds=0,
                std_seconds=0,
                total_cases=0,
            )

        await self.set_cached(query, result, ttl=3600)
        return result


class GetReworkHandler(AnalyticsQueryHandlerBase):
    """Handler for GetReworkQuery.

    Identifies repeated activities within cases.
    """

    async def handle(self, query: GetReworkQuery) -> ReworkResult:
        cached = await self.get_cached(query)
        if cached:
            return cached

        parquet_path = await self.get_parquet_path(query.dataset_id)

        # Use isolated connection for thread-safe concurrent execution
        with self.get_isolated_connection() as conn:
            # Single optimized query - reads Parquet once, computes all rework stats
            sql = f"""
                WITH raw_data AS (
                    SELECT
                        "case:concept:name" as case_id,
                        "concept:name" as activity
                    FROM read_parquet('{parquet_path}')
                ),
                total_cases AS (
                    SELECT COUNT(DISTINCT case_id) as cnt FROM raw_data
                ),
                activity_counts AS (
                    SELECT
                        case_id,
                        activity,
                        COUNT(*) as repeat_count
                    FROM raw_data
                    GROUP BY case_id, activity
                    HAVING COUNT(*) > 1
                ),
                rework_stats AS (
                    SELECT
                        COUNT(DISTINCT case_id) as cases_with_rework
                    FROM activity_counts
                ),
                activity_rework AS (
                    SELECT
                        activity,
                        SUM(repeat_count) as total_repeats,
                        COUNT(DISTINCT case_id) as case_count
                    FROM activity_counts
                    GROUP BY activity
                    ORDER BY total_repeats DESC
                    LIMIT 20
                )
                SELECT
                    ar.activity,
                    ar.total_repeats,
                    ar.case_count,
                    ar.case_count * 100.0 / tc.cnt as percentage,
                    rs.cases_with_rework,
                    tc.cnt as total_cases
                FROM activity_rework ar, total_cases tc, rework_stats rs
            """

            rows = conn.execute(sql).fetchall()

        if rows:
            cases_with_rework = rows[0][4]
            total = rows[0][5]
            patterns = [
                ReworkItem(
                    activity=row[0],
                    repeat_count=row[1],
                    case_count=row[2],
                    percentage=row[3] or 0,
                )
                for row in rows
            ]
        else:
            cases_with_rework = 0
            total = 1
            patterns = []

        result = ReworkResult(
            rework_patterns=patterns,
            total_cases_with_rework=cases_with_rework,
            rework_rate=cases_with_rework / total if total > 0 else 0,
        )

        await self.set_cached(query, result, ttl=3600)
        return result


class GetThroughputHandler(AnalyticsQueryHandlerBase):
    """Handler for GetThroughputQuery.

    Computes throughput statistics from Parquet.
    """

    async def handle(self, query: GetThroughputQuery) -> ThroughputResult:
        cached = await self.get_cached(query)
        if cached:
            return cached

        parquet_path = await self.get_parquet_path(query.dataset_id)

        # Use isolated connection for thread-safe concurrent execution
        with self.get_isolated_connection() as conn:
            sql = f"""
                WITH case_times AS (
                    SELECT
                        "case:concept:name" as case_id,
                        MIN("time:timestamp") as start_time,
                        MAX("time:timestamp") as end_time
                    FROM read_parquet('{parquet_path}')
                    GROUP BY "case:concept:name"
                ),
                stats AS (
                    SELECT
                        COUNT(*) as total_cases,
                        MIN(start_time) as earliest_start,
                        MAX(end_time) as latest_end
                    FROM case_times
                )
                SELECT
                    total_cases,
                    total_cases as completed_cases,
                    EXTRACT(DAY FROM (latest_end - earliest_start)) as time_range_days
                FROM stats
            """

            row = conn.execute(sql).fetchone()

        if row:
            total_cases = row[0] or 0
            time_range_days = row[2] or 1
            # Avoid division by zero
            if time_range_days < 1:
                time_range_days = 1

            result = ThroughputResult(
                total_cases=total_cases,
                completed_cases=total_cases,  # Assuming all cases are completed
                cases_per_day=total_cases / time_range_days,
                cases_per_week=total_cases / time_range_days * 7,
                cases_per_month=total_cases / time_range_days * 30,
                time_range_days=time_range_days,
            )
        else:
            result = ThroughputResult(
                total_cases=0,
                completed_cases=0,
                cases_per_day=0,
                cases_per_week=0,
                cases_per_month=0,
                time_range_days=0,
            )

        await self.set_cached(query, result, ttl=3600)
        return result


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BottlenecksResult",
    "CycleTimeResult",
    "GetBottlenecksHandler",
    "GetBottlenecksQuery",
    "GetCycleTimeHandler",
    "GetCycleTimeQuery",
    "GetDFGQuery",
    "GetReworkHandler",
    "GetReworkQuery",
    "GetThroughputHandler",
    "GetThroughputQuery",
    "GetVariantsQuery",
    "ReworkResult",
    "ThroughputResult",
]
