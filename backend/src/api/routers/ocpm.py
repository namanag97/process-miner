"""Object-Centric Process Mining (OCPM) API Router.

Provides endpoints for OCEL 2.0 file handling and object-centric process mining:
- Upload OCEL files (JSON, SQLite, XML formats)
- List and retrieve OCEL logs
- Object type analysis
- Object-Centric Petri Net discovery
- Object-Centric DFG discovery
- Flattening to traditional event logs
"""

import json
import time
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_session
from src.core.logging_config import get_logger
from src.models.orm import OCELLog, OCELObjectType, OCPetriNet
from src.models.schemas import (
    DiscoverOCPNRequest,
    OCDFGResponse,
    OCELLogListResponse,
    OCELLogResponse,
    OCELObjectTypeResponse,
    OCELStatisticsResponse,
    OCPetriNetResponse,
)
from src.services.ocpm import ocpm_service

logger = get_logger(__name__)

router = APIRouter(prefix="/ocpm", tags=["Object-Centric Process Mining"])


# =============================================================================
# OCEL Upload and Management
# =============================================================================


@router.post("/upload", response_model=OCELLogResponse)
async def upload_ocel(
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    session: AsyncSession = Depends(get_session),
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

    logger.info("ocel_upload_started", filename=filename, source_format=source_format, name=name)
    start_time = time.perf_counter()

    # Read file content
    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    logger.debug("ocel_file_read", size_mb=round(file_size_mb, 2))

    try:
        # Parse OCEL using PM4Py
        ocel = ocpm_service.read_ocel_from_bytes(content, source_format)

        # Get statistics
        stats = ocpm_service.get_ocel_statistics(ocel)

        # Create database record with raw OCEL data for later re-parsing
        log_name = name or filename.rsplit(".", 1)[0]
        log_model = OCELLog(
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
            ocel_data=content,  # Store raw OCEL for OC-DFG and other analyses
        )
        session.add(log_model)

        # Store object types
        for ot_name in stats["object_types"]:
            ot_model = OCELObjectType(
                log_id=log_model.id,
                name=ot_name,
                object_count=stats["objects_per_type"].get(ot_name, 0),
            )
            session.add(ot_model)

        await session.commit()
        await session.refresh(log_model)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "ocel_upload_completed",
            log_id=log_model.id,
            total_events=log_model.total_events,
            total_objects=log_model.total_objects,
            total_object_types=log_model.total_object_types,
            duration_ms=round(duration_ms, 2),
        )

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
            created_at=log_model.created_at,
        )

    except Exception as e:
        logger.error("ocel_upload_failed", filename=filename, error=str(e), exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to parse OCEL file: {str(e)}")


@router.get("/logs", response_model=OCELLogListResponse)
async def list_ocel_logs(
    session: AsyncSession = Depends(get_session),
):
    """
    List all OCEL logs.

    Returns a list of all uploaded object-centric event logs with their metadata.
    """
    result = await session.execute(select(OCELLog).order_by(OCELLog.created_at.desc()))
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
                object_types=list(metadata.get("objects_per_type", {}).keys()),
                activities=metadata.get("activities", []),
                created_at=log.created_at,
            )
        )

    return OCELLogListResponse(logs=response_logs, total=len(response_logs))


