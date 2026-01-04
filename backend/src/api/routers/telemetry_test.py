"""Telemetry Test Router - Verify traces are working."""

from fastapi import APIRouter

from src.core.logging_config import get_logger
from src.infrastructure.tracing import create_span

logger = get_logger(__name__)
router = APIRouter(prefix="/test-telemetry", tags=["Test"])


@router.get("/trace")
async def test_trace():
    """Test endpoint that creates a trace span."""
    logger.info("test_trace_called", message="Testing trace generation")

    # Create a custom span
    with create_span("test_operation", {"test_attribute": "test_value"}) as span:
        if span:
            span.set_attribute("custom.data", "This is a test trace")
            span.add_event("test_event", {"event_data": "test"})

    return {
        "status": "ok",
        "message": "Trace generated! Check DevConsole for: 🌐 GET /api/v1/test-telemetry/trace and ⚙️ test_operation",
    }
