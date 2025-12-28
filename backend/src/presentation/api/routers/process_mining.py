"""Process Mining API Router - Advanced PM4Py Capabilities."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.application.core.pm4py_service import pm4py_service
from src.presentation.api.routers.auth import require_auth, User


router = APIRouter(prefix="/process-mining")


class FootprintsResponse(BaseModel):
    sequence: List[str]
    parallel: List[str]
    activities: List[str]
    start_activities: Optional[List[str]] = None
    end_activities: Optional[List[str]] = None


class LogSkeletonResponse(BaseModel):
    equivalence_count: int
    always_after_count: int
    always_before_count: int
    never_together_count: int
    equivalence: List[str]
    always_after: List[str]
    always_before: List[str]
    never_together: List[str]


class RoleInfo(BaseModel):
    resources: List[str]
    activities: List[str]


class OrganizationalRolesResponse(BaseModel):
    roles: List[Dict[str, Any]]
    total_roles: int


class SNAResponse(BaseModel):
    network_type: str
    status: str
    matrix_shape: Optional[Any] = None


class BatchInfo(BaseModel):
    activity: str
    resource: str
    batch_type_count: int
    batch_types: Dict[str, int]


class BatchDetectionResponse(BaseModel):
    total_batch_patterns: int
    batch_summary: List[Dict[str, Any]]


class TransitionSystemResponse(BaseModel):
    states_count: int
    transitions_count: int
    status: str


class ProcessTreeResponse(BaseModel):
    tree_string: str
    operator: str
    label: Optional[str] = None


class CaseDurationStatsResponse(BaseModel):
    min_duration_seconds: float
    max_duration_seconds: float
    avg_duration_seconds: float
    median_duration_seconds: float
    total_cases: int


class CaseArrivalRateResponse(BaseModel):
    average_arrival_seconds: float
    average_arrival_minutes: float
    average_arrival_hours: float


@router.get("/footprints/{log_id}")
async def get_footprints(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get footprint analysis (behavioral relations between activities).
    Shows sequence, parallel, and other relations.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.discover_footprints(log)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Footprints analysis failed: {str(e)}")


@router.get("/log-skeleton/{log_id}")
async def get_log_skeleton(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get log skeleton (declarative process model constraints).
    Shows always_after, always_before, never_together relationships.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.discover_log_skeleton(log)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Log skeleton analysis failed: {str(e)}")


@router.get("/sna/{log_id}")
async def get_social_network_analysis(
    log_id: UUID,
    network_type: str = "handover",
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get Social Network Analysis.
    
    Args:
        network_type: "handover" or "working_together"
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        if network_type == "handover":
            result = pm4py_service.calculate_sna_handover(log)
        elif network_type == "working_together":
            result = pm4py_service.calculate_sna_working_together(log)
        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid network_type. Use 'handover' or 'working_together'"
            )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SNA failed: {str(e)}")


@router.get("/roles/{log_id}")
async def get_organizational_roles(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Discover organizational roles based on activity-resource patterns.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.discover_organizational_roles(log)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Roles discovery failed: {str(e)}")


@router.get("/batches/{log_id}")
async def detect_batches(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Detect batch processing patterns in the event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.detect_batches(log)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch detection failed: {str(e)}")


@router.get("/transition-system/{log_id}")
async def get_transition_system(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Build transition system from event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.build_transition_system(log)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transition system failed: {str(e)}")


@router.get("/process-tree/{log_id}")
async def get_process_tree(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Discover process tree using inductive miner.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.discover_process_tree(log)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Process tree discovery failed: {str(e)}")


@router.get("/duration-stats/{log_id}")
async def get_case_duration_statistics(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get case duration statistics using PM4Py.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.get_case_duration_statistics(log)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Duration stats failed: {str(e)}")


@router.get("/arrival-rate/{log_id}")
async def get_case_arrival_rate(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get average case arrival rate.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.get_case_arrival_rate(log)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Arrival rate calculation failed: {str(e)}")


@router.get("/comprehensive/{log_id}")
async def get_comprehensive_analysis(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Run comprehensive PM4Py analysis.
    Returns all available analyses in a single response.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.get_comprehensive_analysis(log)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")


@router.get("/variants/{log_id}")
async def get_variants(
    log_id: UUID,
    top_n: int = 20,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get process variants with counts.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.get_variants(log, top_n)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Variants analysis failed: {str(e)}")


@router.get("/start-activities/{log_id}")
async def get_start_activities(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get start activities with frequencies.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.get_start_activities(log)
        return {"start_activities": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Start activities failed: {str(e)}")


@router.get("/end-activities/{log_id}")
async def get_end_activities(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get end activities with frequencies.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        result = pm4py_service.get_end_activities(log)
        return {"end_activities": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"End activities failed: {str(e)}")
