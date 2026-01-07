"""Get Cycle Time Query - Analytics query using DuckDB.

Computes cycle time (case duration) statistics from Parquet files.
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
class GetCycleTimeQuery(BaseQuery):
    """Query to get cycle time statistics.

    Cycle time is the total duration from first to last event in a case.
    """

    dataset_id: str
    filters: dict = field(default_factory=dict)


@dataclass
class CycleTimeResult:
    """Result for cycle time analysis."""

    dataset_id: str
    avg_cycle_time_hours: float
    min_cycle_time_hours: float
    max_cycle_time_hours: float
    median_cycle_time_hours: float
    std_dev_hours: float
    total_cases: int


class GetCycleTimeHandler(QueryHandler[GetCycleTimeQuery, CycleTimeResult]):
    """Handles cycle time analysis queries using DuckDB.

    Uses DuckDB to query Parquet files directly for OLAP performance.
    """

    def __init__(self, db: AsyncSession, duckdb: DuckDBManager):
        self.db = db
        self.duckdb = duckdb

    async def handle(self, query: GetCycleTimeQuery) -> CycleTimeResult:
        """Execute cycle time analysis query.

        Args:
            query: Query parameters including dataset_id and filters

        Returns:
            CycleTimeResult with statistics

        Raises:
            NotFoundError: If dataset doesn't exist
        """
        logger.debug("get_cycle_time_query", dataset_id=query.dataset_id)

        # Check cache first
        cache_key = f"cycle_time:{CACHE_VERSION}:{query.dataset_id}"
        cached = cache_service.get(cache_key)
        if cached:
            return CycleTimeResult(**cached)

        # Get dataset metadata
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == query.dataset_id)
        )
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise NotFoundError(f"Dataset {query.dataset_id} not found")

        if not dataset.parquet_path:
            # Return zeros if no parquet data
            return CycleTimeResult(
                dataset_id=query.dataset_id,
                avg_cycle_time_hours=0,
                min_cycle_time_hours=0,
                max_cycle_time_hours=0,
                median_cycle_time_hours=0,
                std_dev_hours=0,
                total_cases=0,
            )

        # Query DuckDB for cycle time statistics
        try:
            cycle_time = self._compute_cycle_time(
                dataset.parquet_path,
                query.dataset_id,
                query.filters,
            )

            # Cache results
            cache_service.set(cache_key, cycle_time.__dict__, ttl=3600)

            return cycle_time

        except Exception as e:
            logger.error(
                "cycle_time_query_failed",
                dataset_id=query.dataset_id,
                error=str(e),
            )
            raise

    def _compute_cycle_time(
        self,
        parquet_path: str,
        dataset_id: str,
        filters: dict,
    ) -> CycleTimeResult:
        """Compute cycle time statistics using DuckDB SQL."""
        # Build filter clause
        where_clause = ""
        if filters:
            conditions = [f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}" 
                          for k, v in filters.items()]
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

        # Query to compute cycle time per case
        sql = f"""
        WITH case_times AS (
            SELECT 
                case_id,
                EXTRACT(EPOCH FROM (MAX(timestamp) - MIN(timestamp))) / 3600.0 as cycle_time_hours
            FROM read_parquet('{parquet_path}')
            {where_clause}
            GROUP BY case_id
        )
        SELECT 
            AVG(cycle_time_hours) as avg_ct,
            MIN(cycle_time_hours) as min_ct,
            MAX(cycle_time_hours) as max_ct,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cycle_time_hours) as median_ct,
            STDDEV(cycle_time_hours) as std_ct,
            COUNT(*) as total_cases
        FROM case_times
        """

        try:
            result = self.duckdb.execute(sql)
            row = result.fetchone()

            if row:
                return CycleTimeResult(
                    dataset_id=dataset_id,
                    avg_cycle_time_hours=float(row[0] or 0),
                    min_cycle_time_hours=float(row[1] or 0),
                    max_cycle_time_hours=float(row[2] or 0),
                    median_cycle_time_hours=float(row[3] or 0),
                    std_dev_hours=float(row[4] or 0),
                    total_cases=int(row[5] or 0),
                )
        except Exception as e:
            logger.error("duckdb_cycle_time_query_failed", error=str(e))

        # Return zeros on error
        return CycleTimeResult(
            dataset_id=dataset_id,
            avg_cycle_time_hours=0,
            min_cycle_time_hours=0,
            max_cycle_time_hours=0,
            median_cycle_time_hours=0,
            std_dev_hours=0,
            total_cases=0,
        )
