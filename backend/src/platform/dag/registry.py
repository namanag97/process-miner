"""DAG Task Registry.

Provides a registry for DAG-compatible task functions and context management.

Components:
- DAGContext: Shared execution context passed to all tasks
- TaskResult: Standardized task return value
- TaskRegistry: Singleton registry for task function lookup
- @dag_task: Decorator for registering task functions
"""

from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, Callable, Awaitable

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class DAGContext:
    """Shared execution context passed to all DAG task nodes.

    Provides common data needed by all steps in a DAG run, including
    identifiers and a shared data dict for inter-step communication.
    """

    run_id: str
    user_id: str | None = None
    dataset_id: str | None = None
    model_id: str | None = None
    shared_data: dict[str, Any] = field(default_factory=dict)
    step_id: str | None = None
    started_at: datetime = field(default_factory=datetime.utcnow)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from shared_data."""
        return self.shared_data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set a value in shared_data for downstream steps."""
        self.shared_data[key] = value


@dataclass
class TaskResult:
    """Standardized return value for DAG task functions.

    All registered task functions should return a TaskResult to ensure
    consistent handling by the DAG executor.
    """

    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    duration_ms: float | None = None

    @classmethod
    def ok(cls, data: dict[str, Any] | None = None, duration_ms: float | None = None) -> "TaskResult":
        """Create a successful result."""
        return cls(success=True, data=data or {}, duration_ms=duration_ms)

    @classmethod
    def fail(cls, error: str, data: dict[str, Any] | None = None) -> "TaskResult":
        """Create a failed result."""
        return cls(success=False, data=data or {}, error=error)


# Type alias for task functions
TaskFunction = Callable[[DAGContext, dict[str, Any]], Awaitable[TaskResult]]


class TaskRegistry:
    """Registry for DAG-compatible task functions.

    Provides registration and lookup of task functions by name.
    Task functions must be async and accept (DAGContext, params) args.

    Example:
        @task_registry.register("validate_file")
        async def validate_file(ctx: DAGContext, params: dict) -> TaskResult:
            ...
    """

    def __init__(self):
        self._tasks: dict[str, TaskFunction] = {}
        self._metadata: dict[str, dict[str, Any]] = {}

    def register(
        self,
        name: str,
        timeout_seconds: int = 3600,
        max_retries: int = 3,
    ) -> Callable[[TaskFunction], TaskFunction]:
        """Decorator to register a task function.

        Args:
            name: Unique task name for registry lookup
            timeout_seconds: Task timeout (default 1 hour)
            max_retries: Maximum retry attempts on failure

        Returns:
            Decorator function
        """
        def decorator(func: TaskFunction) -> TaskFunction:
            if name in self._tasks:
                logger.warning("task_registry_overwrite", task_name=name)

            @wraps(func)
            async def wrapper(ctx: DAGContext, params: dict[str, Any]) -> TaskResult:
                return await func(ctx, params)

            self._tasks[name] = wrapper
            self._metadata[name] = {
                "timeout_seconds": timeout_seconds,
                "max_retries": max_retries,
                "function_name": func.__name__,
                "module": func.__module__,
            }

            logger.debug("task_registered", task_name=name, function=func.__name__)
            return wrapper

        return decorator

    def get(self, name: str) -> TaskFunction | None:
        """Get a registered task function by name."""
        return self._tasks.get(name)

    def get_metadata(self, name: str) -> dict[str, Any] | None:
        """Get metadata for a registered task."""
        return self._metadata.get(name)

    def list_tasks(self) -> list[str]:
        """List all registered task names."""
        return list(self._tasks.keys())

    def is_registered(self, name: str) -> bool:
        """Check if a task is registered."""
        return name in self._tasks

    def clear(self) -> None:
        """Clear all registered tasks (for testing)."""
        self._tasks.clear()
        self._metadata.clear()


# Singleton instance
task_registry = TaskRegistry()


def dag_task(
    name: str,
    timeout_seconds: int = 3600,
    max_retries: int = 3,
) -> Callable[[TaskFunction], TaskFunction]:
    """Convenience decorator for registering DAG tasks.

    Usage:
        @dag_task("validate_file")
        async def validate_file(ctx: DAGContext, params: dict) -> TaskResult:
            ...
    """
    return task_registry.register(name, timeout_seconds, max_retries)
