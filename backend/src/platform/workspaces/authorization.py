"""Authorization service - Re-exports from platform.users.services.

Provides:
- Workspace membership verification
- Permission checks based on workspace roles
- Row-level security helpers for org_id filtering
"""

from src.platform.users.services.authorization import (  # noqa: F401
    AuthorizationService,
    require_dataset_permission,
    require_project_permission,
)

__all__ = [
    "AuthorizationService",
    "require_dataset_permission",
    "require_project_permission",
]
