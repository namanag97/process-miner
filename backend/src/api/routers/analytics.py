"""Analytics Router - Performance Analytics API.

Provides endpoints for bottleneck detection, rework analysis, service times,
cycle times, throughput metrics, and performance dashboards.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.core.logging_config import get_logger
from src.infrastructure.cache import cache_service
from src.models.orm import EventLog
from src.models.schemas import (
    BottleneckListResponse,
    BottleneckResponse,
    CycleTimeResponse,
    PerformanceDashboardResponse,
    ReworkListResponse,
    ReworkResponse,
    ServiceTimeResponse,
    ThroughputResponse,
    PatternResponse,
)
from src.services.analytics import analytics_service
from src.services.filtering import filtering_service

logger = get_logger(__name__)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


async def _get_pm4py_log(log_id: str, db: AsyncSession):
    """Helper to get PM4Py log from log_id."""
    query = select(EventLog).where(EventLog.id == log_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")
    return filtering_service.to_pm4py_log(event_log), event_log


@router.get("/logs/{log_id}/bottlenecks", response_model=BottleneckListResponse)
async def get_bottlenecks(log_id: str, db: AsyncSession = Depends(get_db)) -> BottleneckListResponse:
    """Detect process bottlenecks based on waiting times."""
    logger.info("getting_bottlenecks", log_id=log_id)

    # Try cache first
    cache_key = f"bottlenecks:{log_id}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    pm4py_log, _ = await _get_pm4py_log(log_id, db)
    result = analytics_service.detect_bottlenecks(pm4py_log)
    response = BottleneckListResponse(
        log_id=log_id,
        bottlenecks=[BottleneckResponse(**b) for b in result["bottlenecks"]],
        total_bottlenecks=result["total_bottlenecks"],
    )

    # Cache for 1 hour
    cache_service.set(cache_key, response, ttl=3600)
    return response


@router.get("/logs/{log_id}/rework", response_model=ReworkListResponse)
async def get_rework(log_id: str, db: AsyncSession = Depends(get_db)) -> ReworkListResponse:
    """Analyze rework (repeated activities) in cases."""
    logger.info("getting_rework", log_id=log_id)

    # Try cache first
    cache_key = f"rework:{log_id}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    pm4py_log, _ = await _get_pm4py_log(log_id, db)
    result = analytics_service.analyze_rework(pm4py_log)
    response = ReworkListResponse(
        log_id=log_id,
        rework_activities=[ReworkResponse(**r) for r in result["rework_activities"]],
        total_rework_cases=result["total_rework_cases"],
        rework_percentage=result["rework_percentage"],
    )

    # Cache for 1 hour
    cache_service.set(cache_key, response, ttl=3600)
    return response


@router.get("/logs/{log_id}/service-times")
async def get_service_times(log_id: str, db: AsyncSession = Depends(get_db)) -> list[ServiceTimeResponse]:
    """Get service time statistics per activity."""
    logger.info("getting_service_times", log_id=log_id)

    # Try cache first
    cache_key = f"service_times:{log_id}"
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    pm4py_log, _ = await _get_pm4py_log(log_id, db)
    result = analytics_service.get_service_times(pm4py_log)
    response = [ServiceTimeResponse(**s) for s in result]

    # Cache for 1 hour
    cache_service.set(cache_key, response, ttl=3600)
    return response


@router.get("/logs/{log_id}/cycle-time", response_model=CycleTimeResponse)
async def get_cycle_time(log_id: str, db: AsyncSession = Depends(get_db)) -> CycleTimeResponse:
    """Get cycle time (case duration) statistics."""
    logger.info("getting_cycle_time", log_id=log_id)
    pm4py_log, _ = await _get_pm4py_log(log_id, db)
    result = analytics_service.get_cycle_time(pm4py_log)
    return CycleTimeResponse(log_id=log_id, **result)


@router.get("/logs/{log_id}/throughput", response_model=ThroughputResponse)
async def get_throughput(log_id: str, db: AsyncSession = Depends(get_db)) -> ThroughputResponse:
    """Get throughput metrics (cases per day/week/month)."""
    logger.info("getting_throughput", log_id=log_id)
    pm4py_log, _ = await _get_pm4py_log(log_id, db)
    result = analytics_service.get_throughput(pm4py_log)
    return ThroughputResponse(log_id=log_id, **result)


@router.get("/logs/{log_id}/patterns")
async def get_patterns(log_id: str, min_support: float = 0.1, db: AsyncSession = Depends(get_db)) -> list[PatternResponse]:
    """Get frequent activity patterns/subsequences."""
    logger.info("getting_patterns", log_id=log_id, min_support=min_support)
    pm4py_log, _ = await _get_pm4py_log(log_id, db)
    result = analytics_service.get_frequent_patterns(pm4py_log, min_support)
    return [PatternResponse(**p) for p in result]


@router.get("/logs/{log_id}/performance", response_model=PerformanceDashboardResponse)
async def get_performance_dashboard(log_id: str, db: AsyncSession = Depends(get_db)) -> PerformanceDashboardResponse:
    """Get comprehensive performance dashboard."""
    logger.info("getting_performance_dashboard", log_id=log_id)
    pm4py_log, _ = await _get_pm4py_log(log_id, db)
    result = analytics_service.get_performance_dashboard(pm4py_log)
    return PerformanceDashboardResponse(
        log_id=log_id,
        cycle_time=CycleTimeResponse(log_id=log_id, **result["cycle_time"]),
        throughput=ThroughputResponse(log_id=log_id, **result["throughput"]),
        top_bottlenecks=[BottleneckResponse(**b) for b in result["top_bottlenecks"]],
        rework_summary=result["rework_summary"],
    )
