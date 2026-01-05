"""Business logic services.

Note: Uses lazy imports to avoid circular dependencies during Phase 7 migration.
"""

__all__ = [
    "analytics_service",
    "conformance_service",
    # High-performance
    "duckdb_ingestion_service",
    "event_log_loader",
    "filtering_service",
    "ingestion_service",
    "mining_service",
    "ocpm_service",
    "organizational_service",
    "prediction_service",
    "simulation_service",
    "storage_service",
    "workflow_service",
]


def __getattr__(name: str):
    """Lazy-load services to avoid circular imports."""
    if name == "mining_service":
        from src.services.mining import mining_service
        return mining_service
    elif name == "ingestion_service":
        from src.services.ingestion import ingestion_service
        return ingestion_service
    elif name == "duckdb_ingestion_service":
        from src.services.duckdb_ingestion import duckdb_ingestion_service
        return duckdb_ingestion_service
    elif name == "analytics_service":
        from src.services.analytics import analytics_service
        return analytics_service
    elif name == "conformance_service":
        from src.services.conformance import conformance_service
        return conformance_service
    elif name == "event_log_loader":
        from src.services.event_log_loader import event_log_loader
        return event_log_loader
    elif name == "filtering_service":
        from src.services.filtering import filtering_service
        return filtering_service
    elif name == "ocpm_service":
        from src.services.ocpm import ocpm_service
        return ocpm_service
    elif name == "organizational_service":
        from src.services.organizational import organizational_service
        return organizational_service
    elif name == "prediction_service":
        from src.services.prediction import prediction_service
        return prediction_service
    elif name == "simulation_service":
        from src.services.simulation import simulation_service
        return simulation_service
    elif name == "storage_service":
        from src.services.platform.storage import storage_service
        return storage_service
    elif name == "workflow_service":
        from src.services.workflow import workflow_service
        return workflow_service
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
