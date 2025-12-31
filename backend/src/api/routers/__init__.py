"""API routers."""

from src.api.routers.analytics import router as analytics_router
from src.api.routers.conformance import router as conformance_router
from src.api.routers.dev_log import router as dev_log_router
from src.api.routers.discovery import router as discovery_router
from src.api.routers.filtering import router as filtering_router
from src.api.routers.ocpm import router as ocpm_router
from src.api.routers.organizational import router as organizational_router
from src.api.routers.predictions import router as predictions_router
from src.api.routers.processes import router as processes_router
from src.api.routers.projects import router as projects_router
from src.api.routers.simulation import router as simulation_router
from src.api.routers.visualization import router as visualization_router
from src.api.routers.workflows import router as workflows_router

__all__ = [
    "processes_router",
    "projects_router",
    "discovery_router",
    "visualization_router",
    "conformance_router",
    "ocpm_router",
    "workflows_router",
    "filtering_router",
    "analytics_router",
    "organizational_router",
    "predictions_router",
    "simulation_router",
    "dev_log_router",
]
