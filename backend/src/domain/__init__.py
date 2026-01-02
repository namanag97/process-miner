"""Domain layer package.

Provides rich domain model components:
- Value Objects: Immutable domain primitives (CaseId, ActivitySequence, TimeRange)
- Entities: Domain objects with identity and behavior
- Aggregates: Consistency boundaries (DatasetAggregate)
- Repositories: Data access abstractions
"""

from src.domain.value_objects import (
    CaseId,
    ActivityName,
    ResourceId,
    ActivitySequence,
    TimeRange,
    QualityMetrics,
    ProcessStatistics,
    VariantStats,
)

from src.domain.entities import (
    ProcessEvent,
    ProcessCase,
    DatasetAggregate,
)

__all__ = [
    # Value Objects
    "CaseId",
    "ActivityName", 
    "ResourceId",
    "ActivitySequence",
    "TimeRange",
    "QualityMetrics",
    "ProcessStatistics",
    "VariantStats",
    # Entities
    "ProcessEvent",
    "ProcessCase",
    "DatasetAggregate",
]

