"""Permission system - RBAC for workspace-level access control.

This module defines:
- Permission enum (dataset:read, model:create, etc.)
- Role -> Permission mappings
- Helper functions for permission checks
"""

from enum import Enum


class Permission(str, Enum):
    """Granular permissions for resource actions.

    Format: {resource}:{action}
    """

    # Dataset permissions
    DATASET_READ = "dataset:read"
    DATASET_CREATE = "dataset:create"
    DATASET_UPDATE = "dataset:update"
    DATASET_DELETE = "dataset:delete"
    DATASET_EXPORT = "dataset:export"

    # Analysis permissions
    ANALYSIS_READ = "analysis:read"
    ANALYSIS_CREATE = "analysis:create"
    ANALYSIS_UPDATE = "analysis:update"
    ANALYSIS_DELETE = "analysis:delete"

    # Model (ProcessModel) permissions
    MODEL_READ = "model:read"
    MODEL_CREATE = "model:create"
    MODEL_UPDATE = "model:update"
    MODEL_DELETE = "model:delete"
    MODEL_EXPORT = "model:export"

    # Project permissions
    PROJECT_READ = "project:read"
    PROJECT_CREATE = "project:create"
    PROJECT_UPDATE = "project:update"
    PROJECT_DELETE = "project:delete"

    # Workspace permissions
    WORKSPACE_READ = "workspace:read"
    WORKSPACE_UPDATE = "workspace:update"
    WORKSPACE_INVITE = "workspace:invite"
    WORKSPACE_REMOVE_MEMBERS = "workspace:remove_members"
    WORKSPACE_DELETE = "workspace:delete"

    # Organization permissions (org-level, not workspace)
    ORG_READ = "org:read"
    ORG_UPDATE = "org:update"
    ORG_DELETE = "org:delete"


# =============================================================================
# Role Definitions
# =============================================================================

# Viewer: Read-only access to all resources
VIEWER_PERMISSIONS = [
    Permission.DATASET_READ,
    Permission.ANALYSIS_READ,
    Permission.MODEL_READ,
    Permission.PROJECT_READ,
    Permission.WORKSPACE_READ,
    Permission.ORG_READ,
]

# Analyst: Can read + create analyses and models (no data management)
ANALYST_PERMISSIONS = [
    *VIEWER_PERMISSIONS,
    Permission.DATASET_EXPORT,
    Permission.ANALYSIS_CREATE,
    Permission.ANALYSIS_UPDATE,
    Permission.ANALYSIS_DELETE,
    Permission.MODEL_CREATE,
    Permission.MODEL_EXPORT,
]

# Editor: Can read + create + update everything except workspace/org admin
EDITOR_PERMISSIONS = [
    *ANALYST_PERMISSIONS,
    Permission.DATASET_CREATE,
    Permission.DATASET_UPDATE,
    Permission.DATASET_DELETE,
    Permission.MODEL_UPDATE,
    Permission.MODEL_DELETE,
    Permission.PROJECT_CREATE,
    Permission.PROJECT_UPDATE,
    Permission.PROJECT_DELETE,
    Permission.WORKSPACE_UPDATE,
]

# Admin: All permissions except workspace/org deletion
ADMIN_PERMISSIONS = [
    *EDITOR_PERMISSIONS,
    Permission.WORKSPACE_INVITE,
    Permission.WORKSPACE_REMOVE_MEMBERS,
    Permission.ORG_UPDATE,
]

# Owner: Full control (can delete workspace/org)
OWNER_PERMISSIONS = [
    *ADMIN_PERMISSIONS,
    Permission.WORKSPACE_DELETE,
    Permission.ORG_DELETE,
]

# Member: Legacy role, treat as Analyst
MEMBER_PERMISSIONS = ANALYST_PERMISSIONS


# Map role names to permission sets
ROLE_PERMISSIONS: dict[str, list[Permission]] = {
    "viewer": VIEWER_PERMISSIONS,
    "analyst": ANALYST_PERMISSIONS,
    "editor": EDITOR_PERMISSIONS,
    "admin": ADMIN_PERMISSIONS,
    "owner": OWNER_PERMISSIONS,
    "member": MEMBER_PERMISSIONS,  # Legacy compatibility
}


# =============================================================================
# Permission Checking Utilities
# =============================================================================


def get_role_permissions(role: str) -> list[Permission]:
    """Get all permissions for a role.

    Args:
        role: Role name (viewer, analyst, editor, admin, owner)

    Returns:
        List of permissions granted to this role

    Raises:
        ValueError: If role is unknown
    """
    if role not in ROLE_PERMISSIONS:
        raise ValueError(f"Unknown role: {role}")
    return ROLE_PERMISSIONS[role]


def has_permission(role: str, permission: Permission) -> bool:
    """Check if a role has a specific permission.

    Args:
        role: Role name
        permission: Permission to check

    Returns:
        True if role has permission, False otherwise
    """
    try:
        return permission in get_role_permissions(role)
    except ValueError:
        return False


def has_any_permission(role: str, permissions: list[Permission]) -> bool:
    """Check if role has ANY of the given permissions.

    Args:
        role: Role name
        permissions: List of permissions to check

    Returns:
        True if role has at least one permission
    """
    role_perms = get_role_permissions(role)
    return any(perm in role_perms for perm in permissions)


def has_all_permissions(role: str, permissions: list[Permission]) -> bool:
    """Check if role has ALL of the given permissions.

    Args:
        role: Role name
        permissions: List of permissions to check

    Returns:
        True if role has all permissions
    """
    role_perms = get_role_permissions(role)
    return all(perm in role_perms for perm in permissions)
