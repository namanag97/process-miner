"""Organizations Module.

Organization management for multi-tenant SaaS platform.
Organizations contain workspaces and users.
"""

from src.platform.organizations.router import router

__all__ = ["router"]
