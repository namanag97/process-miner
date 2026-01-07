"""Object-Centric Process Mining (OCPM) API Router.

OCEL 2.0 support for multi-object process mining.
"""

import asyncio
import json
import time

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse
from sqlalchemy import select

from src.api.dependencies import CurrentUser, ReadDBSession
from src.features.process_mining.models import (
    Dataset,
    DatasetStatus,
    OCELLog,
    OCELObjectType,
    OCPetriNet,
)
from src.features.process_mining.ocpm.service import ocpm_service
from src.features.process_mining.ocpm.storage import ocel_storage  # BUG-077 FIX
from src.features.process_mining.schemas import (
    DiscoverOCPNRequest,
    OCDFGResponse,
    OCELLogListResponse,
    OCELLogResponse,
    OCELObjectTypeResponse,
    OCELStatisticsResponse,
    OCPetriNetResponse,
)
from src.infra.core.exceptions import (
    BadRequestError,
    DiscoveryError,
    ModelNotFoundError,
    NotFoundError,
    ProcessingError,
)
from src.infra.core.logging_config import get_logger
from src.infra.models import AsyncJob

logger = get_logger(__name__)

router = APIRouter(prefix="/ocpm", tags=["Object-Centric Process Mining"])

MAX_FILE_SIZE_MB = 100
CHUNK_SIZE = 64 * 1024


# =============================================================================
# OCEL Upload and Management
# =============================================================================


@router.post("/upload", response_model=OCELLogResponse)
async def upload_ocel(
    db: ReadDBSession,
    user: CurrentUser,  # BUG-078 FIX: Require authentication
    file: UploadFile = File(...),
    name: str | None = Form(None),
    async_mode: bool = True,
):
    """Upload an OCEL file (JSON, SQLite, or XML format)."""
    filename = file.filename or "unknown.jsonocel"
    source_format = (
        "sqlite"
        if filename.endswith(".sqlite")
        else "xmlocel"
        if filename.endswith(".xmlocel")
        else "jsonocel"
    )

    logger.info("ocel_upload_started", filename=filename, source_format=source_format)
    start_time = time.perf_counter()

    try:
        total_size = 0
        # BUG-076 FIX: Read file content directly into memory
        content_chunks = []
        while chunk := await file.read(CHUNK_SIZE):
            total_size += len(chunk)
            if total_size > MAX_FILE_SIZE_MB * 1024 * 1024:
                raise BadRequestError(
                    message=f"File too large (>{MAX_FILE_SIZE_MB}MB)"
                )
            content_chunks.append(chunk)

        content = b"".join(content_chunks)

        # BUG-075 FIX: Run blocking PM4Py operations in thread pool
        ocel = await asyncio.to_thread(ocpm_service.read_ocel_from_bytes, content, source_format)
        stats = await asyncio.to_thread(ocpm_service.get_ocel_statistics, ocel)

        log_name = name or filename.rsplit(".", 1)[0]

        # BUG-077 FIX: Store OCEL data in local filesystem instead of database
        storage_key = ocel_storage.store(content, log_name)

        log_model = OCELLog(
            name=log_name,
            source_file=filename,
            source_format=source_format,
            total_events=stats["total_events"],
            total_objects=stats["total_objects"],
            total_object_types=stats["total_object_types"],
            metadata_json=json.dumps(
                {"activities": stats["activities"], "objects_per_type": stats["objects_per_type"]}
            ),
            ocel_storage_key=storage_key,  # BUG-077 FIX: Store reference instead of blob
        )
        db.add(log_model)
        await db.flush()

        for ot_name in stats["object_types"]:
            ot_model = OCELObjectType(
                dataset_id=log_model.id,
                name=ot_name,
                object_count=stats["objects_per_type"].get(ot_name, 0),
            )
            db.add(ot_model)

        # BUG-081 & BUG-082 FIX: Handle async persistence properly
        if not async_mode:
            # Synchronous: Do persistence immediately
            await ocpm_service.persist_ocel_2_0(db, ocel, source_dataset_id=log_model.id)
        else:
            # Async: Create background job for persistence
            from src.infra.core.enums import EntityType, JobStatus, JobType

            job = AsyncJob(
                job_type=JobType.OCEL_PERSIST.value
                if hasattr(JobType, "OCEL_PERSIST")
                else "ocel_persist",
                status=JobStatus.QUEUED.value,
                entity_type=EntityType.DATASET.value,
                entity_id=log_model.id,
                parameters_json=json.dumps({"ocel_log_id": log_model.id}),
            )
            db.add(job)
            logger.info(
                "ocel_persistence_job_created", job_type=job.job_type, dataset_id=log_model.id
            )

        await db.commit()
        await db.refresh(log_model)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "ocel_upload_completed", dataset_id=log_model.id, duration_ms=round(duration_ms, 2)
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
        raise BadRequestError(message=f"Failed to parse OCEL file: {e!s}")


