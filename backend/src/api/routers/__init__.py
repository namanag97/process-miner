"""API routers."""

from src.api.routers.conformance import router as conformance_router
from src.api.routers.discovery import router as discovery_router
from src.api.routers.ocpm import router as ocpm_router
from src.api.routers.processes import router as processes_router
from src.api.routers.visualization import router as visualization_router
from src.api.routers.workflows import router as workflows_router

__all__ = [
    "processes_router",
    "discovery_router",
    "visualization_router",
    "conformance_router",
    "ocpm_router",
    "workflows_router",
]
