"""API routers - Central registry for all API routers.

Consolidated architecture:
- Platform: Auth, organizations, workspaces, projects, health, jobs, DAGs
- Process Mining: Discovery, conformance, analytics, visualization, datasets, etc.
"""

# ============================================================================
# Platform Routers (Users & Infrastructure)
# ============================================================================
from src.platform.users.api import (
    auth_router,
    organizations_router,
    projects_router,
    workspaces_router,
)

# Platform Infrastructure
from src.platform.dag.router import router as dags_router
from src.platform.devtools.router import router as dev_log_router
from src.platform.health.router import router as health_router
from src.platform.jobs.router import router as jobs_router

# ============================================================================
# Process Mining Feature Routers
# ============================================================================
from src.features.process_mining.analyses import router as analyses_router
from src.features.process_mining.analytics import router as analytics_router
from src.features.process_mining.business_use_cases import router as business_use_cases_router
from src.features.process_mining.conformance import router as conformance_router
from src.features.process_mining.discovery import router as discovery_router
from src.features.process_mining.filtering import router as filtering_router
from src.features.process_mining.ocpm import router as ocpm_router
from src.features.process_mining.organizational import router as organizational_router
from src.features.process_mining.predictions import router as predictions_router
from src.features.process_mining.simulation import router as simulation_router
from src.features.process_mining.statistics import router as statistics_router
from src.features.process_mining.visualization import router as visualization_router
from src.features.process_mining.workflows import router as workflows_router

# ============================================================================
# Datasets Routers (from features/process_mining/datasets)
# ============================================================================
from src.features.process_mining.datasets.api import (
    crud_router as datasets_crud_router,
    export_router as datasets_export_router,
    ingest_router as datasets_ingest_router,
    mapping_router as datasets_mapping_router,
    router as datasets_router,
    upload_router as datasets_upload_router,
)

__all__ = [
    # Platform - Users
    "auth_router",
    "organizations_router",
    "workspaces_router",
    "projects_router",
    # Platform - Infrastructure
    "dags_router",
    "dev_log_router",
    "health_router",
    "jobs_router",
    # Datasets
    "datasets_router",
    "datasets_crud_router",
    "datasets_upload_router",
    "datasets_mapping_router",
    "datasets_ingest_router",
    "datasets_export_router",
    # Process Mining Features
    "statistics_router",
    "analyses_router",
    "analytics_router",
    "discovery_router",
    "conformance_router",
    "visualization_router",
    "filtering_router",
    "predictions_router",
    "organizational_router",
    "simulation_router",
    "ocpm_router",
    "business_use_cases_router",
    "workflows_router",
]
