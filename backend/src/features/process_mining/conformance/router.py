"""Conformance Checking API Router.

Endpoints for checking conformance between event logs and process models.

## Business Context
Conformance checking compares actual process execution (event logs) against
expected process (models) to find deviations:
- **Fitness**: How well does the log fit the model? (0-1, higher is better)
- **Precision**: How much extra behavior does the model allow? (0-1, higher is better)
- **Generalization**: How well does the model generalize? (0-1)
- **Simplicity**: How simple/readable is the model? (0-1)

## Testing Instructions

### Prerequisites
1. Have a dataset in READY status
2. Discover a process model: `POST /api/v1/discovery/discover`
3. Get both dataset_id and model_id

### Test Flow
1. **Check Conformance**:
   ```
   POST /api/v1/conformance/check
   {"dataset_id": "{id}", "model_id": "{id}", "method": "token_replay"}
   ```
2. **Get Quality Metrics**: `GET /api/v1/conformance/quality/{dataset_id}/{model_id}`
3. **Get Diagnostics**: `GET /api/v1/conformance/diagnostics/{dataset_id}/{model_id}`
4. **Get Deviations**: `GET /api/v1/conformance/deviations/{dataset_id}/{model_id}`
5. **Root Cause Analysis**: `GET /api/v1/conformance/root-cause/{dataset_id}/{model_id}`
6. **List Results**: `GET /api/v1/conformance/results`
7. **Import PNML/BPMN**: `POST /api/v1/conformance/import-model`

### Methods
- `token_replay`: Fast, good for quick checks
- `alignment`: More accurate, slower (for detailed analysis)

### Common Errors
- **400**: Model has no serialized data (rediscover)
- **404**: Dataset or Model not found
- **409**: Dataset not ready (complete ingestion first)
"""

import json
import time

from fastapi import APIRouter, HTTPException, Query
from pydantic import ValidationError
from sqlalchemy import func, select

from src.api.dependencies import ReadDBSession, ServiceContainer
from src.features.process_mining.enums import ConformanceMethod, ModelFormat
from src.features.process_mining.models import (
    ConformanceResult,
    Dataset,
    DatasetStatus,
    ProcessModel,
)
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
from src.platform.core.exceptions import (
    BadRequestError,
    ConformanceError,
    ModelNotFoundError,
    NotFoundError,
    ProcessingError,
    ProjectNotFoundError,
)

logger = get_logger(__name__)

router = APIRouter(prefix="/conformance", tags=["Conformance"])


# =============================================================================
# Helper functions
# =============================================================================


async def _get_dataset_or_404(db: ReadDBSession, dataset_id: str) -> Dataset:
    """Get dataset or raise 404."""
    result = await db.execute(select(Dataset).where(Dataset.id == dataset_id))
    dataset = result.scalar_one_or_none()
    if not dataset:
        raise NotFoundError(resource='Dataset', resource_id='unknown')
    return dataset


async def _get_model_or_404(db: ReadDBSession, model_id: str) -> ProcessModel:
    """Get process model or raise 404."""
    result = await db.execute(select(ProcessModel).where(ProcessModel.id == model_id))
    model = result.scalar_one_or_none()
    if not model:
        raise ModelNotFoundError(model_id='unknown')
    if not model.serialized_model:
        raise BadRequestError(message="Process model has no serialized data")
    return model


# =============================================================================
# ENDPOINTS
# =============================================================================


