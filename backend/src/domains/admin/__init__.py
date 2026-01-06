"""Admin Domain - User & Organization Management.

This domain handles:
- Authentication and authorization
- Organization management (multi-tenancy root)
- Workspace management (work contexts within orgs)
- Project management (containers for datasets/analyses)
- User management and roles

Key Models:
- Organization: Multi-tenancy root entity
- Workspace: Work context with member management
- Project: Container for event logs and analyses
- User: User entity with org/workspace associations

APIs:
- POST /auth/login - JWT authentication
- CRUD /organizations - Organization management
- CRUD /workspaces - Workspace management
- CRUD /projects - Project management
"""

# NOTE: API routers should be imported directly from src.domains.admin.api
# NOT from this module to avoid circular imports
