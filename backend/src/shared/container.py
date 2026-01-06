"""Request-Scoped Dependency Container.

Provides lazy-instantiated, request-scoped services with shared session.
All services within a request share the same database session and container.

Usage in routes:
    @router.get("/example")
    async def example(container: Container = Depends(get_container)):
        result = await container.ingestion.process(...)
        analytics = await container.analytics.compute(...)
"""

from functools import cached_property
from typing import TYPE_CHECKING

from sqlalchemy.ext.asyncio import AsyncSession

if TYPE_CHECKING:
    from src.features.process_mining.analytics.service import AnalyticsService
    from src.features.process_mining.conformance.service import ConformanceService
    from src.features.process_mining.discovery.service import MiningService
    from src.features.process_mining.filtering.service import FilteringService
    from src.features.process_mining.ingestion.service import IngestionService
    from src.features.process_mining.ocpm.service import OCPMService
    from src.features.process_mining.organizational.service import OrganizationalService
    from src.features.process_mining.predictions.service import PredictionService
    from src.features.process_mining.simulation.service import SimulationService
    from src.features.process_mining.visualization.service import VisualizationService
    from src.platform.dag.service import DAGService
    from src.platform.jobs.service import JobService
    from src.platform.storage.storage import StorageService


class Container:
    """Request-scoped dependency container.
    
    Services are lazily instantiated on first access and cached for the request.
    All services share the same database session for transaction consistency.
    
    Example:
        container = Container(session)
        await container.ingestion.ingest_csv(...)  # Creates IngestionService
        await container.analytics.compute(...)      # Creates AnalyticsService
        # Both share the same session
    """
    
    # Note: Cannot use __slots__ with @cached_property (requires __dict__)
    
    def __init__(self, session: AsyncSession, user_id: str | None = None):
        self._session = session
        self._user_id = user_id
    
    @property
    def session(self) -> AsyncSession:
        """Direct session access when needed."""
        return self._session
    
    @property
    def user_id(self) -> str | None:
        """Current user ID if authenticated."""
        return self._user_id
    
    # =========================================================================
    # Process Mining Services
    # =========================================================================
    
    @cached_property
    def ingestion(self) -> "IngestionService":
        """Data ingestion service for CSV/XES parsing."""
        from src.features.process_mining.ingestion.service import IngestionService
        return IngestionService()
    
    @cached_property
    def discovery(self) -> "MiningService":
        """Process discovery and mining service."""
        from src.features.process_mining.discovery.service import MiningService
        return MiningService()
    
    @cached_property
    def analytics(self) -> "AnalyticsService":
        """Analytics and statistics service."""
        from src.features.process_mining.analytics.service import AnalyticsService
        return AnalyticsService()
    
    @cached_property
    def filtering(self) -> "FilteringService":
        """Event log filtering service."""
        from src.features.process_mining.filtering.service import FilteringService
        return FilteringService()
    
    @cached_property
    def conformance(self) -> "ConformanceService":
        """Conformance checking service."""
        from src.features.process_mining.conformance.service import ConformanceService
        return ConformanceService()
    
    @cached_property
    def visualization(self) -> "VisualizationService":
        """Process visualization service."""
        from src.features.process_mining.visualization.service import VisualizationService
        return VisualizationService()
    
    @cached_property
    def simulation(self) -> "SimulationService":
        """Process simulation service."""
        from src.features.process_mining.simulation.service import SimulationService
        return SimulationService()
    
    @cached_property
    def predictions(self) -> "PredictionService":
        """Predictive analytics service."""
        from src.features.process_mining.predictions.service import PredictionService
        return PredictionService()
    
    @cached_property
    def organizational(self) -> "OrganizationalService":
        """Organizational mining service."""
        from src.features.process_mining.organizational.service import OrganizationalService
        return OrganizationalService()
    
    @cached_property
    def ocpm(self) -> "OCPMService":
        """Object-centric process mining service."""
        from src.features.process_mining.ocpm.service import OCPMService
        return OCPMService()
    
    @cached_property
    def dags(self) -> "DAGService":
        """DAG workflow orchestration service."""
        from src.platform.dag.service import DAGService
        return DAGService(self._session)
    
    # =========================================================================
    # Platform Services
    # =========================================================================
    
    @cached_property
    def jobs(self) -> "JobService":
        """Async job management service."""
        from src.platform.jobs.service import JobService
        return JobService()
    
    @cached_property
    def storage(self) -> "StorageService":
        """File storage service."""
        from src.platform.storage.storage import StorageService
        return StorageService()
