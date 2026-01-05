"""Analysis Layer - Process Mining Features.

This layer contains all process mining algorithms and analysis:
- Discovery (DFG, Petri nets, BPMN, etc.)
- Conformance checking
- Analytics (KPIs, bottlenecks)
- Predictions (ML models)
- Simulation

The Analysis layer:
- CAN depend on: Datasets layer (for data access)
- CANNOT depend on: Platform layer directly (goes through Datasets)
"""

from src.analysis.enums import ConformanceMethod, MinerType, ModelFormat

__all__ = [
    "MinerType",
    "ModelFormat",
    "ConformanceMethod",
]
