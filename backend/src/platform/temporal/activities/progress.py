"""Activity Progress Publisher.

Utility for publishing real-time progress updates from Temporal activities
to Redis pub/sub for SSE streaming to frontend clients.

Usage in activities:
    from src.platform.temporal.activities.progress import publish_progress

    @activity.defn
    async def my_activity(input: MyInput) -> MyResult:
        await publish_progress(
            workflow_id=f"ingest-dataset-{input.dataset_id}",
            step="parsing",
            progress=50,
            details={"rows_processed": 1000},
        )
        # ... do work ...

The frontend can subscribe to real-time updates via:
    GET /api/v1/operations/{workflow_id}/stream
"""

import json
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from src.platform.core.config import get_settings
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ProgressEventType(str, Enum):
    """Event types for workflow progress."""

    STEP_STARTED = "step:started"
    STEP_PROGRESS = "step:progress"
    STEP_COMPLETED = "step:completed"
    STEP_FAILED = "step:failed"
    WORKFLOW_PROGRESS = "workflow:progress"
    WORKFLOW_COMPLETED = "workflow:completed"
    WORKFLOW_FAILED = "workflow:failed"


class ActivityProgressPublisher:
    """Publishes activity progress to Redis for real-time streaming."""

    def __init__(self):
        self._redis = None

    async def _get_redis(self):
        """Lazy-load async Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as redis

                self._redis = redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                logger.debug("activity_progress_redis_connected")
            except Exception as e:
                logger.warning("activity_progress_redis_unavailable", error=str(e))
                self._redis = None
        return self._redis

    def _channel_name(self, workflow_id: str) -> str:
        """Build Redis channel name for a workflow."""
        return f"workflow:progress:{workflow_id}"

    async def publish(
        self,
        workflow_id: str,
        event_type: ProgressEventType,
        step: str,
        progress: int,
        details: dict[str, Any] | None = None,
    ) -> bool:
        """Publish a progress event to Redis.

        Args:
            workflow_id: The Temporal workflow ID
            event_type: Type of progress event
            step: Current step/activity name
            progress: Progress percentage (0-100)
            details: Additional event details

        Returns:
            True if published successfully, False otherwise
        """
        redis = await self._get_redis()
        if not redis:
            return False

        try:
            event_data = {
                "workflow_id": workflow_id,
                "event": event_type.value,
                "step": step,
                "progress": progress,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": details or {},
            }

            # Format as SSE
            sse_message = f"event: {event_type.value}\ndata: {json.dumps(event_data)}\n\n"

            # Publish to workflow-specific channel
            channel = self._channel_name(workflow_id)
            await redis.publish(channel, sse_message)

            # Also publish to a global channel for monitoring dashboards
            await redis.publish("workflow:progress:all", sse_message)

            logger.debug(
                "activity_progress_published",
                workflow_id=workflow_id,
                event_type=event_type.value,
                step=step,
                progress=progress,
            )
            return True

        except Exception as e:
            logger.warning("activity_progress_publish_failed", error=str(e))
            return False

    async def step_started(
        self,
        workflow_id: str,
        step: str,
        progress: int = 0,
        details: dict[str, Any] | None = None,
    ) -> bool:
        """Publish a step started event."""
        return await self.publish(
            workflow_id=workflow_id,
            event_type=ProgressEventType.STEP_STARTED,
            step=step,
            progress=progress,
            details=details,
        )

    async def step_progress(
        self,
        workflow_id: str,
        step: str,
        progress: int,
        details: dict[str, Any] | None = None,
    ) -> bool:
        """Publish a step progress update."""
        return await self.publish(
            workflow_id=workflow_id,
            event_type=ProgressEventType.STEP_PROGRESS,
            step=step,
            progress=progress,
            details=details,
        )

    async def step_completed(
        self,
        workflow_id: str,
        step: str,
        progress: int = 100,
        details: dict[str, Any] | None = None,
    ) -> bool:
        """Publish a step completed event."""
        return await self.publish(
            workflow_id=workflow_id,
            event_type=ProgressEventType.STEP_COMPLETED,
            step=step,
            progress=progress,
            details=details,
        )

    async def step_failed(
        self,
        workflow_id: str,
        step: str,
        error: str,
        details: dict[str, Any] | None = None,
    ) -> bool:
        """Publish a step failed event."""
        return await self.publish(
            workflow_id=workflow_id,
            event_type=ProgressEventType.STEP_FAILED,
            step=step,
            progress=0,
            details={"error": error, **(details or {})},
        )

    async def workflow_completed(
        self,
        workflow_id: str,
        result: dict[str, Any] | None = None,
    ) -> bool:
        """Publish workflow completed event."""
        return await self.publish(
            workflow_id=workflow_id,
            event_type=ProgressEventType.WORKFLOW_COMPLETED,
            step="completed",
            progress=100,
            details={"result": result or {}},
        )

    async def workflow_failed(
        self,
        workflow_id: str,
        error: str,
        step: str = "unknown",
    ) -> bool:
        """Publish workflow failed event."""
        return await self.publish(
            workflow_id=workflow_id,
            event_type=ProgressEventType.WORKFLOW_FAILED,
            step=step,
            progress=0,
            details={"error": error},
        )


# Global singleton instance
_publisher: ActivityProgressPublisher | None = None


def get_progress_publisher() -> ActivityProgressPublisher:
    """Get the global progress publisher instance."""
    global _publisher
    if _publisher is None:
        _publisher = ActivityProgressPublisher()
    return _publisher


# Convenience functions for direct use in activities
async def publish_progress(
    workflow_id: str,
    step: str,
    progress: int,
    details: dict[str, Any] | None = None,
) -> bool:
    """Publish progress from an activity.

    This is the main function to call from activities.

    Args:
        workflow_id: The workflow ID (e.g., "ingest-dataset-{uuid}")
        step: Current step name (e.g., "parsing", "validating")
        progress: Progress percentage 0-100
        details: Optional additional details

    Returns:
        True if published, False if Redis unavailable

    Example:
        @activity.defn
        async def parse_to_parquet_activity(input: ParseInput) -> ParseResult:
            workflow_id = f"ingest-dataset-{input.dataset_id}"

            await publish_progress(workflow_id, "parsing", 0, {"status": "starting"})

            for i, chunk in enumerate(chunks):
                activity.heartbeat(f"chunk_{i}")
                process_chunk(chunk)
                progress = int((i + 1) / len(chunks) * 100)
                await publish_progress(workflow_id, "parsing", progress, {
                    "chunks_processed": i + 1,
                    "total_chunks": len(chunks),
                })

            return result
    """
    publisher = get_progress_publisher()
    return await publisher.step_progress(workflow_id, step, progress, details)


async def publish_step_started(
    workflow_id: str,
    step: str,
    details: dict[str, Any] | None = None,
) -> bool:
    """Publish that a step has started."""
    publisher = get_progress_publisher()
    return await publisher.step_started(workflow_id, step, 0, details)


async def publish_step_completed(
    workflow_id: str,
    step: str,
    details: dict[str, Any] | None = None,
) -> bool:
    """Publish that a step has completed."""
    publisher = get_progress_publisher()
    return await publisher.step_completed(workflow_id, step, 100, details)


async def publish_step_failed(
    workflow_id: str,
    step: str,
    error: str,
) -> bool:
    """Publish that a step has failed."""
    publisher = get_progress_publisher()
    return await publisher.step_failed(workflow_id, step, error)
