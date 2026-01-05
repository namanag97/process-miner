"""Analytics Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.analytics.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.analytics import analytics_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.analytics import analytics_service
"""

from src.features.process_mining.analytics import (
    AnalyticsService,
    analytics_service,
)

__all__ = [
    "AnalyticsService",
    "analytics_service",
]
