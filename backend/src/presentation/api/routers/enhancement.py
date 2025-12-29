"""Process Enhancement API Router."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.core.enhancement_service import enhancement_service
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.presentation.api.routers.auth import User, require_auth
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

router = APIRouter(prefix="/enhancement")


class PerformanceResponse(BaseModel):
    avg_case_duration_seconds: float
    median_case_duration_seconds: float
    min_case_duration_seconds: float
    max_case_duration_seconds: float
    bottleneck_activities: List[str]


class KPIResponse(BaseModel):
    total_cases: int
    total_events: int
    unique_activities: int
    unique_variants: int
    avg_case_duration_seconds: float
    throughput_per_day: float
    bottleneck_activities: List[str]


class ActivityStatResponse(BaseModel):
    activity: str
    total_count: int
    case_count: int
    avg_duration_seconds: float


class CaseStatResponse(BaseModel):
    case_id: str
    event_count: int
    variant: str
    duration_seconds: float


@router.get("/performance/{log_id}", response_model=PerformanceResponse)
async def get_performance(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get performance analysis for an event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    try:
        metrics = enhancement_service.analyze_performance(log)

        return PerformanceResponse(
            avg_case_duration_seconds=metrics.avg_case_duration.total_seconds,
            median_case_duration_seconds=metrics.median_case_duration.total_seconds,
            min_case_duration_seconds=metrics.min_case_duration.total_seconds,
            max_case_duration_seconds=metrics.max_case_duration.total_seconds,
            bottleneck_activities=metrics.bottleneck_activities,
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Performance analysis failed: {str(e)}")


@router.get("/kpis/{log_id}", response_model=KPIResponse)
async def get_kpis(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get KPIs for an event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    try:
        kpis = enhancement_service.get_kpis(log)

        return KPIResponse(
            total_cases=kpis["total_cases"],
            total_events=kpis["total_events"],
            unique_activities=kpis["unique_activities"],
            unique_variants=kpis["unique_variants"],
            avg_case_duration_seconds=kpis["avg_case_duration_seconds"],
            throughput_per_day=kpis["throughput_per_day"],
            bottleneck_activities=kpis["bottleneck_activities"],
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"KPI calculation failed: {str(e)}")


@router.get("/activities/{log_id}", response_model=List[ActivityStatResponse])
async def get_activity_statistics(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get activity statistics for an event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    try:
        stats = enhancement_service.get_activity_statistics(log)

        return [
            ActivityStatResponse(
                activity=s["activity"],
                total_count=s["total_count"],
                case_count=s["case_count"],
                avg_duration_seconds=s["avg_duration_seconds"],
            )
            for s in stats
        ]
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Activity statistics failed: {str(e)}")


@router.get("/cases/{log_id}", response_model=List[CaseStatResponse])
async def get_case_statistics(
    log_id: UUID,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get case statistics for an event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    try:
        stats = enhancement_service.get_case_statistics(log, limit)

        return [
            CaseStatResponse(
                case_id=s["case_id"],
                event_count=s["event_count"],
                variant=s["variant"][:100] if s["variant"] else "",
                duration_seconds=s["duration_seconds"],
            )
            for s in stats
        ]
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Case statistics failed: {str(e)}")


@router.get("/bottlenecks/{log_id}")
async def get_bottlenecks(
    log_id: UUID,
    top_n: int = 5,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get bottleneck activities for an event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    try:
        metrics = enhancement_service.analyze_performance(log)

        return {
            "bottlenecks": metrics.bottleneck_activities[:top_n],
            "waiting_times": {
                k: v
                for k, v in sorted(metrics.waiting_times.items(), key=lambda x: x[1], reverse=True)[
                    :top_n
                ]
            },
        }
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Bottleneck analysis failed: {str(e)}")
