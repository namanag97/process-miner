"""Idempotency middleware for mutation endpoints.

Provides at-most-once semantics for POST/PUT/DELETE operations:
- Clients include Idempotency-Key header
- Server caches responses for duplicate requests
- Prevents duplicate resource creation on retries

Usage:
    # Apply middleware to specific routes
    @router.post("/processes/upload")
    @idempotent(ttl=86400)
    async def upload_process(...):
        ...
    
    # Or use as middleware for all mutations
    app.add_middleware(IdempotencyMiddleware)
"""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, Optional

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging_config import get_logger

logger = get_logger(__name__)


# =============================================================================
# Idempotency Storage
# =============================================================================

@dataclass
class IdempotencyRecord:
    """Stored response for an idempotency key."""
    status_code: int
    headers: Dict[str, str]
    body: bytes
    created_at: datetime
    expires_at: datetime


class IdempotencyStore:
    """In-memory storage for idempotency records.
    
    In production, use Redis for distributed caching.
    """
    
    def __init__(self):
        self._records: Dict[str, IdempotencyRecord] = {}
    
    async def get(self, key: str) -> Optional[IdempotencyRecord]:
        """Get a stored response by idempotency key."""
        record = self._records.get(key)
        if record and record.expires_at > datetime.utcnow():
            return record
        elif record:
            # Expired, clean up
            del self._records[key]
        return None
    
    async def set(
        self, 
        key: str, 
        status_code: int,
        headers: Dict[str, str],
        body: bytes,
        ttl: int = 86400,
    ) -> None:
        """Store a response for an idempotency key."""
        now = datetime.utcnow()
        self._records[key] = IdempotencyRecord(
            status_code=status_code,
            headers=headers,
            body=body,
            created_at=now,
            expires_at=now + timedelta(seconds=ttl),
        )
        
        # Cleanup expired entries periodically
        await self._cleanup()
    
    async def _cleanup(self) -> None:
        """Remove expired entries."""
        now = datetime.utcnow()
        expired = [k for k, v in self._records.items() if v.expires_at < now]
        for key in expired:
            del self._records[key]
    
    async def delete(self, key: str) -> bool:
        """Delete an idempotency record."""
        if key in self._records:
            del self._records[key]
            return True
        return False


# Global store instance
_idempotency_store = IdempotencyStore()


# =============================================================================
# Idempotency Middleware
# =============================================================================

class IdempotencyMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces idempotency for mutation requests.
    
    Only applies to POST, PUT, PATCH, DELETE requests that include
    an Idempotency-Key header.
    """
    
    MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
    HEADER_NAME = "Idempotency-Key"
    TTL = 86400  # 24 hours
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Only apply to mutations with idempotency key
        if request.method not in self.MUTATION_METHODS:
            return await call_next(request)
        
        idempotency_key = request.headers.get(self.HEADER_NAME)
        if not idempotency_key:
            return await call_next(request)
        
        # Create a unique cache key including path and method
        cache_key = self._create_cache_key(
            idempotency_key,
            request.method,
            str(request.url.path),
        )
        
        # Check for existing response
        existing = await _idempotency_store.get(cache_key)
        if existing:
            logger.info(
                "idempotent_request_replayed",
                idempotency_key=idempotency_key,
                path=str(request.url.path),
            )
            return Response(
                content=existing.body,
                status_code=existing.status_code,
                headers={
                    **existing.headers,
                    "X-Idempotent-Replayed": "true",
                },
            )
        
        # Execute request
        response = await call_next(request)
        
        # Only cache successful responses
        if 200 <= response.status_code < 300:
            # Read response body
            body = b""
            async for chunk in response.body_iterator:
                body += chunk
            
            # Cache the response
            await _idempotency_store.set(
                key=cache_key,
                status_code=response.status_code,
                headers=dict(response.headers),
                body=body,
                ttl=self.TTL,
            )
            
            logger.debug(
                "idempotent_response_cached",
                idempotency_key=idempotency_key,
                path=str(request.url.path),
            )
            
            # Return new response with body
            return Response(
                content=body,
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        
        return response
    
    def _create_cache_key(
        self, 
        idempotency_key: str, 
        method: str, 
        path: str
    ) -> str:
        """Create a unique cache key."""
        combined = f"{idempotency_key}:{method}:{path}"
        return hashlib.sha256(combined.encode()).hexdigest()


# =============================================================================
# Decorator for Specific Endpoints
# =============================================================================

def idempotent(ttl: int = 86400):
    """Decorator to make an endpoint idempotent.
    
    Usage:
        @router.post("/items")
        @idempotent(ttl=3600)
        async def create_item(request: Request, ...):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract request from args/kwargs
            request: Optional[Request] = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if not request:
                request = kwargs.get("request")
            
            if not request:
                return await func(*args, **kwargs)
            
            idempotency_key = request.headers.get("Idempotency-Key")
            if not idempotency_key:
                return await func(*args, **kwargs)
            
            cache_key = hashlib.sha256(
                f"{idempotency_key}:{request.method}:{request.url.path}".encode()
            ).hexdigest()
            
            # Check cache
            existing = await _idempotency_store.get(cache_key)
            if existing:
                return Response(
                    content=existing.body,
                    status_code=existing.status_code,
                    headers={**existing.headers, "X-Idempotent-Replayed": "true"},
                )
            
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache successful responses
            if isinstance(result, Response):
                if 200 <= result.status_code < 300:
                    body = result.body if hasattr(result, 'body') else b""
                    await _idempotency_store.set(
                        cache_key, 
                        result.status_code,
                        dict(result.headers),
                        body,
                        ttl,
                    )
            
            return result
        
        return wrapper
    return decorator
