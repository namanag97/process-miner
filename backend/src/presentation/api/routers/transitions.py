"""Transitions API Router - DFG Edge Analysis."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.application.core.transition_service import transition_service
from src.presentation.api.routers.auth import require_auth, User


router = APIRouter(prefix="/transitions")


class TransitionResponse(BaseModel):
    """Response model for a single transition."""
    source_activity: str
    target_activity: str
    frequency: int
    probability: float
    avg_duration_seconds: float
    min_duration_seconds: float
    max_duration_seconds: float


class TransitionsResponse(BaseModel):
    """Response model for transitions list."""
    log_id: str
    transitions: List[TransitionResponse]
    statistics: Dict[str, Any]


class GatewayResponse(BaseModel):
    """Response model for a gateway."""
    activity: str
    gateway_type: str
    direction: str
    branches: List[str]


class StartEndActivitiesResponse(BaseModel):
    """Response model for start/end activities."""
    start_activities: Dict[str, int]
    end_activities: Dict[str, int]


@router.get("/{log_id}", response_model=TransitionsResponse)
async def get_transitions(
    log_id: UUID,
    include_duration: bool = True,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get all DFG transitions for an event log.
    
    Returns transitions sorted by frequency (descending).
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        transitions = transition_service.compute_transitions(
            log,
            include_duration=include_duration,
        )
        
        # Apply limit
        transitions = transitions[:limit]
        
        # Get statistics
        all_transitions = transition_service.compute_transitions(log, include_duration=False)
        stats = transition_service.get_transition_statistics(all_transitions)
        
        return TransitionsResponse(
            log_id=str(log_id),
            transitions=[
                TransitionResponse(
                    source_activity=t.source_activity,
                    target_activity=t.target_activity,
                    frequency=t.frequency,
                    probability=t.probability,
                    avg_duration_seconds=t.avg_duration_seconds,
                    min_duration_seconds=t.min_duration_seconds,
                    max_duration_seconds=t.max_duration_seconds,
                )
                for t in transitions
            ],
            statistics=stats,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{log_id}/gateways", response_model=List[GatewayResponse])
async def get_gateways(
    log_id: UUID,
    threshold: int = 2,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Detect gateways (splits and joins) in the process.
    
    Args:
        threshold: Minimum branches to consider a gateway (default: 2)
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        transitions = transition_service.compute_transitions(log, include_duration=False)
        gateways = transition_service.detect_gateways(transitions, threshold=threshold)
        
        return [
            GatewayResponse(
                activity=g.activity,
                gateway_type=g.gateway_type.value,
                direction=g.direction.value,
                branches=list(g.branches),
            )
            for g in gateways
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{log_id}/start-end", response_model=StartEndActivitiesResponse)
async def get_start_end_activities(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get start and end activities for an event log.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        start_acts = transition_service.get_start_activities(log)
        end_acts = transition_service.get_end_activities(log)
        
        return StartEndActivitiesResponse(
            start_activities=start_acts,
            end_activities=end_acts,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{log_id}/activity/{activity_name}")
async def get_activity_transitions(
    log_id: UUID,
    activity_name: str,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get all transitions involving a specific activity.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        all_transitions = transition_service.compute_transitions(log)
        
        # Filter for transitions involving this activity
        incoming = [t.to_dict() for t in all_transitions if t.target_activity == activity_name]
        outgoing = [t.to_dict() for t in all_transitions if t.source_activity == activity_name]
        
        return {
            "activity": activity_name,
            "incoming_transitions": incoming,
            "outgoing_transitions": outgoing,
            "total_incoming": sum(t["frequency"] for t in incoming),
            "total_outgoing": sum(t["frequency"] for t in outgoing),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
