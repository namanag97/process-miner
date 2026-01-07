import threading
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

import duckdb

from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)


class DuckDBManager:
    """
    Manager for DuckDB connections with proper isolation.

    Provides two connection patterns:
    1. get_connection() - Returns a shared connection for simple queries
       (legacy, use with caution in concurrent scenarios)
    2. get_isolated_connection() - Context manager that yields an isolated
       connection for each request, preventing race conditions

    For analytics queries on Parquet files, use get_isolated_connection()
    to ensure thread safety and automatic cleanup of temp tables.
    """

    _instance = None
    _lock = threading.RLock()  # RLock allows re-entrant acquisition (fixes deadlock)
    _extensions_installed = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._shared_conn = None
        self._initialized = True
        logger.info("DuckDBManager initialized")

    def _ensure_extensions(self, conn: duckdb.DuckDBPyConnection) -> None:
        """Load required extensions (they are typically pre-installed with DuckDB)."""
        if not DuckDBManager._extensions_installed:
            with DuckDBManager._lock:
                if not DuckDBManager._extensions_installed:
                    try:
                        # Just load extensions - they come bundled with DuckDB
                        # Avoid INSTALL which triggers network checks
                        conn.execute("LOAD parquet;")
                        conn.execute("LOAD httpfs;")
                        DuckDBManager._extensions_installed = True
                        logger.info("duckdb_extensions_loaded")
                    except Exception as e:
                        # Extensions may not be available, log and continue
                        logger.warning("duckdb_extensions_load_failed", reason=str(e))
                        DuckDBManager._extensions_installed = True

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get the shared DuckDB connection (legacy, not thread-safe).

        WARNING: This returns a shared connection. For concurrent requests,
        use get_isolated_connection() instead to prevent race conditions.
        """
        if self._shared_conn is None:
            with self._lock:
                if self._shared_conn is None:
                    self._shared_conn = duckdb.connect(":memory:")
                    self._ensure_extensions(self._shared_conn)
                    logger.info("duckdb_shared_connection_created")
        return self._shared_conn

    @contextmanager
    def get_isolated_connection(self) -> Iterator[duckdb.DuckDBPyConnection]:
        """Get an isolated DuckDB connection for thread-safe operations.

        This context manager creates a fresh in-memory connection for each
        use, ensuring complete isolation between concurrent requests.
        Temp tables are automatically cleaned up when the context exits.

        Usage:
            with duckdb_manager.get_isolated_connection() as conn:
                result = conn.execute("SELECT * FROM read_parquet(...)").fetchall()

        Yields:
            Isolated DuckDB connection
        """
        conn = duckdb.connect(":memory:")
        try:
            self._ensure_extensions(conn)
            logger.debug("duckdb_isolated_connection_created")
            yield conn
        finally:
            try:
                conn.close()
                logger.debug("duckdb_isolated_connection_closed")
            except Exception as e:
                logger.warning("duckdb_connection_close_failed", error=str(e))

    def execute(self, query: str, parameters: list | None = None) -> Any:
        """Execute a query directly on the shared connection.

        WARNING: Not thread-safe. For concurrent operations, use
        get_isolated_connection() context manager instead.
        """
        conn = self.get_connection()
        if parameters:
            return conn.execute(query, parameters)
        return conn.execute(query)

    def query_to_arrow(self, query: str, parameters: list | None = None) -> Any:
        """Execute query and return Arrow table."""
        return self.execute(query, parameters).arrow()

    def query_to_df(self, query: str, parameters: list | None = None) -> Any:
        """Execute query and return Pandas DataFrame."""
        return self.execute(query, parameters).df()

    def register_arrow(self, name: str, arrow_table: Any):
        """Register an Arrow table as a view/table in DuckDB."""
        conn = self.get_connection()
        conn.register(name, arrow_table)
        logger.info("arrow_table_registered", table_name=name)


# Global instance
duckdb_manager = DuckDBManager()
