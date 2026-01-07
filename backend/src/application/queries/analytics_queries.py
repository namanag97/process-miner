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


# =============================================================================
# Query Handlers
# =============================================================================


class AnalyticsQueryHandlerBase(QueryHandler):
    """Base class for analytics query handlers.

    Provides common functionality for Parquet/DuckDB queries.
    """

    def __init__(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection | None = None,
        db: AsyncSession | None = None,
        cache: Any | None = None,
    ):
        super().__init__(duckdb_conn=duckdb_conn, cache=cache)
        self.db = db  # For metadata lookups only

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

        assert self.duckdb is not None, "DuckDB connection is required"
        parquet_path = await self.get_parquet_path(query.dataset_id)

        # DuckDB query - compute wait times between activities
        sql = f"""
            WITH events AS (
                SELECT
                    "case:concept:name" as case_id,
                    "concept:name" as activity,
                    "time:timestamp" as ts,
                    LAG("time:timestamp") OVER (
                        PARTITION BY "case:concept:name"
                        ORDER BY "time:timestamp"
                    ) as prev_ts
                FROM read_parquet('{parquet_path}')
            ),
            wait_times AS (
                SELECT
                    activity,
                    EXTRACT(EPOCH FROM (ts - prev_ts)) as wait_seconds
                FROM events
                WHERE prev_ts IS NOT NULL
            )
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
        """

        result = self.duckdb.execute(sql).fetchall()

        bottlenecks = [
            BottleneckResult(
                activity=row[0],
                avg_wait_time_seconds=row[1] or 0,
                median_wait_time_seconds=row[2] or 0,
                max_wait_time_seconds=row[3] or 0,
                occurrence_count=row[4],
            )
            for row in result
        ]

        # Get total activities
        total_sql = f"""
            SELECT COUNT(DISTINCT "concept:name")
            FROM read_parquet('{parquet_path}')
        """
        total_row = self.duckdb.execute(total_sql).fetchone()
        total = total_row[0] if total_row else 0

        response = BottlenecksResult(
            bottlenecks=bottlenecks,
            total_activities=total or 0,
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

        assert self.duckdb is not None, "DuckDB connection is required"
        parquet_path = await self.get_parquet_path(query.dataset_id)

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

        row = self.duckdb.execute(sql).fetchone()

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

        assert self.duckdb is not None, "DuckDB connection is required"
        parquet_path = await self.get_parquet_path(query.dataset_id)

        sql = f"""
            WITH activity_counts AS (
                SELECT
                    "case:concept:name" as case_id,
                    "concept:name" as activity,
                    COUNT(*) as repeat_count
                FROM read_parquet('{parquet_path}')
                GROUP BY "case:concept:name", "concept:name"
                HAVING COUNT(*) > 1
            ),
            total_cases AS (
                SELECT COUNT(DISTINCT "case:concept:name") as cnt
                FROM read_parquet('{parquet_path}')
            )
            SELECT
                a.activity,
                SUM(a.repeat_count) as total_repeats,
                COUNT(DISTINCT a.case_id) as case_count,
                COUNT(DISTINCT a.case_id) * 100.0 / t.cnt as percentage
            FROM activity_counts a, total_cases t
            GROUP BY a.activity, t.cnt
            ORDER BY total_repeats DESC
            LIMIT 20
        """

        rows = self.duckdb.execute(sql).fetchall()

        patterns = [
            ReworkItem(
                activity=row[0],
                repeat_count=row[1],
                case_count=row[2],
                percentage=row[3] or 0,
            )
            for row in rows
        ]

        # Get total cases with any rework
        rework_sql = f"""
            WITH activity_counts AS (
                SELECT
                    "case:concept:name" as case_id,
                    "concept:name" as activity,
                    COUNT(*) as cnt
                FROM read_parquet('{parquet_path}')
                GROUP BY "case:concept:name", "concept:name"
                HAVING COUNT(*) > 1
            ),
            total_cases AS (
                SELECT COUNT(DISTINCT "case:concept:name") as cnt
                FROM read_parquet('{parquet_path}')
            )
            SELECT
                COUNT(DISTINCT case_id) as cases_with_rework,
                (SELECT cnt FROM total_cases) as total
            FROM activity_counts
        """
        stats = self.duckdb.execute(rework_sql).fetchone()
        cases_with_rework = stats[0] if stats else 0
        total = stats[1] if stats else 1

        result = ReworkResult(
            rework_patterns=patterns,
            total_cases_with_rework=cases_with_rework,
            rework_rate=cases_with_rework / total if total > 0 else 0,
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
    "GetVariantsQuery",
    "ReworkResult",
]
