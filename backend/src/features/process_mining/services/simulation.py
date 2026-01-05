"""Simulation Service - Re-export shim for backwards compatibility.

This module re-exports from the feature layer for backwards compatibility.
New code should import directly from src.features.process_mining.simulation.

Example:
    # Legacy (still works):
    from src.features.process_mining.services.simulation import simulation_service

    # Preferred (DDD-compliant):
    from src.features.process_mining.simulation import simulation_service
"""

from src.features.process_mining.simulation import (
    SimulationService,
    simulation_service,
)

__all__ = [
    "SimulationService",
    "simulation_service",
]
