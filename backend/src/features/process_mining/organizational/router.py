"""Organizational Mining Router - Social Network Analysis API.

Resource and team behavior analysis from event logs.

## Business Context
Organizational mining analyzes how people work together:
- **Handover Network**: Who passes work to whom
- **Collaboration Network**: Who works on same cases
- **Resource Similarity**: Who does similar activities
- **Role Discovery**: Cluster resources by behavior
- **Resource Profiles**: Performance per individual

## Testing Instructions

### Prerequisites
1. Have a dataset with a "resource" column mapped

### Endpoints
- **Handover**: `GET /api/v1/organizational/datasets/{id}/handover-network`
- **Collaboration**: `GET /api/v1/organizational/datasets/{id}/collaboration-network`
- **Similarity**: `GET /api/v1/organizational/datasets/{id}/resource-similarity`
- **Roles**: `GET /api/v1/organizational/datasets/{id}/roles`
- **Profile**: `GET /api/v1/organizational/datasets/{id}/resources/{name}/profile`
- **Workload**: `GET /api/v1/organizational/datasets/{id}/workload`

### Common Errors
- **404**: Dataset not found
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from src.api.dependencies import CurrentUser, ReadDBSession, ServiceContainer
from src.features.process_mining.models import Dataset
from src.features.process_mining.schemas import (
    NetworkEdge,
    NetworkNode,
    ResourceProfileResponse,
    ResourceRoleResponse,
    ResourceWorkloadResponse,
    SocialNetworkResponse,
)
from src.platform.core.logging_config import get_logger
from src.platform.core.permissions import Permission
from src.platform.workspaces.authorization import require_dataset_permission
from src.platform.core.exceptions import NotFoundError

logger = get_logger(__name__)

router = APIRouter(prefix="/organizational", tags=["Organizational Mining"])


async def _get_pm4py_log(dataset_id: str, db: ReadDBSession, container: ServiceContainer):
    """Helper to get PM4Py log from dataset_id."""
    query = select(Dataset).where(Dataset.id == dataset_id)
    result = await db.execute(query)
    event_log = result.scalar_one_or_none()
    if not event_log:
        raise NotFoundError(resource='Dataset', resource_id=dataset_id)
    return container.filtering.to_pm4py_log(event_log)


@router.get("/datasets/{dataset_id}/handover-network", response_model=SocialNetworkResponse)
async def get_handover_network(
    dataset_id: str, db: ReadDBSession, user: CurrentUser, container: ServiceContainer
) -> SocialNetworkResponse:
    """Discover handover of work network."""
    await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    logger.info("getting_handover_network", dataset_id=dataset_id)
    pm4py_log = await _get_pm4py_log(dataset_id, db, container)
    result = container.organizational.discover_handover_network(pm4py_log)
    return SocialNetworkResponse(
        dataset_id=dataset_id,
        network_type=result["network_type"],
        nodes=[NetworkNode(**n) for n in result["nodes"]],
        edges=[NetworkEdge(**e) for e in result["edges"]],
        metrics=result["metrics"],
    )


@router.get("/datasets/{dataset_id}/collaboration-network", response_model=SocialNetworkResponse)
async def get_collaboration_network(
    dataset_id: str, db: ReadDBSession, user: CurrentUser, container: ServiceContainer
) -> SocialNetworkResponse:
    """Discover working together network."""
    await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    logger.info("getting_collaboration_network", dataset_id=dataset_id)
    pm4py_log = await _get_pm4py_log(dataset_id, db, container)
    result = container.organizational.discover_working_together_network(pm4py_log)
    return SocialNetworkResponse(
        dataset_id=dataset_id,
        network_type=result["network_type"],
        nodes=[NetworkNode(**n) for n in result["nodes"]],
        edges=[NetworkEdge(**e) for e in result["edges"]],
        metrics=result["metrics"],
    )


@router.get("/datasets/{dataset_id}/resource-similarity", response_model=SocialNetworkResponse)
async def get_resource_similarity(
    dataset_id: str, db: ReadDBSession, user: CurrentUser, container: ServiceContainer
) -> SocialNetworkResponse:
    """Discover resource similarity based on activities."""
    await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    logger.info("getting_resource_similarity", dataset_id=dataset_id)
    pm4py_log = await _get_pm4py_log(dataset_id, db, container)
    result = container.organizational.discover_resource_similarity(pm4py_log)
    return SocialNetworkResponse(
        dataset_id=dataset_id,
        network_type=result["network_type"],
        nodes=[NetworkNode(**n) for n in result["nodes"]],
        edges=[NetworkEdge(**e) for e in result["edges"]],
        metrics=result["metrics"],
    )


@router.get("/datasets/{dataset_id}/roles", response_model=list[ResourceRoleResponse])
async def get_roles(
    dataset_id: str, db: ReadDBSession, user: CurrentUser, container: ServiceContainer
) -> list[ResourceRoleResponse]:
    """Discover organizational roles."""
    await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    logger.info("getting_roles", dataset_id=dataset_id)
    pm4py_log = await _get_pm4py_log(dataset_id, db, container)
    result = container.organizational.discover_roles(pm4py_log)
    return [ResourceRoleResponse(**r) for r in result]


@router.get(
    "/datasets/{dataset_id}/resources/{resource}/profile", response_model=ResourceProfileResponse
)
async def get_resource_profile(
    dataset_id: str, resource: str, db: ReadDBSession, user: CurrentUser, container: ServiceContainer
) -> ResourceProfileResponse:
    """Get detailed profile for a specific resource."""
    await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    logger.info("getting_resource_profile", dataset_id=dataset_id, resource=resource)
    pm4py_log = await _get_pm4py_log(dataset_id, db, container)
    result = container.organizational.get_resource_profile(pm4py_log, resource)
    return ResourceProfileResponse(**result)


@router.get("/datasets/{dataset_id}/workload", response_model=ResourceWorkloadResponse)
async def get_workload(
    dataset_id: str, db: ReadDBSession, user: CurrentUser, container: ServiceContainer
) -> ResourceWorkloadResponse:
    """Get workload distribution across resources."""
    await require_dataset_permission(db, dataset_id, user, Permission.DATASET_READ)
    logger.info("getting_workload", dataset_id=dataset_id)
    pm4py_log = await _get_pm4py_log(dataset_id, db, container)
    result = container.organizational.get_resource_workload(pm4py_log)
    return ResourceWorkloadResponse(dataset_id=dataset_id, **result)
