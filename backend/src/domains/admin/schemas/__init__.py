"""Admin Domain Schemas.

Re-exports platform schemas for domain-based access.
"""

from src.platform.organizations.schemas import (
    OrganizationCreate,
    OrganizationResponse,
    OrganizationUpdate,
)
from src.platform.workspaces.schemas import (
    WorkspaceCreate,
    WorkspaceResponse,
)

__all__ = [
    "OrganizationCreate",
    "OrganizationResponse",
    "OrganizationUpdate",
    "WorkspaceCreate",
    "WorkspaceResponse",
]
