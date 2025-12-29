"""Processes Organization Sub-Router."""

from collections import defaultdict
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.presentation.api.routers.auth import User, require_auth
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

router = APIRouter()


class ResourceResponse(BaseModel):
    id: str
    identifier: str
    name: Optional[str]
    role: Optional[str]
    total_activities: int
    total_cases: int
    frequent_activities: List[Dict[str, Any]]


class HandoverEdge(BaseModel):
    from_resource: str
    to_resource: str
    activity: str
    frequency: int


class HandoverNetworkResponse(BaseModel):
    process_id: str
    total_resources: int
    total_handovers: int
    nodes: List[Dict[str, Any]]
    edges: List[HandoverEdge]


class WorkingTogetherEdge(BaseModel):
    resource_a: str
    resource_b: str
    shared_cases: int


class WorkingTogetherResponse(BaseModel):
    process_id: str
    total_resources: int
    nodes: List[Dict[str, Any]]
    edges: List[WorkingTogetherEdge]


class RoleCluster(BaseModel):
    role_id: str
    role_name: str
    resources: List[str]
    common_activities: List[str]


class RoleMiningResponse(BaseModel):
    process_id: str
    total_resources: int
    discovered_roles: int
    roles: List[RoleCluster]


class WorkloadResponse(BaseModel):
    process_id: str
    resources: List[Dict[str, Any]]
    avg_activities_per_resource: float
    max_workload_resource: Optional[str]


@router.get("/resources", response_model=List[ResourceResponse])
async def get_resources(
    process_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")

    resource_data = defaultdict(lambda: {"activities": defaultdict(int), "cases": set()})
    for case in log.cases or []:
        for event in case.events or []:
            if event.resource:
                resource_data[event.resource]["activities"][event.activity_name] += 1
                resource_data[event.resource]["cases"].add(case.case_id)

    resources = []
    for r_id, data in list(resource_data.items())[:limit]:
        freq_acts = sorted(data["activities"].items(), key=lambda x: x[1], reverse=True)[:5]
        resources.append(
            ResourceResponse(
                id=r_id,
                identifier=r_id,
                name=None,
                role=None,
                total_activities=sum(data["activities"].values()),
                total_cases=len(data["cases"]),
                frequent_activities=[{"activity": a, "count": c} for a, c in freq_acts],
            )
        )
    return resources


@router.get("/handover-network", response_model=HandoverNetworkResponse)
async def get_handover_network(
    process_id: UUID,
    min_frequency: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")

    handovers = defaultdict(int)
    resources = set()

    for case in log.cases or []:
        events = sorted(case.events or [], key=lambda e: e.timestamp)
        for i in range(len(events) - 1):
            if events[i].resource and events[i + 1].resource:
                r1, r2 = events[i].resource, events[i + 1].resource
                if r1 != r2:
                    handovers[(r1, r2, events[i + 1].activity_name)] += 1
                    resources.add(r1)
                    resources.add(r2)

    edges = [
        HandoverEdge(from_resource=r1, to_resource=r2, activity=act, frequency=freq)
        for (r1, r2, act), freq in handovers.items()
        if freq >= min_frequency
    ]

    return HandoverNetworkResponse(
        process_id=str(process_id),
        total_resources=len(resources),
        total_handovers=len(edges),
        nodes=[{"id": r, "label": r} for r in resources],
        edges=edges,
    )


@router.get("/working-together", response_model=WorkingTogetherResponse)
async def get_working_together(
    process_id: UUID,
    min_shared_cases: int = Query(1, ge=1),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")

    case_resources = defaultdict(set)
    for case in log.cases or []:
        for event in case.events or []:
            if event.resource:
                case_resources[case.case_id].add(event.resource)

    together = defaultdict(int)
    resources = set()
    for case_id, res_set in case_resources.items():
        res_list = list(res_set)
        resources.update(res_set)
        for i in range(len(res_list)):
            for j in range(i + 1, len(res_list)):
                pair = tuple(sorted([res_list[i], res_list[j]]))
                together[pair] += 1

    edges = [
        WorkingTogetherEdge(resource_a=p[0], resource_b=p[1], shared_cases=c)
        for p, c in together.items()
        if c >= min_shared_cases
    ]

    return WorkingTogetherResponse(
        process_id=str(process_id),
        total_resources=len(resources),
        nodes=[{"id": r, "label": r} for r in resources],
        edges=edges,
    )


@router.get("/roles", response_model=RoleMiningResponse)
async def discover_roles(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")

    resource_acts = defaultdict(set)
    for case in log.cases or []:
        for event in case.events or []:
            if event.resource:
                resource_acts[event.resource].add(event.activity_name)

    # Simple clustering by activity set
    role_clusters = defaultdict(list)
    for res, acts in resource_acts.items():
        key = tuple(sorted(acts))
        role_clusters[key].append(res)

    roles = []
    for i, (acts, members) in enumerate(role_clusters.items()):
        roles.append(
            RoleCluster(
                role_id=f"role_{i + 1}",
                role_name=f"Role {i + 1}" if len(acts) > 3 else "-".join(acts[:3]),
                resources=members,
                common_activities=list(acts),
            )
        )

    return RoleMiningResponse(
        process_id=str(process_id),
        total_resources=len(resource_acts),
        discovered_roles=len(roles),
        roles=roles,
    )


@router.get("/workload", response_model=WorkloadResponse)
async def get_workload(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process not found")

    workload = defaultdict(int)
    for case in log.cases or []:
        for event in case.events or []:
            if event.resource:
                workload[event.resource] += 1

    if not workload:
        return WorkloadResponse(
            process_id=str(process_id),
            resources=[],
            avg_activities_per_resource=0,
            max_workload_resource=None,
        )

    resources = [{"resource": r, "activities": c} for r, c in workload.items()]
    avg = sum(workload.values()) / len(workload)
    max_r = max(workload.items(), key=lambda x: x[1])[0]

    return WorkloadResponse(
        process_id=str(process_id),
        resources=resources,
        avg_activities_per_resource=avg,
        max_workload_resource=max_r,
    )
