"""Analysis Models - Re-exports from domains for backward compatibility.

DEPRECATED: These models have been moved to src.domains.analysis.models
Import from the new location instead.
"""

# Re-export from analysis domain
from src.domains.analysis.models.analysis import (  # noqa: F401
    Analysis,
    AnalyticsCache,
    ConformanceResult,
)

__all__ = [
    "Analysis",
    "ConformanceResult",
    "AnalyticsCache",
]
