"""API routers."""

from src.api.routers.analyses import router as analyses_router
from src.api.routers.analytics import router as analytics_router
from src.api.routers.auth import router as auth_router
from src.api.routers.conformance import router as conformance_router
from src.api.routers.datasets import router as datasets_router
from src.api.routers.dev_log import router as dev_log_router
from src.api.routers.discovery import router as discovery_router
from src.api.routers.filtering import router as filtering_router
from src.api.routers.jobs import router as jobs_router
from src.api.routers.ocpm import router as ocpm_router
from src.api.routers.organizational import router as organizational_router
from src.api.routers.predictions import router as predictions_router
from src.api.routers.projects import router as projects_router
from src.api.routers.simulation import router as simulation_router
from src.api.routers.visualization import router as visualization_router

# workflows_router removed - orphaned code with no frontend consumers
from src.api.routers.workspaces import router as workspaces_router

__all__ = [
    "analyses_router",
    "analytics_router",
    "auth_router",
    "conformance_router",
    "datasets_router",
    "dev_log_router",
    "discovery_router",
    "filtering_router",
    "jobs_router",
    "ocpm_router",
    "organizational_router",
    "predictions_router",
    "projects_router",
    "simulation_router",
    "visualization_router",

    "workspaces_router",
]
