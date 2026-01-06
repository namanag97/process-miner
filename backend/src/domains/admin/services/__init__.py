"""Admin Domain Services.

Authorization and authentication services.
"""

# Import from local domain services
from src.domains.admin.services.authorization import (
    AuthorizationService,
    require_dataset_permission,
    require_project_permission,
)

__all__ = [
    "AuthorizationService",
    "require_dataset_permission",
    "require_project_permission",
]
