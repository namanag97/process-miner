"""Rate limiting for API endpoints.

Provides configurable rate limiting with:
- Token bucket algorithm
- Per-endpoint limits
- Per-client tracking (IP or API key)
- Sliding window support

Usage:
    @router.post("/upload")
    @rate_limit(requests=10, window=60)  # 10 req/min
    async def upload(...):
        ...

    # Or use middleware for global limits
    app.add_middleware(RateLimitMiddleware, default_limit=100, window=60)
"""

import asyncio
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.platform.core.logging_config import get_logger
from src.platform.core.exceptions import BadRequestError

logger = get_logger(__name__)


# =============================================================================
# Token Bucket Implementation
# =============================================================================


@dataclass
class TokenBucket:
    """Token bucket rate limiter.

    Tokens are added at a fixed rate. Each request consumes one token.
    If no tokens available, request is rate limited.
    """

    capacity: int  # Max tokens
    refill_rate: float  # Tokens per second
    tokens: float = field(default=0.0)
    last_refill: float = field(default_factory=time.monotonic)

    def __post_init__(self):
        self.tokens = float(self.capacity)

    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if allowed."""
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False

    def time_until_available(self, tokens: int = 1) -> float:
        """Seconds until enough tokens are available."""
        self._refill()
        if self.tokens >= tokens:
            return 0.0
        needed = tokens - self.tokens
        return needed / self.refill_rate


# =============================================================================
# Rate Limit Store
# =============================================================================


class RateLimitStore:
    """In-memory rate limit tracking.

    In production, use Redis for distributed rate limiting.
    """

    def __init__(self):
        self._buckets: dict[str, TokenBucket] = {}
        self._lock = asyncio.Lock()

    async def get_bucket(self, key: str, capacity: int, window: int) -> TokenBucket:
        """Get or create a token bucket for a client."""
        async with self._lock:
            if key not in self._buckets:
                # Tokens per second = capacity / window
                refill_rate = capacity / window
                self._buckets[key] = TokenBucket(
                    capacity=capacity,
                    refill_rate=refill_rate,
                )
            return self._buckets[key]

    async def cleanup(self, max_age: float = 3600) -> int:
        """Remove stale buckets. Returns count removed."""
        now = time.monotonic()
        async with self._lock:
            stale = [k for k, v in self._buckets.items() if now - v.last_refill > max_age]
            for key in stale:
                del self._buckets[key]
            return len(stale)


# Global store
_rate_limit_store = RateLimitStore()


# =============================================================================
# Rate Limit Decorator
# =============================================================================


def rate_limit(
    requests: int = 100,
    window: int = 60,
    key_func: Callable[[Request], str] | None = None,
    error_message: str = "Rate limit exceeded",
):
    """Decorator to rate limit an endpoint.

    Args:
        requests: Maximum requests allowed in window
        window: Time window in seconds
        key_func: Function to extract client key from request (default: IP)
        error_message: Message to return when rate limited

    Usage:
        @router.get("/items")
        @rate_limit(requests=100, window=60)
        async def list_items(request: Request):
            ...
    """

    def get_client_key(request: Request) -> str:
        """Default key function using client IP."""
        if key_func:
            return key_func(request)
        # Use IP address as default
        client_ip = request.client.host if request.client else "unknown"
        return f"{request.url.path}:{client_ip}"

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find request in args/kwargs
            request: Request | None = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")

            if not request:
                return await func(*args, **kwargs)

            # Get bucket and check rate limit
            client_key = get_client_key(request)
            bucket = await _rate_limit_store.get_bucket(client_key, requests, window)

            if not bucket.consume():
                retry_after = int(bucket.time_until_available()) + 1

                logger.warning(
                    "rate_limit_exceeded",
                    client_key=client_key,
                    endpoint=str(request.url.path),
                    retry_after=retry_after,
                )

                # Rate limit with proper exception
                raise BadRequestError(
                    message=f"{error_message}. Try again in {retry_after} seconds.",
                    details={
                        "error_code": "ERR_510",
                        "limit": requests,
                        "window_seconds": window,
                        "retry_after": retry_after,
                    },
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# =============================================================================
# Rate Limit Middleware
# =============================================================================


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Global rate limiting middleware.

    Applies rate limits based on endpoint and client IP.
    """

    def __init__(
        self,
        app,
        default_limit: int = 100,
        window: int = 60,
        endpoint_limits: dict[str, tuple[int, int]] | None = None,
    ):
        """
        Args:
            app: FastAPI app
            default_limit: Default requests per window
            window: Default window in seconds
            endpoint_limits: Dict of path -> (limit, window) for specific endpoints
        """
        super().__init__(app)
        self.default_limit = default_limit
        self.window = window
        self.endpoint_limits = endpoint_limits or {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health"):
            return await call_next(request)

        # Get limit for this endpoint
        limit, window = self._get_limit(request.url.path)

        # Create client key
        client_ip = request.client.host if request.client else "unknown"
        client_key = f"global:{request.url.path}:{client_ip}"

        # Check rate limit
        bucket = await _rate_limit_store.get_bucket(client_key, limit, window)

        if not bucket.consume():
            retry_after = int(bucket.time_until_available()) + 1

            logger.warning(
                "rate_limit_exceeded",
                client_key=client_key,
                endpoint=str(request.url.path),
            )

            return Response(
                content='{"error": "Rate limit exceeded"}',
                status_code=429,
                headers={
                    "Content-Type": "application/json",
                    "Retry-After": str(retry_after),
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                },
            )

        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(int(bucket.tokens))

        return response

    def _get_limit(self, path: str) -> tuple[int, int]:
        """Get rate limit for a path."""
        for pattern, limits in self.endpoint_limits.items():
            if path.startswith(pattern):
                return limits
        return self.default_limit, self.window


# =============================================================================
# Convenience Functions
# =============================================================================

# Pre-configured rate limiters for common use cases


def rate_limit_strict():
    """Strict rate limit: 10 requests per minute."""
    return rate_limit(requests=10, window=60)


def rate_limit_standard():
    """Standard rate limit: 100 requests per minute."""
    return rate_limit(requests=100, window=60)


def rate_limit_relaxed():
    """Relaxed rate limit: 1000 requests per minute."""
    return rate_limit(requests=1000, window=60)


def rate_limit_upload():
    """Upload rate limit: 5 uploads per minute."""
    return rate_limit(
        requests=5,
        window=60,
        error_message="Too many uploads. Please wait before uploading more files.",
    )