@router.get("/logs", response_model=OCELLogListResponse)
async def list_ocel_logs(db: ReadDBSession, user: CurrentUser):
    """List all OCEL logs."""
    result = await db.execute(select(OCELLog).order_by(OCELLog.created_at.desc()))
    response_logs = [OCELLogResponse.model_validate(log) for log in result.scalars().all()]
    return OCELLogListResponse(logs=response_logs, total=len(response_logs))


@router.get("/datasets/{dataset_id}", response_model=OCELLogResponse)
async def get_ocel_log(dataset_id: str, db: ReadDBSession, user: CurrentUser):
    """Get OCEL log details."""
    result = await db.execute(select(OCELLog).where(OCELLog.id == dataset_id))
    log = result.scalar_one_or_none()
    if not log:
        raise NotFoundError(resource='OCEL Log', resource_id='unknown')
    return OCELLogResponse.model_validate(log)


@router.delete("/datasets/{dataset_id}")
async def delete_ocel_log(dataset_id: str, db: ReadDBSession, user: CurrentUser):
    """Delete an OCEL log."""
    result = await db.execute(select(OCELLog).where(OCELLog.id == dataset_id))
    log = result.scalar_one_or_none()
    if not log:
        raise NotFoundError(resource='OCEL Log', resource_id='unknown')
    await db.delete(log)
    await db.commit()
    return {"status": "deleted", "dataset_id": dataset_id}


# =============================================================================
# Object Types & Statistics
# =============================================================================


@router.get("/datasets/{dataset_id}/object-types", response_model=list[OCELObjectTypeResponse])
async def get_object_types(dataset_id: str, db: ReadDBSession, user: CurrentUser):
    """Get object types in an OCEL log."""
    result = await db.execute(select(OCELObjectType).where(OCELObjectType.dataset_id == dataset_id))
    object_types = result.scalars().all()
    if not object_types:
        log_result = await db.execute(select(OCELLog).where(OCELLog.id == dataset_id))
        if not log_result.scalar_one_or_none():
            raise NotFoundError(resource='OCEL Log', resource_id='unknown')
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


@router.get("/datasets/{dataset_id}/statistics", response_model=OCELStatisticsResponse)
async def get_ocel_statistics(dataset_id: str, db: ReadDBSession, user: CurrentUser):
    """Get detailed statistics for an OCEL log."""
    result = await db.execute(select(OCELLog).where(OCELLog.id == dataset_id))
    log = result.scalar_one_or_none()
    if not log:
        raise NotFoundError(resource='OCEL Log', resource_id='unknown')
    metadata = json.loads(log.metadata_json) if log.metadata_json else {}
    return OCELStatisticsResponse(
        dataset_id=log.id,
        total_events=log.total_events,
        total_objects=log.total_objects,
        total_object_types=log.total_object_types,
        total_activities=len(metadata.get("activities", [])),
        object_types=list(metadata.get("objects_per_type", {}).keys()),
        activities=metadata.get("activities", []),
        objects_per_type=metadata.get("objects_per_type", {}),
    )


# =============================================================================
# Discovery & Analysis
# =============================================================================


