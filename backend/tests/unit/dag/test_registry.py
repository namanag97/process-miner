"""Unit tests for DAG Task Registry."""

import pytest
from unittest.mock import AsyncMock

from src.platform.dag.registry import (
    DAGContext,
    TaskResult,
    TaskRegistry,
    dag_task,
    task_registry,
)


class TestDAGContext:
    """Tests for DAGContext dataclass."""

    def test_create_context(self):
        """Test basic context creation."""
        ctx = DAGContext(
            run_id="run-123",
            user_id="user-456",
            dataset_id="dataset-789",
        )

        assert ctx.run_id == "run-123"
        assert ctx.user_id == "user-456"
        assert ctx.dataset_id == "dataset-789"
        assert ctx.shared_data == {}

    def test_context_get_set(self):
        """Test shared_data get/set methods."""
        ctx = DAGContext(run_id="run-123")

        ctx.set("key1", "value1")
        ctx.set("key2", {"nested": "data"})

        assert ctx.get("key1") == "value1"
        assert ctx.get("key2") == {"nested": "data"}
        assert ctx.get("missing") is None
        assert ctx.get("missing", "default") == "default"

    def test_context_with_shared_data(self):
        """Test context with pre-populated shared_data."""
        ctx = DAGContext(
            run_id="run-123",
            shared_data={"existing": "value"},
        )

        assert ctx.get("existing") == "value"
        ctx.set("new", "added")
        assert ctx.get("new") == "added"


class TestTaskResult:
    """Tests for TaskResult dataclass."""

    def test_ok_result(self):
        """Test successful result creation."""
        result = TaskResult.ok({"key": "value"}, duration_ms=100.5)

        assert result.success is True
        assert result.data == {"key": "value"}
        assert result.error is None
        assert result.duration_ms == 100.5

    def test_ok_result_empty(self):
        """Test successful result with no data."""
        result = TaskResult.ok()

        assert result.success is True
        assert result.data == {}
        assert result.error is None

    def test_fail_result(self):
        """Test failed result creation."""
        result = TaskResult.fail("Something went wrong")

        assert result.success is False
        assert result.error == "Something went wrong"
        assert result.data == {}

    def test_fail_result_with_data(self):
        """Test failed result with partial data."""
        result = TaskResult.fail("Error", data={"partial": "result"})

        assert result.success is False
        assert result.error == "Error"
        assert result.data == {"partial": "result"}


class TestTaskRegistry:
    """Tests for TaskRegistry."""

    def setup_method(self):
        """Clear registry before each test."""
        self.registry = TaskRegistry()

    def test_register_and_get(self):
        """Test task registration and lookup."""

        @self.registry.register("test_task")
        async def test_task(ctx: DAGContext, params: dict) -> TaskResult:
            return TaskResult.ok({"test": True})

        task = self.registry.get("test_task")
        assert task is not None
        assert callable(task)

    def test_get_nonexistent(self):
        """Test lookup of unregistered task."""
        task = self.registry.get("nonexistent")
        assert task is None

    def test_is_registered(self):
        """Test is_registered check."""

        @self.registry.register("existing_task")
        async def existing_task(ctx: DAGContext, params: dict) -> TaskResult:
            return TaskResult.ok()

        assert self.registry.is_registered("existing_task") is True
        assert self.registry.is_registered("nonexistent") is False

    def test_list_tasks(self):
        """Test listing all registered tasks."""

        @self.registry.register("task_a")
        async def task_a(ctx: DAGContext, params: dict) -> TaskResult:
            return TaskResult.ok()

        @self.registry.register("task_b")
        async def task_b(ctx: DAGContext, params: dict) -> TaskResult:
            return TaskResult.ok()

        tasks = self.registry.list_tasks()
        assert "task_a" in tasks
        assert "task_b" in tasks
        assert len(tasks) == 2

    def test_metadata_storage(self):
        """Test task metadata is stored correctly."""

        @self.registry.register("timed_task", timeout_seconds=120, max_retries=5)
        async def timed_task(ctx: DAGContext, params: dict) -> TaskResult:
            return TaskResult.ok()

        metadata = self.registry.get_metadata("timed_task")
        assert metadata is not None
        assert metadata["timeout_seconds"] == 120
        assert metadata["max_retries"] == 5
        assert metadata["function_name"] == "timed_task"

    def test_clear(self):
        """Test registry clear."""

        @self.registry.register("to_clear")
        async def to_clear(ctx: DAGContext, params: dict) -> TaskResult:
            return TaskResult.ok()

        assert self.registry.is_registered("to_clear")

        self.registry.clear()

        assert not self.registry.is_registered("to_clear")
        assert self.registry.list_tasks() == []

    @pytest.mark.asyncio
    async def test_task_execution(self):
        """Test that registered tasks can be executed."""

        @self.registry.register("executable_task")
        async def executable_task(ctx: DAGContext, params: dict) -> TaskResult:
            return TaskResult.ok({"param_value": params.get("key")})

        task = self.registry.get("executable_task")
        ctx = DAGContext(run_id="test-run")
        result = await task(ctx, {"key": "test_value"})

        assert result.success is True
        assert result.data["param_value"] == "test_value"


class TestDagTaskDecorator:
    """Tests for the @dag_task convenience decorator."""

    def setup_method(self):
        """Clear the global registry before each test."""
        task_registry.clear()

    def test_decorator_registers_task(self):
        """Test that @dag_task registers with global registry."""

        @dag_task("global_task")
        async def global_task(ctx: DAGContext, params: dict) -> TaskResult:
            return TaskResult.ok()

        assert task_registry.is_registered("global_task")

    def test_decorator_with_options(self):
        """Test decorator with timeout and retry options."""

        @dag_task("configured_task", timeout_seconds=60, max_retries=1)
        async def configured_task(ctx: DAGContext, params: dict) -> TaskResult:
            return TaskResult.ok()

        metadata = task_registry.get_metadata("configured_task")
        assert metadata["timeout_seconds"] == 60
        assert metadata["max_retries"] == 1
