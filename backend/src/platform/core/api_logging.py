"""API Logging Middleware - Comprehensive request/response logging for MVP debugging.

Provides:
- Auto-generated correlation_id for every request
- Full request body capture (with size limits)
- Response body capture for errors (4xx/5xx)
- Timing and performance metrics
- Integration with DevConsole for frontend correlation
"""

import json
import time
import uuid
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.platform.core.logging_config import bind_context, clear_context, get_logger

logger = get_logger(__name__)

# Maximum request/response body size to capture (bytes)
MAX_BODY_SIZE = 10_000  # 10KB


class APILoggingMiddleware(BaseHTTPMiddleware):
    """Comprehensive API logging middleware for debugging.

    Features:
    - Generates correlation_id for request tracing across frontend/backend
    - Captures request body for debugging (respecting size limits)
    - Captures response body for errors
    - Measures request duration
    - Integrates with structlog context
    """

    def __init__(self, app: ASGIApp, exclude_paths: list[str] | None = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/health/live",
            "/health/ready",
            "/metrics",
            "/openapi.json",
            "/docs",
            "/redoc",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip logging for excluded paths
        if any(request.url.path.startswith(p) for p in self.exclude_paths):
            return await call_next(request)

        # Generate or extract correlation_id
        correlation_id = request.headers.get("X-Correlation-ID") or f"req-{uuid.uuid4().hex[:12]}"
        request_id = request.headers.get("X-Request-ID") or correlation_id

        # Bind context for all logs in this request
        bind_context(
            correlation_id=correlation_id,
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        # Capture request details
        request_body = None
        content_type = request.headers.get("content-type", "")

        # Only capture body for JSON requests (avoid binary files)
        if "application/json" in content_type:
            try:
                body_bytes = await request.body()
                if len(body_bytes) <= MAX_BODY_SIZE:
                    request_body = json.loads(body_bytes) if body_bytes else None
                else:
                    request_body = {"_truncated": True, "size_bytes": len(body_bytes)}
            except Exception:
                request_body = {"_parse_error": True}

        # Log request start
        logger.info(
            "📥 API_REQUEST_START",
            correlation_id=correlation_id,
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params) if request.query_params else None,
            body=_safe_log_body(request_body),
            content_type=content_type,
            user_agent=request.headers.get("user-agent", "")[:100],
        )

        # Process request and measure time
        start_time = time.perf_counter()
        response = None
        error_detail = None

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Capture response body for errors
            response_body = None
            if response.status_code >= 400:
                # Need to read response body for error logging
                response_body = await _capture_response_body(response)

            # Determine log level and emoji based on status
            if response.status_code >= 500:
                log_fn = logger.error
                emoji = "🔥"
                log_level = "ERROR"
            elif response.status_code >= 400:
                log_fn = logger.warning
                emoji = "⚠️"
                log_level = "WARN"
            elif duration_ms > 1000:
                log_fn = logger.warning
                emoji = "🐌"
                log_level = "SLOW"
            else:
                log_fn = logger.info
                emoji = "✅"
                log_level = "OK"

            log_fn(
                f"{emoji} API_REQUEST_COMPLETE",
                correlation_id=correlation_id,
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                log_level=log_level,
                response_body=_safe_log_body(response_body) if response_body else None,
            )

            # Add correlation_id to response headers for frontend
            response.headers["X-Correlation-ID"] = correlation_id
            response.headers["X-Request-Duration-Ms"] = str(round(duration_ms, 2))

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            error_detail = {
                "type": type(e).__name__,
                "message": str(e)[:500],
            }

            logger.error(
                "💥 API_REQUEST_EXCEPTION",
                correlation_id=correlation_id,
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error=error_detail,
                exc_info=True,
            )
            raise

        finally:
            # Clear context after request
            clear_context()


async def _capture_response_body(response: Response) -> dict | None:
    """Capture response body for error responses.

    Note: This requires reading the response body, which means we need
    to recreate the response with the same body.
    """
    try:
        # For StreamingResponse, we can't easily capture the body
        # Only capture for regular responses
        if hasattr(response, "body"):
            body_bytes = response.body
            if len(body_bytes) <= MAX_BODY_SIZE:
                return json.loads(body_bytes)
    except Exception:
        pass
    return None


def _safe_log_body(body: Any) -> Any:
    """Safely prepare body for logging, redacting sensitive fields."""
    if body is None:
        return None

    if isinstance(body, dict):
        # Redact sensitive fields
        sensitive_keys = {
            "password",
            "token",
            "secret",
            "api_key",
            "authorization",
            "access_token",
            "refresh_token",
        }
        return {
            k: "[REDACTED]" if k.lower() in sensitive_keys else _safe_log_body(v)
            for k, v in body.items()
        }

    if isinstance(body, list):
        # Limit array size
        if len(body) > 10:
            return [*body[:10], f"... ({len(body) - 10} more items)"]
        return [_safe_log_body(item) for item in body]

    if isinstance(body, str) and len(body) > 500:
        return body[:500] + "... [truncated]"

    return body


# =============================================================================
# Convenience Decorator for Detailed Operation Logging
# =============================================================================


def log_api_operation(
    operation_name: str,
    *,
    include_args: list[str] | None = None,
    log_result: bool = False,
    log_level: str = "info",
):
    """Enhanced operation logging decorator with more detailed context.

    Use this for critical operations where you want detailed tracing.

    Args:
        operation_name: Name of the operation (e.g., "discover_model")
        include_args: List of argument names to include in logs
        log_result: Whether to include result in success log
        log_level: Default log level (info, debug)

    Example:
        @router.post("/discover")
        @log_api_operation("discover_model", include_args=["dataset_id", "miner_type"])
        async def discover(dataset_id: str, miner_type: str):
            ...
    """
    import asyncio
    from functools import wraps

    def decorator(func):
        op_logger = get_logger(func.__module__)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Build context from specified args
            context = {"operation": operation_name}
            if include_args:
                for arg_name in include_args:
                    if arg_name in kwargs:
                        val = kwargs[arg_name]
                        # Handle Pydantic models
                        if hasattr(val, "model_dump"):
                            context[arg_name] = _safe_log_body(val.model_dump())
                        elif hasattr(val, "dict"):
                            context[arg_name] = _safe_log_body(val.dict())
                        else:
                            context[arg_name] = val

            op_logger.info(f"🚀 {operation_name}_STARTED", **context)
            start_time = time.perf_counter()

            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000

                success_context = {
                    **context,
                    "duration_ms": round(duration_ms, 2),
                    "status": "success",
                }

                if log_result and result is not None:
                    if hasattr(result, "id"):
                        success_context["result_id"] = result.id
                    elif isinstance(result, dict) and "id" in result:
                        success_context["result_id"] = result["id"]

                op_logger.info(f"✅ {operation_name}_COMPLETED", **success_context)
                return result

            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                op_logger.error(
                    f"❌ {operation_name}_FAILED",
                    **context,
                    duration_ms=round(duration_ms, 2),
                    error_type=type(e).__name__,
                    error_message=str(e)[:500],
                    exc_info=True,
                )
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            context = {"operation": operation_name}
            if include_args:
                for arg_name in include_args:
                    if arg_name in kwargs:
                        context[arg_name] = kwargs[arg_name]

            op_logger.info(f"🚀 {operation_name}_STARTED", **context)
            start_time = time.perf_counter()

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start_time) * 1000
                op_logger.info(
                    f"✅ {operation_name}_COMPLETED",
                    **context,
                    duration_ms=round(duration_ms, 2),
                )
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start_time) * 1000
                op_logger.error(
                    f"❌ {operation_name}_FAILED",
                    **context,
                    duration_ms=round(duration_ms, 2),
                    error_type=type(e).__name__,
                    error_message=str(e)[:500],
                    exc_info=True,
                )
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
