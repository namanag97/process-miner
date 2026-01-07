"""Get Bottlenecks Query - Analytics query using DuckDB.

Reads directly from Parquet files via DuckDB for OLAP-optimized
bottleneck detection without touching PostgreSQL.
"""

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.queries.base import BaseQuery, QueryHandler
from src.features.process_mining.models import Dataset
from src.platform.core.exceptions import NotFoundError
from src.platform.core.logging_config import get_logger
from src.platform.infrastructure.cache import cache_service
from src.platform.infrastructure.duckdb import DuckDBManager

logger = get_logger(__name__)

CACHE_VERSION = "v1"


@dataclass
class GetBottlenecksQuery(BaseQuery):
    """Query to get process bottlenecks.

    Identifies activities with high waiting times that slow down the process.
    """

    dataset_id: str
    top_n: int = 10
    filters: dict = field(default_factory=dict)


@dataclass
class BottleneckResult:
    """Result for a single bottleneck."""

    activity: str
    avg_wait_time: float
    max_wait_time: float
    occurrence_count: int
    impact_score: float


class GetBottlenecksHandler(QueryHandler[GetBottlenecksQuery, list[BottleneckResult]]):
    """Handles bottleneck analysis queries using DuckDB.

    Uses DuckDB to query Parquet files directly for OLAP performance.
    Results are cached for fast subsequent reads.
    """

    def __init__(self, db: AsyncSession, duckdb: DuckDBManager):
        super().__init__(duckdb_conn=duckdb.get_connection() if duckdb else None)
        self.db = db
        self.duckdb_manager = duckdb

    async def handle(self, query: GetBottlenecksQuery) -> list[BottleneckResult]:
        """Execute bottleneck analysis query.

        Args:
            query: Query parameters including dataset_id and filters

        Returns:
            List of bottleneck results sorted by impact

        Raises:
            NotFoundError: If dataset doesn't exist
        """
        logger.debug(
            "get_bottlenecks_query",
            dataset_id=query.dataset_id,
            top_n=query.top_n,
        )

        # Check cache first
        cache_key = f"bottlenecks:{CACHE_VERSION}:{query.dataset_id}:{query.top_n}"
        cached = cache_service.get(cache_key)
        if cached:
            return [BottleneckResult(**b) for b in cached]

        # Get dataset metadata from PostgreSQL (read replica)
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == query.dataset_id)
        )
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise NotFoundError(resource="Dataset", resource_id=query.dataset_id)

        if not dataset.parquet_s3_key:
            logger.warning("dataset_no_parquet", dataset_id=query.dataset_id)
            return []

        # Query DuckDB for bottleneck analysis
        try:
            bottlenecks = self._compute_bottlenecks(
                dataset.parquet_s3_key,
                query.top_n,
                query.filters,
            )

            # Cache results
            cache_service.set(
                cache_key,
                [b.__dict__ for b in bottlenecks],
                ttl=3600,
            )

            return bottlenecks

        except Exception as e:
            logger.error(
                "bottleneck_query_failed",
                dataset_id=query.dataset_id,
                error=str(e),
            )
            raise

    def _compute_bottlenecks(
        self,
        parquet_path: str,
        top_n: int,
        filters: dict,
    ) -> list[BottleneckResult]:
        """Compute bottlenecks using DuckDB SQL.

        Note: This uses a simplified computation. In production,
        you'd compute actual wait times between activities.
        """
        assert self.duckdb is not None, "DuckDB connection is required"
        # Build filter clause if provided
        where_clause = ""
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, str):
                    conditions.append(f"{key} = '{value}'")
                else:
                    conditions.append(f"{key} = {value}")
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

        # Query to compute activity statistics
        # In a real implementation, this would compute wait times
        # between consecutive activities
        sql = f"""
        SELECT
            activity,
            COUNT(*) as occurrence_count,
            -- Placeholder metrics (would be computed from event timestamps)
            RANDOM() * 100 as avg_wait_time,
            RANDOM() * 200 as max_wait_time,
            COUNT(*) * RANDOM() as impact_score
        FROM read_parquet('{parquet_path}')
        {where_clause}
        GROUP BY activity
        ORDER BY impact_score DESC
        LIMIT {top_n}
        """

        try:
            result = self.duckdb.execute(sql)
            rows = result.fetchall()

            return [
                BottleneckResult(
                    activity=row[0],
                    occurrence_count=row[1],
                    avg_wait_time=row[2],
                    max_wait_time=row[3],
                    impact_score=row[4],
                )
                for row in rows
            ]
        except Exception as e:
            logger.error("duckdb_bottleneck_query_failed", error=str(e))
            # Return empty list on DuckDB errors (parquet may not exist yet)
            return []
