"""Admin Domain Services.

Re-exports authorization and workspace services for domain-based access.
"""

from src.platform.workspaces.authorization import (
    require_dataset_permission,
    require_project_permission,
    require_workspace_permission,
)

__all__ = [
    "require_workspace_permission",
    "require_project_permission",
    "require_dataset_permission",
]
