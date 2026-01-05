"""Mining Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.discovery.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.mining import mining_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.discovery import mining_service
"""

# Re-export everything from the feature layer
from src.features.process_mining.discovery import (
    MiningService,
    mining_service,
)

__all__ = [
    "MiningService",
    "mining_service",
]
