"""Admin Domain Services.

Re-exports authorization and workspace services for domain-based access.
"""

from src.platform.workspaces.authorization import (
    AuthorizationService,
    filter_by_org,
    filter_by_workspace_membership,
    require_dataset_permission,
    require_project_permission,
)

__all__ = [
    "AuthorizationService",
    "require_project_permission",
    "require_dataset_permission",
    "filter_by_org",
    "filter_by_workspace_membership",
]

