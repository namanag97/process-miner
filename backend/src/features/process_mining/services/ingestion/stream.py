"""SSE Event Stream Manager.

Job-Centric Architecture: Provides Server-Sent Events (SSE) for real-time
job progress updates using Redis pub/sub.

Usage:
    from src.features.process_mining.services.ingestion.stream import event_stream_manager

    # In Celery task:
    await event_stream_manager.publish_progress(user_id, job_id, progress, stage)

    # In API router:
    async def stream_events():
        async for event in event_stream_manager.subscribe(user_id, job_id):
            yield event
"""

import json
from collections.abc import AsyncGenerator
from datetime import datetime
from enum import Enum

from src.infra.core.config import get_settings
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()


class EventType(str, Enum):
    """SSE event types for job tracking."""

    JOB_CREATED = "job:created"
    JOB_STARTED = "job:started"
    JOB_PROGRESS = "job:progress"
    JOB_COMPLETED = "job:completed"
    JOB_FAILED = "job:failed"
    JOB_CANCELLED = "job:cancelled"
    DATASET_STATUS_CHANGED = "dataset:status_changed"
    ENTITY_CREATED = "entity:created"


class SSEEvent:
    """Server-Sent Event structure."""

    def __init__(
        self,
        event_type: EventType,
        data: dict,
        event_id: str | None = None,
    ):
        self.event_type = event_type
        self.data = data
        self.event_id = event_id or datetime.utcnow().isoformat()

    def to_sse_format(self) -> str:
        """Format as SSE wire protocol."""
        lines = []
        if self.event_id:
            lines.append(f"id: {self.event_id}")
        lines.append(f"event: {self.event_type.value}")
        lines.append(f"data: {json.dumps(self.data)}")
        lines.append("")  # Empty line to end event
        return "\n".join(lines) + "\n"


class EventStreamManager:
    """Manages SSE event publishing and subscription via Redis pub/sub."""

    def __init__(self):
        self._redis = None
        self._pubsub = None

    async def _get_redis(self):
        """Lazy-load Redis connection."""
        if self._redis is None:
            try:
                import redis.asyncio as redis

                self._redis = redis.from_url(
                    settings.redis_url,
                    encoding="utf-8",
                    decode_responses=True,
                )
                logger.info("event_stream_redis_connected")
            except Exception as e:
                logger.warning("event_stream_redis_unavailable", error=str(e))
                self._redis = None
        return self._redis

    def _channel_name(self, user_id: str, job_id: str | None = None) -> str:
        """Build Redis channel name."""
        if job_id:
            return f"events:{user_id}:job:{job_id}"
        return f"events:{user_id}"

    async def publish_event(
        self,
        user_id: str,
        job_id: str,
        event_type: EventType,
        data: dict,
    ) -> bool:
        """Publish an event to Redis pub/sub.

        Args:
            user_id: User to notify
            job_id: Job ID
            event_type: Type of event
            data: Event payload

        Returns:
            True if published, False if Redis unavailable
        """
        redis = await self._get_redis()
        if not redis:
            return False

        try:
            event = SSEEvent(
                event_type,
                {
                    "job_id": job_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    **data,
                },
            )

            # Publish to both user channel and job-specific channel
            await redis.publish(self._channel_name(user_id), event.to_sse_format())
            await redis.publish(self._channel_name(user_id, job_id), event.to_sse_format())

            logger.debug(
                "event_published",
                user_id=user_id,
                job_id=job_id,
                event_type=event_type.value,
            )
            return True

        except Exception as e:
            logger.warning("event_publish_failed", error=str(e))
            return False

    async def publish_progress(
        self,
        user_id: str,
        job_id: str,
        progress: int,
        stage: str,
    ) -> bool:
        """Convenience method to publish progress update."""
        return await self.publish_event(
            user_id=user_id,
            job_id=job_id,
            event_type=EventType.JOB_PROGRESS,
            data={"progress": progress, "stage": stage},
        )

    async def publish_completed(
        self,
        user_id: str,
        job_id: str,
        entity_id: str | None = None,
        result: dict | None = None,
    ) -> bool:
        """Convenience method to publish job completion."""
        return await self.publish_event(
            user_id=user_id,
            job_id=job_id,
            event_type=EventType.JOB_COMPLETED,
            data={"entity_id": entity_id, "result": result or {}},
        )

    async def publish_failed(
        self,
        user_id: str,
        job_id: str,
        error: str,
    ) -> bool:
        """Convenience method to publish job failure."""
        return await self.publish_event(
            user_id=user_id,
            job_id=job_id,
            event_type=EventType.JOB_FAILED,
            data={"error": error},
        )

    async def subscribe(
        self,
        user_id: str,
        job_id: str | None = None,
    ) -> AsyncGenerator[str, None]:
        """Subscribe to events for a user or specific job.

        Yields SSE-formatted strings for streaming to client.

        Args:
            user_id: User ID to subscribe to
            job_id: Optional job ID for job-specific events

        Yields:
            SSE-formatted event strings
        """
        redis = await self._get_redis()
        if not redis:
            # Fallback: yield heartbeat and return
            yield ": heartbeat\n\n"
            return

        channel = self._channel_name(user_id, job_id)

        try:
            pubsub = redis.pubsub()
            await pubsub.subscribe(channel)
            logger.info("event_stream_subscribed", channel=channel)

            async for message in pubsub.listen():
                if message["type"] == "message":
                    yield message["data"]

        except Exception as e:
            logger.warning("event_stream_error", error=str(e))
        finally:
            if pubsub:
                await pubsub.unsubscribe(channel)
                await pubsub.close()


# Global singleton instance
event_stream_manager = EventStreamManager()
