"""Organizational Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.organizational.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.organizational import organizational_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.organizational import organizational_service
"""

from src.features.process_mining.organizational import (
    OrganizationalService,
    organizational_service,
)

__all__ = [
    "OrganizationalService",
    "organizational_service",
]
