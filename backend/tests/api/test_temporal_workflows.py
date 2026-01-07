"""
Tests for Temporal Workflow Components.

Tests cover:
- Workflow Query Handlers (get_progress)
- Activity Progress Publisher
- Workflow Progress Tracking
"""

import json
from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Progress Publisher Tests
# =============================================================================


class TestActivityProgressPublisher:
    """Tests for the ActivityProgressPublisher."""

    @pytest.mark.asyncio
    async def test_publish_progress_with_redis(self):
        """Test publishing progress to Redis."""
        from src.platform.temporal.activities.progress import ActivityProgressPublisher

        publisher = ActivityProgressPublisher()

        # Mock Redis client
        mock_redis = AsyncMock()
        publisher._redis = mock_redis

        # Publish progress
        result = await publisher.step_progress(
            workflow_id="ingest-dataset-abc123",
            step="parse_to_parquet",
            progress=50,
            details={"rows_processed": 1000},
        )

        assert result is True
        assert mock_redis.publish.call_count == 2  # workflow-specific + global channel

        # Verify channel names
        calls = mock_redis.publish.call_args_list
        assert "workflow:progress:ingest-dataset-abc123" in calls[0][0][0]
        assert "workflow:progress:all" in calls[1][0][0]

    @pytest.mark.asyncio
    async def test_publish_progress_without_redis(self):
        """Test graceful handling when Redis is unavailable."""
        from src.platform.temporal.activities.progress import ActivityProgressPublisher

        publisher = ActivityProgressPublisher()
        publisher._redis = None

        # Mock the _get_redis to return None (Redis unavailable)
        publisher._get_redis = AsyncMock(return_value=None)

        result = await publisher.step_progress(
            workflow_id="ingest-dataset-abc123",
            step="validate_file",
            progress=10,
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_step_started_event(self):
        """Test step started event publishing."""
        from src.platform.temporal.activities.progress import (
            ActivityProgressPublisher,
            ProgressEventType,
        )

        publisher = ActivityProgressPublisher()
        mock_redis = AsyncMock()
        publisher._redis = mock_redis

        await publisher.step_started(
            workflow_id="ingest-dataset-abc123",
            step="validate_file",
            details={"file_size": 1024},
        )

        # Verify SSE event format
        call_args = mock_redis.publish.call_args_list[0][0]
        message = call_args[1]
        assert "event: step:started" in message
        assert '"step": "validate_file"' in message

    @pytest.mark.asyncio
    async def test_step_completed_event(self):
        """Test step completed event publishing."""
        from src.platform.temporal.activities.progress import ActivityProgressPublisher

        publisher = ActivityProgressPublisher()
        mock_redis = AsyncMock()
        publisher._redis = mock_redis

        await publisher.step_completed(
            workflow_id="ingest-dataset-abc123",
            step="parse_to_parquet",
            details={"total_events": 5000},
        )

        call_args = mock_redis.publish.call_args_list[0][0]
        message = call_args[1]
        assert "event: step:completed" in message
        assert '"progress": 100' in message

    @pytest.mark.asyncio
    async def test_step_failed_event(self):
        """Test step failed event publishing."""
        from src.platform.temporal.activities.progress import ActivityProgressPublisher

        publisher = ActivityProgressPublisher()
        mock_redis = AsyncMock()
        publisher._redis = mock_redis

        await publisher.step_failed(
            workflow_id="ingest-dataset-abc123",
            step="validate_file",
            error="Invalid file format",
        )

        call_args = mock_redis.publish.call_args_list[0][0]
        message = call_args[1]
        assert "event: step:failed" in message
        assert '"error": "Invalid file format"' in message

    @pytest.mark.asyncio
    async def test_workflow_completed_event(self):
        """Test workflow completed event publishing."""
        from src.platform.temporal.activities.progress import ActivityProgressPublisher

        publisher = ActivityProgressPublisher()
        mock_redis = AsyncMock()
        publisher._redis = mock_redis

        await publisher.workflow_completed(
            workflow_id="ingest-dataset-abc123",
            result={"total_cases": 100, "total_events": 500},
        )

        call_args = mock_redis.publish.call_args_list[0][0]
        message = call_args[1]
        assert "event: workflow:completed" in message
        assert '"total_cases": 100' in message

    @pytest.mark.asyncio
    async def test_workflow_failed_event(self):
        """Test workflow failed event publishing."""
        from src.platform.temporal.activities.progress import ActivityProgressPublisher

        publisher = ActivityProgressPublisher()
        mock_redis = AsyncMock()
        publisher._redis = mock_redis

        await publisher.workflow_failed(
            workflow_id="ingest-dataset-abc123",
            error="Database connection failed",
            step="compute_statistics",
        )

        call_args = mock_redis.publish.call_args_list[0][0]
        message = call_args[1]
        assert "event: workflow:failed" in message
        assert '"error": "Database connection failed"' in message


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestProgressConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_publish_progress_function(self):
        """Test the publish_progress convenience function."""
        with patch(
            "src.platform.temporal.activities.progress.get_progress_publisher"
        ) as mock_get:
            mock_publisher = AsyncMock()
            mock_get.return_value = mock_publisher

            from src.platform.temporal.activities.progress import publish_progress

            await publish_progress(
                workflow_id="test-workflow",
                step="test_step",
                progress=50,
                details={"key": "value"},
            )

            mock_publisher.step_progress.assert_called_once_with(
                "test-workflow", "test_step", 50, {"key": "value"}
            )

    @pytest.mark.asyncio
    async def test_publish_step_started_function(self):
        """Test the publish_step_started convenience function."""
        with patch(
            "src.platform.temporal.activities.progress.get_progress_publisher"
        ) as mock_get:
            mock_publisher = AsyncMock()
            mock_get.return_value = mock_publisher

            from src.platform.temporal.activities.progress import publish_step_started

            await publish_step_started(
                workflow_id="test-workflow",
                step="test_step",
                details={"key": "value"},
            )

            mock_publisher.step_started.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_step_completed_function(self):
        """Test the publish_step_completed convenience function."""
        with patch(
            "src.platform.temporal.activities.progress.get_progress_publisher"
        ) as mock_get:
            mock_publisher = AsyncMock()
            mock_get.return_value = mock_publisher

            from src.platform.temporal.activities.progress import publish_step_completed

            await publish_step_completed(
                workflow_id="test-workflow",
                step="test_step",
                details={"key": "value"},
            )

            mock_publisher.step_completed.assert_called_once()


# =============================================================================
# Progress Event Type Tests
# =============================================================================


class TestProgressEventTypes:
    """Tests for ProgressEventType enum."""

    def test_event_type_values(self):
        """Test that event types have correct SSE values."""
        from src.platform.temporal.activities.progress import ProgressEventType

        assert ProgressEventType.STEP_STARTED.value == "step:started"
        assert ProgressEventType.STEP_PROGRESS.value == "step:progress"
        assert ProgressEventType.STEP_COMPLETED.value == "step:completed"
        assert ProgressEventType.STEP_FAILED.value == "step:failed"
        assert ProgressEventType.WORKFLOW_PROGRESS.value == "workflow:progress"
        assert ProgressEventType.WORKFLOW_COMPLETED.value == "workflow:completed"
        assert ProgressEventType.WORKFLOW_FAILED.value == "workflow:failed"


# =============================================================================
# Workflow Progress State Tests
# =============================================================================


class TestIngestionProgressState:
    """Tests for IngestionProgress dataclass."""

    def test_default_values(self):
        """Test default values for IngestionProgress."""
        from src.platform.temporal.workflows.ingestion import IngestionProgress

        progress = IngestionProgress()
        assert progress.progress_percent == 0
        assert progress.current_step == "initializing"
        assert progress.total_events == 0
        assert progress.total_cases == 0
        assert progress.error_message is None
        assert progress.details == {}

    def test_custom_values(self):
        """Test IngestionProgress with custom values."""
        from src.platform.temporal.workflows.ingestion import IngestionProgress

        progress = IngestionProgress(
            progress_percent=50,
            current_step="parse_to_parquet",
            total_events=1000,
            total_cases=100,
            details={"step": 2, "total_steps": 3},
        )
        assert progress.progress_percent == 50
        assert progress.current_step == "parse_to_parquet"
        assert progress.total_events == 1000
        assert progress.total_cases == 100


class TestValidationProgressState:
    """Tests for ValidationProgress dataclass."""

    def test_default_values(self):
        """Test default values for ValidationProgress."""
        from src.platform.temporal.workflows.ingestion import ValidationProgress

        progress = ValidationProgress()
        assert progress.progress_percent == 0
        assert progress.current_step == "initializing"
        assert progress.error_message is None


class TestAnalysisProgressState:
    """Tests for AnalysisProgress dataclass."""

    def test_default_values(self):
        """Test default values for AnalysisProgress."""
        from src.platform.temporal.workflows.analysis import AnalysisProgress

        progress = AnalysisProgress()
        assert progress.progress_percent == 0
        assert progress.current_step == "initializing"
        assert progress.error_message is None
        assert progress.details is None


class TestQualityProgressState:
    """Tests for QualityProgress dataclass."""

    def test_default_values(self):
        """Test default values for QualityProgress."""
        from src.platform.temporal.workflows.quality import QualityProgress

        progress = QualityProgress()
        assert progress.progress_percent == 0
        assert progress.current_step == "initializing"
        assert progress.error_message is None
        assert progress.computed_metrics is None


# =============================================================================
# SSE Message Format Tests
# =============================================================================


class TestSSEMessageFormat:
    """Tests for SSE message formatting."""

    @pytest.mark.asyncio
    async def test_sse_message_structure(self):
        """Test that SSE messages follow correct format."""
        from src.platform.temporal.activities.progress import ActivityProgressPublisher

        publisher = ActivityProgressPublisher()
        mock_redis = AsyncMock()
        publisher._redis = mock_redis

        await publisher.step_progress(
            workflow_id="test-workflow",
            step="test_step",
            progress=50,
        )

        # Get the SSE message
        call_args = mock_redis.publish.call_args_list[0][0]
        message = call_args[1]

        # Verify SSE format: "event: {type}\ndata: {json}\n\n"
        assert message.startswith("event: step:progress\n")
        assert "data: " in message
        assert message.endswith("\n\n")

        # Extract and parse JSON data
        data_line = [line for line in message.split("\n") if line.startswith("data: ")][0]
        json_data = json.loads(data_line[6:])  # Remove "data: " prefix

        assert json_data["workflow_id"] == "test-workflow"
        assert json_data["event"] == "step:progress"
        assert json_data["step"] == "test_step"
        assert json_data["progress"] == 50
        assert "timestamp" in json_data

    @pytest.mark.asyncio
    async def test_sse_channel_naming(self):
        """Test Redis channel naming convention."""
        from src.platform.temporal.activities.progress import ActivityProgressPublisher

        publisher = ActivityProgressPublisher()
        mock_redis = AsyncMock()
        publisher._redis = mock_redis

        await publisher.step_progress(
            workflow_id="ingest-dataset-abc123",
            step="test",
            progress=0,
        )

        # Check workflow-specific channel
        call_args = mock_redis.publish.call_args_list[0][0]
        assert call_args[0] == "workflow:progress:ingest-dataset-abc123"

        # Check global monitoring channel
        call_args = mock_redis.publish.call_args_list[1][0]
        assert call_args[0] == "workflow:progress:all"


# =============================================================================
# Singleton Publisher Tests
# =============================================================================


class TestPublisherSingleton:
    """Tests for publisher singleton behavior."""

    def test_get_progress_publisher_returns_singleton(self):
        """Test that get_progress_publisher returns the same instance."""
        from src.platform.temporal.activities.progress import (
            ActivityProgressPublisher,
            get_progress_publisher,
        )

        # Reset singleton for test isolation
        import src.platform.temporal.activities.progress as progress_module

        progress_module._publisher = None

        publisher1 = get_progress_publisher()
        publisher2 = get_progress_publisher()

        assert publisher1 is publisher2
        assert isinstance(publisher1, ActivityProgressPublisher)

        # Cleanup
        progress_module._publisher = None
