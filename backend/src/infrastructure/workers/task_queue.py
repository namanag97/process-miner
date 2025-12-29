"""Background task queue (mock RabbitMQ)."""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Optional
from uuid import UUID, uuid4

from src.application.ports import TaskQueuePort

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Job execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    """Background job definition."""

    id: UUID
    job_type: str
    payload: Dict[str, Any]
    status: JobStatus = JobStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "job_type": self.job_type,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class BackgroundTaskQueue(TaskQueuePort):
    """
    In-memory background task queue.
    Simulates RabbitMQ-like behavior for local development.
    """

    def __init__(self, max_workers: int = 4):
        self._handlers: Dict[str, Callable] = {}
        self._jobs: Dict[UUID, Job] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None

    def register_handler(self, job_type: str, handler: Callable) -> None:
        """Register a handler for a job type."""
        self._handlers[job_type] = handler
        logger.info(f"Handler registered for job type: {job_type}")

    async def enqueue(self, job_type: str, payload: Dict[str, Any]) -> UUID:
        """Add a job to the queue."""
        job = Job(
            id=uuid4(),
            job_type=job_type,
            payload=payload,
        )
        self._jobs[job.id] = job
        await self._queue.put(job)
        logger.info(f"Job enqueued: {job.id} ({job_type})")
        return job.id

    def get_job(self, job_id: UUID) -> Optional[Job]:
        """Get job status by ID."""
        return self._jobs.get(job_id)

    async def start(self) -> None:
        """Start the background worker."""
        if self._running:
            return

        self._running = True
        self._worker_task = asyncio.create_task(self._worker_loop())
        logger.info("Background task queue started")

    async def stop(self) -> None:
        """Stop the background worker."""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        self._executor.shutdown(wait=True)
        logger.info("Background task queue stopped")

    async def _worker_loop(self) -> None:
        """Main worker loop."""
        while self._running:
            try:
                job = await asyncio.wait_for(self._queue.get(), timeout=1.0)
                await self._process_job(job)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")

    async def _process_job(self, job: Job) -> None:
        """Process a single job."""
        handler = self._handlers.get(job.job_type)
        if not handler:
            job.status = JobStatus.FAILED
            job.error = f"No handler for job type: {job.job_type}"
            job.completed_at = datetime.utcnow()
            logger.error(job.error)
            return

        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()

        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(job.payload)
            else:
                # Run sync handler in thread pool
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(self._executor, handler, job.payload)

            job.status = JobStatus.COMPLETED
            job.result = result
            logger.info(f"Job completed: {job.id}")
        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = str(e)
            logger.error(f"Job failed: {job.id} - {e}")
        finally:
            job.completed_at = datetime.utcnow()


# Singleton instance
task_queue = BackgroundTaskQueue()


async def enqueue_job(job_type: str, payload: Dict[str, Any]) -> UUID:
    """Convenience function to enqueue a job."""
    return await task_queue.enqueue(job_type, payload)


def get_job_status(job_id: UUID) -> Optional[Job]:
    """Convenience function to get job status."""
    return task_queue.get_job(job_id)
