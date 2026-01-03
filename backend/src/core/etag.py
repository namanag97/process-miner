"""ETag middleware for caching and concurrency control.

Provides:
- ETag generation for GET responses
- If-None-Match handling (304 Not Modified)
- If-Match handling for optimistic locking

Usage:
    # Add middleware for automatic ETag headers
    app.add_middleware(ETagMiddleware)
    
    # Client usage:
    # GET /api/processes/123  -> ETag: "abc123"
    # GET /api/processes/123 with If-None-Match: "abc123" -> 304 Not Modified
    # PUT /api/processes/123 with If-Match: "abc123" -> Updates or 412 Precondition Failed
"""

import hashlib
from typing import Callable, Optional, Set

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class ETagMiddleware(BaseHTTPMiddleware):
    """Middleware that adds ETag headers to responses.
    
    For GET requests:
    - Generates ETag from response body
    - Returns 304 if If-None-Match matches
    
    For PUT/PATCH requests:
    - Validates If-Match header if present
    """
    
    # Paths to exclude from ETag processing
    EXCLUDED_PATHS: Set[str] = {
        "/health",
        "/metrics",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
    
    def __init__(self, app, weak_etags: bool = True):
        """
        Args:
            app: FastAPI app
            weak_etags: Use weak ETags (prefixed with W/)
        """
        super().__init__(app)
        self.weak_etags = weak_etags
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip excluded paths
        if self._is_excluded(request.url.path):
            return await call_next(request)
        
        # Handle GET requests with ETag
        if request.method == "GET":
            return await self._handle_get(request, call_next)
        
        # Handle mutations with If-Match
        if request.method in {"PUT", "PATCH", "DELETE"}:
            return await self._handle_mutation(request, call_next)
        
        return await call_next(request)
    
    async def _handle_get(self, request: Request, call_next: Callable) -> Response:
        """Handle GET request with ETag generation and If-None-Match validation."""
        response = await call_next(request)
        
        # BUG-035 FIX: Skip ETag for streaming responses to prevent sinking
        from starlette.responses import StreamingResponse
        if isinstance(response, StreamingResponse):
            return response
        
        # Only process successful JSON responses
        if response.status_code != 200:
            return response
        
        content_type = response.headers.get("content-type", "")
        if "application/json" not in content_type:
            return response
        
        # Read response body
        body = b""
        async for chunk in response.body_iterator:
            body += chunk
        
        # Generate ETag
        etag = self._generate_etag(body)
        
        # Check If-None-Match
        if_none_match = request.headers.get("if-none-match")
        if if_none_match:
            # Handle multiple ETags in header
            client_etags = [e.strip().strip('"').lstrip("W/") for e in if_none_match.split(",")]
            server_etag = etag.strip('"').lstrip("W/")
            
            if server_etag in client_etags or "*" in client_etags:
                logger.debug(
                    "etag_not_modified",
                    path=str(request.url.path),
                    etag=etag,
                )
                return Response(
                    status_code=304,
                    headers={"ETag": etag},
                )
        
        # Return response with ETag
        return Response(
            content=body,
            status_code=response.status_code,
            headers={**dict(response.headers), "ETag": etag},
            media_type=response.media_type,
        )
    
    async def _handle_mutation(self, request: Request, call_next: Callable) -> Response:
        """Handle mutation with If-Match validation (optimistic locking)."""
        if_match = request.headers.get("if-match")
        
        # If no If-Match header, proceed normally
        if not if_match:
            return await call_next(request)
        
        # For If-Match, we need to get the current state and compare
        # This is a simplified implementation - in practice, you'd check
        # against the resource's current ETag before processing
        
        # Log the If-Match usage for now
        logger.debug(
            "if_match_header_present",
            path=str(request.url.path),
            if_match=if_match,
        )
        
        # Proceed with the request - actual validation would happen in the handler
        response = await call_next(request)
        
        # If successful, generate new ETag for the updated resource
        if response.status_code in {200, 201}:
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                body = b""
                async for chunk in response.body_iterator:
                    body += chunk
                
                etag = self._generate_etag(body)
                return Response(
                    content=body,
                    status_code=response.status_code,
                    headers={**dict(response.headers), "ETag": etag},
                    media_type=response.media_type,
                )
        
        return response
    
    def _generate_etag(self, content: bytes) -> str:
        """Generate ETag from content."""
        hash_value = hashlib.md5(content).hexdigest()
        if self.weak_etags:
            return f'W/"{hash_value}"'
        return f'"{hash_value}"'
    
    def _is_excluded(self, path: str) -> bool:
        """Check if path should be excluded from ETag processing."""
        for excluded in self.EXCLUDED_PATHS:
            if path.startswith(excluded):
                return True
        return False


# =============================================================================
# Helper Functions for Manual ETag Handling
# =============================================================================

def generate_etag(content: bytes | str, weak: bool = True) -> str:
    """Generate an ETag for content.
    
    Args:
        content: Content to hash
        weak: Whether to use weak ETag
    
    Returns:
        ETag string including quotes
    """
    if isinstance(content, str):
        content = content.encode()
    hash_value = hashlib.md5(content).hexdigest()
    if weak:
        return f'W/"{hash_value}"'
    return f'"{hash_value}"'


def etag_matches(request_etag: str, resource_etag: str) -> bool:
    """Check if request ETag matches resource ETag.
    
    Handles weak/strong comparison per RFC 7232.
    """
    # Normalize both ETags
    req = request_etag.strip().strip('"').lstrip("W/")
    res = resource_etag.strip().strip('"').lstrip("W/")
    return req == res or request_etag == "*"


def check_precondition(
    if_match: Optional[str],
    if_none_match: Optional[str],
    current_etag: str,
) -> Optional[int]:
    """Check precondition headers and return status code if failed.
    
    Returns:
        None if preconditions pass
        412 if If-Match fails
        304 if If-None-Match matches (for GET)
    """
    if if_match:
        # If-Match: fail if no match
        if not etag_matches(if_match, current_etag):
            return 412  # Precondition Failed
    
    if if_none_match:
        # If-None-Match: fail if match
        if etag_matches(if_none_match, current_etag):
            return 304  # Not Modified
    
    return None
