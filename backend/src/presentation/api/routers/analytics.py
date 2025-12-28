"""Analytics API Router."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.application.support.analytics_service import analytics_service
from src.application.core.prediction_service import prediction_service
from src.presentation.api.routers.auth import require_auth, User


router = APIRouter(prefix="/analytics")


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


@router.get("/dashboard/{log_id}", response_model=DashboardResponse)
async def get_dashboard(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get comprehensive dashboard data for an event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        data = analytics_service.get_dashboard_data(log)
        return DashboardResponse(**data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dashboard generation failed: {str(e)}")


@router.get("/variants/{log_id}", response_model=VariantStatsResponse)
async def get_variant_statistics(
    log_id: UUID,
    top_n: int = 20,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detailed variant statistics.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        stats = analytics_service.get_variant_statistics(log, top_n)
        return VariantStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variant statistics failed: {str(e)}")


@router.get("/resources/{log_id}", response_model=ResourceStatsResponse)
async def get_resource_statistics(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get resource/user statistics.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        stats = analytics_service.get_resource_statistics(log)
        return ResourceStatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resource statistics failed: {str(e)}")


@router.get("/time/{log_id}", response_model=TimeAnalysisResponse)
async def get_time_analysis(
    log_id: UUID,
    granularity: str = "day",
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get time-based analysis.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        analysis = analytics_service.get_time_analysis(log, granularity)
        return TimeAnalysisResponse(**analysis)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Time analysis failed: {str(e)}")


@router.get("/insights/{log_id}", response_model=InsightsResponse)
async def get_insights(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get process insights.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        insights = prediction_service.get_process_insights(log)
        return InsightsResponse(**insights)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Insights generation failed: {str(e)}")


@router.get("/anomalies/{log_id}", response_model=List[AnomalyResponse])
async def detect_anomalies(
    log_id: UUID,
    threshold: float = 2.0,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Detect anomalous cases in the event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        anomalies = prediction_service.detect_anomalies(log, threshold)
        return [AnomalyResponse(**a) for a in anomalies]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")
