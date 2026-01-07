"""Analytics Router - Performance Analytics API (CQRS).

Performance analysis endpoints using CQRS query bus for read operations.
All queries use DuckDB to read from Parquet files - never PostgreSQL for analytics.

## Business Context
Analytics provides operational insights from process execution:
- **Bottlenecks**: Activities with high waiting times slowing the process
- **Rework**: Repeated activities indicating inefficiency or errors
- **Service Times**: How long each activity takes to execute
- **Cycle Time**: End-to-end case duration statistics
- **Throughput**: Cases completed per time period
- **Variants**: Unique process paths taken by cases

## CQRS Architecture
All endpoints use QueryBusDep to dispatch read operations:
- Queries are handled by dedicated QueryHandlers
- QueryHandlers use DuckDB for OLAP on Parquet files
- Results are cached with automatic invalidation on data changes
"""

from fastapi import APIRouter

from src.api.dependencies import CurrentUser, QueryBusDep
from src.application.queries.analytics_queries import (
    GetBottlenecksQuery,
    GetCycleTimeQuery,
    GetReworkQuery,
    GetThroughputQuery,
)
from src.application.queries.get_variants import GetVariantsQuery
from src.features.process_mining.schemas import (
    BottleneckListResponse,
    BottleneckResponse,
    CycleTimeResponse,
    ReworkListResponse,
    ReworkResponse,
    ThroughputResponse,
    VariantListResponse,
    VariantResponse,
)
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/datasets/{dataset_id}/bottlenecks", response_model=BottleneckListResponse)
async def get_bottlenecks(
    dataset_id: str,
    user: CurrentUser,
    query_bus: QueryBusDep,
    limit: int = 10,
) -> BottleneckListResponse:
    """Detect process bottlenecks based on waiting times.

    Uses CQRS QueryBus to dispatch GetBottlenecksQuery.
    Query handler uses DuckDB on Parquet for OLAP performance.
    """
    logger.info("get_bottlenecks", dataset_id=dataset_id, user_id=user.id)

    query = GetBottlenecksQuery(dataset_id=dataset_id, limit=limit)
    result = await query_bus.dispatch(query)

    return BottleneckListResponse(
        dataset_id=dataset_id,
        bottlenecks=[
            BottleneckResponse(
                activity=b.activity,
                avg_waiting_time_seconds=b.avg_wait_time_seconds,
                avg_service_time_seconds=0,  # Not available in current query result
                frequency=b.occurrence_count,
                is_bottleneck=True,
                severity="high" if b.avg_wait_time_seconds > 3600 else "medium" if b.avg_wait_time_seconds > 600 else "low",
                preceding_activities=[],
                following_activities=[],
                bottleneck_impact_score=min(1.0, b.avg_wait_time_seconds / 7200),  # Normalize to 0-1
            )
            for b in result.bottlenecks
        ],
        total_bottlenecks=result.total_activities,
    )


@router.get("/datasets/{dataset_id}/cycle-time", response_model=CycleTimeResponse)
async def get_cycle_time(
    dataset_id: str,
    user: CurrentUser,
    query_bus: QueryBusDep,
) -> CycleTimeResponse:
    """Get cycle time (case duration) statistics.

    Uses CQRS QueryBus to dispatch GetCycleTimeQuery.
    """
    logger.info("get_cycle_time", dataset_id=dataset_id, user_id=user.id)

    query = GetCycleTimeQuery(dataset_id=dataset_id)
    result = await query_bus.dispatch(query)

    return CycleTimeResponse(
        dataset_id=dataset_id,
        min_seconds=result.min_seconds,
        max_seconds=result.max_seconds,
        avg_seconds=result.mean_seconds,
        median_seconds=result.median_seconds,
        percentile_25_seconds=0,  # Not available in current query result
        percentile_75_seconds=0,
        percentile_95_seconds=0,
    )


@router.get("/datasets/{dataset_id}/throughput", response_model=ThroughputResponse)
async def get_throughput(
    dataset_id: str,
    user: CurrentUser,
    query_bus: QueryBusDep,
) -> ThroughputResponse:
    """Get throughput statistics for a dataset.

    Uses CQRS QueryBus to dispatch GetThroughputQuery.
    """
    logger.info("get_throughput", dataset_id=dataset_id, user_id=user.id)

    query = GetThroughputQuery(dataset_id=dataset_id)
    result = await query_bus.dispatch(query)

    return ThroughputResponse(
        dataset_id=dataset_id,
        total_cases=result.total_cases,
        completed_cases=result.completed_cases,
        cases_per_day=result.cases_per_day,
        cases_per_week=result.cases_per_week,
        cases_per_month=result.cases_per_month,
        time_range_days=result.time_range_days,
    )


@router.get("/datasets/{dataset_id}/rework", response_model=ReworkListResponse)
async def get_rework(
    dataset_id: str,
    user: CurrentUser,
    query_bus: QueryBusDep,
) -> ReworkListResponse:
    """Analyze rework (repeated activities) in cases.

    Uses CQRS QueryBus to dispatch GetReworkQuery.
    """
    logger.info("get_rework", dataset_id=dataset_id, user_id=user.id)

    query = GetReworkQuery(dataset_id=dataset_id)
    result = await query_bus.dispatch(query)

    return ReworkListResponse(
        dataset_id=dataset_id,
        rework_activities=[
            ReworkResponse(
                activity=r.activity,
                rework_count=r.repeat_count,
                cases_with_rework=r.case_count,
                rework_percentage=r.percentage,
            )
            for r in result.rework_patterns
        ],
        total_rework_cases=result.total_cases_with_rework,
        rework_percentage=result.rework_rate * 100,
    )


@router.get("/datasets/{dataset_id}/variants", response_model=VariantListResponse)
async def get_variants(
    dataset_id: str,
    user: CurrentUser,
    query_bus: QueryBusDep,
    top_n: int = 20,
) -> VariantListResponse:
    """Get process variants (unique activity sequences).

    Uses CQRS QueryBus to dispatch GetVariantsQuery.
    """
    logger.info("get_variants", dataset_id=dataset_id, user_id=user.id)

    query = GetVariantsQuery(dataset_id=dataset_id, top_n=top_n)
    result = await query_bus.dispatch(query)

    return VariantListResponse(
        dataset_id=dataset_id,
        variants=[
            VariantResponse(
                variant_id=v.variant_id,
                activities=v.activities,
                case_count=v.case_count,
                percentage=v.percentage,
            )
            for v in result.variants
        ],
        total_variants=result.total_variants,
        total_cases=result.total_cases,
    )
