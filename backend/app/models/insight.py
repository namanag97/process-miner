"""
Insight model - Queryable extracted findings.

Insights are structured findings extracted from process mining analysis,
stored in a queryable format for aggregation and reporting.
"""

from datetime import datetime
from typing import Optional, Literal, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .models import Dataset


def generate_uuid() -> str:
    import uuid
    return str(uuid.uuid4())


# =============================================================================
# Insight Models
# =============================================================================

InsightType = Literal["bottleneck", "rework", "deviation", "kpi_alert", "recommendation"]
InsightSeverity = Literal["low", "medium", "high", "critical"]


class Insight(SQLModel, table=True):
    """Insight table - queryable extracted findings from analysis."""
    __tablename__ = "insights"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    dataset_id: str = Field(foreign_key="datasets.id", index=True)
    
    # Classification
    insight_type: str = Field(index=True)  # bottleneck, rework, deviation, kpi_alert, recommendation
    severity: str = Field(default="medium", index=True)  # low, medium, high, critical
    severity_score: float = Field(default=0.5)  # 0.0 to 1.0 for sorting
    
    # Content
    title: str
    description: str
    
    # Affected entities
    affected_activity: Optional[str] = None
    affected_case_count: int = 0
    affected_case_ids_json: Optional[str] = None  # JSON array of case IDs
    
    # Metrics
    metric_name: Optional[str] = None  # e.g., "wait_time_ms", "rework_count"
    metric_value: Optional[float] = None
    metric_threshold: Optional[float] = None  # What threshold was breached
    
    # Detailed data (JSON)
    data_json: Optional[str] = None
    
    # Status
    is_acknowledged: bool = False
    acknowledged_at: Optional[datetime] = None
    acknowledged_by: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    dataset: Optional["Dataset"] = Relationship(back_populates="insights")
    
    @property
    def affected_case_ids(self) -> list[str]:
        """Parse case IDs JSON."""
        if not self.affected_case_ids_json:
            return []
        import json
        return json.loads(self.affected_case_ids_json)
    
    @property
    def data(self) -> dict:
        """Parse data JSON."""
        if not self.data_json:
            return {}
        import json
        return json.loads(self.data_json)


class InsightCreate(SQLModel):
    """Insight creation (internal use during analysis)."""
    dataset_id: str
    insight_type: str
    severity: str = "medium"
    severity_score: float = 0.5
    title: str
    description: str
    affected_activity: Optional[str] = None
    affected_case_count: int = 0
    affected_case_ids: Optional[list[str]] = None
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    metric_threshold: Optional[float] = None
    data: Optional[dict] = None


class InsightResponse(SQLModel):
    """Insight API response."""
    id: str
    dataset_id: str
    insight_type: str
    severity: str
    severity_score: float
    title: str
    description: str
    affected_activity: Optional[str]
    affected_case_count: int
    metric_name: Optional[str]
    metric_value: Optional[float]
    is_acknowledged: bool
    created_at: datetime


class InsightSummary(SQLModel):
    """Aggregated insight summary for a process/dataset."""
    total_insights: int = 0
    by_type: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    critical_count: int = 0
    unacknowledged_count: int = 0
