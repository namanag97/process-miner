"""CQRS Queries - Read Operations.

Queries represent requests for data. Each query has:
- A data class defining the query parameters
- A handler that executes the query
- A response type (usually a pydantic model or dataclass)

Usage:
    query = GetBottlenecksQuery(dataset_id="...", top_n=10)
    result = await query_bus.dispatch(query)
"""

from src.application.queries.base import BaseQuery, QueryBus, QueryHandler

__all__ = ["BaseQuery", "QueryBus", "QueryHandler"]
