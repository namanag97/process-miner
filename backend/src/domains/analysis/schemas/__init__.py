"""Analysis Domain Schemas.

Request/Response schemas for analysis operations:
- Statistics schemas
- Discovery schemas
- Conformance schemas
- Analytics schemas
- Visualization schemas
"""

from src.features.process_mining.schemas import (
    # Statistics & Analytics
    ActivityDetailResponse,
    CaseListResponse,
    CaseResponse,
    EventResponse,
    StatisticsResponse,
    VariantResponse,
)
from src.features.process_mining.schemas.analytics import (
    BottleneckAnalysisResponse,
    CycleTimeResponse,
)
from src.features.process_mining.schemas.conformance import (
    ConformanceCheckResponse,
    TokenReplayResponse,
)
from src.features.process_mining.schemas.discovery import (
    DiscoveryRequest,
    DiscoveryResponse,
)
from src.features.process_mining.schemas.visualization import (
    DFGResponse,
    GraphLayoutResponse,
)

__all__ = [
    # Statistics
    "StatisticsResponse",
    "CaseResponse",
    "CaseListResponse",
    "EventResponse",
    "VariantResponse",
    "ActivityDetailResponse",
    # Discovery
    "DiscoveryRequest",
    "DiscoveryResponse",
    # Conformance
    "ConformanceCheckResponse",
    "TokenReplayResponse",
    # Analytics
    "BottleneckAnalysisResponse",
    "CycleTimeResponse",
    # Visualization
    "DFGResponse",
    "GraphLayoutResponse",
]
