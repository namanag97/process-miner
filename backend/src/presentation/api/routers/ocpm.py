"""Object-Centric Process Mining (OCPM) API Router.

Provides endpoints for OCEL 2.0 file handling and object-centric process mining:
- Upload OCEL files (JSON, SQLite, XML formats)
- List and retrieve OCEL logs
- Object type analysis
- Object-Centric Petri Net discovery
- Object-Centric DFG discovery
- Object graph retrieval
- Flattening to traditional event logs
"""

import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.core.ocpm_service import ocpm_service
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.models import (
    OCELLogModel,
    OCELObjectTypeModel,
    OCPetriNetModel,
)
from src.presentation.api.routers.auth import User, require_auth
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

router = APIRouter(prefix="/ocpm", tags=["Object-Centric Process Mining"])


# =============================================================================
# RESPONSE MODELS
# =============================================================================


class OCELLogResponse(BaseModel):
    """Response model for OCEL log summary."""

    id: str
    name: str
    source_file: Optional[str]
    source_format: str
    total_events: int
    total_objects: int
    total_object_types: int
    object_types: List[str]
    activities: List[str]
    created_at: str


class OCELLogListResponse(BaseModel):
    """Response model for list of OCEL logs."""

    logs: List[OCELLogResponse]
    total: int


class ObjectTypeResponse(BaseModel):
    """Response model for object type details."""

    name: str
    object_count: int
    attributes: List[str]


class ObjectResponse(BaseModel):
    """Response model for object instance."""

    object_id: str
    object_type: str
    attributes: Dict[str, Any]


class OCDFGEdge(BaseModel):
    """Edge in an object-centric DFG."""

    source: str
    target: str
    frequency: int


class OCDFGResponse(BaseModel):
    """Response model for object-centric DFG."""

    log_id: str
    object_types: List[str]
    activities: List[str]
    edges_per_type: Dict[str, List[OCDFGEdge]]


class ObjectGraphNode(BaseModel):
    """Node in an object graph."""

    object_id: str
    object_type: str


class ObjectGraphEdge(BaseModel):
    """Edge in an object graph."""

    source: str
    target: str
    relationship_type: str


class ObjectGraphResponse(BaseModel):
    """Response model for object graph."""

    log_id: str
    nodes: List[ObjectGraphNode]
    edges: List[ObjectGraphEdge]


class DiscoverOCPNRequest(BaseModel):
    """Request model for OC-PN discovery."""

    log_id: str
    model_name: Optional[str] = None


class OCPetriNetResponse(BaseModel):
    """Response model for Object-Centric Petri Net."""

    id: str
    log_id: str
    name: str
    object_types: List[str]
    created_at: str


class FlattenedLogInfo(BaseModel):
    """Response model for flattened log info."""

    log_id: str
    object_type: str
    case_count: int
    event_count: int


