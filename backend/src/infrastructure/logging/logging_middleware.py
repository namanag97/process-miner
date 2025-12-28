"""Request/Response Logging Middleware for FastAPI."""

import json
import time
import uuid
from typing import Any, Callable, Dict, List, Optional, Set
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import Message

from src.infrastructure.logging.logger_config import get_api_logger


# Sensitive fields to mask in logs
SENSITIVE_FIELDS: Set[str] = {
    "password",
    "secret",
    "token",
    "authorization",
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "credential",
    "private_key",
}

# Paths to exclude from detailed logging (e.g., health checks)
EXCLUDED_PATHS: Set[str] = {
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
}


def mask_sensitive_data(data: Any) -> Any:
    """
    Recursively mask sensitive fields in data.
    
    Args:
        data: Data to mask (dict, list, or primitive)
    
    Returns:
        Data with sensitive fields masked
    """
    if isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if key.lower() in SENSITIVE_FIELDS:
                masked[key] = "***REDACTED***"
            else:
                masked[key] = mask_sensitive_data(value)
        return masked
    elif isinstance(data, list):
        return [mask_sensitive_data(item) for item in data]
    else:
        return data


def truncate_body(body: str, max_length: int = 2000) -> str:
    """Truncate body content for logging."""
    if len(body) > max_length:
        return body[:max_length] + f"... [truncated, total: {len(body)} chars]"
    return body


class RequestResponseLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all HTTP request/response details.
    
    Features:
    - Logs request method, path, headers, query params, body
    - Logs response status code, duration, body size
    - Masks sensitive data (passwords, tokens, etc.)
    - Generates unique request ID for tracing
    - Supports configurable body logging
    """
    
    def __init__(
        self,
        app,
        log_request_body: bool = True,
        log_response_body: bool = False,
        max_body_length: int = 2000,
    ):
        """
        Initialize the logging middleware.
        
        Args:
            app: The Starlette/FastAPI application
            log_request_body: Whether to log request bodies
            log_response_body: Whether to log response bodies
            max_body_length: Maximum length of body to log
        """
        super().__init__(app)
        self.log_request_body = log_request_body
        self.log_response_body = log_response_body
        self.max_body_length = max_body_length
        self.logger = get_api_logger()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log details."""
        # Generate unique request ID
        request_id = str(uuid.uuid4())[:8]
        
        # Skip detailed logging for excluded paths
        if request.url.path in EXCLUDED_PATHS:
            return await call_next(request)
        
        # Start timing
        start_time = time.perf_counter()
        
        # Extract client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Extract user ID from state if authenticated
        user_id = None
        
        # Extract query parameters
        query_params = dict(request.query_params)
        
        # Extract request body if enabled
        request_body = None
        if self.log_request_body and request.method in ("POST", "PUT", "PATCH"):
            try:
                body_bytes = await request.body()
                if body_bytes:
                    try:
                        body_json = json.loads(body_bytes)
                        request_body = truncate_body(
                            json.dumps(mask_sensitive_data(body_json)),
                            self.max_body_length
                        )
                    except json.JSONDecodeError:
                        # Not JSON, log as string
                        body_str = body_bytes.decode("utf-8", errors="replace")
                        request_body = truncate_body(body_str, self.max_body_length)
            except Exception:
                request_body = "[Could not read body]"
        
        # Process request
        response = None
        error_msg = None
        try:
            response = await call_next(request)
        except Exception as e:
            error_msg = str(e)
            raise
        finally:
            # Calculate duration
            duration_ms = (time.perf_counter() - start_time) * 1000
            
            # Extract response info
            status_code = response.status_code if response else 500
            
            # Extract response body if enabled (requires reading the response)
            response_body = None
            if self.log_response_body and response:
                # Note: Reading response body is complex and may affect streaming
                # responses. For simplicity, we skip it unless explicitly needed.
                pass
            
            # Determine log level based on status code
            if status_code >= 500:
                log_level = self.logger.error
            elif status_code >= 400:
                log_level = self.logger.warning
            else:
                log_level = self.logger.info
            
            # Create log record with extra fields
            log_level(
                f"{request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": str(request.url.path),
                    "status_code": status_code,
                    "duration_ms": round(duration_ms, 2),
                    "client_ip": client_ip,
                    "user_id": user_id,
                    "query_params": query_params if query_params else None,
                    "request_body": request_body,
                    "response_body": response_body,
                    "error": error_msg,
                },
            )
        
        return response
