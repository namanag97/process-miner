"""Base query infrastructure for CQRS read operations.

Provides:
- BaseQuery: Abstract base for all query data classes
- QueryHandler: Handler interface for processing queries
- QueryBus: Dispatcher that routes queries to handlers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound="BaseQuery")
R = TypeVar("R")  # Result type


@dataclass
class BaseQuery(ABC):
    """Base class for all queries (read operations).

    Queries represent requests to retrieve data. They should:
    - Be immutable
    - Contain only the parameters needed to fetch data
    - Never mutate state

    Example:
        @dataclass
        class GetDatasetQuery(BaseQuery):
            dataset_id: str
            include_events: bool = False
    """

    @property
    def query_type(self) -> str:
        """Return the query type name for logging/tracing."""
        return self.__class__.__name__


class QueryHandler(ABC, Generic[T, R]):
    """Abstract handler for processing queries.

    Each query type has exactly one handler. Handlers should:
    - Execute read-only operations
    - Use read-optimized data stores (DuckDB, read replicas, caches)
    - Never mutate state

    Example:
        class GetDatasetHandler(QueryHandler[GetDatasetQuery, DatasetResponse]):
            async def handle(self, query: GetDatasetQuery) -> DatasetResponse:
                # Fetch and return data
    """

    @abstractmethod
    async def handle(self, query: T) -> R:
        """Execute the query and return the result."""


class QueryBus:
    """Dispatches queries to their registered handlers.

    Provides centralized query routing with:
    - Handler registration
    - Logging and tracing
    - Caching support (optional)

    Usage:
        bus = QueryBus()
        bus.register(GetDatasetQuery, GetDatasetHandler(read_db, duckdb))
        result = await bus.dispatch(GetDatasetQuery(dataset_id="..."))
    """

    def __init__(self):
        self._handlers: dict[type[BaseQuery], QueryHandler] = {}

    def register(self, query_type: type[T], handler: QueryHandler[T, Any]) -> None:
        """Register a handler for a query type."""
        if query_type in self._handlers:
            raise ValueError(f"Handler already registered for {query_type.__name__}")
        self._handlers[query_type] = handler
        logger.debug("query_handler_registered", query_type=query_type.__name__)

    async def dispatch(self, query: BaseQuery) -> Any:
        """Dispatch a query to its handler.

        Args:
            query: The query to execute

        Returns:
            The result from the handler

        Raises:
            ValueError: If no handler is registered for the query type
            Exception: Any exception raised by the handler
        """
        query_type = type(query)
        handler = self._handlers.get(query_type)

        if not handler:
            raise ValueError(f"No handler registered for {query_type.__name__}")

        logger.debug(
            "query_dispatched",
            query_type=query.query_type,
        )

        try:
            result = await handler.handle(query)
            logger.debug(
                "query_completed",
                query_type=query.query_type,
            )
            return result
        except Exception as e:
            logger.error(
                "query_failed",
                query_type=query.query_type,
                error=str(e),
            )
            raise

    def has_handler(self, query_type: type[BaseQuery]) -> bool:
        """Check if a handler is registered for a query type."""
        return query_type in self._handlers


# Global query bus instance
query_bus = QueryBus()
