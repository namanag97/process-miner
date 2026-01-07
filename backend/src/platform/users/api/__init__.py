"""Platform Users API Routers.

Provides authentication, organization, workspace, and project management.
"""

from src.platform.users.api.auth import router as auth_router
from src.platform.users.api.organizations import router as organizations_router
from src.platform.users.api.projects import router as projects_router
from src.platform.users.api.workspaces import router as workspaces_router

__all__ = [
    "auth_router",
    "organizations_router",
    "projects_router",
    "workspaces_router",
]
