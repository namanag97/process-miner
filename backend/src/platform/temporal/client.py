"""Temporal Client Factory.

Provides async client for connecting to Temporal server.
Manages connection lifecycle and provides singleton access.
"""


from temporalio.client import Client

from src.platform.core.logging_config import get_logger
from src.platform.temporal.config import get_temporal_config

logger = get_logger(__name__)

# Module-level client cache
_client: Client | None = None


async def get_temporal_client() -> Client:
    """Get or create Temporal client connection.

    Returns a singleton client instance. The client is created on first call
    and reused for subsequent calls.

    Returns:
        Connected Temporal client

    Raises:
        RuntimeError: If connection to Temporal server fails
    """
    global _client

    if _client is not None:
        return _client

    config = get_temporal_config()

    try:
        _client = await Client.connect(
            config.host,
            namespace=config.namespace,
            tls=config.use_tls,
        )
        return _client
    except Exception as e:
        raise RuntimeError(f"Failed to connect to Temporal at {config.host}: {e}") from e


async def close_temporal_client() -> None:
    """Close the Temporal client connection."""
    global _client

    if _client is not None:
        # Note: Temporal client doesn't have explicit close, but we clear the cache
        _client = None


def get_temporal_client_sync() -> Client | None:
    """Get cached client without creating (for sync contexts).

    Returns:
        Cached client if exists, None otherwise
    """
    return _client
