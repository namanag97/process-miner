"""
Process model - Business process container.

Processes group uploads and their analysis results by business function
(e.g., "Order-to-Cash", "Procure-to-Pay", "Hire-to-Retire").
"""

from datetime import datetime
from typing import Optional, Literal, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .organization import Organization
    from .models import Upload


def generate_uuid() -> str:
    import uuid
    return str(uuid.uuid4())


# =============================================================================
# Process Models
# =============================================================================

ProcessStatus = Literal["active", "archived", "draft"]


class ProcessBase(SQLModel):
    """Base process fields."""
    name: str
    description: Optional[str] = None
    status: str = "active"  # active, archived, draft


class Process(ProcessBase, table=True):
    """Process table - groups uploads by business process."""
    __tablename__ = "processes"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    org_id: str = Field(foreign_key="organizations.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    icon: Optional[str] = None  # Emoji or icon name
    color: Optional[str] = None  # Hex color for UI
    
    # Relationships
    organization: Optional["Organization"] = Relationship(back_populates="processes")
    uploads: list["Upload"] = Relationship(back_populates="process", cascade_delete=True)


class ProcessCreate(SQLModel):
    """Process creation request."""
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class ProcessUpdate(SQLModel):
    """Process update request."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None


class ProcessResponse(ProcessBase):
    """Process API response."""
    id: str
    org_id: str
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    upload_count: int = 0
    dataset_count: int = 0


class ProcessWithStats(ProcessResponse):
    """Process with aggregated statistics."""
    total_cases: int = 0
    total_events: int = 0
    avg_case_duration_ms: float = 0
    last_analysis_at: Optional[datetime] = None
