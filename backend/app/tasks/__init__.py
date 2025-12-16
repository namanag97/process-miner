"""
Celery Tasks Module

This module exports all Celery tasks for the application.
"""

from .mining_tasks import run_mining_task

__all__ = ["run_mining_task"]
