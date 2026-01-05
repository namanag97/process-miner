"""Platform Layer - Generic SaaS infrastructure.

This layer contains code that would exist regardless of the specific
product vertical (process mining, CRM, analytics, etc.).

IMPORTANT: Platform code must NEVER import from src.features.*
"""

# Sub-packages are imported lazily to avoid circular imports
# Use direct imports like: from src.platform.core.config import get_settings

__all__ = [
    "auth",
    "core",
    "infrastructure",
    "jobs",
    "projects",
    "storage",
    "users",
    "workspaces",
]
