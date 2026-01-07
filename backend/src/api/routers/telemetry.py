"""Telemetry Router.

Handles OpenTelemetry traces and other observability data from the frontend.
"""

from typing import Any

from fastapi import APIRouter, Request, Response, status
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/telemetry", tags=["Observability"])


@router.post("/traces", status_code=status.HTTP_202_ACCEPTED)
async def receive_traces(request: Request) -> Response:
    """Receive and process traces from the frontend.
    
    This endpoint currently accepts traces and logs their presence.
    In a full implementation, this might forward them to an OTLP collector.
    """
    try:
        # We don't necessarily need to parse the body if we just want to suppress 404s
        # and log that telemetry is being sent.
        body = await request.json()
        logger.debug(
            "received_frontend_traces",
            count=len(body.get("resourceSpans", [])) if isinstance(body, dict) else 0,
        )
    except Exception as e:
        logger.warning("failed_to_parse_telemetry_body", error=str(e))
    
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.get("/status")
async def get_telemetry_status() -> dict[str, Any]:
    """Check telemetry ingestion status."""
    return {"status": "active", "provider": "internal"}
