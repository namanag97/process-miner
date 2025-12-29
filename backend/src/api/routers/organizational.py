"""Organizational Mining Router - Social Network Analysis API.

Provides endpoints for handover networks, working together networks,
resource similarity, role discovery, and resource profiling.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.core.logging_config import get_logger
from src.models.orm import EventLog
from src.models.schemas import (
    NetworkEdge,
    NetworkNode,
    ResourceProfileResponse,
    ResourceRoleResponse,
    ResourceWorkloadResponse,
    SocialNetworkResponse,
)
from src.services.filtering import filtering_service
from src.services.organizational import organizational_service

logger = get_logger(__name__)

router = APIRouter(prefix="/organizational", tags=["Organizational Mining"])


async def _get_pm4py_log(log_id: str, db: AsyncSession):
    """Helper to get PM4Py log from log_id."""
    query = select(EventLog).where(EventLog.id == log_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail=f"Event log {log_id} not found")
    return filtering_service.to_pm4py_log(event_log)


@router.get("/logs/{log_id}/handover-network", response_model=SocialNetworkResponse)
async def get_handover_network(log_id: str, db: AsyncSession = Depends(get_db)) -> SocialNetworkResponse:
    """Discover handover of work network."""
    logger.info("getting_handover_network", log_id=log_id)
    pm4py_log = await _get_pm4py_log(log_id, db)
    result = organizational_service.discover_handover_network(pm4py_log)
    return SocialNetworkResponse(
        log_id=log_id,
        network_type=result["network_type"],
        nodes=[NetworkNode(**n) for n in result["nodes"]],
        edges=[NetworkEdge(**e) for e in result["edges"]],
        metrics=result["metrics"],
    )


@router.get("/logs/{log_id}/collaboration-network", response_model=SocialNetworkResponse)
async def get_collaboration_network(log_id: str, db: AsyncSession = Depends(get_db)) -> SocialNetworkResponse:
    """Discover working together network."""
    logger.info("getting_collaboration_network", log_id=log_id)
    pm4py_log = await _get_pm4py_log(log_id, db)
    result = organizational_service.discover_working_together_network(pm4py_log)
    return SocialNetworkResponse(
        log_id=log_id,
        network_type=result["network_type"],
        nodes=[NetworkNode(**n) for n in result["nodes"]],
        edges=[NetworkEdge(**e) for e in result["edges"]],
        metrics=result["metrics"],
    )


@router.get("/logs/{log_id}/resource-similarity", response_model=SocialNetworkResponse)
async def get_resource_similarity(log_id: str, db: AsyncSession = Depends(get_db)) -> SocialNetworkResponse:
    """Discover resource similarity based on activities."""
    logger.info("getting_resource_similarity", log_id=log_id)
    pm4py_log = await _get_pm4py_log(log_id, db)
    result = organizational_service.discover_resource_similarity(pm4py_log)
    return SocialNetworkResponse(
        log_id=log_id,
        network_type=result["network_type"],
        nodes=[NetworkNode(**n) for n in result["nodes"]],
        edges=[NetworkEdge(**e) for e in result["edges"]],
        metrics=result["metrics"],
    )


@router.get("/logs/{log_id}/roles")
async def get_roles(log_id: str, db: AsyncSession = Depends(get_db)) -> list[ResourceRoleResponse]:
    """Discover organizational roles."""
    logger.info("getting_roles", log_id=log_id)
    pm4py_log = await _get_pm4py_log(log_id, db)
    result = organizational_service.discover_roles(pm4py_log)
    return [ResourceRoleResponse(**r) for r in result]


@router.get("/logs/{log_id}/resources/{resource}/profile", response_model=ResourceProfileResponse)
async def get_resource_profile(log_id: str, resource: str, db: AsyncSession = Depends(get_db)) -> ResourceProfileResponse:
    """Get detailed profile for a specific resource."""
    logger.info("getting_resource_profile", log_id=log_id, resource=resource)
    pm4py_log = await _get_pm4py_log(log_id, db)
    result = organizational_service.get_resource_profile(pm4py_log, resource)
    return ResourceProfileResponse(**result)


@router.get("/logs/{log_id}/workload", response_model=ResourceWorkloadResponse)
async def get_workload(log_id: str, db: AsyncSession = Depends(get_db)) -> ResourceWorkloadResponse:
    """Get workload distribution across resources."""
    logger.info("getting_workload", log_id=log_id)
    pm4py_log = await _get_pm4py_log(log_id, db)
    result = organizational_service.get_resource_workload(pm4py_log)
    return ResourceWorkloadResponse(log_id=log_id, **result)
