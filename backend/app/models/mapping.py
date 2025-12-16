from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from .common import generate_uuid

if TYPE_CHECKING:
    from .upload import Upload
    from .job import Job
    from .dataset import Dataset

class MappingBase(SQLModel):
    """Shared mapping fields (used for create and response)."""
    case_id_column: str
    activity_column: str
    timestamp_column: str
    timestamp_format: Optional[str] = None
    resource_column: Optional[str] = None
    cost_column: Optional[str] = None


class MappingCreate(MappingBase):
    """Mapping creation request."""
    pass


class Mapping(MappingBase, table=True):
    """Mapping table - stores column mapping configurations."""
    __tablename__ = "mappings"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    upload_id: str = Field(foreign_key="uploads.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    upload: Optional["Upload"] = Relationship(back_populates="mappings")
    jobs: list["Job"] = Relationship(back_populates="mapping", cascade_delete=True)
    datasets: list["Dataset"] = Relationship(back_populates="mapping", cascade_delete=True)


class MappingResponse(MappingBase):
    """Mapping API response."""
    mapping_id: str
    upload_id: str
    created_at: datetime
