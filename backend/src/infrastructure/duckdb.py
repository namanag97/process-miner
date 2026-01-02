
import duckdb
import threading
from typing import Optional, Any
from src.core.logging_config import get_logger

logger = get_logger(__name__)

class DuckDBManager:
    """
    Singleton manager for DuckDB connections.
    Maintains a persistent in-memory database shared across the application.
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DuckDBManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        
        self._conn = None
        self._initialized = True
        logger.info("DuckDBManager initialized")

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get the shared DuckDB connection."""
        if self._conn is None:
            # Create a shared in-memory database
            self._conn = duckdb.connect(":memory:")
            # Install/Load extensions if needed
            self._conn.execute("INSTALL httpfs; LOAD httpfs;")
            self._conn.execute("INSTALL parquet; LOAD parquet;")
            logger.info("duckdb_connection_created")
        return self._conn

    def execute(self, query: str, parameters: Optional[list] = None) -> Any:
        """Execute a query directly on the shared connection."""
        conn = self.get_connection()
        if parameters:
            return conn.execute(query, parameters)
        return conn.execute(query)

    def query_to_arrow(self, query: str, parameters: Optional[list] = None) -> Any:
        """Execute query and return Arrow table."""
        return self.execute(query, parameters).arrow()

    def query_to_df(self, query: str, parameters: Optional[list] = None) -> Any:
        """Execute query and return Pandas DataFrame."""
        return self.execute(query, parameters).df()

    def register_arrow(self, name: str, arrow_table: Any):
        """Register an Arrow table as a view/table in DuckDB."""
        conn = self.get_connection()
        # registration in duckdb python api usually happens via the connection object
        # referencing the python variable in the query often works, or using .register()
        conn.register(name, arrow_table)
        logger.info("arrow_table_registered", table_name=name)

# Global instance
duckdb_manager = DuckDBManager()
