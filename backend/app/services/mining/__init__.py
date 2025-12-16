from .core import create_event_log
from .discovery import discover_dfg
from .variants import get_variants, detect_deviations
from .stats import get_statistics, get_activity_stats
from .transforms import transform_dfg_for_react_flow, transform_variants


class MiningError(Exception):
    """Base exception for process mining operations."""

    def __init__(self, message: str, operation: str, cause: Exception | None = None):
        self.message = message
        self.operation = operation
        self.cause = cause
        super().__init__(f"[{operation}] {message}")


class EmptyEventLogError(MiningError):
    """Raised when event log is empty after processing."""

    def __init__(self, message: str = "Event log is empty", operation: str = "create_event_log"):
        super().__init__(message, operation)


class DFGDiscoveryError(MiningError):
    """Raised when DFG discovery fails."""
    pass


class StatisticsError(MiningError):
    """Raised when statistics calculation fails."""
    pass


class VariantExtractionError(MiningError):
    """Raised when variant extraction fails."""
    pass

class PM4PyService:
    """
    Facade for process mining operations.
    Delegates to functional modules in the mining package.
    """
    
    def create_event_log(self, *args, **kwargs):
        return create_event_log(*args, **kwargs)
        
    def discover_dfg(self, *args, **kwargs):
        return discover_dfg(*args, **kwargs)
        
    def get_variants(self, *args, **kwargs):
        return get_variants(*args, **kwargs)
        
    def detect_deviations(self, *args, **kwargs):
        return detect_deviations(*args, **kwargs)
        
    def get_statistics(self, *args, **kwargs):
        return get_statistics(*args, **kwargs)
        
    def get_activity_stats(self, *args, **kwargs):
        return get_activity_stats(*args, **kwargs)
        
    def transform_dfg_for_react_flow(self, *args, **kwargs):
        return transform_dfg_for_react_flow(*args, **kwargs)
        
    def transform_variants(self, *args, **kwargs):
        return transform_variants(*args, **kwargs)

# Singleton instance
pm4py_service = PM4PyService()

__all__ = [
    "PM4PyService",
    "pm4py_service",
    "MiningError",
    "EmptyEventLogError",
    "DFGDiscoveryError",
    "StatisticsError",
    "VariantExtractionError",
]
