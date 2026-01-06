"""Admin Domain API Routers.

Re-exports routers from platform layer to provide domain-based access.
This allows gradual migration while maintaining backward compatibility.
"""

from fastapi import APIRouter

# Re-export from current platform locations
from src.platform.auth.router import router as auth_router
from src.platform.organizations.router import router as organizations_router
from src.platform.projects.router import router as projects_router
from src.platform.workspaces.router import router as workspaces_router

# Combined admin router for convenience
router = APIRouter(tags=["Admin"])

__all__ = [
    "router",
    "auth_router",
    "organizations_router",
    "workspaces_router",
    "projects_router",
]
