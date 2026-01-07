"""Analytics schemas - CQRS-compliant response models.

Contains schemas for analytics query responses:
- Bottleneck detection
- Rework analysis
- Cycle time statistics
- Process variants
"""

from pydantic import BaseModel, Field

# =============================================================================
# Bottleneck Analysis
# =============================================================================


class BottleneckResponse(BaseModel):
    """Single bottleneck result."""

    activity: str
    avg_wait_time: float = Field(description="Average wait time in seconds")
    median_wait_time: float = Field(default=0, description="Median wait time in seconds")
    max_wait_time: float = Field(default=0, description="Maximum wait time in seconds")
    count: int = Field(description="Number of occurrences")


class BottleneckListResponse(BaseModel):
    """List of detected bottlenecks."""

    dataset_id: str
    bottlenecks: list[BottleneckResponse]
    total_bottlenecks: int


# =============================================================================
# Rework Analysis
# =============================================================================


class ReworkResponse(BaseModel):
    """Single rework pattern result."""

    activity: str
    repeat_count: int = Field(description="Total repeat occurrences")
    case_count: int = Field(description="Number of cases with this rework")
    percentage: float = Field(description="Percentage of cases with this rework")


class ReworkListResponse(BaseModel):
    """Rework analysis results."""

    dataset_id: str
    rework_activities: list[ReworkResponse]
    total_rework_cases: int
    rework_percentage: float


class ReworkChain(BaseModel):
    """A chain of consecutive rework activities."""

    activity: str
    chain_length: int
    frequency: int
    avg_chain_duration_seconds: float = 0.0
    example_case_ids: list[str] = []


class ReworkChainListResponse(BaseModel):
    """Response for rework chain analysis."""

    dataset_id: str
    chains: list[ReworkChain]
    total_chains: int
    most_problematic_activity: str | None = None
    cases_with_chains: int = 0
    chains_percentage: float = 0.0


# =============================================================================
# Cycle Time
# =============================================================================


class CycleTimeResponse(BaseModel):
    """Cycle time (case duration) statistics."""

    dataset_id: str
    mean_duration: float = Field(description="Mean case duration in seconds")
    median_duration: float = Field(description="Median case duration in seconds")
    min_duration: float = Field(description="Minimum case duration in seconds")
    max_duration: float = Field(description="Maximum case duration in seconds")
    std_deviation: float = Field(default=0, description="Standard deviation in seconds")
    total_cases: int = Field(description="Total number of cases")


# =============================================================================
# Process Variants
# =============================================================================


class VariantResponse(BaseModel):
    """Single process variant."""

    variant_id: int
    activities: list[str] = Field(description="Sequence of activities in this variant")
    case_count: int = Field(description="Number of cases following this variant")
    percentage: float = Field(description="Percentage of total cases")


class VariantListResponse(BaseModel):
    """Process variants analysis results."""

    dataset_id: str
    variants: list[VariantResponse]
    total_variants: int
    total_cases: int


# =============================================================================
# Service Time & Throughput (for backward compatibility)
# =============================================================================


class ServiceTimeResponse(BaseModel):
    """Service time per activity."""

    activity: str
    min_seconds: float
    max_seconds: float
    avg_seconds: float
    median_seconds: float
    std_dev_seconds: float = 0


class ThroughputResponse(BaseModel):
    """Throughput metrics."""

    dataset_id: str
    total_cases: int
    completed_cases: int = 0
    cases_per_day: float = 0
    cases_per_week: float = 0
    cases_per_month: float = 0
    time_range_days: float = 0


class PatternResponse(BaseModel):
    """Frequent pattern result."""

    pattern: list[str]
    support: float
    case_count: int


# =============================================================================
# Performance Dashboard (aggregated view)
# =============================================================================


class PerformanceDashboardResponse(BaseModel):
    """Comprehensive performance dashboard."""

    dataset_id: str
    cycle_time: CycleTimeResponse
    throughput: ThroughputResponse
    top_bottlenecks: list[BottleneckResponse]
    rework_summary: dict
