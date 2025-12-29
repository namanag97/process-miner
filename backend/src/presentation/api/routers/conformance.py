"""Conformance Checking API Router."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.core.conformance_service import conformance_service
from src.domain.value_objects import ConformanceMethod
from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import (
    ConformanceResultRepository,
    EventLogRepository,
    ProcessModelRepository,
)
from src.presentation.api.routers.auth import User, require_auth
from src.domain.constants import HttpStatus, DisplayLimits, PaginationDefaults

router = APIRouter(prefix="/conformance")


class ConformanceRequest(BaseModel):
    log_id: str
    model_id: str
    method: str = "token_replay"


class ConformanceResponse(BaseModel):
    result_id: str
    log_id: str
    model_id: str
    fitness: float
    precision: Optional[float]
    is_conformant: bool
    method: str


class DiagnosticsResponse(BaseModel):
    total_traces: int
    fitting_traces: int
    non_fitting_traces: int
    trace_fitness_ratio: float
    deviations: List[Dict[str, Any]]


class DeviationResponse(BaseModel):
    case_id: str
    deviation_type: str
    details: str


# =============================================================================
# FLOW 3 RESPONSE MODELS - Alignments, Deviation Patterns, Quality Metrics
# =============================================================================


class AlignmentStepResponse(BaseModel):
    """A single step in an alignment."""

    step_index: int
    step_type: str  # sync, model_move, log_move, invisible
    log_activity: Optional[str]
    model_activity: Optional[str]
    cost: int = 0


class CaseAlignmentResponse(BaseModel):
    """Alignment result for a single case."""

    case_id: str
    fitness: float
    is_fitting: bool
    alignment_cost: int
    sync_moves: int
    model_moves: int
    log_moves: int
    alignment: List[AlignmentStepResponse]


class AlignmentResultResponse(BaseModel):
    """Full alignment results for all cases."""

    log_id: str
    model_id: str
    total_traces: int
    fitting_traces: int
    average_fitness: float
    average_cost: float
    aligned_traces: List[CaseAlignmentResponse]


class DeviationPatternResponse(BaseModel):
    """A clustered deviation pattern."""

    pattern_id: str
    pattern_type: str  # missing, unexpected, wrong_sequence
    description: str
    activity: Optional[str]
    occurrence_count: int
    occurrence_rate: float
    affected_cases: List[str]
    severity: str  # low, medium, high, critical


class DeviationPatternsResponse(BaseModel):
    """Summary of all deviation patterns."""

    log_id: str
    model_id: str
    total_deviations: int
    deviation_rate: float
    total_cases_with_deviations: int
    patterns: List[DeviationPatternResponse]


class ComprehensiveQualityResponse(BaseModel):
    """Comprehensive quality metrics combining all dimensions."""

    log_id: str
    model_id: str
    # Fitness metrics
    fitness: float
    trace_fitness: float
    log_fitness: float
    # Precision metrics
    precision: Optional[float]
    # Quality dimensions
    generalization: Optional[float]
    simplicity: Optional[float]
    # Conformance summary
    fitting_traces_count: int
    non_fitting_traces_count: int
    fitting_traces_percentage: float
    # Overall
    overall_quality: float


@router.post("/check", response_model=ConformanceResponse)
async def check_conformance(
    request: ConformanceRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Check conformance between an event log and a process model.
    """
    # Get log and model
    log_repo = EventLogRepository(session)
    model_repo = ProcessModelRepository(session)

    log = await log_repo.get_by_id(UUID(request.log_id))
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    model = await model_repo.get_by_id(UUID(request.model_id))
    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    # Validate method
    try:
        method = ConformanceMethod(request.method)
    except ValueError:
        raise HTTPException(
            status_code=HttpStatus.BAD_REQUEST,
            detail=f"Invalid method. Valid options: {[m.value for m in ConformanceMethod]}",
        )

    try:
        # Check conformance
        aggregate = conformance_service.check_conformance(
            event_log=log,
            model=model,
            method=method,
        )

        result = aggregate.conformance

        # Save result
        result_repo = ConformanceResultRepository(session)
        await result_repo.save(result)

        return ConformanceResponse(
            result_id=str(result.id),
            log_id=request.log_id,
            model_id=request.model_id,
            fitness=result.fitness,
            precision=result.precision,
            is_conformant=result.is_conformant,
            method=method.value,
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Conformance check failed: {str(e)}")


@router.get("/fitness")
async def get_fitness(
    log_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Calculate fitness score for log-model pair.
    """
    log_repo = EventLogRepository(session)
    model_repo = ProcessModelRepository(session)

    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        fitness = conformance_service.calculate_fitness(log, model)
        return {"fitness": fitness, "log_id": str(log_id), "model_id": str(model_id)}
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Fitness calculation failed: {str(e)}")


@router.get("/precision")
async def get_precision(
    log_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Calculate precision score for log-model pair.
    """
    log_repo = EventLogRepository(session)
    model_repo = ProcessModelRepository(session)

    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        precision = conformance_service.calculate_precision(log, model)
        return {"precision": precision, "log_id": str(log_id), "model_id": str(model_id)}
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Precision calculation failed: {str(e)}")


@router.get("/diagnostics", response_model=DiagnosticsResponse)
async def get_diagnostics(
    log_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detailed conformance diagnostics.
    """
    log_repo = EventLogRepository(session)
    model_repo = ProcessModelRepository(session)

    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        diagnostics = conformance_service.get_diagnostics(log, model)
        return DiagnosticsResponse(**diagnostics)
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Diagnostics failed: {str(e)}")


@router.get("/deviations", response_model=List[DeviationResponse])
async def detect_deviations(
    log_id: UUID,
    model_id: UUID,
    threshold: float = 0.8,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Detect deviations from the process model.
    """
    log_repo = EventLogRepository(session)
    model_repo = ProcessModelRepository(session)

    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        deviations = conformance_service.detect_deviations(log, model, threshold)
        return [
            DeviationResponse(
                case_id=d.case_id,
                deviation_type=d.deviation_type,
                details=d.details,
            )
            for d in deviations
        ]
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Deviation detection failed: {str(e)}")


# =============================================================================
# FLOW 3 ENHANCED ENDPOINTS - Alignments, Patterns, Quality Metrics
# =============================================================================


@router.post("/alignment", response_model=AlignmentResultResponse)
async def get_alignments(
    log_id: UUID,
    model_id: UUID,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detailed alignment results for each case.
    Shows sync moves, model moves, and log moves.
    """
    import pm4py

    from src.application.core.discovery_service import discovery_service

    log_repo = EventLogRepository(session)
    model_repo = ProcessModelRepository(session)

    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        # Get Petri net
        net, im, fm = discovery_service._get_petri_net(model)

        # Convert log to PM4Py format
        pm4py_log = discovery_service._to_pm4py_log(log)

        # Compute alignments
        aligned_traces = pm4py.conformance_diagnostics_alignments(pm4py_log, net, im, fm)

        # Build response
        case_alignments = []
        total_fitness = 0.0
        total_cost = 0
        fitting_count = 0

        for i, (trace, alignment_info) in enumerate(zip(pm4py_log, aligned_traces[:limit])):
            case_id = trace.attributes.get("concept:name", str(i))

            # Parse alignment
            alignment_steps = []
            sync_moves = 0
            model_moves = 0
            log_moves = 0

            if alignment_info and "alignment" in alignment_info:
                for step_idx, step in enumerate(alignment_info["alignment"]):
                    log_act = step[0] if step[0] != ">>" else None
                    model_act = step[1] if step[1] != ">>" else None

                    if log_act and model_act:
                        step_type = "sync"
                        sync_moves += 1
                    elif model_act and not log_act:
                        step_type = "model_move"
                        model_moves += 1
                    else:
                        step_type = "log_move"
                        log_moves += 1

                    alignment_steps.append(
                        AlignmentStepResponse(
                            step_index=step_idx,
                            step_type=step_type,
                            log_activity=log_act,
                            model_activity=model_act,
                            cost=0 if step_type == "sync" else 1,
                        )
                    )

            cost = alignment_info.get("cost", 0) if alignment_info else 0
            fitness = alignment_info.get("fitness", 1.0) if alignment_info else 1.0
            is_fitting = cost == 0

            total_fitness += fitness
            total_cost += cost
            if is_fitting:
                fitting_count += 1

            case_alignments.append(
                CaseAlignmentResponse(
                    case_id=case_id,
                    fitness=round(fitness, 4),
                    is_fitting=is_fitting,
                    alignment_cost=cost,
                    sync_moves=sync_moves,
                    model_moves=model_moves,
                    log_moves=log_moves,
                    alignment=alignment_steps[:50],  # Limit steps per trace
                )
            )

        num_traces = len(aligned_traces[:limit])

        return AlignmentResultResponse(
            log_id=str(log_id),
            model_id=str(model_id),
            total_traces=num_traces,
            fitting_traces=fitting_count,
            average_fitness=round(total_fitness / max(num_traces, 1), 4),
            average_cost=round(total_cost / max(num_traces, 1), 2),
            aligned_traces=case_alignments,
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Alignment computation failed: {str(e)}")


@router.get("/deviation-patterns", response_model=DeviationPatternsResponse)
async def get_deviation_patterns(
    log_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get clustered deviation patterns.
    Groups similar deviations and provides statistics.
    """
    log_repo = EventLogRepository(session)
    model_repo = ProcessModelRepository(session)

    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        # Get diagnostics
        diagnostics = conformance_service.get_diagnostics(log, model)

        # Build pattern map
        pattern_map: Dict[str, Dict] = {}
        total_deviations = 0
        cases_with_deviations = set()

        for dev in diagnostics.get("deviations", []):
            dev_type = dev.get("type", "unknown")
            activity = dev.get("activity", "unknown")
            case_id = dev.get("case_id", "unknown")

            pattern_key = f"{dev_type}:{activity}"

            if pattern_key not in pattern_map:
                pattern_map[pattern_key] = {
                    "type": dev_type,
                    "activity": activity,
                    "cases": [],
                    "count": 0,
                }

            pattern_map[pattern_key]["count"] += 1
            pattern_map[pattern_key]["cases"].append(case_id)
            total_deviations += 1
            cases_with_deviations.add(case_id)

        # Convert to response
        patterns = []
        for idx, (key, data) in enumerate(
            sorted(pattern_map.items(), key=lambda x: x[1]["count"], reverse=True)
        ):
            occurrence_rate = data["count"] / max(log.total_cases, 1)

            # Determine severity
            if occurrence_rate > 0.5:
                severity = "critical"
            elif occurrence_rate > 0.2:
                severity = "high"
            elif occurrence_rate > 0.05:
                severity = "medium"
            else:
                severity = "low"

            patterns.append(
                DeviationPatternResponse(
                    pattern_id=f"PAT-{idx + 1:03d}",
                    pattern_type=data["type"],
                    description=f"{data['type'].replace('_', ' ').title()} for activity '{data['activity']}'",
                    activity=data["activity"],
                    occurrence_count=data["count"],
                    occurrence_rate=round(occurrence_rate, 4),
                    affected_cases=list(set(data["cases"]))[:20],  # Limit case IDs
                    severity=severity,
                )
            )

        return DeviationPatternsResponse(
            log_id=str(log_id),
            model_id=str(model_id),
            total_deviations=total_deviations,
            deviation_rate=round(len(cases_with_deviations) / max(log.total_cases, 1), 4),
            total_cases_with_deviations=len(cases_with_deviations),
            patterns=patterns,
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Deviation pattern analysis failed: {str(e)}")


@router.get("/quality-metrics", response_model=ComprehensiveQualityResponse)
async def get_comprehensive_quality(
    log_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get comprehensive quality metrics for conformance checking.
    Combines all four quality dimensions with detailed fitness breakdown.
    """
    from src.application.core.discovery_service import discovery_service
    from src.application.core.pm4py_service import pm4py_service

    log_repo = EventLogRepository(session)
    model_repo = ProcessModelRepository(session)

    log = await log_repo.get_by_id(log_id)
    if not log:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Event log not found")

    model = await model_repo.get_by_id(model_id)
    if not model:
        raise HTTPException(status_code=HttpStatus.NOT_FOUND, detail="Process model not found")

    try:
        # Get diagnostics for fitness breakdown
        diagnostics = conformance_service.get_diagnostics(log, model)

        # Calculate all metrics
        fitness = conformance_service.calculate_fitness(log, model)

        try:
            precision = conformance_service.calculate_precision(log, model)
        except Exception:
            precision = None

        generalization = None
        simplicity = None
        try:
            net, im, fm = discovery_service._get_petri_net(model)
            generalization = pm4py_service.evaluate_generalization(log, net, im, fm)
            simplicity = pm4py_service.evaluate_simplicity(net)
        except Exception:
            pass

        # Calculate overall quality
        metrics = [fitness]
        if precision is not None:
            metrics.append(precision)
        if generalization is not None:
            metrics.append(generalization)
        if simplicity is not None:
            metrics.append(simplicity)

        overall_quality = sum(metrics) / len(metrics)

        return ComprehensiveQualityResponse(
            log_id=str(log_id),
            model_id=str(model_id),
            fitness=round(fitness, 4),
            trace_fitness=round(diagnostics.get("trace_fitness_ratio", fitness), 4),
            log_fitness=round(fitness, 4),
            precision=round(precision, 4) if precision else None,
            generalization=round(generalization, 4) if generalization else None,
            simplicity=round(simplicity, 4) if simplicity else None,
            fitting_traces_count=diagnostics.get("fitting_traces", 0),
            non_fitting_traces_count=diagnostics.get("non_fitting_traces", 0),
            fitting_traces_percentage=round(diagnostics.get("trace_fitness_ratio", 1.0) * 100, 2),
            overall_quality=round(overall_quality, 4),
        )
    except Exception as e:
        raise HTTPException(status_code=HttpStatus.INTERNAL_ERROR, detail=f"Quality metrics calculation failed: {str(e)}")