@router.post("/discover")
async def discover_oc_petri_net(
    request: DiscoverOCPNRequest, db: ReadDBSession, user: CurrentUser, async_mode: bool = True
):
    """Discover Object-Centric Petri Net from an OCEL log."""
    result = await db.execute(select(OCELLog).where(OCELLog.id == request.dataset_id))
    log = result.scalar_one_or_none()
    if not log:
        raise NotFoundError(resource='OCEL Log', resource_id='unknown')
    if not log.ocel_storage_key:
        raise BadRequestError(message="OCEL data not stored. Please re-upload.")

    model_name = request.model_name or f"OC-PN_{log.name}"

    if async_mode:
        import uuid

        job_id = str(uuid.uuid4())
        async_job = AsyncJob(
            id=job_id,
            task_id=job_id,
            job_type="ocpn_discovery",
            status="pending",
            parameters_json=json.dumps(
                {"dataset_id": request.dataset_id, "model_name": model_name}
            ),
        )
        db.add(async_job)
        await db.commit()
        return {"job_id": job_id, "status": "pending", "message": "OC-PN discovery started."}

    logger.info("oc_pn_discovery_started", dataset_id=log.id, model_name=model_name)
    start_time = time.perf_counter()

    try:
        # BUG-077 FIX: Retrieve OCEL data from storage
        ocel_data = ocel_storage.retrieve(log.ocel_storage_key)
        ocel = ocpm_service.read_ocel_from_bytes(ocel_data, log.source_format)
        oc_pn = ocpm_service.discover_oc_petri_net(ocel)
        serialized_pn = ocpm_service.serialize_oc_petri_net(oc_pn)
        metadata = json.loads(log.metadata_json) if log.metadata_json else {}
        object_types = list(metadata.get("objects_per_type", {}).keys())

        oc_pn_model = OCPetriNet(
            dataset_id=log.id,
            name=model_name,
            object_types_json=json.dumps(object_types),
            serialized_model=serialized_pn,
        )
        db.add(oc_pn_model)
        await db.commit()
        await db.refresh(oc_pn_model)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "oc_pn_discovery_completed", model_id=oc_pn_model.id, duration_ms=round(duration_ms, 2)
        )

        return OCPetriNetResponse(
            id=oc_pn_model.id,
            dataset_id=oc_pn_model.dataset_id,
            name=oc_pn_model.name,
            object_types=object_types,
            created_at=oc_pn_model.created_at,
        )
    except Exception as e:
        logger.error("oc_pn_discovery_failed", error=str(e), exc_info=True)
        raise DiscoveryError(message=f"OC-PN discovery failed: {e!s}")


@router.get("/models", response_model=list[OCPetriNetResponse])
async def list_oc_petri_nets(db: ReadDBSession, user: CurrentUser):
    """List all discovered Object-Centric Petri Nets."""
    result = await db.execute(select(OCPetriNet).order_by(OCPetriNet.created_at.desc()))
    return [OCPetriNetResponse.model_validate(m) for m in result.scalars().all()]


