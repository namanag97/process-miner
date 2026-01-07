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
    avg_waiting_time_seconds: float = Field(description="Average wait time in seconds")
    avg_service_time_seconds: float = Field(default=0, description="Average service time in seconds")
    frequency: int = Field(description="Number of occurrences")
    is_bottleneck: bool = Field(default=True, description="Whether this is flagged as a bottleneck")
    severity: str = Field(default="medium", description="Severity level: low, medium, high")
    preceding_activities: list[str] = Field(default_factory=list, description="Activities that precede this one")
    following_activities: list[str] = Field(default_factory=list, description="Activities that follow this one")
    bottleneck_impact_score: float = Field(default=0.0, description="Impact score 0-1")


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
    rework_count: int = Field(description="Total repeat occurrences")
    cases_with_rework: int = Field(description="Number of cases with this rework")
    rework_percentage: float = Field(description="Percentage of cases with this rework")


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
    min_seconds: float = Field(description="Minimum case duration in seconds")
    max_seconds: float = Field(description="Maximum case duration in seconds")
    avg_seconds: float = Field(description="Mean case duration in seconds")
    median_seconds: float = Field(description="Median case duration in seconds")
    percentile_25_seconds: float = Field(default=0, description="25th percentile in seconds")
    percentile_75_seconds: float = Field(default=0, description="75th percentile in seconds")
    percentile_95_seconds: float = Field(default=0, description="95th percentile in seconds")


# =============================================================================
# Process Variants (Analytics-specific - simple schema for CQRS queries)
# =============================================================================


class AnalyticsVariantResponse(BaseModel):
    """Single process variant for analytics queries (CQRS read model).

    Note: This is a simpler schema than datasets.VariantResponse.
    Use this for analytics/performance endpoints.
    Use datasets.VariantResponse for data exploration endpoints.
    """

    variant_id: int
    activities: list[str] = Field(description="Sequence of activities in this variant")
    case_count: int = Field(description="Number of cases following this variant")
    percentage: float = Field(description="Percentage of total cases")


class AnalyticsVariantListResponse(BaseModel):
    """Process variants analysis results from CQRS query."""

    dataset_id: str
    variants: list[AnalyticsVariantResponse]
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
