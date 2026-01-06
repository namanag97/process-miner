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

# Re-export from current locations for gradual migration
# Note: analytics.py from datasets is moved here as it's analysis, not data management
from src.features.process_mining.analyses import router as analyses_router
from src.features.process_mining.analytics import router as analytics_router
from src.features.process_mining.api.datasets.analytics import router as statistics_router
from src.features.process_mining.business_use_cases import router as business_use_cases_router
from src.features.process_mining.conformance import router as conformance_router
from src.features.process_mining.discovery import router as discovery_router
from src.features.process_mining.filtering import router as filtering_router
from src.features.process_mining.ocpm import router as ocpm_router
from src.features.process_mining.organizational import router as organizational_router
from src.features.process_mining.predictions import router as predictions_router
from src.features.process_mining.simulation import router as simulation_router
from src.features.process_mining.visualization import router as visualization_router
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
