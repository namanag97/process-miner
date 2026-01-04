"""Domain layer package.

Provides rich domain model components:
- Value Objects: Immutable domain primitives (CaseId, ActivitySequence, TimeRange)
- Entities: Domain objects with identity and behavior
- Aggregates: Consistency boundaries (DatasetAggregate)
- Repositories: Data access abstractions
"""

from src.domain.entities import (
    DatasetAggregate,
    ProcessCase,
    ProcessEvent,
)
from src.domain.value_objects import (
    ActivityName,
    ActivitySequence,
    CaseId,
    ProcessStatistics,
    QualityMetrics,
    ResourceId,
    TimeRange,
    VariantStats,
)

__all__ = [
    "ActivityName",
    "ActivitySequence",
    # Value Objects
    "CaseId",
    "DatasetAggregate",
    "ProcessCase",
    # Entities
    "ProcessEvent",
    "ProcessStatistics",
    "QualityMetrics",
    "ResourceId",
    "TimeRange",
    "VariantStats",
]
