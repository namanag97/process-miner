"""API routers - Central registry for all API routers.

Following Domain-Driven Design architecture:
- Admin Domain: Auth, organizations, workspaces, projects
- Datasets Domain: Upload, mapping, ingestion, CRUD
- Analysis Domain: Discovery, conformance, analytics, visualization
- Platform: Infrastructure (jobs, health, devtools)
"""

# ============================================================================
# Admin Domain Routers
# ============================================================================
from src.domains.admin.api import (
    auth_router,
    organizations_router,
    projects_router,
    workspaces_router,
)

# ============================================================================
# Datasets Domain Routers
# ============================================================================
from src.domains.datasets.api import (
    crud_router as datasets_crud_router,
    export_router as datasets_export_router,
    ingest_router as datasets_ingest_router,
    mapping_router as datasets_mapping_router,
    router as datasets_router,
    upload_router as datasets_upload_router,
)

# ============================================================================
# Analysis Domain Routers
# ============================================================================
from src.domains.analysis.api import (
    analyses_router,
    analytics_router,
    business_use_cases_router,
    conformance_router,
    discovery_router,
    filtering_router,
    ocpm_router,
    organizational_router,
    predictions_router,
    simulation_router,
    statistics_router,
    visualization_router,
    workflows_router,
)

# ============================================================================
# Platform Infrastructure Routers
# ============================================================================
from src.platform.dag.router import router as dags_router
from src.platform.devtools.router import router as dev_log_router
from src.platform.health.router import router as health_router
from src.platform.jobs.router import router as jobs_router

__all__ = [
    # Admin domain
    "auth_router",
    "organizations_router",
    "workspaces_router",
    "projects_router",
    # Datasets domain
    "datasets_router",
    "datasets_crud_router",
    "datasets_upload_router",
    "datasets_mapping_router",
    "datasets_ingest_router",
    "datasets_export_router",
    # Analysis domain
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
    # Platform infrastructure
    "dags_router",
    "dev_log_router",
    "health_router",
    "jobs_router",
]
