"""Redis-backed Log Broker for Multi-Worker SSE.

Solves the "Worker Wall" problem where global module variables break
with multiple Uvicorn workers.

Problem:
- Each Uvicorn worker = separate Python process = separate globals
- User connects to Worker B, but background task runs on Worker A → user sees nothing

Solution:
- Redis pubsub broadcasts logs to all workers
- Any worker can publish, all connected clients receive

Performance:
- Redis pubsub is extremely fast (< 1ms latency)
- No persistent storage (logs are ephemeral)
"""

import asyncio
import json
from collections import deque
from typing import AsyncGenerator, Deque, Optional

import redis.asyncio as redis
from pydantic import BaseModel

from src.core.config import get_settings
from src.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

# Channel names
DEV_LOGS_CHANNEL = "dev:logs"
DEV_HEARTBEAT_CHANNEL = "dev:heartbeat"


class LogBroker:
    """Redis-backed log broker for multi-worker SSE.

    Features:
    - Publishes logs to all workers via Redis pubsub
    - Maintains local buffer for initial connection (last 500 logs)
    - Graceful fallback if Redis unavailable
    """

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._connected = False
        self._local_buffer: Deque = deque(maxlen=500)
        self._log_id_counter = 0

    async def connect(self):
        """Connect to Redis with retry logic."""
        if self._connected:
            return

        try:
            # Use redis_url from settings if available, otherwise use default
            redis_url = getattr(settings, 'redis_url', 'redis://localhost:6379/0')

            self._redis = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
                socket_keepalive=True,
            )

            # Test connection
            await self._redis.ping()
            self._connected = True
            logger.info("log_broker_connected", redis_url=redis_url)

        except (redis.ConnectionError, redis.TimeoutError, Exception) as e:
            logger.warning(
                "log_broker_connection_failed",
                error=str(e),
                fallback="in-memory buffer only"
            )
            self._redis = None
            self._connected = False

    async def disconnect(self):
        """Gracefully disconnect from Redis."""
        if self._redis:
            try:
                await self._redis.close()
            except Exception:
                pass
            finally:
                self._redis = None
                self._connected = False
                logger.info("log_broker_disconnected")

    async def publish_log(self, entry_dict: dict):
        """Publish log entry to all workers.

        Args:
            entry_dict: Log entry as dictionary (from DevLogEntry.model_dump())
        """
        # Always add to local buffer for initial connections
        self._local_buffer.append(entry_dict)

        # Try to publish to Redis (broadcast to all workers)
        if self._redis and self._connected:
            try:
                await self._redis.publish(
                    DEV_LOGS_CHANNEL,
                    json.dumps(entry_dict)
                )
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning(
                    "log_broker_publish_failed",
                    error=str(e),
                    fallback="local buffer only"
                )
                # Mark as disconnected to avoid spamming errors
                self._connected = False

    async def publish_heartbeat(self, heartbeat_dict: dict):
        """Publish heartbeat to all workers.

        Args:
            heartbeat_dict: Heartbeat as dictionary (from HeartbeatMessage.model_dump())
        """
        if self._redis and self._connected:
            try:
                await self._redis.publish(
                    DEV_HEARTBEAT_CHANNEL,
                    json.dumps(heartbeat_dict)
                )
            except (redis.ConnectionError, redis.TimeoutError):
                # Silently fail for heartbeats (not critical)
                pass

    async def subscribe_logs(
        self,
        include_recent: bool = True
    ) -> AsyncGenerator[tuple[str, str], None]:
        """Subscribe to logs from all workers.

        Yields:
            Tuple of (event_type, json_data) where event_type is "log" or "heartbeat"
        """
        # Yield recent logs from local buffer first
        if include_recent:
            for entry in list(self._local_buffer)[-50:]:
                yield ("log", json.dumps(entry))

        # If Redis unavailable, can't receive cross-worker logs
        if not self._redis or not self._connected:
            logger.warning(
                "log_broker_subscribe_without_redis",
                limitation="Only logs from THIS worker will be visible"
            )
            # Could return here, or implement a local-only fallback
            # For now, just return (client will still get logs via direct notification)
            return

        # Subscribe to Redis pubsub
        try:
            pubsub = self._redis.pubsub()
            await pubsub.subscribe(DEV_LOGS_CHANNEL, DEV_HEARTBEAT_CHANNEL)

            logger.info("log_broker_subscribed", channels=[DEV_LOGS_CHANNEL, DEV_HEARTBEAT_CHANNEL])

            # Listen for messages
            try:
                async for message in pubsub.listen():
                    if message["type"] != "message":
                        continue

                    channel = message["channel"]
                    data = message["data"]

                    if channel == DEV_LOGS_CHANNEL:
                        yield ("log", data)
                    elif channel == DEV_HEARTBEAT_CHANNEL:
                        yield ("heartbeat", data)

            finally:
                await pubsub.unsubscribe(DEV_LOGS_CHANNEL, DEV_HEARTBEAT_CHANNEL)
                await pubsub.close()

        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.error(
                "log_broker_subscribe_failed",
                error=str(e),
            )
            # Re-raise to let caller handle
            raise

    def get_recent_logs(self, limit: int = 50) -> list[dict]:
        """Get recent logs from local buffer.

        Args:
            limit: Maximum number of logs to return

        Returns:
            List of log entry dictionaries
        """
        return list(self._local_buffer)[-limit:]

    async def health_check(self) -> dict:
        """Check broker health status.

        Returns:
            Dictionary with health status
        """
        health = {
            "connected": self._connected,
            "buffer_size": len(self._local_buffer),
            "redis_available": False,
        }

        if self._redis:
            try:
                await self._redis.ping()
                health["redis_available"] = True
            except Exception:
                health["redis_available"] = False

        return health


# Singleton instance
log_broker = LogBroker()


# Lifecycle management
async def startup_log_broker():
    """Connect to Redis on application startup."""
    await log_broker.connect()


async def shutdown_log_broker():
    """Disconnect from Redis on application shutdown."""
    await log_broker.disconnect()
