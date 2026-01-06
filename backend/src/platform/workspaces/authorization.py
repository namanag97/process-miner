"""Authorization service - Re-exports from domain services for backward compatibility.

DEPRECATED: This module re-exports from the new domain location.
New code should import from:
- from src.domains.admin.services import AuthorizationService, require_dataset_permission, etc.

Provides:
- Workspace membership verification
- Permission checks based on workspace roles
- Row-level security helpers for org_id filtering
"""

# Re-export from admin domain for backward compatibility
from src.domains.admin.services.authorization import (  # noqa: F401
    AuthorizationService,
    require_dataset_permission,
    require_project_permission,
)

__all__ = [
    "AuthorizationService",
    "require_dataset_permission",
    "require_project_permission",
]
