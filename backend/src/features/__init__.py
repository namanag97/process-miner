"""Features Layer - Domain-specific business logic.

This layer contains code specific to the product vertical.
Currently: Process Mining SaaS.

Modules:
- process_mining: Process discovery, conformance, analytics

Features CAN import from src.infra.* but platform CANNOT import from features.
"""

from src.features import process_mining

__all__ = ["process_mining"]
