"""Organizational mining schemas - Social networks and resource analysis.

Contains schemas for:
- Social network graphs
- Resource roles and profiles
- Workload distribution
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class NetworkNode(BaseModel):
    """Node in a social network graph."""

    id: str
    label: str
    type: str = "resource"
    weight: float = 1.0


class NetworkEdge(BaseModel):
    """Edge in a social network graph."""

    source: str
    target: str
    weight: float
    label: str | None = None


class SocialNetworkResponse(BaseModel):
    """Social network response."""

    dataset_id: str
    network_type: str
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]
    metrics: dict[str, Any]


class ResourceRoleResponse(BaseModel):
    """Discovered organizational role."""

    role_id: str
    resources: list[str]
    activities: list[str]


class ResourceProfileResponse(BaseModel):
    """Resource profile details."""

    resource: str
    total_events: int
    activities: dict[str, int]
    avg_processing_time_seconds: float
    first_activity: datetime | None
    last_activity: datetime | None


class ResourceWorkloadResponse(BaseModel):
    """Resource workload distribution."""

    dataset_id: str
    workload: dict[str, int]
    avg_events_per_resource: float
