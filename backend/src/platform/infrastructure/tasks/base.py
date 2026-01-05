"""Celery Task Infrastructure.

Shared base classes, configuration, and utilities for all Celery tasks.
"""

import asyncio
from typing import Any

import structlog
from celery import Celery, Task
from celery.result import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.platform.core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()

# =============================================================================
# Celery App Configuration
# =============================================================================

celery_app = Celery(
    "process_mining",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,  # One task at a time
    task_acks_late=True,  # Acknowledge after completion
    task_reject_on_worker_lost=True,
)


# =============================================================================
# Async Database Session for Tasks
# =============================================================================

async_engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# =============================================================================
# Base Task Classes
# =============================================================================


class AsyncTask(Task):
    """Base task class with async support."""

    def __call__(self, *args, **kwargs):
        """Run async function in event loop."""
        # Celery binds the decorated async function to self.run
        return asyncio.run(self.run(*args, **kwargs))

    async def run(self, *args, **kwargs):
        """Standard Celery method, implementing classes should override."""
        raise NotImplementedError


# =============================================================================
# Task Status Utilities
# =============================================================================


def get_task_status(task_id: str) -> dict[str, Any]:
    """Get status of a Celery task.

    Args:
        task_id: Celery task ID

    Returns:
        dict with status, result, and progress info
    """
    task_result = AsyncResult(task_id, app=celery_app)

    result = {
        "task_id": task_id,
        "status": task_result.state,
        "ready": task_result.ready(),
        "successful": task_result.successful() if task_result.ready() else None,
    }

    if task_result.state == "PROGRESS":
        result["progress"] = task_result.info
    elif task_result.ready():
        if task_result.successful():
            result["result"] = task_result.result
        else:
            result["error"] = str(task_result.info)

    return result
