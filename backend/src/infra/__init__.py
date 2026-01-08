"""Infrastructure Layer - Generic SaaS infrastructure.

This layer contains code that would exist regardless of the specific
product vertical (process mining, CRM, analytics, etc.).

Modules:
- core/           - Config, exceptions, logging, middleware
- infrastructure/ - Database, storage, cache
- auth/           - JWT authentication
- users/          - User management + API routers
- organizations/  - Organization management
- workspaces/     - Workspace RBAC
- projects/       - Project management
- temporal/       - Temporal workflow orchestration
- jobs/           - Background job tracking
- health/         - Health check endpoints
- devconsole/     - Developer tools (SSE logs)

IMPORTANT: This layer must NEVER import from src.features.*
"""

# Sub-packages are imported lazily to avoid circular imports
# Use direct imports like: from src.infra.core.config import get_settings

__all__ = [
    "auth",
    "core",
    "infrastructure",
    "jobs",
    "organizations",
    "projects",
    "storage",
    "temporal",
    "users",
    "workspaces",
]
