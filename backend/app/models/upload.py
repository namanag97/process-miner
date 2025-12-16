from datetime import datetime
from typing import Optional, Literal, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

from .common import generate_uuid

if TYPE_CHECKING:
    from .user import User
    from .process import Process
    from .mapping import Mapping

class UploadBase(SQLModel):
    """Shared upload fields."""
    filename: str
    file_size_bytes: int = 0
    row_count: int = 0


class Upload(UploadBase, table=True):
    """Upload table - tracks uploaded files."""
    __tablename__ = "uploads"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    user_id: str = Field(foreign_key="users.id")
    process_id: Optional[str] = Field(default=None, foreign_key="processes.id", index=True)
    file_path: str
    status: str = "uploaded"  # uploaded, processing, completed, error
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # NEW: Cache column metadata to avoid re-parsing files
    columns_json: Optional[str] = None
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="uploads")
    process: Optional["Process"] = Relationship(back_populates="uploads")
    mappings: list["Mapping"] = Relationship(back_populates="upload", cascade_delete=True)


class ColumnMetadata(SQLModel):
    """Metadata about a detected column in uploaded file."""
    name: str
    detected_type: Literal["string", "number", "datetime", "boolean"]
    sample_values: list[str] = Field(default_factory=list)
    null_percentage: float = 0.0
    unique_count: int = 0
    detected_format: Optional[str] = None


class UploadResponse(UploadBase):
    """Upload API response with detected columns."""
    upload_id: str
    columns: list[ColumnMetadata] = []
    created_at: datetime
