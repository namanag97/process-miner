"""
Celery Application Configuration

This module configures Celery for background task processing.
Tasks are defined in the `tasks/` directory.
"""

from celery import Celery
from .config import get_settings

settings = get_settings()

# Create Celery app
celery_app = Celery(
    "process_miner",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.mining_tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution
    task_acks_late=True,  # Acknowledge after task completes (safer)
    task_reject_on_worker_lost=True,
    
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Process one task at a time (for CPU-intensive mining)
    worker_concurrency=2,  # Number of concurrent workers
    
    # Task tracking
    task_track_started=True,
    task_send_sent_event=True,
)

# Optional: Configure task routes for different queues
celery_app.conf.task_routes = {
    "app.tasks.mining_tasks.*": {"queue": "mining"},
}
