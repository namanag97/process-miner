"""Simulation schemas - Process simulation and what-if analysis.

Contains schemas for:
- Play-out (synthetic log generation)
- What-if simulation
"""

from typing import Any

from pydantic import BaseModel, Field


class PlayOutRequest(BaseModel):
    """Request to generate synthetic log from model."""

    num_traces: int = Field(default=100, ge=1, le=10000)


class PlayOutResponse(BaseModel):
    """Play-out result."""

    model_id: str
    generated_dataset_id: str
    traces_generated: int
    events_generated: int


class SimulationRequest(BaseModel):
    """What-if simulation request."""

    modifications: list[dict[str, Any]] = Field(
        ...,
        description="Modifications to simulate",
    )


class SimulationResponse(BaseModel):
    """Simulation result."""

    dataset_id: str
    scenario: str
    original_metrics: dict[str, float]
    simulated_metrics: dict[str, float]
    impact: dict[str, float]