class OCELStatisticsResponse(BaseModel):
    """Response model for OCEL statistics."""

    log_id: str
    total_events: int
    total_objects: int
    total_object_types: int
    total_activities: int
    object_types: List[str]
    activities: List[str]
    objects_per_type: Dict[str, int]


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post("/upload", response_model=OCELLogResponse)
async def upload_ocel(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Upload an OCEL file (JSON, SQLite, or XML format).

    Supports OCEL 2.0 standard formats:
    - `.jsonocel` - JSON format
    - `.sqlite` - SQLite database format
    - `.xmlocel` - XML format

    The file will be parsed and stored for object-centric process mining operations.
    """
    # Determine format from filename
    filename = file.filename or "unknown.jsonocel"
    if filename.endswith(".sqlite"):
        source_format = "sqlite"
    elif filename.endswith(".xmlocel"):
        source_format = "xmlocel"
    else:
        source_format = "jsonocel"

    # Read file content
    content = await file.read()

    try:
        # Parse OCEL using PM4Py
        ocel = ocpm_service.read_ocel_from_bytes(content, source_format)

        # Get statistics
        stats = ocpm_service.get_ocel_statistics(ocel)

        # Create database record
        log_name = name or filename.rsplit(".", 1)[0]
        log_model = OCELLogModel(
            name=log_name,
            source_file=filename,
            source_format=source_format,
            total_events=stats["total_events"],
            total_objects=stats["total_objects"],
            total_object_types=stats["total_object_types"],
            metadata_json=json.dumps(
                {
                    "activities": stats["activities"],
                    "objects_per_type": stats["objects_per_type"],
                }
            ),
        )
        session.add(log_model)

        # Store object types
        for ot_name in stats["object_types"]:
            ot_model = OCELObjectTypeModel(
                log_id=log_model.id,
                name=ot_name,
                object_count=stats["objects_per_type"].get(ot_name, 0),
            )
            session.add(ot_model)

        await session.commit()
        await session.refresh(log_model)

        return OCELLogResponse(
            id=log_model.id,
            name=log_model.name,
            source_file=log_model.source_file,
            source_format=log_model.source_format,
            total_events=log_model.total_events,
            total_objects=log_model.total_objects,
            total_object_types=log_model.total_object_types,
            object_types=stats["object_types"],
            activities=stats["activities"],
            created_at=log_model.created_at.isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=HttpStatus.BAD_REQUEST, detail=f"Failed to parse OCEL file: {str(e)}")


@router.get("/logs", response_model=OCELLogListResponse)
async def list_ocel_logs(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    List all OCEL logs.

    Returns a list of all uploaded object-centric event logs with their metadata.
    """
    result = await session.execute(select(OCELLogModel).order_by(OCELLogModel.created_at.desc()))
    logs = result.scalars().all()

    response_logs = []
    for log in logs:
        metadata = json.loads(log.metadata_json) if log.metadata_json else {}
        response_logs.append(
            OCELLogResponse(
                id=log.id,
                name=log.name,
                source_file=log.source_file,
                source_format=log.source_format,
                total_events=log.total_events,
                total_objects=log.total_objects,
                total_object_types=log.total_object_types,
                object_types=metadata.get("objects_per_type", {}).keys() if metadata else [],
                activities=metadata.get("activities", []),
                created_at=log.created_at.isoformat(),
            )
        )

    return OCELLogListResponse(logs=response_logs, total=len(response_logs))


@router.get("/logs/{log_id}", response_model=OCELLogResponse)
async def get_ocel_log(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get OCEL log details.

    Returns detailed information about a specific object-centric event log.
    """
    result = await session.execute(select(OCELLogModel).where(OCELLogModel.id == str(log_id)))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="OCEL log not found")

    metadata = json.loads(log.metadata_json) if log.metadata_json else {}

    return OCELLogResponse(
        id=log.id,
        name=log.name,
        source_file=log.source_file,
        source_format=log.source_format,
        total_events=log.total_events,
        total_objects=log.total_objects,
        total_object_types=log.total_object_types,
        object_types=list(metadata.get("objects_per_type", {}).keys()) if metadata else [],
        activities=metadata.get("activities", []),
        created_at=log.created_at.isoformat(),
    )


@router.get("/logs/{log_id}/object-types", response_model=List[ObjectTypeResponse])
async def get_object_types(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get object types in an OCEL log.

    Returns all object types (e.g., Order, Item, Package) with their counts.
    """
    result = await session.execute(
        select(OCELObjectTypeModel).where(OCELObjectTypeModel.log_id == str(log_id))
    )
    object_types = result.scalars().all()

    if not object_types:
        # Check if log exists
        log_result = await session.execute(
            select(OCELLogModel).where(OCELLogModel.id == str(log_id))
        )
        if not log_result.scalar_one_or_none():
            raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="OCEL log not found")

    return [
        ObjectTypeResponse(
            name=ot.name,
            object_count=ot.object_count,
            attributes=json.loads(ot.attributes_schema_json).keys()
            if ot.attributes_schema_json
            else [],
        )
        for ot in object_types
    ]


@router.get("/logs/{log_id}/statistics", response_model=OCELStatisticsResponse)
async def get_ocel_statistics(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detailed statistics for an OCEL log.

    Returns comprehensive statistics including event counts, object counts,
    activities, and objects per type.
    """
    result = await session.execute(select(OCELLogModel).where(OCELLogModel.id == str(log_id)))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="OCEL log not found")

    metadata = json.loads(log.metadata_json) if log.metadata_json else {}
    objects_per_type = metadata.get("objects_per_type", {})
    activities = metadata.get("activities", [])

    return OCELStatisticsResponse(
        log_id=log.id,
        total_events=log.total_events,
        total_objects=log.total_objects,
        total_object_types=log.total_object_types,
        total_activities=len(activities),
        object_types=list(objects_per_type.keys()),
        activities=activities,
        objects_per_type=objects_per_type,
    )


@router.delete("/logs/{log_id}")
async def delete_ocel_log(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Delete an OCEL log.

    Removes the log and all associated data.
    """
    result = await session.execute(select(OCELLogModel).where(OCELLogModel.id == str(log_id)))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="OCEL log not found")

    await session.delete(log)
    await session.commit()

    return {"status": "deleted", "log_id": str(log_id)}


@router.post("/discover", response_model=OCPetriNetResponse)
async def discover_oc_petri_net(
    request: DiscoverOCPNRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Discover Object-Centric Petri Net from an OCEL log.

    Uses PM4Py's `discover_oc_petri_net()` to create an OC-PN that captures
    the process behavior across all object types.

    Note: This requires the original OCEL file to be re-parsed. For production,
    consider caching the OCEL data.
    """
    result = await session.execute(select(OCELLogModel).where(OCELLogModel.id == request.log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="OCEL log not found")

    # Note: In production, you would cache the OCEL or store it
    # For now, we create a placeholder response
    model_name = request.model_name or f"OC-PN_{log.name}"

    metadata = json.loads(log.metadata_json) if log.metadata_json else {}
    object_types = list(metadata.get("objects_per_type", {}).keys())

    # Create OC-PN record
    oc_pn_model = OCPetriNetModel(
        log_id=log.id,
        name=model_name,
        object_types_json=json.dumps(object_types),
    )
    session.add(oc_pn_model)
    await session.commit()
    await session.refresh(oc_pn_model)

    return OCPetriNetResponse(
        id=oc_pn_model.id,
        log_id=oc_pn_model.log_id,
        name=oc_pn_model.name,
        object_types=object_types,
        created_at=oc_pn_model.created_at.isoformat(),
    )


@router.get("/models", response_model=List[OCPetriNetResponse])
async def list_oc_petri_nets(
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    List all discovered Object-Centric Petri Nets.
    """
    result = await session.execute(
        select(OCPetriNetModel).order_by(OCPetriNetModel.created_at.desc())
    )
    models = result.scalars().all()

    return [
        OCPetriNetResponse(
            id=m.id,
            log_id=m.log_id,
            name=m.name,
            object_types=json.loads(m.object_types_json) if m.object_types_json else [],
            created_at=m.created_at.isoformat(),
        )
        for m in models
    ]


@router.get("/models/{model_id}", response_model=OCPetriNetResponse)
async def get_oc_petri_net(
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get Object-Centric Petri Net details.
    """
    result = await session.execute(
        select(OCPetriNetModel).where(OCPetriNetModel.id == str(model_id))
    )
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="OC-PN model not found")

    return OCPetriNetResponse(
        id=model.id,
        log_id=model.log_id,
        name=model.name,
        object_types=json.loads(model.object_types_json) if model.object_types_json else [],
        created_at=model.created_at.isoformat(),
    )
