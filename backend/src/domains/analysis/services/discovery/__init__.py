"""Discovery Services.

Process discovery algorithms and services.
"""

from src.domains.analysis.services.discovery.algorithms import (
    AlphaMiner,
    HeuristicsMiner,
    InductiveMiner,
)
from src.domains.analysis.services.discovery.service import DiscoveryService

discovery_service = DiscoveryService()

__all__ = [
    "DiscoveryService",
    "discovery_service",
    "AlphaMiner",
    "HeuristicsMiner",
    "InductiveMiner",
]
