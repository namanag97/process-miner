"""Analytics schemas - Bottleneck, Rework, and Performance metrics.

Contains schemas for:
- Bottleneck detection and analysis
- Rework analysis and chains
- Service time, cycle time, and throughput metrics
"""

from pydantic import BaseModel


# =============================================================================
# Bottleneck Analysis
# =============================================================================


class BottleneckResponse(BaseModel):
    """Bottleneck detection result."""

    activity: str
    avg_waiting_time_seconds: float
    avg_service_time_seconds: float
    frequency: int
    is_bottleneck: bool
    severity: str  # 'low', 'medium', 'high'
    preceding_activities: list[str] = []
    following_activities: list[str] = []
    bottleneck_impact_score: float = 0.0  # 0-1 score based on wait time and frequency


class BottleneckListResponse(BaseModel):
    """List of detected bottlenecks."""

    dataset_id: str
    bottlenecks: list[BottleneckResponse]
    total_bottlenecks: int


# =============================================================================
# Rework Analysis
# =============================================================================


class ReworkResponse(BaseModel):
    """Rework analysis result."""

    activity: str
    rework_count: int
    cases_with_rework: int
    rework_percentage: float


class ReworkListResponse(BaseModel):
    """Rework analysis results."""

    dataset_id: str
    rework_activities: list[ReworkResponse]
    total_rework_cases: int
    rework_percentage: float


class ReworkChain(BaseModel):
    """A chain of rework activities showing patterns of repeated work."""

    activity: str
    chain_length: int  # How many times it repeats in a row
    frequency: int  # How many cases have this chain
    avg_chain_duration_seconds: float = 0.0
    example_case_ids: list[str] = []  # Sample case IDs exhibiting this pattern


class ReworkChainListResponse(BaseModel):
    """Response for rework chain analysis."""

    dataset_id: str
    chains: list[ReworkChain]
    total_chains: int
    most_problematic_activity: str | None = None
    cases_with_chains: int = 0
    chains_percentage: float = 0.0


# =============================================================================
# Performance Metrics
# =============================================================================


class ServiceTimeResponse(BaseModel):
    """Service time per activity."""

    activity: str
    min_seconds: float
    max_seconds: float
    avg_seconds: float
    median_seconds: float
    std_dev_seconds: float


class CycleTimeResponse(BaseModel):
    """Cycle time statistics."""

    dataset_id: str
    min_seconds: float
    max_seconds: float
    avg_seconds: float
    median_seconds: float
    percentile_25_seconds: float
    percentile_75_seconds: float
    percentile_95_seconds: float


class ThroughputResponse(BaseModel):
    """Throughput metrics."""

    dataset_id: str
    total_cases: int
    completed_cases: int
    cases_per_day: float
    cases_per_week: float
    cases_per_month: float
    time_range_days: float