@router.get("/logs/{log_id}", response_model=OCELLogResponse)
async def get_ocel_log(
    log_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get OCEL log details.

    Returns detailed information about a specific object-centric event log.
    """
    result = await session.execute(select(OCELLog).where(OCELLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="OCEL log not found")

    metadata = json.loads(log.metadata_json) if log.metadata_json else {}

    return OCELLogResponse(
        id=log.id,
        name=log.name,
        source_file=log.source_file,
        source_format=log.source_format,
        total_events=log.total_events,
        total_objects=log.total_objects,
        total_object_types=log.total_object_types,
        object_types=list(metadata.get("objects_per_type", {}).keys()),
        activities=metadata.get("activities", []),
        created_at=log.created_at,
    )


@router.delete("/logs/{log_id}")
async def delete_ocel_log(
    log_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete an OCEL log.

    Removes the log and all associated data (object types, models).
    """
    result = await session.execute(select(OCELLog).where(OCELLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="OCEL log not found")

    await session.delete(log)
    await session.commit()

    return {"status": "deleted", "log_id": log_id}


# =============================================================================
# Object Types
# =============================================================================


@router.get("/logs/{log_id}/object-types", response_model=list[OCELObjectTypeResponse])
async def get_object_types(
    log_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get object types in an OCEL log.

    Returns all object types (e.g., Order, Item, Package) with their counts.
    """
    result = await session.execute(select(OCELObjectType).where(OCELObjectType.log_id == log_id))
    object_types = result.scalars().all()

    if not object_types:
        # Check if log exists
        log_result = await session.execute(select(OCELLog).where(OCELLog.id == log_id))
        if not log_result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="OCEL log not found")

    return [
        OCELObjectTypeResponse(
            name=ot.name,
            object_count=ot.object_count,
            attributes=list(json.loads(ot.attributes_schema_json).keys())
            if ot.attributes_schema_json
            else [],
        )
        for ot in object_types
    ]


@router.get("/logs/{log_id}/statistics", response_model=OCELStatisticsResponse)
async def get_ocel_statistics(
    log_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get detailed statistics for an OCEL log.

    Returns comprehensive statistics including event counts, object counts,
    activities, and objects per type.
    """
    result = await session.execute(select(OCELLog).where(OCELLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="OCEL log not found")

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


# =============================================================================
# Discovery
# =============================================================================


@router.post("/discover", response_model=OCPetriNetResponse)
async def discover_oc_petri_net(
    request: DiscoverOCPNRequest,
    session: AsyncSession = Depends(get_session),
):
    """
    Discover Object-Centric Petri Net from an OCEL log.

    Uses PM4Py's `discover_oc_petri_net()` to create an OC-PN that captures
    the process behavior across all object types.
    """
    result = await session.execute(select(OCELLog).where(OCELLog.id == request.log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="OCEL log not found")

    if not log.ocel_data:
        raise HTTPException(
            status_code=400, detail="OCEL data not stored. Please re-upload the OCEL file."
        )

    model_name = request.model_name or f"OC-PN_{log.name}"

    logger.info("oc_pn_discovery_started", log_id=log.id, model_name=model_name)
    start_time = time.perf_counter()

    try:
        # Re-parse OCEL from stored blob
        ocel = ocpm_service.read_ocel_from_bytes(log.ocel_data, log.source_format)

        # Discover OC-PN using PM4Py
        oc_pn = ocpm_service.discover_oc_petri_net(ocel)

        # Serialize the OC-PN for storage
        serialized_pn = ocpm_service.serialize_oc_petri_net(oc_pn)

        metadata = json.loads(log.metadata_json) if log.metadata_json else {}
        object_types = list(metadata.get("objects_per_type", {}).keys())

        # Create OC-PN record with serialized model
        oc_pn_model = OCPetriNet(
            log_id=log.id,
            name=model_name,
            object_types_json=json.dumps(object_types),
            serialized_model=serialized_pn,
        )
        session.add(oc_pn_model)
        await session.commit()
        await session.refresh(oc_pn_model)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "oc_pn_discovery_completed",
            log_id=log.id,
            model_id=oc_pn_model.id,
            duration_ms=round(duration_ms, 2),
        )

        return OCPetriNetResponse(
            id=oc_pn_model.id,
            log_id=oc_pn_model.log_id,
            name=oc_pn_model.name,
            object_types=object_types,
            created_at=oc_pn_model.created_at,
        )

    except Exception as e:
        logger.error("oc_pn_discovery_failed", log_id=log.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"OC-PN discovery failed: {str(e)}")


@router.get("/models", response_model=list[OCPetriNetResponse])
async def list_oc_petri_nets(
    session: AsyncSession = Depends(get_session),
):
    """
    List all discovered Object-Centric Petri Nets.
    """
    result = await session.execute(select(OCPetriNet).order_by(OCPetriNet.created_at.desc()))
    models = result.scalars().all()

    return [
        OCPetriNetResponse(
            id=m.id,
            log_id=m.log_id,
            name=m.name,
            object_types=json.loads(m.object_types_json) if m.object_types_json else [],
            created_at=m.created_at,
        )
        for m in models
    ]


@router.get("/models/{model_id}", response_model=OCPetriNetResponse)
async def get_oc_petri_net(
    model_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get Object-Centric Petri Net details.
    """
    result = await session.execute(select(OCPetriNet).where(OCPetriNet.id == model_id))
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="OC-PN model not found")

    return OCPetriNetResponse(
        id=model.id,
        log_id=model.log_id,
        name=model.name,
        object_types=json.loads(model.object_types_json) if model.object_types_json else [],
        created_at=model.created_at,
    )


@router.delete("/models/{model_id}")
async def delete_oc_petri_net(
    model_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete an Object-Centric Petri Net.
    """
    result = await session.execute(select(OCPetriNet).where(OCPetriNet.id == model_id))
    model = result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="OC-PN model not found")

    await session.delete(model)
    await session.commit()

    return {"status": "deleted", "model_id": model_id}


# =============================================================================
# Analysis
# =============================================================================


@router.get("/logs/{log_id}/relationships", response_model=dict)
async def get_object_relationships(
    log_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get object-event relationships summary.

    Shows how many events and cases are associated with each object type.
    This is stored metadata from the upload - actual graph requires re-parsing.
    """
    result = await session.execute(select(OCELLog).where(OCELLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="OCEL log not found")

    metadata = json.loads(log.metadata_json) if log.metadata_json else {}
    objects_per_type = metadata.get("objects_per_type", {})

    return {
        "log_id": log.id,
        "object_types": list(objects_per_type.keys()),
        "objects_per_type": objects_per_type,
        "total_objects": log.total_objects,
        "total_events": log.total_events,
    }


@router.get("/logs/{log_id}/oc-dfg", response_model=OCDFGResponse)
async def get_oc_dfg(
    log_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get Object-Centric Directly-Follows Graph (OC-DFG) for an OCEL log.

    Computes the OC-DFG using PM4Py's `ocel_discover_ocdfg()` function.
    Returns separate DFG graphs for each object type, showing how activities
    relate to each other within the context of different object types.

    This endpoint requires the OCEL data to be stored (uploaded after Phase 2.1).
    """
    result = await session.execute(select(OCELLog).where(OCELLog.id == log_id))
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(status_code=404, detail="OCEL log not found")

    if not log.ocel_data:
        raise HTTPException(
            status_code=400, detail="OCEL data not stored. Please re-upload the OCEL file."
        )

    logger.info("oc_dfg_computation_started", log_id=log.id)
    start_time = time.perf_counter()

    try:
        # Re-parse OCEL from stored blob
        ocel = ocpm_service.read_ocel_from_bytes(log.ocel_data, log.source_format)

        # Compute OC-DFG
        ocdfg_data = ocpm_service.get_ocdfg_graph_data(ocel)

        if "error" in ocdfg_data and ocdfg_data["error"]:
            raise HTTPException(
                status_code=500, detail=f"OC-DFG computation failed: {ocdfg_data['error']}"
            )

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "oc_dfg_computation_completed",
            log_id=log.id,
            object_types=len(ocdfg_data["object_types"]),
            duration_ms=round(duration_ms, 2),
        )

        return OCDFGResponse(
            log_id=log.id,
            object_types=ocdfg_data["object_types"],
            activities=ocdfg_data["activities"],
            graphs_by_type=ocdfg_data["graphs_by_type"],
            total_events=log.total_events,
            total_objects=log.total_objects,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("oc_dfg_computation_failed", log_id=log.id, error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"OC-DFG computation failed: {str(e)}")


@router.get("/formats")
async def list_supported_formats():
    """
    List supported OCEL file formats.
    """
    return [
        {
            "extension": ".jsonocel",
            "name": "JSON OCEL",
            "description": "OCEL 2.0 JSON format",
            "mime_type": "application/json",
        },
        {
            "extension": ".sqlite",
            "name": "SQLite OCEL",
            "description": "OCEL 2.0 SQLite database format",
            "mime_type": "application/x-sqlite3",
        },
        {
            "extension": ".xmlocel",
            "name": "XML OCEL",
            "description": "OCEL 2.0 XML format",
            "mime_type": "application/xml",
        },
    ]
