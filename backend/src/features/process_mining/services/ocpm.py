"""OCPM Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.ocpm.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.ocpm import ocpm_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.ocpm import ocpm_service
"""

from src.features.process_mining.ocpm import (
    OCPMService,
    ocpm_service,
)

__all__ = [
    "OCPMService",
    "ocpm_service",
]
