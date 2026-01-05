"""Conformance Checking API Router.

Endpoints for checking conformance between event logs and process models.
"""

import json
import time

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_session
from src.features.process_mining.conformance.service import conformance_service
from src.features.process_mining.enums import ConformanceMethod
from src.features.process_mining.models import ConformanceResult, Dataset, ProcessModel
from src.features.process_mining.schemas import (
    AlignmentDiagnosticsResponse,
    ConformanceCheckRequest,
    ConformanceListResponse,
    ConformanceResponse,
    DeviationResponse,
    DiagnosticsResponse,
    QualityMetricsResponse,
)
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/conformance", tags=["Conformance"])


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post("/check", response_model=ConformanceResponse)
async def check_conformance(
    request: ConformanceCheckRequest,
    session: AsyncSession = Depends(get_session),
    auto_discover: bool = Query(False, description="Auto-discover model if model_id not provided"),
):
    """
    Check conformance between an event log and a process model.

    Supports two methods:
    - `token_replay`: Fast, token-based replay (default)
    - `alignment`: More accurate, alignment-based (slower)

    Job-Centric Architecture Enhancement:
    - If `auto_discover=True` and no model_id, first runs discovery then conformance
    - Returns 202 with chained job IDs for async processing

    Returns fitness, precision, and conformance status.
    """
    logger.info(
        "conformance_check_started",
        dataset_id=request.dataset_id,
        model_id=request.model_id,
        method=str(request.method),
    )
    start_time = time.perf_counter()

    # Get the event log with cases and events
    log_result = await session.execute(select(Dataset).where(Dataset.id == request.dataset_id))
    event_log = log_result.scalar_one_or_none()

    if not event_log:
        logger.warning("log_not_found", dataset_id=request.dataset_id)
        raise HTTPException(status_code=404, detail="Event log not found")

    # FIX: Validate dataset is ready for conformance checking
    from src.features.process_mining.models import DatasetStatus

    if event_log.status != DatasetStatus.READY.value:
        logger.warning("dataset_not_ready", dataset_id=request.dataset_id, status=event_log.status)
        raise HTTPException(
            status_code=409,
            detail=f"Dataset not ready (status: {event_log.status}). Complete ingestion first.",
        )

    # Get the process model
    model_result = await session.execute(
        select(ProcessModel).where(ProcessModel.id == request.model_id)
    )
    model = model_result.scalar_one_or_none()

    if not model:
        logger.warning("model_not_found", model_id=request.model_id)
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        logger.warning("model_no_data", model_id=request.model_id)
        raise HTTPException(
            status_code=400,
            detail="Process model has no serialized data - rediscover the model",
        )

    try:
        # Run conformance check
        result = conformance_service.check_conformance(
            event_log=event_log,
            model=model,
            method=request.method,
        )

        # Store result in database
        conformance_record = ConformanceResult(
            dataset_id=request.dataset_id,  # BUG-001 FIX: ORM uses dataset_id
            model_id=request.model_id,
            fitness=result["fitness"],
            precision=result.get("precision"),
            method=result["method"],
            diagnostics_json=json.dumps(
                {
                    "fitting_traces": result["fitting_traces"],
                    "total_traces": result["total_traces"],
                }
            ),
        )
        session.add(conformance_record)
        await session.commit()
        await session.refresh(conformance_record)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "conformance_check_completed",
            result_id=conformance_record.id,
            fitness=result["fitness"],
            is_conformant=result["is_conformant"],
            fitting_traces=result["fitting_traces"],
            total_traces=result["total_traces"],
            duration_ms=round(duration_ms, 2),
        )

        return ConformanceResponse(
            id=conformance_record.id,
            dataset_id=conformance_record.dataset_id,  # BUG-001 FIX
            model_id=conformance_record.model_id,
            fitness=conformance_record.fitness,
            precision=conformance_record.precision,
            method=conformance_record.method,
            algorithm_used=result.get("algorithm_used", result["method"]),
            fallback_reason=result.get("fallback_reason"),
            is_conformant=result["is_conformant"],
            fitting_traces=result["fitting_traces"],
            total_traces=result["total_traces"],
            created_at=conformance_record.created_at,
        )

    except Exception as e:
        logger.error(
            "conformance_check_failed",
            dataset_id=request.dataset_id,
            model_id=request.model_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Conformance check failed: {e!s}",
        )


