"""DevTools - Development-only observability and debugging utilities.

Exports:
- trace: Decorator to log function entry/exit to DevConsole
- trace_class: Decorator to trace all methods of a class
- dev_data_router: Router for database inspection endpoints
"""

from .dev_data import router as dev_data_router

__all__ = ["dev_data_router"]
