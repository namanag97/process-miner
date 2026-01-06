"""Shared Layer - Cross-cutting concerns used by both Platform and Features.

Modules:
- base_repository: Generic repository base class
- base_schemas: Pydantic schema base classes and mixins
- container: Request-scoped dependency container
- events: Event sourcing for audit trail
- pipeline: DAG-based computation pipeline
- protocols: Service protocols for structural typing
- repositories: Entity-specific repositories
- types: Shared type definitions (Result, etc.)
- utils: Pure utility functions
- constants: Configuration, enums
"""

from src.shared.base_schemas import (
    BaseSchema,
    IDMixin,
    TimestampMixin,
    PaginatedResponse,
    SuccessResponse,
    ErrorResponse,
    JobResponse,
)
from src.shared.container import Container
from src.shared.base_repository import BaseRepository, ReadOnlyRepository

__all__ = [
    # Base classes
    "BaseSchema",
    "BaseRepository",
    "ReadOnlyRepository",
    "Container",
    # Mixins
    "IDMixin",
    "TimestampMixin",
    # Response types
    "PaginatedResponse",
    "SuccessResponse",
    "ErrorResponse",
    "JobResponse",
    # Legacy
    "constants",
    "types",
    "utils",
]

