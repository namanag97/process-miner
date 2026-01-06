"""Admin Domain API Routers.

Provides authentication, organization, workspace, and project management.
This domain handles all user and multi-tenancy administration.
"""

from fastapi import APIRouter

# Import routers from domain locations
from src.domains.admin.api.auth import router as auth_router
from src.domains.admin.api.organizations import router as organizations_router
from src.domains.admin.api.projects import router as projects_router
from src.domains.admin.api.workspaces import router as workspaces_router

# Combined admin router for convenience
router = APIRouter(tags=["Admin"])

__all__ = [
    "router",
    "auth_router",
    "organizations_router",
    "workspaces_router",
    "projects_router",
]
