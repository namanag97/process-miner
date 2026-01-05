"""Conformance schemas - Conformance checking and alignment.

Contains schemas for:
- Conformance check requests and responses
- Deviation and diagnostics
- Alignment moves and case alignments
- Quality metrics
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from src.features.process_mining.enums import ConformanceMethod
from src.shared.schemas import PaginatedResponse


class ConformanceCheckRequest(BaseModel):
    """Request for conformance checking."""

    dataset_id: str
    model_id: str
    method: ConformanceMethod = ConformanceMethod.TOKEN_REPLAY


class ConformanceResponse(BaseModel):
    """Conformance check result."""

    id: str
    dataset_id: str
    model_id: str
    fitness: float
    precision: float | None
    generalization: float | None = None  # FE expects this metric
    simplicity: float | None = None  # FE expects this metric
    method: str  # What method was requested
    algorithm_used: str  # What algorithm actually ran (may differ if fallback)
    fallback_reason: str | None = None  # Reason for fallback if different from method
    is_conformant: bool  # fitness >= 0.8
    fitting_traces: int
    total_traces: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DeviationDetail(BaseModel):
    """Structured deviation for conformance diagnostics."""

    case_id: str
    activity: str
    violation_type: str  # 'missing_activity' | 'wrong_order' | 'extra_activity'
    expected_after: str | None = None
    frequency: int = 1
    impact: str = "medium"  # 'low' | 'medium' | 'high'


class DiagnosticsResponse(BaseModel):
    """Detailed conformance diagnostics."""

    fitness: float
    precision: float | None
    generalization: float | None = None
    simplicity: float | None = None
    f_score: float | None = None  # Harmonic mean of fitness & precision
    total_traces: int
    fitting_traces: int
    non_fitting_traces: int
    fitness_ratio: float
    average_alignment_cost: float | None = None
    deviations: list[DeviationDetail] | None = None  # Structured deviations


class QualityMetricsResponse(BaseModel):
    """Full quality metrics for a process model.

    Contains all 4 quality dimensions from PM4py:
    - Fitness: How well the log fits the model
    - Precision: How much the model allows for behavior not in the log
    - Generalization: How well the model generalizes beyond observed behavior
    - Simplicity: How simple/understandable the model is
    """

    dataset_id: str
    model_id: str
    fitness: float
    precision: float | None = None
    generalization: float | None = None
    simplicity: float | None = None
    f_score: float | None = None  # Harmonic mean of fitness & precision


class ConformanceListResponse(PaginatedResponse):
    """Paginated conformance results list."""

    items: list[ConformanceResponse]


class DeviationResponse(BaseModel):
    """Conformance deviation detail."""

    case_id: str
    activity: str | None
    deviation_type: str
    details: str


class AlignmentMove(BaseModel):
    """Single move in an alignment sequence."""

    log_move: str | None = None
    model_move: str | None = None
    move_type: str  # 'sync', 'log_only', 'model_only'


class CaseAlignmentResponse(BaseModel):
    """Alignment result for a single case."""

    case_id: str
    fitness: float
    cost: int = 0
    alignment: list[AlignmentMove]
    is_fit: bool = True


class AlignmentDiagnosticsResponse(BaseModel):
    """Response for alignment diagnostics endpoint."""

    dataset_id: str
    model_id: str
    total_cases: int
    fitting_cases: int
    average_fitness: float
    case_alignments: list[CaseAlignmentResponse]