@router.get("/models/{model_id}", response_model=OCPetriNetResponse)
async def get_oc_petri_net(model_id: str, db: ReadDBSession, user: CurrentUser):
    """Get Object-Centric Petri Net details."""
    result = await db.execute(select(OCPetriNet).where(OCPetriNet.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise ModelNotFoundError(model_id='unknown')
    return OCPetriNetResponse.model_validate(model)


@router.delete("/models/{model_id}")
async def delete_oc_petri_net(model_id: str, db: ReadDBSession, user: CurrentUser):
    """Delete an Object-Centric Petri Net."""
    result = await db.execute(select(OCPetriNet).where(OCPetriNet.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise ModelNotFoundError(model_id='unknown')
    await db.delete(model)
    await db.commit()
    return {"status": "deleted", "model_id": model_id}


@router.get("/datasets/{dataset_id}/relationships", response_model=dict)
async def get_object_relationships(dataset_id: str, db: ReadDBSession, user: CurrentUser):
    """Get object-event relationships summary."""
    result = await db.execute(select(OCELLog).where(OCELLog.id == dataset_id))
    log = result.scalar_one_or_none()
    if not log:
        raise NotFoundError(resource='OCEL Log', resource_id='unknown')
    metadata = json.loads(log.metadata_json) if log.metadata_json else {}
    objects_per_type = metadata.get("objects_per_type", {})
    return {
        "dataset_id": log.id,
        "object_types": list(objects_per_type.keys()),
        "objects_per_type": objects_per_type,
        "total_objects": log.total_objects,
        "total_events": log.total_events,
    }


@router.get("/datasets/{dataset_id}/oc-dfg", response_model=OCDFGResponse)
async def get_oc_dfg(dataset_id: str, db: ReadDBSession, user: CurrentUser):
    """Get Object-Centric Directly-Follows Graph (OC-DFG)."""
    result = await db.execute(select(OCELLog).where(OCELLog.id == dataset_id))
    log = result.scalar_one_or_none()
    if not log:
        raise NotFoundError(resource='OCEL Log', resource_id='unknown')
    if not log.ocel_storage_key:
        raise BadRequestError(message="OCEL data not stored.")

    start_time = time.perf_counter()
    try:
        # BUG-077 FIX: Retrieve OCEL data from storage
        ocel_data = ocel_storage.retrieve(log.ocel_storage_key)
        ocel = ocpm_service.read_ocel_from_bytes(ocel_data, log.source_format)
        ocdfg_data = ocpm_service.get_ocdfg_graph_data(ocel)
        if ocdfg_data.get("error"):
            raise ProcessingError(
                message=f"OC-DFG computation failed: {ocdfg_data['error']}"
            )
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "oc_dfg_computation_completed", dataset_id=log.id, duration_ms=round(duration_ms, 2)
        )
        return OCDFGResponse(
            dataset_id=log.id,
            object_types=ocdfg_data["object_types"],
            activities=ocdfg_data["activities"],
            graphs_by_type=ocdfg_data["graphs_by_type"],
            total_events=log.total_events,
            total_objects=log.total_objects,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("oc_dfg_computation_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"OC-DFG computation failed: {e!s}")


@router.get("/formats")
async def list_supported_formats():
    """List supported OCEL file formats."""
    return [
        {"extension": ".jsonocel", "name": "JSON OCEL", "description": "OCEL 2.0 JSON format"},
        {
            "extension": ".sqlite",
            "name": "SQLite OCEL",
            "description": "OCEL 2.0 SQLite database format",
        },
        {"extension": ".xmlocel", "name": "XML OCEL", "description": "OCEL 2.0 XML format"},
    ]


@router.post("/datasets/{dataset_id}/flatten")
async def flatten_ocel_to_dataset(
    dataset_id: str,
    db: ReadDBSession,
    user: CurrentUser,
    object_type: str = Form(..., description="Object type to flatten on"),
    name: str | None = Form(None, description="Name for the created dataset"),
):
    """Flatten an OCEL log to a traditional event log based on an object type."""
    from src.infra.core.enums import EntityType, JobStatus, JobType

    result = await db.execute(select(OCELLog).where(OCELLog.id == dataset_id))
    log = result.scalar_one_or_none()
    if not log:
        raise NotFoundError(resource='OCEL Log', resource_id='unknown')
    if not log.ocel_storage_key:
        raise BadRequestError(message="OCEL data not stored.")

    metadata = json.loads(log.metadata_json) if log.metadata_json else {}
    available_types = list(metadata.get("objects_per_type", {}).keys())
    if object_type not in available_types:
        raise BadRequestError(
            message=f"Object type '{object_type}' not found. Available: {', '.join(available_types)}"
        )

    dataset_name = name or f"{log.name}_flattened_{object_type}"
    dataset = Dataset(
        name=dataset_name, source_format="ocel_flattened", status=DatasetStatus.PENDING.value
    )
    db.add(dataset)
    await db.flush()

    job = AsyncJob(
        job_type=JobType.FLATTEN.value,
        status=JobStatus.QUEUED.value,
        entity_type=EntityType.DATASET.value,
        entity_id=dataset.id,
        parameters_json=json.dumps(
            {"ocel_dataset_id": dataset_id, "object_type": object_type, "dataset_id": dataset.id}
        ),
    )
    db.add(job)
    await db.flush()

    dataset.ingestion_job_id = job.id
    await db.commit()

    logger.info(
        "ocel_flatten_queued", job_id=job.id, dataset_id=dataset.id, object_type=object_type
    )
    return JSONResponse(
        status_code=202,
        content={
            "job_id": job.id,
            "dataset_id": dataset.id,
            "status": "queued",
            "message": f"Flattening OCEL on '{object_type}'. Use /api/v1/jobs/{job.id} to track progress.",
        },
    )
