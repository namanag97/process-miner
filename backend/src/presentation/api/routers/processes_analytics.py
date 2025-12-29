"""Processes Analytics Sub-Router."""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.core.prediction_service import prediction_service
from src.application.support.analytics_service import analytics_service
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.presentation.api.routers.auth import User, require_auth
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

router = APIRouter()


class DashboardResponse(BaseModel):
    summary: Dict[str, int]
    kpis: Dict[str, Any]
    top_activities: List[Dict[str, Any]]
    top_variants: List[Dict[str, Any]]


class VariantStatsResponse(BaseModel):
    total_variants: int
    top_variants: List[Dict[str, Any]]
    variants_needed_for_80: int


class ResourceStatsResponse(BaseModel):
    total_resources: int
    resources: List[Dict[str, Any]]


class TimeAnalysisResponse(BaseModel):
    time_series: List[Dict[str, Any]]
    weekday_distribution: List[Dict[str, Any]]
    hourly_distribution: List[Dict[str, Any]]


class InsightsResponse(BaseModel):
    process_complexity: Dict[str, Any]
    process_standardization: Dict[str, Any]
    activity_distribution: Dict[str, float]
    likely_start_activities: Dict[str, int]
    likely_end_activities: Dict[str, int]


class AnomalyResponse(BaseModel):
    case_id: str
    reasons: List[Dict[str, Any]]
    severity: str


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")
    data = analytics_service.get_dashboard_data(log)
    return DashboardResponse(**data)


@router.get("/variants", response_model=VariantStatsResponse)
async def get_variant_statistics(
    process_id: UUID,
    top_n: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")
    stats = analytics_service.get_variant_statistics(log, top_n)
    return VariantStatsResponse(**stats)


@router.get("/resources", response_model=ResourceStatsResponse)
async def get_resource_statistics(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")
    stats = analytics_service.get_resource_statistics(log)
    return ResourceStatsResponse(**stats)


@router.get("/time", response_model=TimeAnalysisResponse)
async def get_time_analysis(
    process_id: UUID,
    granularity: str = Query("day", pattern="^(hour|day|week|month)$"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")
    analysis = analytics_service.get_time_analysis(log, granularity)
    return TimeAnalysisResponse(**analysis)


@router.get("/insights", response_model=InsightsResponse)
async def get_insights(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")
    insights = prediction_service.get_process_insights(log)
    return InsightsResponse(**insights)


@router.get("/anomalies", response_model=List[AnomalyResponse])
async def detect_anomalies(
    process_id: UUID,
    threshold: float = Query(2.0, ge=0.5, le=5.0),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")
    anomalies = prediction_service.detect_anomalies(log, threshold)
    return [AnomalyResponse(**a) for a in anomalies]
