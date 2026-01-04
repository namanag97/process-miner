"""Logging and observability middleware for FastAPI."""

import time
import uuid
from collections.abc import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from src.core.logging_config import bind_context, clear_context, get_logger

logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that logs all HTTP requests with timing and context.

    Features:
    - Generates or captures request_id from X-Request-ID header
    - Binds request context to all logs within the request
    - Logs request start and completion with timing
    - Adds request_id to response headers
    - Streams logs to frontend DevConsole in dev mode
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or get request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Bind context for all logs in this request
        bind_context(
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        # Log request start
        logger.info(
            "request_started",
            query_string=str(request.query_params) if request.query_params else None,
        )

        # Filter: Don't log observability endpoints to avoid feedback loop
        should_log_to_devconsole = not request.url.path.startswith(
            (
                "/api/v1/dev/log",  # DevConsole log ingestion
                "/metrics",  # Prometheus metrics
                "/health",  # Health checks
            )
        )

        # Stream to frontend DevConsole (dev mode only)
        if should_log_to_devconsole:
            try:
                from src.api.routers.dev_logs_stream import log_api_request

                log_api_request(request.method, request.url.path, request_id)
            except ImportError:
                pass

        # Process request with timing
        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - start_time) * 1000

            # Log request completion
            logger.info(
                "request_completed",
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
            )

            # Stream to frontend DevConsole (dev mode only, filtered)
            if should_log_to_devconsole:
                try:
                    from src.api.routers.dev_logs_stream import log_api_response

                    log_api_response(
                        request.method,
                        request.url.path,
                        response.status_code,
                        int(duration_ms),
                        request_id,
                    )
                except ImportError:
                    pass

            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.error(
                "request_failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_ms=round(duration_ms, 2),
            )

            # Stream error to frontend DevConsole
            try:
                from src.api.routers.dev_logs_stream import log_error

                log_error(
                    request.url.path,
                    str(e),
                    details={"error_type": type(e).__name__},
                )
            except ImportError:
                pass

            raise

        finally:
            # Clear context at end of request
            clear_context()


class PerformanceLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware that warns on slow requests.

    Logs a warning if request takes longer than threshold.
    Default threshold: 1 second.
    """

    def __init__(self, app, slow_request_threshold_ms: float = 1000):
        super().__init__(app)
        self.slow_request_threshold_ms = slow_request_threshold_ms

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.perf_counter()
        response = await call_next(request)
        duration_ms = (time.perf_counter() - start_time) * 1000

        if duration_ms > self.slow_request_threshold_ms:
            logger.warning(
                "slow_request",
                path=request.url.path,
                method=request.method,
                duration_ms=round(duration_ms, 2),
                threshold_ms=self.slow_request_threshold_ms,
            )

        return response
