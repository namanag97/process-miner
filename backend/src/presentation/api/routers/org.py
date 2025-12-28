"""Organizational Mining API Router.

Phase 5.2: Social Network Analysis & Org Mining
Covers business activities: ORG-001 to ORG-007, ORG-008 to ORG-010
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.infrastructure.persistence.models import (
    ResourceProfileModel,
    HandoffModel,
)
from src.presentation.api.routers.auth import require_auth, User


router = APIRouter(prefix="/org")


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class ResourceResponse(BaseModel):
    """Resource profile with workload metrics."""
    id: str
    identifier: str
    name: Optional[str]
    role: Optional[str]
    department: Optional[str]
    total_activities: int
    total_cases: int
    avg_activities_per_case: float
    frequent_activities: List[Dict[str, Any]]


class HandoverEdge(BaseModel):
    """An edge in the handover network."""
    from_resource: str
    to_resource: str
    activity: str
    frequency: int
    avg_handoff_time_seconds: float


class HandoverNetworkResponse(BaseModel):
    """Handover of work network - social network analysis."""
    log_id: str
    total_resources: int
    total_handovers: int
    nodes: List[Dict[str, Any]]
    edges: List[HandoverEdge]


class WorkingTogetherEdge(BaseModel):
    """An edge in the working together network."""
    resource_a: str
    resource_b: str
    shared_cases: int
    collaboration_score: float


class WorkingTogetherNetworkResponse(BaseModel):
    """Working together network - resources collaborating on same cases."""
    log_id: str
    total_resources: int
    nodes: List[Dict[str, Any]]
    edges: List[WorkingTogetherEdge]


class RoleCluster(BaseModel):
    """A discovered organizational role cluster."""
    role_id: str
    role_name: str
    resources: List[str]
    common_activities: List[str]
    avg_workload: float


class RoleMiningResponse(BaseModel):
    """Discovered organizational roles."""
    log_id: str
    total_resources: int
    discovered_roles: int
    roles: List[RoleCluster]


class ResourceWorkloadResponse(BaseModel):
    """Resource workload analysis."""
    log_id: str
    resources: List[Dict[str, Any]]
    avg_activities_per_resource: float
    max_workload_resource: Optional[str]
    min_workload_resource: Optional[str]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_uuid() -> str:
    """Generate a UUID string."""
    from uuid import uuid4
    return str(uuid4())


async def extract_resources(log) -> Dict[str, Dict[str, Any]]:
    """Extract resource profiles from event log."""
    resources = {}
    
    for case in log.cases:
        case_resources = set()
        for event in case.events:
            resource = str(event.resource) if event.resource else None
            if resource and resource != "None":
                if resource not in resources:
                    resources[resource] = {
                        "identifier": resource,
                        "total_activities": 0,
                        "cases": set(),
                        "activities": {},
                    }
                resources[resource]["total_activities"] += 1
                resources[resource]["cases"].add(str(case.case_id))
                
                activity = str(event.activity)
                if activity not in resources[resource]["activities"]:
                    resources[resource]["activities"][activity] = 0
                resources[resource]["activities"][activity] += 1
                case_resources.add(resource)
    
    return resources


async def calculate_handovers(log) -> List[Dict[str, Any]]:
    """Calculate handover of work network."""
    handovers = {}
    
    for case in log.cases:
        sorted_events = sorted(case.events, key=lambda e: e.timestamp.value)
        
        for i in range(len(sorted_events) - 1):
            from_resource = str(sorted_events[i].resource) if sorted_events[i].resource else None
            to_resource = str(sorted_events[i + 1].resource) if sorted_events[i + 1].resource else None
            
            if from_resource and to_resource and from_resource != to_resource and from_resource != "None" and to_resource != "None":
                activity = str(sorted_events[i + 1].activity)
                key = (from_resource, to_resource, activity)
                
                if key not in handovers:
                    handovers[key] = {
                        "from_resource": from_resource,
                        "to_resource": to_resource,
                        "activity": activity,
                        "frequency": 0,
                        "times": [],
                    }
                
                handovers[key]["frequency"] += 1
                
                try:
                    time_diff = (sorted_events[i + 1].timestamp.value - sorted_events[i].timestamp.value).total_seconds()
                    if time_diff >= 0:
                        handovers[key]["times"].append(time_diff)
                except:
                    pass
    
    # Calculate averages
    result = []
    for key, data in handovers.items():
        avg_time = sum(data["times"]) / len(data["times"]) if data["times"] else 0
        result.append({
            "from_resource": data["from_resource"],
            "to_resource": data["to_resource"],
            "activity": data["activity"],
            "frequency": data["frequency"],
            "avg_handoff_time_seconds": round(avg_time, 2),
        })
    
    return sorted(result, key=lambda x: x["frequency"], reverse=True)


async def calculate_working_together(log) -> List[Dict[str, Any]]:
    """Calculate working together network - resources on same cases."""
    case_resources = {}
    
    # Get resources per case
    for case in log.cases:
        case_id = str(case.case_id)
        case_resources[case_id] = set()
        for event in case.events:
            resource = str(event.resource) if event.resource else None
            if resource and resource != "None":
                case_resources[case_id].add(resource)
    
    # Calculate co-occurrence
    pairs = {}
    for case_id, resources in case_resources.items():
        resource_list = list(resources)
        for i in range(len(resource_list)):
            for j in range(i + 1, len(resource_list)):
                r1, r2 = sorted([resource_list[i], resource_list[j]])
                key = (r1, r2)
                if key not in pairs:
                    pairs[key] = 0
                pairs[key] += 1
    
    # Build edges
    total_cases = len(case_resources)
    result = []
    for (r1, r2), count in pairs.items():
        result.append({
            "resource_a": r1,
            "resource_b": r2,
            "shared_cases": count,
            "collaboration_score": round(count / total_cases, 4) if total_cases > 0 else 0,
        })
    
    return sorted(result, key=lambda x: x["shared_cases"], reverse=True)


async def discover_roles(resources: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Discover organizational roles by clustering resources with similar activities."""
    if not resources:
        return []
    
    # Group resources by their activity patterns
    activity_signatures = {}
    for resource, data in resources.items():
        # Create signature from top activities
        top_activities = sorted(data["activities"].items(), key=lambda x: x[1], reverse=True)[:5]
        signature = tuple(sorted([a[0] for a in top_activities]))
        
        if signature not in activity_signatures:
            activity_signatures[signature] = []
        activity_signatures[signature].append(resource)
    
    # Create role clusters
    roles = []
    for idx, (signature, members) in enumerate(activity_signatures.items()):
        if len(members) >= 1:  # Only create roles with at least 1 member
            total_workload = sum(resources[m]["total_activities"] for m in members)
            roles.append({
                "role_id": generate_uuid(),
                "role_name": f"Role {idx + 1}" if len(signature) == 0 else f"Role: {', '.join(list(signature)[:3])}...",
                "resources": members,
                "common_activities": list(signature),
                "avg_workload": round(total_workload / len(members), 2),
            })
    
    return sorted(roles, key=lambda x: len(x["resources"]), reverse=True)


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.get("/resources/{log_id}", response_model=List[ResourceResponse])
async def get_resources(
    log_id: UUID,
    limit: int = Query(default=50, le=200),
    sort_by: str = Query(default="total_activities", pattern="^(total_activities|total_cases|identifier)$"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get list of resources (performers) extracted from the event log.
    
    Returns resource profiles with workload metrics and frequent activities.
    
    **Sort Options:**
    - total_activities: Most active resources first
    - total_cases: Resources handling most cases first
    - identifier: Alphabetical order
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Check for existing resource profiles
        stmt = select(ResourceProfileModel).where(
            ResourceProfileModel.log_id == str(log_id)
        )
        result = await session.execute(stmt)
        existing = list(result.scalars())
        
        if existing:
            # Return from stored profiles
            resources = []
            for r in existing:
                frequent = json.loads(r.frequent_activities_json) if r.frequent_activities_json else []
                resources.append(ResourceResponse(
                    id=r.id,
                    identifier=r.identifier,
                    name=r.name,
                    role=r.role,
                    department=r.department,
                    total_activities=r.total_activities,
                    total_cases=r.total_cases,
                    avg_activities_per_case=r.avg_activities_per_case,
                    frequent_activities=frequent,
                ))
            
            # Sort
            if sort_by == "total_cases":
                resources.sort(key=lambda x: x.total_cases, reverse=True)
            elif sort_by == "identifier":
                resources.sort(key=lambda x: x.identifier)
            else:
                resources.sort(key=lambda x: x.total_activities, reverse=True)
            
            return resources[:limit]
        
        # Extract from log
        resource_data = await extract_resources(log)
        
        # Build response and persist
        resources = []
        for identifier, data in resource_data.items():
            frequent = sorted(data["activities"].items(), key=lambda x: x[1], reverse=True)[:10]
            frequent_list = [{"activity": a, "count": c} for a, c in frequent]
            
            resource_id = generate_uuid()
            total_cases = len(data["cases"])
            avg_per_case = data["total_activities"] / total_cases if total_cases > 0 else 0
            
            # Persist
            profile = ResourceProfileModel(
                id=resource_id,
                log_id=str(log_id),
                identifier=identifier,
                total_activities=data["total_activities"],
                total_cases=total_cases,
                avg_activities_per_case=round(avg_per_case, 2),
                frequent_activities_json=json.dumps(frequent_list),
            )
            session.add(profile)
            
            resources.append(ResourceResponse(
                id=resource_id,
                identifier=identifier,
                name=None,
                role=None,
                department=None,
                total_activities=data["total_activities"],
                total_cases=total_cases,
                avg_activities_per_case=round(avg_per_case, 2),
                frequent_activities=frequent_list,
            ))
        
        await session.commit()
        
        # Sort
        if sort_by == "total_cases":
            resources.sort(key=lambda x: x.total_cases, reverse=True)
        elif sort_by == "identifier":
            resources.sort(key=lambda x: x.identifier)
        else:
            resources.sort(key=lambda x: x.total_activities, reverse=True)
        
        return resources[:limit]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resource extraction failed: {str(e)}")


@router.get("/handover-network/{log_id}", response_model=HandoverNetworkResponse)
async def get_handover_network(
    log_id: UUID,
    min_frequency: int = Query(default=1, ge=1),
    limit: int = Query(default=100, le=500),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Discover handover of work network.
    
    Shows how work is transferred between resources - social network analysis.
    Useful for identifying bottlenecks in handoffs and collaboration patterns.
    
    **Filters:**
    - min_frequency: Minimum handoff occurrences to include
    - limit: Maximum number of edges to return
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Check for existing handoffs
        stmt = select(HandoffModel).where(
            HandoffModel.log_id == str(log_id),
            HandoffModel.frequency >= min_frequency
        ).order_by(HandoffModel.frequency.desc()).limit(limit)
        result = await session.execute(stmt)
        existing = list(result.scalars())
        
        if existing:
            # Build from stored data
            resource_set = set()
            edges = []
            for h in existing:
                resource_set.add(h.from_resource)
                resource_set.add(h.to_resource)
                edges.append(HandoverEdge(
                    from_resource=h.from_resource,
                    to_resource=h.to_resource,
                    activity=h.activity,
                    frequency=h.frequency,
                    avg_handoff_time_seconds=h.avg_handoff_time_seconds,
                ))
            
            nodes = [{"id": r, "label": r} for r in resource_set]
            
            return HandoverNetworkResponse(
                log_id=str(log_id),
                total_resources=len(resource_set),
                total_handovers=len(edges),
                nodes=nodes,
                edges=edges,
            )
        
        # Calculate from log
        handovers = await calculate_handovers(log)
        
        # Filter and persist
        resource_set = set()
        edges = []
        for h in handovers:
            if h["frequency"] >= min_frequency:
                resource_set.add(h["from_resource"])
                resource_set.add(h["to_resource"])
                
                # Persist
                handoff = HandoffModel(
                    id=generate_uuid(),
                    log_id=str(log_id),
                    from_resource=h["from_resource"],
                    to_resource=h["to_resource"],
                    activity=h["activity"],
                    frequency=h["frequency"],
                    avg_handoff_time_seconds=h["avg_handoff_time_seconds"],
                )
                session.add(handoff)
                
                edges.append(HandoverEdge(**h))
                
                if len(edges) >= limit:
                    break
        
        await session.commit()
        
        nodes = [{"id": r, "label": r} for r in resource_set]
        
        return HandoverNetworkResponse(
            log_id=str(log_id),
            total_resources=len(resource_set),
            total_handovers=len(edges),
            nodes=nodes,
            edges=edges,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Handover network discovery failed: {str(e)}")


@router.get("/working-together/{log_id}", response_model=WorkingTogetherNetworkResponse)
async def get_working_together_network(
    log_id: UUID,
    min_shared_cases: int = Query(default=1, ge=1),
    limit: int = Query(default=100, le=500),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Discover working together network.
    
    Shows which resources work together on the same cases.
    Higher collaboration scores indicate resources that frequently work on cases together.
    
    **Filters:**
    - min_shared_cases: Minimum number of shared cases to include edge
    - limit: Maximum number of edges to return
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Calculate from log (always calculate fresh for working-together)
        pairs = await calculate_working_together(log)
        
        # Filter
        resource_set = set()
        edges = []
        for p in pairs:
            if p["shared_cases"] >= min_shared_cases:
                resource_set.add(p["resource_a"])
                resource_set.add(p["resource_b"])
                edges.append(WorkingTogetherEdge(**p))
                
                if len(edges) >= limit:
                    break
        
        nodes = [{"id": r, "label": r} for r in resource_set]
        
        return WorkingTogetherNetworkResponse(
            log_id=str(log_id),
            total_resources=len(resource_set),
            nodes=nodes,
            edges=edges,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Working together network discovery failed: {str(e)}")


@router.get("/roles/{log_id}", response_model=RoleMiningResponse)
async def discover_organizational_roles(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Discover organizational roles from the event log.
    
    Clusters resources based on their activity patterns to identify
    functional roles (e.g., "Approver", "Clerk", "Manager").
    
    Uses activity similarity to group resources into roles.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Extract resources
        resource_data = await extract_resources(log)
        
        # Discover roles
        roles = await discover_roles(resource_data)
        
        return RoleMiningResponse(
            log_id=str(log_id),
            total_resources=len(resource_data),
            discovered_roles=len(roles),
            roles=[RoleCluster(**r) for r in roles],
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Role mining failed: {str(e)}")


@router.get("/workload/{log_id}", response_model=ResourceWorkloadResponse)
async def get_resource_workload(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get resource workload analysis.
    
    Shows workload distribution across resources, identifying
    overloaded and underutilized resources.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Extract resources
        resource_data = await extract_resources(log)
        
        if not resource_data:
            return ResourceWorkloadResponse(
                log_id=str(log_id),
                resources=[],
                avg_activities_per_resource=0,
                max_workload_resource=None,
                min_workload_resource=None,
            )
        
        # Build workload summary
        resources = []
        for identifier, data in resource_data.items():
            resources.append({
                "identifier": identifier,
                "total_activities": data["total_activities"],
                "total_cases": len(data["cases"]),
            })
        
        # Sort by workload
        resources.sort(key=lambda x: x["total_activities"], reverse=True)
        
        total_activities = sum(r["total_activities"] for r in resources)
        avg_activities = total_activities / len(resources) if resources else 0
        
        return ResourceWorkloadResponse(
            log_id=str(log_id),
            resources=resources,
            avg_activities_per_resource=round(avg_activities, 2),
            max_workload_resource=resources[0]["identifier"] if resources else None,
            min_workload_resource=resources[-1]["identifier"] if resources else None,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workload analysis failed: {str(e)}")
