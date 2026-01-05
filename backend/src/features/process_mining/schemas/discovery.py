"""Discovery schemas - Mining algorithms and models.

Contains schemas for:
- Miner information
- Discovery requests
- Process model responses
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.features.process_mining.enums import MinerType
from src.shared.schemas import PaginatedResponse


class MinerInfo(BaseModel):
    """Mining algorithm information."""

    id: str
    name: str
    description: str
    output_format: str


class DiscoverRequest(BaseModel):
    """Request to discover a process model."""

    dataset_id: str = Field(..., description="Dataset ID to mine")
    miner_type: MinerType = MinerType.INDUCTIVE
    model_name: str | None = None


class ModelResponse(BaseModel):
    """Process model response."""

    id: str
    name: str
    miner_type: str
    model_format: str
    dataset_id: str | None
    fitness: float | None
    precision: float | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelListResponse(PaginatedResponse):
    """Paginated model list."""

    items: list[ModelResponse]
