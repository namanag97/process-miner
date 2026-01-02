"""Telemetry Proxy Router - Frontend → Backend → Observability Stack.

Proxies telemetry data from browser (frontend) to backend observability infrastructure.
Avoids CORS issues and provides a central point for frontend telemetry collection.

Endpoints:
- POST /telemetry/traces - OTLP trace data from browser
- POST /telemetry/logs - Browser logs
"""

import json
from typing import Any, Dict
from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from src.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/telemetry", tags=["Telemetry"])


class BrowserTrace(BaseModel):
    """Browser trace data (OTLP format simplified)."""
    resourceSpans: list[Dict[str, Any]]


class BrowserLog(BaseModel):
    """Browser log entry."""
    level: str
    message: str
    timestamp: str
    data: Dict[str, Any] | None = None
    trace_id: str | None = None
    span_id: str | None = None


@router.post("/traces")
async def proxy_traces(request: Request):
    """Proxy OpenTelemetry traces from frontend to DevConsole.

    Accepts OTLP/HTTP JSON format from browser OpenTelemetry SDK.
    In dev mode, sends to DevConsole for real-time visualization.
    In production, would forward to Tempo/Jaeger.
    """
    try:
        # Read raw OTLP data
        body = await request.body()
        otlp_data = json.loads(body)

        # In debug mode, send to DevConsole
        from src.core.config import get_settings
        settings = get_settings()

        if settings.debug:
            # Extract spans and send to DevConsole
            _process_otlp_for_devconsole(otlp_data)

        # TODO: In production, forward to Tempo via OTLP exporter
        # if settings.tempo_otlp_endpoint:
        #     await _forward_to_tempo(otlp_data)

        return Response(status_code=200)

    except Exception as e:
        logger.error("telemetry_proxy_error", error=str(e), exc_info=True)
        return Response(status_code=500, content=str(e))


@router.post("/logs")
async def proxy_logs(log: BrowserLog):
    """Proxy browser logs to backend logging infrastructure.

    In dev mode, sends to DevConsole.
    In production, would send to Loki.
    """
    try:
        from src.core.config import get_settings
        from src.api.routers.dev_logs_stream import devConsoleLog, LogLevel

        settings = get_settings()

        if settings.debug:
            # Map browser log levels to DevConsole levels
            level_map = {
                "debug": LogLevel.INFO,
                "info": LogLevel.INFO,
                "warn": LogLevel.ACTION,
                "error": LogLevel.ERROR,
            }

            devConsoleLog(
                level=level_map.get(log.level.lower(), LogLevel.INFO),
                source=f"FE Browser",
                message=log.message,
                data=log.data,
                extra={
                    "trace_id": log.trace_id,
                    "span_id": log.span_id,
                },
            )

        # TODO: In production, forward to Loki
        # if settings.loki_url:
        #     await _forward_to_loki(log)

        return {"status": "ok"}

    except Exception as e:
        logger.error("log_proxy_error", error=str(e), exc_info=True)
        return {"status": "error", "error": str(e)}


def _process_otlp_for_devconsole(otlp_data: Dict[str, Any]) -> None:
    """Extract spans from OTLP data and send to DevConsole."""
    try:
        from src.api.routers.dev_logs_stream import log_trace_span, TraceSpan
        from datetime import datetime

        # OTLP format: resourceSpans[] -> scopeSpans[] -> spans[]
        for resource_span in otlp_data.get("resourceSpans", []):
            for scope_span in resource_span.get("scopeSpans", []):
                for span_data in scope_span.get("spans", []):
                    # Convert OTLP span to our TraceSpan model
                    trace_id = span_data.get("traceId", "")
                    span_id = span_data.get("spanId", "")
                    parent_span_id = span_data.get("parentSpanId")

                    # Convert nanoseconds timestamps to ISO
                    start_ns = int(span_data.get("startTimeUnixNano", 0))
                    end_ns = int(span_data.get("endTimeUnixNano", 0))

                    start_time = datetime.utcfromtimestamp(start_ns / 1e9).isoformat() + "Z"
                    end_time = datetime.utcfromtimestamp(end_ns / 1e9).isoformat() + "Z"
                    duration_ms = (end_ns - start_ns) / 1e6

                    # Extract attributes
                    attributes = {}
                    for attr in span_data.get("attributes", []):
                        key = attr.get("key", "")
                        value = attr.get("value", {})
                        # Handle different value types
                        if "stringValue" in value:
                            attributes[key] = value["stringValue"]
                        elif "intValue" in value:
                            attributes[key] = int(value["intValue"])
                        elif "doubleValue" in value:
                            attributes[key] = float(value["doubleValue"])
                        elif "boolValue" in value:
                            attributes[key] = value["boolValue"]

                    # Map span kind
                    kind_map = {
                        0: "UNSPECIFIED",
                        1: "INTERNAL",
                        2: "SERVER",
                        3: "CLIENT",
                        4: "PRODUCER",
                        5: "CONSUMER",
                    }
                    kind = kind_map.get(span_data.get("kind", 0), "INTERNAL")

                    # Map status
                    status_code = span_data.get("status", {}).get("code", 0)
                    status = "OK" if status_code == 1 else "ERROR" if status_code == 2 else "UNSET"

                    # Extract events
                    events = []
                    for event_data in span_data.get("events", []):
                        event_ts = int(event_data.get("timeUnixNano", 0))
                        event = {
                            "name": event_data.get("name", ""),
                            "timestamp": datetime.utcfromtimestamp(event_ts / 1e9).isoformat() + "Z",
                            "attributes": {},
                        }
                        events.append(event)

                    # Create and log trace span
                    trace_span = TraceSpan(
                        trace_id=trace_id,
                        span_id=span_id,
                        parent_span_id=parent_span_id,
                        name=span_data.get("name", "unknown"),
                        kind=kind,
                        start_time=start_time,
                        end_time=end_time,
                        duration_ms=duration_ms,
                        status=status,
                        attributes=attributes,
                        events=events,
                        links=[],
                    )

                    log_trace_span(trace_span)

    except Exception as e:
        logger.error("otlp_processing_error", error=str(e), exc_info=True)
