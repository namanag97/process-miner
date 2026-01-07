"""Process mining API routers.

Note: Dataset routers are in src.features.process_mining.datasets.api (canonical path).
This module re-exports other feature routers for convenience.
"""

from src.features.process_mining.analyses import router as analyses_router
from src.features.process_mining.analytics import router as analytics_router
from src.features.process_mining.business_use_cases import (
    router as business_use_cases_router,
)
from src.features.process_mining.conformance import router as conformance_router
from src.features.process_mining.discovery import router as discovery_router
from src.features.process_mining.filtering import router as filtering_router
from src.features.process_mining.ocpm import router as ocpm_router
from src.features.process_mining.organizational import router as organizational_router
from src.features.process_mining.predictions import router as predictions_router
from src.features.process_mining.simulation import router as simulation_router
from src.features.process_mining.visualization import router as visualization_router

__all__ = [
    "analyses_router",
    "analytics_router",
    "business_use_cases_router",
    "conformance_router",
    "discovery_router",
    "filtering_router",
    "ocpm_router",
    "organizational_router",
    "predictions_router",
    "simulation_router",
    "visualization_router",
]
