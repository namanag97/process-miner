"""Analytics Module - Performance analytics and KPIs.

Components:
- service.py: AnalyticsService for bottleneck detection, rework analysis, etc.
- router.py: API router for analytics endpoints
"""

from .router import router
from .service import AnalyticsService, analytics_service

__all__ = [
    "AnalyticsService",
    "analytics_service",
    "router",
]
