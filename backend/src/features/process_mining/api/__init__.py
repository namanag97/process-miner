"""Process mining API routers."""

from src.features.process_mining.api.analyses import router as analyses_router
from src.features.process_mining.api.analytics import router as analytics_router
from src.features.process_mining.api.business_use_cases import (
    router as business_use_cases_router,
)
from src.features.process_mining.api.datasets import router as datasets_router
from src.features.process_mining.api.filtering import router as filtering_router
from src.features.process_mining.api.ocpm import router as ocpm_router
from src.features.process_mining.api.organizational import (
    router as organizational_router,
)
from src.features.process_mining.api.predictions import router as predictions_router
from src.features.process_mining.api.simulation import router as simulation_router
from src.features.process_mining.api.visualization import router as visualization_router
from src.features.process_mining.api.workflows import router as workflows_router
from src.features.process_mining.conformance.router import router as conformance_router
from src.features.process_mining.discovery.router import router as discovery_router

__all__ = [
    "analyses_router",
    "analytics_router",
    "business_use_cases_router",
    "conformance_router",
    "datasets_router",
    "discovery_router",
    "filtering_router",
    "ocpm_router",
    "organizational_router",
    "predictions_router",
    "simulation_router",
    "visualization_router",
    "workflows_router",
]
