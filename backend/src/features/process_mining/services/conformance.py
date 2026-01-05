"""Conformance Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.conformance.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.conformance import conformance_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.conformance import conformance_service
"""

from src.features.process_mining.conformance import (
    ConformanceService,
    conformance_service,
)

__all__ = [
    "ConformanceService",
    "conformance_service",
]
