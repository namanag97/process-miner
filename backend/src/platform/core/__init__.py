"""Platform Core - Configuration, exceptions, and base infrastructure.

This module contains:
- config: Application settings (Pydantic Settings)
- exceptions: Custom exception classes (RFC 7807)
- security: JWT, password hashing
- middleware: Request logging, performance tracking
- permissions: RBAC permission definitions
- logging_config: Structured logging setup
- enums: Shared enumerations
- result: Result type for explicit error handling

Import specific modules directly:
    from src.platform.core.config import get_settings
    from src.platform.core.exceptions import NotFoundError
"""

# Re-export commonly used items
from src.platform.core.config import Settings, get_settings
from src.platform.core.logging_config import configure_logging, get_logger

__all__ = [
    "Settings",
    "get_settings",
    "configure_logging",
    "get_logger",
]
