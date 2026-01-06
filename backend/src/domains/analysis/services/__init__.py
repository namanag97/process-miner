"""Analysis Domain Services.

Services for process mining and analytics:
- Discovery service (process model discovery)
- Conformance service (conformance checking)
- Analytics service (performance analysis)
- Visualization service (graph rendering)
- Prediction service (ML predictions)
- Event log loader (data access)
"""

from src.features.process_mining.analytics.service import analytics_service
from src.features.process_mining.conformance.service import conformance_service
from src.features.process_mining.discovery.service import MiningService
from src.features.process_mining.filtering.service import filtering_service
from src.features.process_mining.organizational.service import organizational_service
from src.features.process_mining.predictions.service import prediction_service
from src.features.process_mining.services.loader import EventLogLoader, event_log_loader
from src.features.process_mining.simulation.service import simulation_service
from src.features.process_mining.visualization.service import visualization_service

__all__ = [
    # Core analysis services
    "MiningService",
    "conformance_service",
    "analytics_service",
    "visualization_service",
    # Advanced services
    "prediction_service",
    "filtering_service",
    "organizational_service",
    "simulation_service",
    # Data access
    "EventLogLoader",
    "event_log_loader",
]


