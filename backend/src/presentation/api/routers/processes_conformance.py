"""Processes Conformance Sub-Router.

Provides conformance checking endpoints nested under /processes/{process_id}/conformance.
This sub-router is included by the main processes router.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import (
    EventLogRepository,
    ProcessModelRepository,
    ConformanceResultRepository,
)
from src.application.core.conformance_service import conformance_service
from src.presentation.api.routers.auth import require_auth, User


# =============================================================================
# SUB-ROUTER DEFINITION
# =============================================================================
router = APIRouter()


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class ConformanceCheckRequest(BaseModel):
    """Request to check conformance."""
    model_id: str
    method: str = "token_replay"


class ConformanceCheckResponse(BaseModel):
    """Response from conformance check."""
    result_id: str
    process_id: str
    model_id: str
    fitness: float
    precision: Optional[float]
    is_conformant: bool
    method: str
    _links: Dict[str, Dict[str, str]] = {}


class AlignmentStepResponse(BaseModel):
    """A single step in an alignment."""
    step_index: int
    step_type: str  # sync, model_move, log_move
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
    process_id: str
    model_id: str
    total_traces: int
    fitting_traces: int
    average_fitness: float
    average_cost: float
    aligned_traces: List[CaseAlignmentResponse]


class DeviationResponse(BaseModel):
    """A single deviation."""
    case_id: str
    deviation_type: str
    activity: Optional[str]
    details: str


class DeviationPatternResponse(BaseModel):
    """A clustered deviation pattern."""
    pattern_id: str
    pattern_type: str
    description: str
    activity: Optional[str]
    occurrence_count: int
    occurrence_rate: float
    affected_cases: List[str]
    severity: str


class DeviationPatternsResponse(BaseModel):
    """Summary of all deviation patterns."""
    process_id: str
    model_id: str
    total_deviations: int
    deviation_rate: float
    total_cases_with_deviations: int
    patterns: List[DeviationPatternResponse]


class DiagnosticsResponse(BaseModel):
    """Conformance diagnostics."""
    total_traces: int
    fitting_traces: int
    non_fitting_traces: int
    trace_fitness_ratio: float
    deviations: List[DeviationResponse]


class ComprehensiveQualityResponse(BaseModel):
    """Comprehensive quality metrics."""
    process_id: str
    model_id: str
    fitness: float
    trace_fitness: float
    log_fitness: float
    precision: Optional[float]
    generalization: Optional[float]
    simplicity: Optional[float]
    fitting_traces_count: int
    non_fitting_traces_count: int
    fitting_traces_percentage: float
    overall_quality: float


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    "/check",
    response_model=ConformanceCheckResponse,
    summary="Check Conformance",
    description="""
    Check conformance between the event log and a process model.
    
    **Methods:**
    - token_replay: Token-based replay (faster)
    - alignments: Alignment-based checking (more accurate)
    """,
)
async def check_conformance(
    process_id: UUID,
    request: ConformanceCheckRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Check conformance between event log and process model.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(UUID(request.model_id))
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        result = conformance_service.check_conformance(log, model, request.method)
        
        # Store result
        result_repo = ConformanceResultRepository(session)
        stored = await result_repo.create({
            "log_id": str(process_id),
            "model_id": request.model_id,
            "fitness": result.get("fitness", 0.0),
            "precision": result.get("precision"),
            "method": request.method,
        })
        await session.commit()
        
        return ConformanceCheckResponse(
            result_id=str(stored.id),
            process_id=str(process_id),
            model_id=request.model_id,
            fitness=result.get("fitness", 0.0),
            precision=result.get("precision"),
            is_conformant=result.get("fitness", 0.0) >= 0.8,
            method=request.method,
            _links={
                "alignments": {"href": f"/api/v1/processes/{process_id}/conformance/alignments?model_id={request.model_id}"},
                "deviations": {"href": f"/api/v1/processes/{process_id}/conformance/deviations?model_id={request.model_id}"},
                "diagnostics": {"href": f"/api/v1/processes/{process_id}/conformance/diagnostics?model_id={request.model_id}"},
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conformance check failed: {str(e)}")


@router.get(
    "/fitness",
    summary="Get Fitness Score",
    description="Calculate fitness score for the log-model pair.",
)
async def get_fitness(
    process_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get fitness score.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        fitness = conformance_service.calculate_fitness(log, model)
        return {"process_id": str(process_id), "model_id": str(model_id), "fitness": fitness}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fitness calculation failed: {str(e)}")


@router.get(
    "/precision",
    summary="Get Precision Score",
    description="Calculate precision score for the log-model pair.",
)
async def get_precision(
    process_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get precision score.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        precision = conformance_service.calculate_precision(log, model)
        return {"process_id": str(process_id), "model_id": str(model_id), "precision": precision}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Precision calculation failed: {str(e)}")


@router.get(
    "/alignments",
    response_model=AlignmentResultResponse,
    summary="Get Alignments",
    description="""
    Get detailed alignment results for each case.
    
    Shows synchronous moves, model moves, and log moves.
    """,
)
async def get_alignments(
    process_id: UUID,
    model_id: UUID,
    limit: int = Query(100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detailed alignments.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        alignments = conformance_service.compute_alignments(log, model, limit)
        
        return AlignmentResultResponse(
            process_id=str(process_id),
            model_id=str(model_id),
            total_traces=alignments.get("total_traces", 0),
            fitting_traces=alignments.get("fitting_traces", 0),
            average_fitness=alignments.get("average_fitness", 0.0),
            average_cost=alignments.get("average_cost", 0.0),
            aligned_traces=[
                CaseAlignmentResponse(
                    case_id=t["case_id"],
                    fitness=t.get("fitness", 0.0),
                    is_fitting=t.get("is_fitting", False),
                    alignment_cost=t.get("alignment_cost", 0),
                    sync_moves=t.get("sync_moves", 0),
                    model_moves=t.get("model_moves", 0),
                    log_moves=t.get("log_moves", 0),
                    alignment=[AlignmentStepResponse(**s) for s in t.get("alignment", [])],
                )
                for t in alignments.get("aligned_traces", [])
            ],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Alignment computation failed: {str(e)}")


@router.get(
    "/deviations",
    summary="Get Deviations",
    description="Detect deviations from the process model.",
)
async def get_deviations(
    process_id: UUID,
    model_id: UUID,
    threshold: float = Query(0.8, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Detect deviations.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        deviations = conformance_service.detect_deviations(log, model, threshold)
        return {
            "process_id": str(process_id),
            "model_id": str(model_id),
            "deviations": [DeviationResponse(**d) for d in deviations],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deviation detection failed: {str(e)}")


@router.get(
    "/deviation-patterns",
    response_model=DeviationPatternsResponse,
    summary="Get Deviation Patterns",
    description="Get clustered deviation patterns with statistics.",
)
async def get_deviation_patterns(
    process_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get clustered deviation patterns.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        patterns = conformance_service.analyze_deviation_patterns(log, model)
        
        return DeviationPatternsResponse(
            process_id=str(process_id),
            model_id=str(model_id),
            total_deviations=patterns.get("total_deviations", 0),
            deviation_rate=patterns.get("deviation_rate", 0.0),
            total_cases_with_deviations=patterns.get("total_cases_with_deviations", 0),
            patterns=[DeviationPatternResponse(**p) for p in patterns.get("patterns", [])],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pattern analysis failed: {str(e)}")


@router.get(
    "/diagnostics",
    response_model=DiagnosticsResponse,
    summary="Get Diagnostics",
    description="Get detailed conformance diagnostics.",
)
async def get_diagnostics(
    process_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get conformance diagnostics.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        diagnostics = conformance_service.get_diagnostics(log, model)
        
        return DiagnosticsResponse(
            total_traces=diagnostics.get("total_traces", 0),
            fitting_traces=diagnostics.get("fitting_traces", 0),
            non_fitting_traces=diagnostics.get("non_fitting_traces", 0),
            trace_fitness_ratio=diagnostics.get("trace_fitness_ratio", 0.0),
            deviations=[DeviationResponse(**d) for d in diagnostics.get("deviations", [])],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnostics failed: {str(e)}")


@router.get(
    "/comprehensive-quality",
    response_model=ComprehensiveQualityResponse,
    summary="Get Comprehensive Quality",
    description="Get all quality metrics combined.",
)
async def get_comprehensive_quality(
    process_id: UUID,
    model_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get comprehensive quality metrics.
    """
    log_repo = EventLogRepository(session)
    log = await log_repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    model_repo = ProcessModelRepository(session)
    model = await model_repo.get_by_id(model_id)
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    try:
        quality = conformance_service.get_comprehensive_quality(log, model)
        
        return ComprehensiveQualityResponse(
            process_id=str(process_id),
            model_id=str(model_id),
            fitness=quality.get("fitness", 0.0),
            trace_fitness=quality.get("trace_fitness", 0.0),
            log_fitness=quality.get("log_fitness", 0.0),
            precision=quality.get("precision"),
            generalization=quality.get("generalization"),
            simplicity=quality.get("simplicity"),
            fitting_traces_count=quality.get("fitting_traces_count", 0),
            non_fitting_traces_count=quality.get("non_fitting_traces_count", 0),
            fitting_traces_percentage=quality.get("fitting_traces_percentage", 0.0),
            overall_quality=quality.get("overall_quality", 0.0),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quality calculation failed: {str(e)}")
