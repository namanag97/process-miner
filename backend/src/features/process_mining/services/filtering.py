"""Filtering Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.filtering.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.filtering import filtering_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.filtering import filtering_service
"""

from src.features.process_mining.filtering import (
    FilteringService,
    filtering_service,
)

__all__ = [
    "FilteringService",
    "filtering_service",
]
