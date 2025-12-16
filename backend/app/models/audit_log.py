"""
AuditLog model - Comprehensive action tracking.

Records all significant user actions for visibility, debugging,
and compliance. Captured automatically via middleware.
"""

from datetime import datetime
from typing import Optional, Literal, Any, TYPE_CHECKING

from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from .models import User


def generate_uuid() -> str:
    import uuid
    return str(uuid.uuid4())


# =============================================================================
# Audit Log Models
# =============================================================================

AuditAction = Literal["create", "update", "delete", "view", "process", "export", "login"]
EntityType = Literal["organization", "process", "upload", "mapping", "job", "dataset", "user"]


class AuditLog(SQLModel, table=True):
    """Audit log table - tracks all significant user actions."""
    __tablename__ = "audit_logs"
    
    id: str = Field(default_factory=generate_uuid, primary_key=True, index=True)
    
    # Who
    user_id: Optional[str] = Field(default=None, foreign_key="users.id", index=True)
    
    # What
    entity_type: str = Field(index=True)  # organization, process, upload, etc.
    entity_id: Optional[str] = Field(default=None, index=True)
    action: str = Field(index=True)  # create, update, delete, view, process
    
    # Details (JSON string)
    details_json: Optional[str] = None
    
    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    
    # When
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Relationships
    user: Optional["User"] = Relationship(back_populates="audit_logs")
    
    @property
    def details(self) -> dict:
        """Parse details JSON."""
        if not self.details_json:
            return {}
        import json
        return json.loads(self.details_json)
    
    @details.setter
    def details(self, value: dict):
        """Serialize details to JSON."""
        import json
        self.details_json = json.dumps(value) if value else None


class AuditLogCreate(SQLModel):
    """Audit log creation (internal use only)."""
    user_id: Optional[str] = None
    entity_type: str
    entity_id: Optional[str] = None
    action: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None


class AuditLogResponse(SQLModel):
    """Audit log API response."""
    id: str
    user_id: Optional[str]
    entity_type: str
    entity_id: Optional[str]
    action: str
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    request_path: Optional[str] = None
    created_at: datetime


class AuditLogFilter(SQLModel):
    """Audit log query filters."""
    user_id: Optional[str] = None
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    action: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 100
    offset: int = 0