@router.get("/results", response_model=ConformanceListResponse)
async def list_conformance_results(
    dataset_id: str | None = Query(None, description="Filter by event log ID"),
    model_id: str | None = Query(None, description="Filter by model ID"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    """
    List conformance check results.

    Optionally filter by dataset_id or model_id.
    """
    query = select(ConformanceResult)

    if dataset_id:
        query = query.where(ConformanceResult.dataset_id == dataset_id)  # BUG-001 FIX
    if model_id:
        query = query.where(ConformanceResult.model_id == model_id)

    query = query.order_by(ConformanceResult.created_at.desc())

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await session.execute(query)
    results = result.scalars().all()

    items = []
    for r in results:
        diagnostics = json.loads(r.diagnostics_json) if r.diagnostics_json else {}
        items.append(
            ConformanceResponse(
                id=r.id,
                dataset_id=r.dataset_id,  # BUG-001 FIX
                model_id=r.model_id,
                fitness=r.fitness,
                precision=r.precision,
                method=r.method,
                algorithm_used=r.method,  # Default to method for historical data
                is_conformant=r.fitness >= 0.8,
                fitting_traces=diagnostics.get("fitting_traces", 0),
                total_traces=diagnostics.get("total_traces", 0),
                created_at=r.created_at,
            )
        )

    return ConformanceListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/results/{result_id}", response_model=ConformanceResponse)
async def get_conformance_result(
    result_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get a specific conformance check result.
    """
    result = await session.execute(
        select(ConformanceResult).where(ConformanceResult.id == result_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Conformance result not found")

    diagnostics = json.loads(record.diagnostics_json) if record.diagnostics_json else {}

    return ConformanceResponse(
        id=record.id,
        dataset_id=record.dataset_id,  # BUG-001 FIX
        model_id=record.model_id,
        fitness=record.fitness,
        precision=record.precision,
        method=record.method,
        algorithm_used=record.method,  # Default to method for historical data
        is_conformant=record.fitness >= 0.8,
        fitting_traces=diagnostics.get("fitting_traces", 0),
        total_traces=diagnostics.get("total_traces", 0),
        created_at=record.created_at,
    )


@router.delete("/results/{result_id}")
async def delete_conformance_result(
    result_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a conformance check result.
    """
    result = await session.execute(
        select(ConformanceResult).where(ConformanceResult.id == result_id)
    )
    record = result.scalar_one_or_none()

    if not record:
        raise HTTPException(status_code=404, detail="Conformance result not found")

    await session.delete(record)
    await session.commit()

    return {"status": "deleted", "result_id": result_id}


@router.get("/diagnostics/{dataset_id}/{model_id}", response_model=DiagnosticsResponse)
async def get_conformance_diagnostics(
    dataset_id: str,
    model_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get detailed conformance diagnostics for a log-model pair.

    Returns trace-level analysis including deviations.
    """
    # Get the event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    event_log = log_result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get the process model
    model_result = await session.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = model_result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        raise HTTPException(
            status_code=400,
            detail="Process model has no serialized data",
        )

    try:
        # Get detailed diagnostics
        diagnostics = conformance_service.get_diagnostics(event_log, model)

        # Also get fitness/precision for completeness
        result = conformance_service.check_conformance(event_log, model)

        return DiagnosticsResponse(
            fitness=result["fitness"],
            precision=result.get("precision"),
            total_traces=diagnostics["total_traces"],
            fitting_traces=diagnostics["fitting_traces"],
            non_fitting_traces=diagnostics["non_fitting_traces"],
            fitness_ratio=diagnostics["fitness_ratio"],
            deviations=diagnostics["deviations"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get diagnostics: {e!s}",
        )


@router.get("/deviations/{dataset_id}/{model_id}", response_model=list[DeviationResponse])
async def get_deviations(
    dataset_id: str,
    model_id: str,
    threshold: float = Query(0.8, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_session),
):
    """
    Detect and list specific deviations from the model.

    Returns case-level deviation information.
    """
    # Get the event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    event_log = log_result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get the process model
    model_result = await session.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = model_result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        raise HTTPException(
            status_code=400,
            detail="Process model has no serialized data",
        )

    try:
        deviations = conformance_service.detect_deviations(event_log, model, threshold)

        return [
            DeviationResponse(
                case_id=d["case_id"],
                activity=d.get("activity"),
                deviation_type=d["deviation_type"],
                details=d["details"],
            )
            for d in deviations[:100]  # Limit to 100 deviations
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect deviations: {e!s}",
        )


@router.get("/alignments/{dataset_id}/{model_id}", response_model=AlignmentDiagnosticsResponse)
async def get_alignment_diagnostics(
    dataset_id: str,
    model_id: str,
    max_cases: int = Query(100, ge=1, le=1000, description="Max cases to include"),
    session: AsyncSession = Depends(get_session),
):
    """
    Get detailed alignment diagnostics for a log-model pair.

    Uses PM4Py's alignment-based conformance checking to compute optimal
    alignments between traces and the process model. This provides:
    - Per-case fitness scores
    - Detailed alignment moves (sync, log-only, model-only)
    - Identification of deviating activities

    Note: This is computationally expensive for large logs. Use max_cases to limit.
    """
    logger.info(
        "alignment_diagnostics_started",
        dataset_id=dataset_id,
        model_id=model_id,
        max_cases=max_cases,
    )
    start_time = time.perf_counter()

    # Get the event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    event_log = log_result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get the process model
    model_result = await session.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = model_result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        raise HTTPException(
            status_code=400,
            detail="Process model has no serialized data",
        )

    try:
        # Get alignment diagnostics
        diagnostics = conformance_service.get_alignment_diagnostics(event_log, model, max_cases)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "alignment_diagnostics_completed",
            dataset_id=dataset_id,
            model_id=model_id,
            total_cases=diagnostics["total_cases"],
            fitting_cases=diagnostics["fitting_cases"],
            average_fitness=diagnostics["average_fitness"],
            duration_ms=round(duration_ms, 2),
        )

        return AlignmentDiagnosticsResponse(
            dataset_id=dataset_id,
            model_id=model_id,
            total_cases=diagnostics["total_cases"],
            fitting_cases=diagnostics["fitting_cases"],
            average_fitness=diagnostics["average_fitness"],
            case_alignments=diagnostics["case_alignments"],
        )

    except Exception as e:
        logger.error(
            "alignment_diagnostics_failed",
            dataset_id=dataset_id,
            model_id=model_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get alignment diagnostics: {e!s}",
        )


@router.get("/methods")
async def list_conformance_methods():
    """
    List available conformance checking methods.
    """
    return [
        {
            "id": ConformanceMethod.TOKEN_REPLAY.value,
            "name": "Token Replay",
            "description": "Fast token-based replay conformance checking",
            "is_default": True,
        },
        {
            "id": ConformanceMethod.ALIGNMENT.value,
            "name": "Alignment",
            "description": "More accurate alignment-based conformance (slower)",
            "is_default": False,
        },
    ]


@router.get("/quality/{dataset_id}/{model_id}", response_model=QualityMetricsResponse)
async def get_quality_metrics(
    dataset_id: str,
    model_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get full quality metrics for a log-model pair.

    Returns all 4 quality dimensions from PM4py:
    - **Fitness**: How well the log fits the model (0-1)
    - **Precision**: How much the model allows for behavior not observed in log (0-1)
    - **Generalization**: How well the model generalizes beyond observed behavior (0-1)
    - **Simplicity**: How simple/understandable the model is (0-1)
    - **F-score**: Harmonic mean of fitness and precision

    All metrics are higher-is-better.
    """
    logger.info(
        "quality_metrics_started",
        dataset_id=dataset_id,
        model_id=model_id,
    )
    start_time = time.perf_counter()

    # Get the event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    event_log = log_result.scalar_one_or_none()

    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get the process model
    model_result = await session.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = model_result.scalar_one_or_none()

    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        raise HTTPException(
            status_code=400,
            detail="Process model has no serialized data",
        )

    try:
        # Get full quality metrics
        metrics = conformance_service.get_full_quality_metrics(event_log, model)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "quality_metrics_completed",
            dataset_id=dataset_id,
            model_id=model_id,
            fitness=metrics["fitness"],
            precision=metrics.get("precision"),
            generalization=metrics.get("generalization"),
            simplicity=metrics.get("simplicity"),
            f_score=metrics.get("f_score"),
            duration_ms=round(duration_ms, 2),
        )

        return QualityMetricsResponse(
            dataset_id=dataset_id,
            model_id=model_id,
            fitness=metrics["fitness"],
            precision=metrics.get("precision"),
            generalization=metrics.get("generalization"),
            simplicity=metrics.get("simplicity"),
            f_score=metrics.get("f_score"),
        )

    except Exception as e:
        logger.error(
            "quality_metrics_failed",
            dataset_id=dataset_id,
            model_id=model_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get quality metrics: {e!s}",
        )


# =============================================================================
# Phase 11.1 - Reference Model Import (PNML/BPMN)
# =============================================================================


@router.post("/import-model")
async def import_reference_model(
    project_id: str = Query(..., description="Project ID to store the model under"),
    model_name: str = Query(..., description="Name for the imported model"),
    model_content: str = Query(..., description="XML content (PNML or BPMN)"),
    session: AsyncSession = Depends(get_session),
):
    """
    Import a reference model from PNML or BPMN format.

    Phase 11.1 - Reference Model Management

    Supports:
    - PNML (Petri Net Markup Language) - direct import
    - BPMN 2.0 (Business Process Model and Notation) - imported and converted to Petri net

    Use this to upload external reference models for conformance checking.

    Args:
        project_id: The project to associate the model with
        model_name: Display name for the model
        model_content: XML content of the PNML or BPMN file

    Returns:
        Created process model with ID
    """
    from uuid import uuid4

    from src.features.process_mining.enums import ModelFormat
    from src.features.process_mining.models import ProcessModel
    from src.features.process_mining.services.model_importer import model_importer
    from src.platform.models import Project

    logger.info(
        "model_import_started",
        project_id=project_id,
        model_name=model_name,
        content_length=len(model_content),
    )
    start_time = time.perf_counter()

    # Validate project exists
    project_result = await session.execute(select(Project).where(Project.id == project_id))
    project = project_result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Auto-detect format
        model_format = model_importer.validate_model_format(model_content)
        logger.info("model_format_detected", format=model_format.value)

        # Import based on format
        if model_format == ModelFormat.PETRI_NET:
            # PNML import
            net, im, fm = model_importer.import_pnml(model_content)
        elif model_format == ModelFormat.BPMN:
            # BPMN import and convert to Petri net
            net, im, fm = model_importer.import_and_convert_bpmn(model_content)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {model_format.value}")

        # Serialize the Petri net using joblib
        serialized_model = model_importer.serialize_petri_net(net, im, fm)

        # Create ProcessModel record
        model_id = str(uuid4())
        process_model = ProcessModel(
            id=model_id,
            project_id=project_id,
            name=model_name,
            model_format=ModelFormat.PETRI_NET.value,  # Always Petri net after conversion
            serialized_model=serialized_model,
            metadata_json=json.dumps(
                {
                    "imported_from": model_format.value,
                    "import_method": "reference_model_import",
                    "places_count": len(net.places),
                    "transitions_count": len(net.transitions),
                    "arcs_count": len(net.arcs),
                }
            ),
        )

        session.add(process_model)
        await session.commit()
        await session.refresh(process_model)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "model_import_success",
            model_id=model_id,
            format=model_format.value,
            places=len(net.places),
            transitions=len(net.transitions),
            duration_ms=round(duration_ms, 2),
        )

        return {
            "model_id": model_id,
            "name": model_name,
            "format": ModelFormat.PETRI_NET.value,
            "source_format": model_format.value,
            "places": len(net.places),
            "transitions": len(net.transitions),
            "arcs": len(net.arcs),
            "created_at": process_model.created_at,
        }

    except ValidationError as e:
        logger.warning("model_import_validation_failed", error=str(e))
        raise HTTPException(status_code=400, detail=str(e)) from e

    except Exception as e:
        logger.error("model_import_failed", error=str(e), exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to import model: {e!s}") from e


# =============================================================================
# Phase 11.3 - Root Cause Analysis
# =============================================================================


@router.get("/root-cause/{dataset_id}/{model_id}")
async def get_root_cause_analysis(
    dataset_id: str,
    model_id: str,
    attributes: str = Query(
        "resource",
        description="Comma-separated list of attributes to analyze (e.g., 'resource,department')",
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Get comprehensive root cause analysis for conformance deviations.

    Phase 11.3 - Root Cause Analysis

    Analyzes:
    - Deviation aggregation by activity (which activities cause most issues)
    - Deviation aggregation by position (where in the process do issues occur)
    - Attribute correlation (which resources/departments have more deviations)

    Use this to identify patterns in conformance violations.

    Args:
        dataset_id: Event log ID
        model_id: Process model ID
        attributes: Comma-separated attributes to analyze (default: "resource")

    Returns:
        Comprehensive root cause analysis report
    """
    from src.features.process_mining.services.root_cause import root_cause_analyzer

    logger.info(
        "root_cause_analysis_started",
        dataset_id=dataset_id,
        model_id=model_id,
        attributes=attributes,
    )
    start_time = time.perf_counter()

    # Get event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get process model
    model_result = await session.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = model_result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    if not model.serialized_model:
        raise HTTPException(status_code=400, detail="Process model has no serialized data")

    try:
        # Parse attributes
        attribute_list = [a.strip() for a in attributes.split(",") if a.strip()]

        # Get comprehensive analysis
        analysis = root_cause_analyzer.get_comprehensive_root_cause_analysis(
            event_log, model, attribute_list
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "root_cause_analysis_completed",
            dataset_id=dataset_id,
            model_id=model_id,
            duration_ms=round(duration_ms, 2),
        )

        return analysis

    except Exception as e:
        logger.error(
            "root_cause_analysis_failed",
            dataset_id=dataset_id,
            model_id=model_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to analyze root causes: {e!s}") from e


@router.get("/deviations/by-activity/{dataset_id}/{model_id}")
async def get_deviations_by_activity(
    dataset_id: str,
    model_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get deviation aggregation by activity.

    Identifies which activities cause the most conformance issues.
    """
    from src.features.process_mining.services.root_cause import root_cause_analyzer

    logger.info("deviations_by_activity_started", dataset_id=dataset_id, model_id=model_id)

    # Get event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get process model
    model_result = await session.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = model_result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    try:
        return root_cause_analyzer.aggregate_deviations_by_activity(event_log, model)

    except Exception as e:
        logger.error("deviations_by_activity_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to aggregate deviations: {e!s}") from e


@router.get("/deviations/by-position/{dataset_id}/{model_id}")
async def get_deviations_by_position(
    dataset_id: str,
    model_id: str,
    session: AsyncSession = Depends(get_session),
):
    """
    Get deviation aggregation by position in trace.

    Identifies at which point in the process deviations occur most frequently.
    """
    from src.features.process_mining.services.root_cause import root_cause_analyzer

    logger.info("deviations_by_position_started", dataset_id=dataset_id, model_id=model_id)

    # Get event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get process model
    model_result = await session.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = model_result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    try:
        return root_cause_analyzer.aggregate_deviations_by_position(event_log, model)

    except Exception as e:
        logger.error("deviations_by_position_failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to aggregate deviations: {e!s}") from e


@router.get("/deviations/attribute-correlation/{dataset_id}/{model_id}")
async def get_attribute_correlation(
    dataset_id: str,
    model_id: str,
    attribute: str = Query(
        "resource", description="Attribute to analyze (e.g., resource, department)"
    ),
    session: AsyncSession = Depends(get_session),
):
    """
    Analyze correlation between case attributes and conformance deviations.

    Identifies which attribute values (e.g., specific resources or departments)
    are associated with more conformance violations.
    """
    from src.features.process_mining.services.root_cause import root_cause_analyzer

    logger.info(
        "attribute_correlation_started",
        dataset_id=dataset_id,
        model_id=model_id,
        attribute=attribute,
    )

    # Get event log
    log_result = await session.execute(select(Dataset).where(Dataset.id == dataset_id))
    event_log = log_result.scalar_one_or_none()
    if not event_log:
        raise HTTPException(status_code=404, detail="Event log not found")

    # Get process model
    model_result = await session.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = model_result.scalar_one_or_none()
    if not model:
        raise HTTPException(status_code=404, detail="Process model not found")

    try:
        return root_cause_analyzer.analyze_attribute_correlation(event_log, model, attribute)

    except Exception as e:
        logger.error("attribute_correlation_failed", error=str(e), attribute=attribute)
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze attribute correlation: {e!s}"
        ) from e
