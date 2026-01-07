"""Workspaces Module.

Workspace management for multi-tenant SaaS platform.
Workspaces organize projects within an organization.
"""

from src.platform.workspaces.router import router
from src.platform.workspaces.schemas import (
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
