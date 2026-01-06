"""Analytics Services.

Performance analytics and bottleneck analysis.
"""

from src.domains.analysis.services.analytics.service import AnalyticsService

analytics_service = AnalyticsService()

__all__ = [
    "AnalyticsService",
    "analytics_service",
]
