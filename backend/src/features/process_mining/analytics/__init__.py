"""Analytics Module - Performance analytics and KPIs.

Components:
- service.py: AnalyticsService for bottleneck detection, rework analysis, etc.
- router.py: API router (not used in DDD - routers stay in api layer)
"""

from .service import AnalyticsService, analytics_service

__all__ = [
    "AnalyticsService",
    "analytics_service",
]
