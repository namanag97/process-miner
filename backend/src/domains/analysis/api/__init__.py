"""Analysis Domain API Routers.

Provides process mining and analytics endpoints:
- Statistics (dataset-level analytics)
- Cases and events exploration
- Variant analysis
- Process discovery
- Conformance checking
- Performance analytics
- Visualization
- Predictions
- Organizational mining
- Simulation
- OCPM (Object-Centric Process Mining)
"""

from fastapi import APIRouter

# Import routers from domain locations
from src.domains.analysis.api.analytics import router as analytics_router
from src.domains.analysis.api.conformance import router as conformance_router
from src.domains.analysis.api.discovery import router as discovery_router
from src.domains.analysis.api.filtering import router as filtering_router
from src.domains.analysis.api.ocpm import router as ocpm_router
from src.domains.analysis.api.organizational import router as organizational_router
from src.domains.analysis.api.predictions import router as predictions_router
from src.domains.analysis.api.simulation import router as simulation_router
from src.domains.analysis.api.statistics import router as statistics_router
from src.domains.analysis.api.visualization import router as visualization_router

# Re-export from current locations for gradual migration (analyses, workflows, business_use_cases)
from src.features.process_mining.analyses import router as analyses_router
from src.features.process_mining.business_use_cases import router as business_use_cases_router
from src.features.process_mining.workflows import router as workflows_router

# Combined analysis router
router = APIRouter(tags=["Analysis"])

__all__ = [
    "router",
    # Core analysis
    "statistics_router",
    "discovery_router",
    "conformance_router",
    "analytics_router",
    "visualization_router",
    # Advanced analysis
    "predictions_router",
    "filtering_router",
    "organizational_router",
    "simulation_router",
    "ocpm_router",
    # Use cases
    "business_use_cases_router",
    "analyses_router",
    "workflows_router",
]
