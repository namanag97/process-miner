from datetime import datetime
from typing import Optional, Literal, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from .common import generate_uuid

if TYPE_CHECKING:
    from .mapping import Mapping

class Job(SQLModel, table=True):
    """Job table - tracks background processing status."""
    __tablename__ = "jobs"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    mapping_id: str = Field(foreign_key="mappings.id")
    status: str = "queued"  # queued, processing, completed, failed
    progress: int = 0
    progress_message: Optional[str] = None
    error: Optional[str] = None
    dataset_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    # Relationships
    mapping: Optional["Mapping"] = Relationship(back_populates="jobs")


class JobResponse(SQLModel):
    """Job status API response."""
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    progress: int = 0
    progress_message: Optional[str] = None
    dataset_id: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class ProcessingRequest(SQLModel):
    """Request to start processing - no additional params needed for MVP."""
    pass
