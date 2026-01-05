"""Rate limiting configuration for API endpoints.

Prevents abuse and protects against:
- Storage quota exhaustion (presigned upload spam)
- API resource exhaustion (compute-heavy endpoints)
- DDoS attacks

Uses slowapi with Redis backend for distributed rate limiting.
"""

from slowapi import Limiter
from slowapi.util import get_remote_address

from src.platform.core.config import get_settings

settings = get_settings()

# Initialize rate limiter with Redis backend
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    strategy="fixed-window",  # Reset limits at fixed intervals
    headers_enabled=True,  # Send X-RateLimit-* headers
)


def get_limiter() -> Limiter:
    """Get rate limiter instance for dependency injection."""
    return limiter
