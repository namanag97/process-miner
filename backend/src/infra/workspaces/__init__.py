"""Workspaces Module.

Workspace management for multi-tenant SaaS platform.
Workspaces organize projects within an organization.
"""

from src.infra.workspaces.router import router
from src.infra.workspaces.schemas import (
    AddMemberRequest,
    UpdateMemberRoleRequest,
    WorkspaceMemberListResponse,
    WorkspaceMemberResponseInline,
)

__all__ = [
    # Requests
    "AddMemberRequest",
    "UpdateMemberRoleRequest",
    "WorkspaceMemberListResponse",
    # Responses
    "WorkspaceMemberResponseInline",
    "router",
]
