"""Event Models - Re-exports from domains for backward compatibility.

DEPRECATED: These models have been moved to src.domains.analysis.models
Import from the new location instead.
"""

# Re-export from analysis domain
from src.domains.analysis.models.events import ProcessCase, ProcessEvent  # noqa: F401

__all__ = [
    "ProcessCase",
    "ProcessEvent",
]
