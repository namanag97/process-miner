"""Get Variants Query - Analytics query using DuckDB.

Computes process variants (unique activity sequences) from Parquet files.
"""

from dataclasses import dataclass, field

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.queries.base import BaseQuery, QueryHandler
from src.features.process_mining.models import Dataset
from src.infra.core.exceptions import NotFoundError
from src.infra.core.logging_config import get_logger
from src.infra.infrastructure.cache import cache_service
from src.infra.infrastructure.duckdb import DuckDBManager

logger = get_logger(__name__)

CACHE_VERSION = "v1"


@dataclass
class GetVariantsQuery(BaseQuery):
    """Query to get process variants.

    A variant is a unique sequence of activities followed by cases.
    """

    dataset_id: str
    top_n: int = 20
    filters: dict = field(default_factory=dict)


@dataclass
class VariantResult:
    """Result for a single variant."""

    variant_id: int
    activities: list[str]
    case_count: int
    percentage: float


@dataclass
class VariantsListResult:
    """Result for variants analysis."""

    dataset_id: str
    variants: list[VariantResult]
    total_variants: int
    total_cases: int


class GetVariantsHandler(QueryHandler[GetVariantsQuery, VariantsListResult]):
    """Handles variants analysis queries using DuckDB.

    Uses DuckDB to query Parquet files directly for OLAP performance.
    """

    def __init__(self, db: AsyncSession, duckdb: DuckDBManager):
        super().__init__(duckdb_conn=duckdb.get_connection() if duckdb else None)
        self.db = db
        self.duckdb_manager = duckdb

    async def handle(self, query: GetVariantsQuery) -> VariantsListResult:
        """Execute variants analysis query.

        Args:
            query: Query parameters including dataset_id and filters

        Returns:
            VariantsListResult with top variants

        Raises:
            NotFoundError: If dataset doesn't exist
        """
        logger.debug(
            "get_variants_query",
            dataset_id=query.dataset_id,
            top_n=query.top_n,
        )

        # Check cache first
        cache_key = f"variants:{CACHE_VERSION}:{query.dataset_id}:{query.top_n}"
        cached = cache_service.get(cache_key)
        if cached:
            variants = [VariantResult(**v) for v in cached["variants"]]
            return VariantsListResult(
                dataset_id=cached["dataset_id"],
                variants=variants,
                total_variants=cached["total_variants"],
                total_cases=cached["total_cases"],
            )

        # Get dataset metadata
        result = await self.db.execute(
            select(Dataset).where(Dataset.id == query.dataset_id)
        )
        dataset = result.scalar_one_or_none()

        if not dataset:
            raise NotFoundError(resource="Dataset", resource_id=query.dataset_id)

        if not dataset.parquet_s3_key:
            return VariantsListResult(
                dataset_id=query.dataset_id,
                variants=[],
                total_variants=0,
                total_cases=0,
            )

        # Build full parquet path
        from src.infra.core.config import get_settings
        settings = get_settings()
        if settings.storage_type == "local":
            parquet_path = f"./data/storage/{settings.s3_bucket_cache}/{dataset.parquet_s3_key}"
        else:
            endpoint = settings.s3_endpoint_url or "s3://"
            parquet_path = f"{endpoint}/{settings.s3_bucket_cache}/{dataset.parquet_s3_key}"

        # Query DuckDB for variants
        try:
            variants_result = self._compute_variants(
                parquet_path,
                query.dataset_id,
                query.top_n,
                query.filters,
            )

            # Cache results
            cache_data = {
                "dataset_id": variants_result.dataset_id,
                "variants": [
                    {
                        "variant_id": v.variant_id,
                        "activities": v.activities,
                        "case_count": v.case_count,
                        "percentage": v.percentage,
                    }
                    for v in variants_result.variants
                ],
                "total_variants": variants_result.total_variants,
                "total_cases": variants_result.total_cases,
            }
            cache_service.set(cache_key, cache_data, ttl=3600)

            return variants_result

        except Exception as e:
            logger.error(
                "variants_query_failed",
                dataset_id=query.dataset_id,
                error=str(e),
            )
            raise

    def _compute_variants(
        self,
        parquet_path: str,
        dataset_id: str,
        top_n: int,
        filters: dict,
    ) -> VariantsListResult:
        """Compute variants using DuckDB SQL."""
        assert self.duckdb is not None, "DuckDB connection is required"
        where_clause = ""
        if filters:
            conditions = [f"{k} = '{v}'" if isinstance(v, str) else f"{k} = {v}"
                          for k, v in filters.items()]
            if conditions:
                where_clause = "WHERE " + " AND ".join(conditions)

        # Query to compute variants (uses PM4Py standard column names)
        sql = f"""
        WITH ordered_events AS (
            SELECT
                "case:concept:name" as case_id,
                "concept:name" as activity,
                "time:timestamp" as timestamp,
                ROW_NUMBER() OVER (PARTITION BY "case:concept:name" ORDER BY "time:timestamp") as event_order
            FROM read_parquet('{parquet_path}')
            {where_clause}
        ),
        case_variants AS (
            SELECT
                case_id,
                STRING_AGG(activity, ' -> ' ORDER BY event_order) as variant_path,
                LIST(activity ORDER BY event_order) as activities
            FROM ordered_events
            GROUP BY case_id
        ),
        variant_counts AS (
            SELECT
                variant_path,
                activities[1] as first_activity,
                COUNT(*) as case_count
            FROM case_variants
            GROUP BY variant_path, activities
        )
        SELECT
            variant_path,
            case_count,
            ROW_NUMBER() OVER (ORDER BY case_count DESC) as variant_id
        FROM variant_counts
        ORDER BY case_count DESC
        LIMIT {top_n}
        """

        try:
            result = self.duckdb.execute(sql)
            rows = result.fetchall()

            # Get total counts (uses PM4Py column names)
            totals_sql = f"""
            WITH ordered_events AS (
                SELECT
                    "case:concept:name" as case_id,
                    "concept:name" as activity,
                    "time:timestamp" as timestamp,
                    ROW_NUMBER() OVER (PARTITION BY "case:concept:name" ORDER BY "time:timestamp") as event_order
                FROM read_parquet('{parquet_path}')
            ),
            case_variants AS (
                SELECT
                    case_id,
                    STRING_AGG(activity, ' -> ' ORDER BY event_order) as variant_path
                FROM ordered_events
                GROUP BY case_id
            )
            SELECT
                COUNT(DISTINCT case_id) as total_cases,
                COUNT(DISTINCT variant_path) as total_variants
            FROM case_variants
            """
            totals_result = self.duckdb.execute(totals_sql)
            totals_row = totals_result.fetchone()
            total_cases = int(totals_row[0]) if totals_row else 0
            total_variants = int(totals_row[1]) if totals_row else 0

            variants = []
            for row in rows:
                variant_path = row[0]
                case_count = int(row[1])
                variant_id = int(row[2])

                activities = variant_path.split(" -> ") if variant_path else []
                percentage = (case_count / total_cases * 100) if total_cases > 0 else 0

                variants.append(
                    VariantResult(
                        variant_id=variant_id,
                        activities=activities,
                        case_count=case_count,
                        percentage=round(percentage, 2),
                    )
                )

            return VariantsListResult(
                dataset_id=dataset_id,
                variants=variants,
                total_variants=total_variants,
                total_cases=total_cases,
            )

        except Exception as e:
            logger.error("duckdb_variants_query_failed", error=str(e))
            return VariantsListResult(
                dataset_id=dataset_id,
                variants=[],
                total_variants=0,
                total_cases=0,
            )
