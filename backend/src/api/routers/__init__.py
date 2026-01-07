"""API routers - Central registry for all API routers.

Consolidated architecture:
- Platform: Auth, organizations, workspaces, projects, health, jobs, operations
- Process Mining: Discovery, conformance, analytics, visualization, datasets, etc.

Note: DAG system was removed - use Temporal workflows via /operations API instead.
"""

# ============================================================================
# Platform Routers (Users & Infrastructure)
# ============================================================================
# Platform Infrastructure
from src.api.routers.operations import router as operations_router  # Unified Temporal API

# from src.api.routers.telemetry import router as telemetry_router  # TODO: Create telemetry router
from src.api.routers.workflows import router as workflows_api_router

# ============================================================================
# Process Mining Feature Routers
# ============================================================================
from src.features.process_mining.analyses import router as analyses_router
from src.features.process_mining.analytics import router as analytics_router

# Algorithm Registry and Quality Metrics
from src.features.process_mining.api.algorithms import router as algorithms_router
from src.features.process_mining.api.quality import router as quality_metrics_router
from src.features.process_mining.business_use_cases import router as business_use_cases_router
from src.features.process_mining.conformance import router as conformance_router

# ============================================================================
# Datasets Routers (from features/process_mining/datasets)
# ============================================================================
from src.features.process_mining.datasets.api import (
    crud_router as datasets_crud_router,
)
from src.features.process_mining.datasets.api import (
    export_router as datasets_export_router,
)
from src.features.process_mining.datasets.api import (
    ingest_router as datasets_ingest_router,
)
from src.features.process_mining.datasets.api import (
    mapping_router as datasets_mapping_router,
)
from src.features.process_mining.datasets.api import (
    router as datasets_router,
)
from src.features.process_mining.datasets.api import (
    upload_router as datasets_upload_router,
)
from src.features.process_mining.discovery import router as discovery_router
from src.features.process_mining.filtering import router as filtering_router
from src.features.process_mining.ocpm import router as ocpm_router
from src.features.process_mining.organizational import router as organizational_router
from src.features.process_mining.predictions import router as predictions_router
from src.features.process_mining.simulation import router as simulation_router
from src.features.process_mining.statistics import router as statistics_router
from src.features.process_mining.visualization import router as visualization_router
from src.features.process_mining.workflows import router as workflows_router

# DAG system removed - use Temporal workflows via /operations API
# from src.infra.dag.router import router as dags_router
from src.infra.devtools.router import router as dev_log_router
from src.infra.health.router import router as health_router
from src.infra.jobs.router import router as jobs_router
from src.infra.users.api import (
    auth_router,
    organizations_router,
    projects_router,
    workspaces_router,
)

__all__ = [
    # Algorithm Registry and Quality Metrics
    "algorithms_router",
    "analyses_router",
    "analytics_router",
    # Platform - Users
    "auth_router",
    "business_use_cases_router",
    "conformance_router",
    # Platform - Infrastructure (DAG removed, use /operations API)
    "datasets_crud_router",
    "datasets_export_router",
    "datasets_ingest_router",
    "datasets_mapping_router",
    # Datasets
    "datasets_router",
    "datasets_upload_router",
    "dev_log_router",
    "discovery_router",
    "filtering_router",
    "health_router",
    "jobs_router",
    "ocpm_router",
    "operations_router",  # Unified Temporal operations API
    "organizational_router",
    "organizations_router",
    "predictions_router",
    "projects_router",
    "quality_metrics_router",
    "simulation_router",
    # Process Mining Features
    "statistics_router",
    # "telemetry_router",  # TODO: Create telemetry router
    "visualization_router",
    "workflows_api_router",
    "workflows_router",
    "workspaces_router",
]
