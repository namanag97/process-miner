"""CQRS Query Infrastructure.

Queries represent read operations that do not modify state.
QueryHandlers execute queries against read-optimized data stores.

Usage:
    # Define a query
    @dataclass
    class GetBottlenecksQuery(BaseQuery):
        dataset_id: str
        limit: int = 10
    
    # Define handler (uses DuckDB, not PostgreSQL)
    class GetBottlenecksHandler(QueryHandler[GetBottlenecksQuery, BottlenecksResult]):
        async def handle(self, query: GetBottlenecksQuery) -> BottlenecksResult:
            result = self.duckdb.execute(f'''
                SELECT activity, AVG(wait_time) 
                FROM read_parquet('{self.parquet_path}')
                GROUP BY activity
            ''')
            return BottlenecksResult(items=result.fetchall())
    
    # Execute via bus
    result = await query_bus.execute(GetBottlenecksQuery(dataset_id="..."))
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import uuid4

import duckdb

# =============================================================================
# Base Types
# =============================================================================

QueryResult = TypeVar("QueryResult")


@dataclass
class BaseQuery:
    """Base class for all queries.
    
    Queries should be immutable value objects that represent
    a request for data without side effects.
    """
    
    query_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: str | None = None
    
    # Pagination defaults
    page: int = 1
    page_size: int = 20
    
    def __post_init__(self):
        """Validate query after initialization."""
        self.validate()
    
    def validate(self) -> None:
        """Override to add custom validation. Raise ValueError on failure."""
        if self.page < 1:
            raise ValueError("Page must be >= 1")
        if self.page_size < 1 or self.page_size > 1000:
            raise ValueError("Page size must be between 1 and 1000")


# =============================================================================
# Query Handler Protocol
# =============================================================================


class QueryHandler(ABC, Generic[QueryResult]):
    """Base class for query handlers.
    
    Query handlers read from optimized read stores:
    - DuckDB for analytics (Parquet files)
    - PostgreSQL read replica for metadata
    - Redis cache for pre-computed results
    
    Query handlers NEVER modify state.
    """
    
    def __init__(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection | None = None,
        cache: Any | None = None,
    ):
        self.duckdb = duckdb_conn
        self.cache = cache
    
    @abstractmethod
    async def handle(self, query: BaseQuery) -> QueryResult:
        """Execute the query and return result."""
        ...
    
    def get_cache_key(self, query: BaseQuery) -> str:
        """Generate cache key for query. Override for custom key generation."""
        import hashlib
        
        query_dict = {k: v for k, v in query.__dict__.items() 
                      if not k.startswith("_") and k not in ("query_id", "timestamp")}
        key_string = f"{type(query).__name__}:{query_dict}"
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    async def get_cached(self, query: BaseQuery) -> QueryResult | None:
        """Try to get result from cache."""
        if not self.cache:
            return None
        
        cache_key = self.get_cache_key(query)
        return self.cache.get(cache_key)
    
    async def set_cached(
        self, 
        query: BaseQuery, 
        result: QueryResult,
        ttl: int = 3600,
    ) -> None:
        """Store result in cache."""
        if not self.cache:
            return
        
        cache_key = self.get_cache_key(query)
        self.cache.set(cache_key, result, ttl=ttl)


# =============================================================================
# Query Bus
# =============================================================================


class QueryBus:
    """Routes queries to their handlers.
    
    The query bus is responsible for:
    1. Finding the appropriate handler for a query
    2. Providing read-optimized dependencies (DuckDB, cache)
    3. Executing the query
    """
    
    def __init__(
        self,
        duckdb_conn: duckdb.DuckDBPyConnection | None = None,
        cache: Any | None = None,
    ):
        self._duckdb = duckdb_conn
        self._cache = cache
        self._handlers: dict[type, type[QueryHandler]] = {}
    
    def register(
        self,
        query_type: type[BaseQuery],
        handler_type: type[QueryHandler],
    ) -> None:
        """Register a handler for a query type."""
        self._handlers[query_type] = handler_type
    
    async def execute(self, query: BaseQuery) -> Any:
        """Execute a query and return the result.
        
        Raises:
            ValueError: If no handler is registered for the query type
            Exception: Any exception raised by the handler
        """
        handler_type = self._handlers.get(type(query))
        if not handler_type:
            raise ValueError(f"No handler registered for {type(query).__name__}")
        
        handler = handler_type(
            duckdb_conn=self._duckdb,
            cache=self._cache,
        )
        
        return await handler.handle(query)


# =============================================================================
# Query Result Types
# =============================================================================


@dataclass
class PaginatedResult(Generic[QueryResult]):
    """Paginated query result."""
    
    items: list[QueryResult]
    total: int
    page: int
    page_size: int
    
    @property
    def total_pages(self) -> int:
        """Calculate total pages."""
        return (self.total + self.page_size - 1) // self.page_size
    
    @property
    def has_next(self) -> bool:
        """Check if there's a next page."""
        return self.page < self.total_pages
    
    @property
    def has_previous(self) -> bool:
        """Check if there's a previous page."""
        return self.page > 1


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "BaseQuery",
    "QueryHandler",
    "QueryBus",
    "PaginatedResult",
]
