"""DevConsole OpenTelemetry Span Exporter.

Exports OpenTelemetry spans to the DevConsole real-time stream for
in-browser trace visualization during development.
"""

from typing import Sequence
from datetime import datetime

try:
    from opentelemetry.sdk.trace import ReadableSpan
    from opentelemetry.sdk.trace.export import SpanExporter, SpanExportResult
    from opentelemetry.trace import SpanKind, StatusCode
    OTEL_AVAILABLE = True
except ImportError:
    OTEL_AVAILABLE = False
    ReadableSpan = None  # type: ignore
    SpanExporter = object  # type: ignore
    SpanExportResult = None  # type: ignore


class DevConsoleSpanExporter(SpanExporter):
    """Export spans to DevConsole SSE stream for real-time visualization."""

    def __init__(self):
        """Initialize the DevConsole exporter."""
        self._shutdown = False

    def export(self, spans: Sequence[ReadableSpan]) -> SpanExportResult:
        """Export spans to DevConsole."""
        if self._shutdown:
            return SpanExportResult.FAILURE

        print(f"[DevConsoleExporter] Exporting {len(spans)} spans")  # DEBUG

        try:
            from src.api.routers.dev_logs_stream import log_trace_span, TraceSpan

            for span in spans:
                # Convert span kind
                kind_map = {
                    SpanKind.INTERNAL: "INTERNAL",
                    SpanKind.SERVER: "SERVER",
                    SpanKind.CLIENT: "CLIENT",
                    SpanKind.PRODUCER: "PRODUCER",
                    SpanKind.CONSUMER: "CONSUMER",
                }

                # Convert status
                status_map = {
                    StatusCode.UNSET: "UNSET",
                    StatusCode.OK: "OK",
                    StatusCode.ERROR: "ERROR",
                }

                # Extract span context
                context = span.get_span_context()
                trace_id = format(context.trace_id, "032x") if context.trace_id else "unknown"
                span_id = format(context.span_id, "016x") if context.span_id else "unknown"

                # Get parent span ID
                parent_id = None
                if span.parent:
                    parent_id = format(span.parent.span_id, "016x")

                # Convert timestamps
                start_time = datetime.utcfromtimestamp(span.start_time / 1e9).isoformat() + "Z"
                end_time = datetime.utcfromtimestamp(span.end_time / 1e9).isoformat() + "Z"
                duration_ms = (span.end_time - span.start_time) / 1e6  # ns to ms

                # Extract attributes (convert to JSON-safe types)
                attributes = {}
                if span.attributes:
                    for key, value in span.attributes.items():
                        # Convert to JSON-safe types
                        if isinstance(value, (str, int, float, bool)):
                            attributes[key] = value
                        else:
                            attributes[key] = str(value)

                # Extract events
                events = []
                if span.events:
                    for event in span.events:
                        event_data = {
                            "name": event.name,
                            "timestamp": datetime.utcfromtimestamp(event.timestamp / 1e9).isoformat() + "Z",
                            "attributes": {k: v for k, v in (event.attributes or {}).items()},
                        }
                        events.append(event_data)

                # Extract links
                links = []
                if span.links:
                    for link in span.links:
                        link_context = link.context
                        link_data = {
                            "trace_id": format(link_context.trace_id, "032x"),
                            "span_id": format(link_context.span_id, "016x"),
                            "attributes": {k: v for k, v in (link.attributes or {}).items()},
                        }
                        links.append(link_data)

                # Create TraceSpan model
                trace_span = TraceSpan(
                    trace_id=trace_id,
                    span_id=span_id,
                    parent_span_id=parent_id,
                    name=span.name,
                    kind=kind_map.get(span.kind, "INTERNAL"),
                    start_time=start_time,
                    end_time=end_time,
                    duration_ms=duration_ms,
                    status=status_map.get(span.status.status_code, "UNSET"),
                    attributes=attributes,
                    events=events,
                    links=links,
                )

                # Send to DevConsole
                print(f"[DevConsoleExporter] Logging span: {trace_span.name}")  # DEBUG
                log_trace_span(trace_span)

            print(f"[DevConsoleExporter] Export complete")  # DEBUG
            return SpanExportResult.SUCCESS

        except Exception as e:
            # Don't fail the application if DevConsole export fails
            print(f"[DevConsoleExporter] Export failed: {e}")  # DEBUG
            import traceback
            traceback.print_exc()
            return SpanExportResult.FAILURE

    def shutdown(self) -> None:
        """Shutdown the exporter."""
        self._shutdown = True

    def force_flush(self, timeout_millis: int = 30000) -> bool:
        """Force flush any pending spans."""
        return True
