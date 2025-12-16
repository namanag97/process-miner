"""
PM4Py Service - Core process mining operations.

This is the heart of the backend. It wraps PM4Py functions and transforms
output into React Flow compatible format for the frontend.
"""

# Re-export from the new mining package
from .mining import PM4PyService, pm4py_service

__all__ = ["PM4PyService", "pm4py_service"]
