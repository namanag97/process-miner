"""Redis caching layer for expensive operations.

Provides caching for:
- Analytics operations (bottleneck detection, rework analysis)
- Process discovery results
- Conformance checking results
- Organizational mining results

Serialization: Uses msgpack for fast, safe binary serialization (replaces pickle).
"""

import hashlib
from collections.abc import Callable
from functools import wraps
from typing import Any

import msgpack
import redis
import structlog

from src.infra.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


class CacheService:
    """Redis-based caching service."""

    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client: redis.Redis | None = None
        self.enabled = settings.cache_enabled

        if self.enabled:
            try:
                self.redis_client = redis.Redis(
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                    decode_responses=False,  # Use binary mode for msgpack
                    socket_connect_timeout=5,
                    socket_timeout=5,
                )
                # Test connection
                self.redis_client.ping()
                logger.info(
                    "redis_connected",
                    host=settings.redis_host,
                    port=settings.redis_port,
                    db=settings.redis_db,
                )
            except (redis.ConnectionError, redis.TimeoutError) as e:
                logger.warning("redis_connection_failed", error=str(e))
                self.enabled = False
                self.redis_client = None

    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from function arguments.

        Args:
            prefix: Key prefix (e.g., 'bottlenecks', 'rework')
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        # Create a deterministic hash from arguments
        key_parts = [str(arg) for arg in args]
        key_parts.extend([f"{k}={v}" for k, v in sorted(kwargs.items())])
        key_string = ":".join(key_parts)

        # Hash for consistent length
        key_hash = hashlib.sha256(key_string.encode()).hexdigest()[:16]

        return f"{prefix}:{key_hash}"

    def get(self, key: str) -> Any | None:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if not self.enabled or not self.redis_client:
            return None

        try:
            cached = self.redis_client.get(key)
            if cached:
                logger.debug("cache_hit", key=key)
                # Deserialize with msgpack (safe, no arbitrary code execution)
                return msgpack.unpackb(cached, raw=False)
            logger.debug("cache_miss", key=key)
            return None
        except Exception as e:
            logger.warning("cache_get_error", key=key, error=str(e))
            return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
    ) -> bool:
        """Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            # Serialize with msgpack (faster than JSON, safer than pickle)
            serialized = msgpack.packb(value, use_bin_type=True)
            self.redis_client.setex(key, ttl, serialized)
            logger.debug("cache_set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.warning("cache_set_error", key=key, error=str(e))
            return False

    def delete(self, key: str) -> bool:
        """Delete value from cache.

        Args:
            key: Cache key

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.delete(key)
            logger.debug("cache_deleted", key=key)
            return True
        except Exception as e:
            logger.warning("cache_delete_error", key=key, error=str(e))
            return False

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern.

        Args:
            pattern: Redis key pattern (e.g., 'bottlenecks:*')

        Returns:
            Number of keys deleted
        """
        if not self.enabled or not self.redis_client:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info("cache_pattern_invalidated", pattern=pattern, count=deleted)
                return deleted
            return 0
        except Exception as e:
            logger.warning("cache_invalidate_error", pattern=pattern, error=str(e))
            return 0

    def clear(self) -> bool:
        """Clear all cached values.

        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not self.redis_client:
            return False

        try:
            self.redis_client.flushdb()
            logger.info("cache_cleared")
            return True
        except Exception as e:
            logger.warning("cache_clear_error", error=str(e))
            return False


# Global cache service instance
cache_service = CacheService()


def cache_result(
    prefix: str,
    ttl: int = 3600,
    key_func: Callable | None = None,
):
    """Decorator to cache function results in Redis.

    Args:
        prefix: Cache key prefix
        ttl: Time-to-live in seconds (default: 1 hour)
        key_func: Optional function to generate custom cache key

    Returns:
        Decorated function

    Example:
        @cache_result("bottlenecks", ttl=1800)
        def detect_bottlenecks(dataset_id: str):
            # Expensive operation
            return results
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_service._generate_key(prefix, *args, **kwargs)

            # Try to get from cache
            cached = cache_service.get(cache_key)
            if cached is not None:
                return cached

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            cache_service.set(cache_key, result, ttl)

            return result

        # Add invalidation helper
        def invalidate(*args, **kwargs):
            """Invalidate cache for specific arguments."""
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = cache_service._generate_key(prefix, *args, **kwargs)
            cache_service.delete(cache_key)

        def invalidate_all():
            """Invalidate all cached results for this function."""
            cache_service.invalidate_pattern(f"{prefix}:*")

        wrapper.invalidate = invalidate
        wrapper.invalidate_all = invalidate_all

        return wrapper

    return decorator


def invalidate_dataset_cache(dataset_id: str):
    """Invalidate all cached results for a specific event log.

    Args:
        dataset_id: Event log ID

    This should be called when:
    - Log is updated or deleted
    - Log is filtered
    - New process model is discovered
    """
    patterns = [
        f"bottlenecks:*{dataset_id}*",
        f"rework:*{dataset_id}*",
        f"variants:*{dataset_id}*",
        f"social_network:*{dataset_id}*",
        f"analytics:*{dataset_id}*",
        f"discovery:*{dataset_id}*",
        f"conformance:*{dataset_id}*",
    ]

    total_deleted = 0
    for pattern in patterns:
        total_deleted += cache_service.invalidate_pattern(pattern)

    logger.info("dataset_cache_invalidated", dataset_id=dataset_id, keys_deleted=total_deleted)
    return total_deleted