@router.post("/check", response_model=ConformanceResponse)
async def check_conformance(
    request: ConformanceCheckRequest,
    db: ReadDBSession,
    container: ServiceContainer,
    auto_discover: bool = Query(False, description="Auto-discover model if model_id not provided"),
):
    """Check conformance between an event log and a process model."""
    logger.info(
        "conformance_check_started",
        dataset_id=request.dataset_id,
        model_id=request.model_id,
        method=str(request.method),
    )
    start_time = time.perf_counter()

    event_log = await _get_dataset_or_404(db, request.dataset_id)

    if event_log.status != DatasetStatus.READY.value:
        raise ConflictError(
            message=f"Dataset not ready (status: {event_log.status}). Complete ingestion first."
        )

    model = await _get_model_or_404(db, request.model_id)

    try:
        result = container.conformance.check_conformance(
            event_log=event_log,
            model=model,
            method=request.method,
        )

        conformance_record = ConformanceResult(
            dataset_id=request.dataset_id,
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
        db.add(conformance_record)
        await db.commit()
        await db.refresh(conformance_record)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "conformance_check_completed",
            result_id=conformance_record.id,
            fitness=result["fitness"],
            duration_ms=round(duration_ms, 2),
        )

        return ConformanceResponse(
            id=conformance_record.id,
            dataset_id=conformance_record.dataset_id,
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
        logger.error("conformance_check_failed", error=str(e), exc_info=True)
        raise ConformanceError(message=f"Conformance check failed: {e!s}")


@router.get("/results", response_model=ConformanceListResponse)
async def list_conformance_results(
    db: ReadDBSession,
    dataset_id: str | None = Query(None),
    model_id: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List conformance check results."""
    query = select(ConformanceResult)
    if dataset_id:
        query = query.where(ConformanceResult.dataset_id == dataset_id)
    if model_id:
        query = query.where(ConformanceResult.model_id == model_id)
    query = query.order_by(ConformanceResult.created_at.desc())

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.offset((page - 1) * page_size).limit(page_size)
    results = (await db.execute(query)).scalars().all()

    items = []
    for r in results:
        diagnostics = json.loads(r.diagnostics_json) if r.diagnostics_json else {}
        items.append(
            ConformanceResponse(
                id=r.id,
                dataset_id=r.dataset_id,
                model_id=r.model_id,
                fitness=r.fitness,
                precision=r.precision,
                method=r.method,
                algorithm_used=r.method,
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
async def get_conformance_result(result_id: str, db: ReadDBSession):
    """Get a specific conformance check result."""
    result = await db.execute(select(ConformanceResult).where(ConformanceResult.id == result_id))
    record = result.scalar_one_or_none()
    if not record:
        raise NotFoundError(resource='Conformance Result', resource_id='unknown')

    diagnostics = json.loads(record.diagnostics_json) if record.diagnostics_json else {}
    return ConformanceResponse(
        id=record.id,
        dataset_id=record.dataset_id,
        model_id=record.model_id,
        fitness=record.fitness,
        precision=record.precision,
        method=record.method,
        algorithm_used=record.method,
        is_conformant=record.fitness >= 0.8,
        fitting_traces=diagnostics.get("fitting_traces", 0),
        total_traces=diagnostics.get("total_traces", 0),
        created_at=record.created_at,
    )


@router.delete("/results/{result_id}")
async def delete_conformance_result(result_id: str, db: ReadDBSession):
    """Delete a conformance check result."""
    result = await db.execute(select(ConformanceResult).where(ConformanceResult.id == result_id))
    record = result.scalar_one_or_none()
    if not record:
        raise NotFoundError(resource='Conformance Result', resource_id='unknown')
    await db.delete(record)
    await db.commit()
    return {"status": "deleted", "result_id": result_id}


@router.get("/diagnostics/{dataset_id}/{model_id}", response_model=DiagnosticsResponse)
async def get_conformance_diagnostics(
    dataset_id: str,
    model_id: str,
    db: ReadDBSession,
    container: ServiceContainer,
):
    """Get detailed conformance diagnostics for a log-model pair."""
    event_log = await _get_dataset_or_404(db, dataset_id)
    model = await _get_model_or_404(db, model_id)

    try:
        diagnostics = container.conformance.get_diagnostics(event_log, model)
        result = container.conformance.check_conformance(event_log, model)

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
        raise ProcessingError(message=f"Failed to get diagnostics: {e!s}")


@router.get("/deviations/{dataset_id}/{model_id}", response_model=list[DeviationResponse])
async def get_deviations(
    dataset_id: str,
    model_id: str,
    db: ReadDBSession,
    container: ServiceContainer,
    threshold: float = Query(0.8, ge=0.0, le=1.0),
):
    """Detect and list specific deviations from the model."""
    event_log = await _get_dataset_or_404(db, dataset_id)
    model = await _get_model_or_404(db, model_id)

    try:
        deviations = container.conformance.detect_deviations(event_log, model, threshold)
        return [
            DeviationResponse(
                case_id=d["case_id"],
                activity=d.get("activity"),
                deviation_type=d["deviation_type"],
                details=d["details"],
            )
            for d in deviations[:100]
        ]
    except Exception as e:
        raise ProcessingError(message=f"Failed to detect deviations: {e!s}")


@router.get("/alignments/{dataset_id}/{model_id}", response_model=AlignmentDiagnosticsResponse)
async def get_alignment_diagnostics(
    dataset_id: str,
    model_id: str,
    db: ReadDBSession,
    container: ServiceContainer,
    max_cases: int = Query(100, ge=1, le=1000),
):
    """Get detailed alignment diagnostics for a log-model pair."""
    logger.info("alignment_diagnostics_started", dataset_id=dataset_id, model_id=model_id)
    start_time = time.perf_counter()

    event_log = await _get_dataset_or_404(db, dataset_id)
    model = await _get_model_or_404(db, model_id)

    try:
        diagnostics = container.conformance.get_alignment_diagnostics(event_log, model, max_cases)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("alignment_diagnostics_completed", duration_ms=round(duration_ms, 2))

        return AlignmentDiagnosticsResponse(
            dataset_id=dataset_id,
            model_id=model_id,
            total_cases=diagnostics["total_cases"],
            fitting_cases=diagnostics["fitting_cases"],
            average_fitness=diagnostics["average_fitness"],
            case_alignments=diagnostics["case_alignments"],
        )
    except Exception as e:
        logger.error("alignment_diagnostics_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"Failed to get alignment diagnostics: {e!s}")


@router.get("/methods")
async def list_conformance_methods():
    """List available conformance checking methods."""
    return [
        {
            "id": ConformanceMethod.TOKEN_REPLAY.value,
            "name": "Token Replay",
            "description": "Fast token-based replay",
            "is_default": True,
        },
        {
            "id": ConformanceMethod.ALIGNMENT.value,
            "name": "Alignment",
            "description": "More accurate alignment-based (slower)",
            "is_default": False,
        },
    ]


@router.get("/quality/{dataset_id}/{model_id}", response_model=QualityMetricsResponse)
async def get_quality_metrics(
    dataset_id: str,
    model_id: str,
    db: ReadDBSession,
    container: ServiceContainer,
):
    """Get full quality metrics for a log-model pair (fitness, precision, generalization, simplicity)."""
    logger.info("quality_metrics_started", dataset_id=dataset_id, model_id=model_id)
    start_time = time.perf_counter()

    event_log = await _get_dataset_or_404(db, dataset_id)
    model = await _get_model_or_404(db, model_id)

    try:
        metrics = container.conformance.get_full_quality_metrics(event_log, model)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("quality_metrics_completed", duration_ms=round(duration_ms, 2))

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
        logger.error("quality_metrics_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"Failed to get quality metrics: {e!s}")


@router.post("/import-model")
async def import_reference_model(
    db: ReadDBSession,
    container: ServiceContainer,
    project_id: str = Query(..., description="Project ID to store the model under"),
    model_name: str = Query(..., description="Name for the imported model"),
    model_content: str = Query(..., description="XML content (PNML or BPMN)"),
):
    """Import a reference model from PNML or BPMN format."""
    from uuid import uuid4

    from src.features.process_mining.services.model_importer import model_importer
    from src.platform.models import Project

    logger.info("model_import_started", project_id=project_id, model_name=model_name)
    start_time = time.perf_counter()

    project_result = await db.execute(select(Project).where(Project.id == project_id))
    if not project_result.scalar_one_or_none():
        raise ProjectNotFoundError(project_id='unknown')

    try:
        model_format = model_importer.validate_model_format(model_content)

        if model_format == ModelFormat.PETRI_NET:
            net, im, fm = model_importer.import_pnml(model_content)
        elif model_format == ModelFormat.BPMN:
            net, im, fm = model_importer.import_and_convert_bpmn(model_content)
        else:
            raise BadRequestError(message=f"Unsupported format: {model_format.value}")

        serialized_model = model_importer.serialize_petri_net(net, im, fm)

        model_id = str(uuid4())
        process_model = ProcessModel(
            id=model_id,
            project_id=project_id,
            name=model_name,
            model_format=ModelFormat.PETRI_NET.value,
            serialized_model=serialized_model,
            metadata_json=json.dumps(
                {
                    "imported_from": model_format.value,
                    "places_count": len(net.places),
                    "transitions_count": len(net.transitions),
                }
            ),
        )

        db.add(process_model)
        await db.commit()
        await db.refresh(process_model)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("model_import_success", model_id=model_id, duration_ms=round(duration_ms, 2))

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
        raise BadRequestError(message=str(e)) from e
    except Exception as e:
        logger.error("model_import_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"Failed to import model: {e!s}") from e


@router.get("/root-cause/{dataset_id}/{model_id}")
async def get_root_cause_analysis(
    dataset_id: str,
    model_id: str,
    db: ReadDBSession,
    container: ServiceContainer,
    attributes: str = Query(
        "resource", description="Comma-separated list of attributes to analyze"
    ),
):
    """Get comprehensive root cause analysis for conformance deviations."""
    from src.features.process_mining.services.root_cause import root_cause_analyzer

    logger.info("root_cause_analysis_started", dataset_id=dataset_id, model_id=model_id)
    start_time = time.perf_counter()

    event_log = await _get_dataset_or_404(db, dataset_id)
    model = await _get_model_or_404(db, model_id)

    try:
        attribute_list = [a.strip() for a in attributes.split(",") if a.strip()]
        analysis = root_cause_analyzer.get_comprehensive_root_cause_analysis(
            event_log, model, attribute_list
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("root_cause_analysis_completed", duration_ms=round(duration_ms, 2))
        return analysis
    except Exception as e:
        logger.error("root_cause_analysis_failed", error=str(e), exc_info=True)
        raise ProcessingError(message=f"Failed to analyze root causes: {e!s}") from e


@router.get("/deviations/by-activity/{dataset_id}/{model_id}")
async def get_deviations_by_activity(
    dataset_id: str,
    model_id: str,
    db: ReadDBSession,
):
    """Get deviation aggregation by activity."""
    from src.features.process_mining.services.root_cause import root_cause_analyzer

    event_log = await _get_dataset_or_404(db, dataset_id)
    model = await _get_model_or_404(db, model_id)

    try:
        return root_cause_analyzer.aggregate_deviations_by_activity(event_log, model)
    except Exception as e:
        raise ProcessingError(message=f"Failed to aggregate deviations: {e!s}") from e


@router.get("/deviations/by-position/{dataset_id}/{model_id}")
async def get_deviations_by_position(
    dataset_id: str,
    model_id: str,
    db: ReadDBSession,
):
    """Get deviation aggregation by position in trace."""
    from src.features.process_mining.services.root_cause import root_cause_analyzer

    event_log = await _get_dataset_or_404(db, dataset_id)
    model = await _get_model_or_404(db, model_id)

    try:
        return root_cause_analyzer.aggregate_deviations_by_position(event_log, model)
    except Exception as e:
        raise ProcessingError(message=f"Failed to aggregate deviations: {e!s}") from e


@router.get("/deviations/attribute-correlation/{dataset_id}/{model_id}")
async def get_attribute_correlation(
    dataset_id: str,
    model_id: str,
    db: ReadDBSession,
    attribute: str = Query("resource", description="Attribute to analyze"),
):
    """Analyze correlation between case attributes and conformance deviations."""
    from src.features.process_mining.services.root_cause import root_cause_analyzer

    event_log = await _get_dataset_or_404(db, dataset_id)
    model = await _get_model_or_404(db, model_id)

    try:
        return root_cause_analyzer.analyze_attribute_correlation(event_log, model, attribute)
    except Exception as e:
        raise ProcessingError(
            message=f"Failed to analyze attribute correlation: {e!s}"
        ) from e
