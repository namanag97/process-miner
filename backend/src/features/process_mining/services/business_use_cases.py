"""Business Use Cases Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.business_use_cases.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.business_use_cases import business_use_cases

    # Preferred (DDD-compliant):
    from src.features.process_mining.business_use_cases import business_use_cases
"""

from src.features.process_mining.business_use_cases import business_use_cases

__all__ = [
    "business_use_cases",
]
