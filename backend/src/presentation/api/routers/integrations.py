"""Integrations API Router."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

from src.application.generic.integration_service import (
    integration_service,
    ConnectorType,
)
from src.presentation.api.routers.auth import require_auth, User


router = APIRouter(prefix="/integrations")


class CreateConnectorRequest(BaseModel):
    name: str
    connector_type: str
    settings: Dict[str, Any]


class ConnectorResponse(BaseModel):
    id: str
    name: str
    connector_type: str
    status: str
    last_sync: Optional[str]
    created_at: str


class SyncRequest(BaseModel):
    query: Optional[Dict[str, Any]] = None


class SyncResultResponse(BaseModel):
    connector_id: str
    success: bool
    records_synced: int
    errors: List[str]
    started_at: str
    completed_at: Optional[str]


class ConnectorTypeInfo(BaseModel):
    type: str
    name: str
    description: str
    config_fields: List[str]


@router.get("/connector-types", response_model=List[ConnectorTypeInfo])
async def list_connector_types(user: User = Depends(require_auth)):
    """List available connector types."""
    types = integration_service.get_available_connector_types()
    return [ConnectorTypeInfo(**t) for t in types]


@router.post("/connectors", response_model=ConnectorResponse)
async def create_connector(
    request: CreateConnectorRequest,
    user: User = Depends(require_auth),
):
    """Create a new connector."""
    try:
        connector_type = ConnectorType(request.connector_type)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid connector type: {request.connector_type}"
        )
    
    config = integration_service.create_connector(
        name=request.name,
        connector_type=connector_type,
        settings=request.settings,
    )
    
    return ConnectorResponse(**config.to_dict())


@router.get("/connectors", response_model=List[ConnectorResponse])
async def list_connectors(user: User = Depends(require_auth)):
    """List all configured connectors."""
    connectors = integration_service.list_connectors()
    return [ConnectorResponse(**c) for c in connectors]


@router.get("/connectors/{connector_id}", response_model=ConnectorResponse)
async def get_connector(
    connector_id: UUID,
    user: User = Depends(require_auth),
):
    """Get connector details."""
    config = integration_service.get_connector(connector_id)
    if not config:
        raise HTTPException(status_code=404, detail="Connector not found")
    return ConnectorResponse(**config.to_dict())


@router.delete("/connectors/{connector_id}")
async def delete_connector(
    connector_id: UUID,
    user: User = Depends(require_auth),
):
    """Delete a connector."""
    deleted = integration_service.delete_connector(connector_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Connector not found")
    return {"message": "Connector deleted"}


@router.post("/connectors/{connector_id}/connect")
async def connect(
    connector_id: UUID,
    user: User = Depends(require_auth),
):
    """Connect to external system."""
    success = await integration_service.connect(connector_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to connect")
    return {"message": "Connected"}


@router.post("/connectors/{connector_id}/disconnect")
async def disconnect(
    connector_id: UUID,
    user: User = Depends(require_auth),
):
    """Disconnect from external system."""
    success = await integration_service.disconnect(connector_id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to disconnect")
    return {"message": "Disconnected"}


@router.post("/connectors/{connector_id}/test")
async def test_connection(
    connector_id: UUID,
    user: User = Depends(require_auth),
):
    """Test connector connection."""
    result = await integration_service.test_connection(connector_id)
    return result


@router.post("/connectors/{connector_id}/sync", response_model=SyncResultResponse)
async def sync_data(
    connector_id: UUID,
    request: SyncRequest = None,
    user: User = Depends(require_auth),
):
    """Synchronize data from external system."""
    result = await integration_service.sync_data(
        connector_id=connector_id,
        query=request.query if request else None,
    )
    return SyncResultResponse(**result.to_dict())


@router.get("/connectors/{connector_id}/tables")
async def get_tables(
    connector_id: UUID,
    user: User = Depends(require_auth),
):
    """Get available tables from connector."""
    try:
        tables = await integration_service.get_available_tables(connector_id)
        return {"tables": tables}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/connectors/{connector_id}/fetch")
async def fetch_data(
    connector_id: UUID,
    request: SyncRequest = None,
    user: User = Depends(require_auth),
):
    """Fetch event data from connector."""
    try:
        data = await integration_service.fetch_event_data(
            connector_id=connector_id,
            query=request.query if request else None,
        )
        return {"records": data, "count": len(data)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/sync-history")
async def get_sync_history(
    connector_id: Optional[UUID] = None,
    limit: int = 100,
    user: User = Depends(require_auth),
):
    """Get synchronization history."""
    history = integration_service.get_sync_history(
        connector_id=connector_id,
        limit=limit,
    )
    return {"history": history}
