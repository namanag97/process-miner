"""Analytics Router - Performance Analytics API.

Provides endpoints for bottleneck detection, rework analysis, service times,
cycle times, throughput metrics, and performance dashboards.
"""

from typing import cast

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.features.process_mining.models import Dataset
from src.features.process_mining.schemas import (
    BottleneckListResponse,
    BottleneckResponse,
    CycleTimeResponse,
    PatternResponse,
    PerformanceDashboardResponse,
    ReworkChain,
    ReworkChainListResponse,
    ReworkListResponse,
    ReworkResponse,
    ServiceTimeResponse,
    ThroughputResponse,
)
from src.features.process_mining.services.analytics import analytics_service
from src.features.process_mining.services.filtering import filtering_service
from src.platform.core.exceptions import ProcessNotFoundError
from src.platform.core.logging_config import get_logger
from src.platform.infrastructure.cache import cache_service

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


async def _get_pm4py_log(dataset_id: str, db: AsyncSession):
    """Helper to get PM4Py log from dataset_id."""
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        raise ProcessNotFoundError(dataset_id)
    return filtering_service.to_pm4py_log(event_log), event_log


@router.get("/datasets/{dataset_id}/bottlenecks", response_model=BottleneckListResponse)
async def get_bottlenecks(
    dataset_id: str, db: AsyncSession = Depends(get_db)
) -> BottleneckListResponse:
    """Detect process bottlenecks based on waiting times."""
    logger.info("getting_bottlenecks", dataset_id=dataset_id)

    # Try cache first
    cache_key = f"bottlenecks:{log_id}"
    cached = cache_service.get(cache_key)
    if cached:
        return cast(BottleneckListResponse, cached)

    pm4py_log, _ = await _get_pm4py_log(dataset_id, db)
    result = analytics_service.detect_bottlenecks(pm4py_log)
    response = BottleneckListResponse(
        dataset_id=dataset_id,
        bottlenecks=[BottleneckResponse(**b) for b in result["bottlenecks"]],
        total_bottlenecks=result["total_bottlenecks"],
    )

    # Cache for 1 hour
    cache_service.set(cache_key, response, ttl=3600)
    return response


@router.get("/datasets/{dataset_id}/rework", response_model=ReworkListResponse)
async def get_rework(dataset_id: str, db: AsyncSession = Depends(get_db)) -> ReworkListResponse:
    """Analyze rework (repeated activities) in cases."""
    logger.info("getting_rework", dataset_id=dataset_id)

    # Try cache first
    cache_key = f"rework:{log_id}"
    cached = cache_service.get(cache_key)
    if cached:
        return cast(ReworkListResponse, cached)

    pm4py_log, _ = await _get_pm4py_log(dataset_id, db)
    result = analytics_service.analyze_rework(pm4py_log)
    response = ReworkListResponse(
        dataset_id=dataset_id,
        rework_activities=[ReworkResponse(**r) for r in result["rework_activities"]],
        total_rework_cases=result["total_rework_cases"],
        rework_percentage=result["rework_percentage"],
    )

    # Cache for 1 hour
    cache_service.set(cache_key, response, ttl=3600)
    return response


@router.get("/datasets/{dataset_id}/service-times")
async def get_service_times(
    dataset_id: str, db: AsyncSession = Depends(get_db)
) -> list[ServiceTimeResponse]:
    """Get service time statistics per activity."""
    logger.info("getting_service_times", dataset_id=dataset_id)

    # Try cache first
    cache_key = f"service_times:{log_id}"
    cached = cache_service.get(cache_key)
    if cached:
        return cast(list[ServiceTimeResponse], cached)

    pm4py_log, _ = await _get_pm4py_log(dataset_id, db)
    result = analytics_service.get_service_times(pm4py_log)
    response = [ServiceTimeResponse(**s) for s in result]

    # Cache for 1 hour
    cache_service.set(cache_key, response, ttl=3600)
    return response


