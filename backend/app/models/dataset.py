from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from .common import generate_uuid
from .analysis import ProcessStats

if TYPE_CHECKING:
    from .mapping import Mapping
    from .insight import Insight

class Dataset(SQLModel, table=True):
    """Dataset table - stores analysis results as JSON."""
    __tablename__ = "datasets"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    mapping_id: str = Field(foreign_key="mappings.id")
    
    # Analysis results stored as JSON strings
    dfg_json: Optional[str] = None
    variants_json: Optional[str] = None
    stats_json: Optional[str] = None
    activity_stats_json: Optional[str] = None
    deviations_json: str = "[]"
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    mapping: Optional["Mapping"] = Relationship(back_populates="datasets")
    insights: list["Insight"] = Relationship(back_populates="dataset", cascade_delete=True)


class DatasetSummary(SQLModel):
    """Summary response for a dataset."""
    dataset_id: str
    stats: ProcessStats
    created_at: datetime
