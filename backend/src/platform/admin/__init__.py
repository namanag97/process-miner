"""Admin Module.

Admin-only system management endpoints.
Superuser access required for all endpoints.
"""

from src.platform.admin.router import router

__all__ = ["router"]