@router.get("/datasets/{dataset_id}/cycle-time", response_model=CycleTimeResponse)
async def get_cycle_time(dataset_id: str, db: AsyncSession = Depends(get_db)) -> CycleTimeResponse:
    """Get cycle time (case duration) statistics."""
    logger.info("getting_cycle_time", dataset_id=dataset_id)
    pm4py_log, _ = await _get_pm4py_log(dataset_id, db)
    result = analytics_service.get_cycle_time(pm4py_log)
    return CycleTimeResponse(dataset_id=dataset_id, **result)


@router.get("/datasets/{dataset_id}/throughput", response_model=ThroughputResponse)
async def get_throughput(dataset_id: str, db: AsyncSession = Depends(get_db)) -> ThroughputResponse:
    """Get throughput metrics (cases per day/week/month)."""
    logger.info("getting_throughput", dataset_id=dataset_id)
    pm4py_log, _ = await _get_pm4py_log(dataset_id, db)
    result = analytics_service.get_throughput(pm4py_log)
    return ThroughputResponse(dataset_id=dataset_id, **result)


@router.get("/datasets/{dataset_id}/patterns")
async def get_patterns(
    dataset_id: str, min_support: float = 0.1, db: AsyncSession = Depends(get_db)
) -> list[PatternResponse]:
    """Get frequent activity patterns/subsequences."""
    logger.info("getting_patterns", dataset_id=dataset_id, min_support=min_support)
    pm4py_log, _ = await _get_pm4py_log(dataset_id, db)
    result = analytics_service.get_frequent_patterns(pm4py_log, min_support)
    return [PatternResponse(**p) for p in result]


@router.get("/datasets/{dataset_id}/rework-chains", response_model=ReworkChainListResponse)
async def get_rework_chains(
    dataset_id: str, db: AsyncSession = Depends(get_db)
) -> ReworkChainListResponse:
    """Detect rework chains - consecutive repetitions of the same activity.

    A rework chain is when an activity appears multiple times consecutively,
    indicating immediate rework/retry patterns. For example, if activity 'Review'
    appears 3 times in a row, that's a chain of length 3.

    Returns:
        - chains: List of detected rework chains with frequency and duration
        - most_problematic_activity: Activity with the most chains
        - cases_with_chains: Number of cases containing chains
    """
    logger.info("getting_rework_chains", dataset_id=dataset_id)

    # Try cache first
    cache_key = f"rework_chains:{log_id}"
    cached = cache_service.get(cache_key)
    if cached:
        return cast(ReworkChainListResponse, cached)

    pm4py_log, _ = await _get_pm4py_log(dataset_id, db)
    result = analytics_service.detect_rework_chains(pm4py_log)

    response = ReworkChainListResponse(
        dataset_id=dataset_id,
        chains=[ReworkChain(**c) for c in result["chains"]],
        total_chains=result["total_chains"],
        most_problematic_activity=result["most_problematic_activity"],
        cases_with_chains=result["cases_with_chains"],
        chains_percentage=result["chains_percentage"],
    )

    # Cache for 1 hour
    cache_service.set(cache_key, response, ttl=3600)
    return response


@router.get("/datasets/{dataset_id}/performance", response_model=PerformanceDashboardResponse)
async def get_performance_dashboard(
    dataset_id: str, db: AsyncSession = Depends(get_db)
) -> PerformanceDashboardResponse:
    """Get comprehensive performance dashboard."""
    logger.info("getting_performance_dashboard", dataset_id=dataset_id)
    pm4py_log, _ = await _get_pm4py_log(dataset_id, db)
    result = analytics_service.get_performance_dashboard(pm4py_log)
    return PerformanceDashboardResponse(
        dataset_id=dataset_id,
        cycle_time=CycleTimeResponse(dataset_id=dataset_id, **result["cycle_time"]),
        throughput=ThroughputResponse(dataset_id=dataset_id, **result["throughput"]),
        top_bottlenecks=[BottleneckResponse(**b) for b in result["top_bottlenecks"]],
        rework_summary=result["rework_summary"],
    )
