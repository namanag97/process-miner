"""Discovery schemas - Mining algorithms and models.

Contains schemas for:
- Miner information
- Discovery requests
- Process model responses
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.features.process_mining.enums import MinerType
from src.shared.schemas import PaginatedResponse

# UUID regex pattern for validation
UUID_PATTERN = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


class MinerInfo(BaseModel):
    """Mining algorithm information."""

    id: str
    name: str
    description: str
    output_format: str


class AlgorithmParameters(BaseModel):
    """Algorithm-specific parameters for process discovery.

    Different mining algorithms support different parameters:
    - inductive/inductive_infrequent: noise_threshold (0.0-1.0)
    - heuristics: dependency_threshold (0.0-1.0), and_threshold (0.0-1.0)
    - ilp: alpha (0.0-1.0)
    - log_skeleton: noise_threshold (0.0-1.0)
    """

    # Inductive Miner parameters
    noise_threshold: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Filter infrequent behavior (0.0-1.0). Used by inductive, log_skeleton miners.",
    )

    # Heuristics Miner parameters
    dependency_threshold: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Minimum dependency measure (0.0-1.0). Used by heuristics miner. Default: 0.5",
    )
    and_threshold: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Minimum AND threshold (0.0-1.0). Used by heuristics miner. Default: 0.65",
    )

    # ILP Miner parameters
    alpha: float | None = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Noise filtering (0.0-1.0). Used by ILP miner. Default: 1.0 (no filtering)",
    )

    # Transition System parameters
    direction: str | None = Field(
        None,
        pattern="^(forward|backward)$",
        description="Direction for transition system. Default: forward",
    )
    window: int | None = Field(
        None,
        ge=1,
        le=10,
        description="Window size for transition system. Default: 2",
    )


class DiscoverRequest(BaseModel):
    """Request to discover a process model."""

    dataset_id: str = Field(
        ...,
        min_length=36,
        max_length=36,
        pattern=UUID_PATTERN,
        description="Dataset UUID to mine",
        examples=["123e4567-e89b-12d3-a456-426614174000"],
    )
    miner_type: MinerType = MinerType.INDUCTIVE
    model_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Optional name for the discovered model",
    )
    parameters: AlgorithmParameters | None = Field(
        None,
        description="Algorithm-specific parameters. If not provided, defaults are used.",
    )

    @field_validator("model_name")
    @classmethod
    def validate_model_name(cls, v: str | None) -> str | None:
        """Ensure model_name is not empty or whitespace-only."""
        if v is not None and not v.strip():
            raise ValueError("Model name cannot be empty or whitespace-only")
        return v.strip() if v else None


class ModelResponse(BaseModel):
    """Process model response."""

    id: str
    name: str
    miner_type: str
    model_format: str
    dataset_id: str | None
    fitness: float | None
    precision: float | None
    metrics_status: str | None = Field(
        None,
        description="Status of quality metrics: 'success', 'failed', or 'not_applicable'",
    )
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ModelListResponse(PaginatedResponse):
    """Paginated model list."""

    items: list[ModelResponse]
