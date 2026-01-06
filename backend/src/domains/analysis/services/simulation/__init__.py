"""Simulation Services.

What-if analysis and process simulation.
"""

from src.domains.analysis.services.simulation.service import SimulationService

simulation_service = SimulationService()

__all__ = [
    "SimulationService",
    "simulation_service",
]
