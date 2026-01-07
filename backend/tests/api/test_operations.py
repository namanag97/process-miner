"""
Tests for Operations API - Unified Temporal Workflow Status.

Tests cover:
- GET /operations/{workflow_id} - Get workflow status
- GET /operations - List operations
- POST /operations/{workflow_id}/cancel - Cancel workflow
- GET /operations/{workflow_id}/result - Get completed result
- GET /operations/{workflow_id}/stream - SSE streaming (basic)

Note: Integration tests that require a running Temporal server are marked
with `pytest.mark.integration`. They're skipped by default but can be run
with: pytest -m integration
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

# Skip integration tests by default (require Temporal server)
pytestmark = pytest.mark.integration

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_temporal_client():
    """Mock Temporal client for testing."""
    with patch("src.infra.temporal.client.get_temporal_client") as mock:
        client = AsyncMock()
        mock.return_value = client
        yield client


@pytest.fixture
def mock_workflow_handle():
    """Create a mock workflow handle."""
    handle = AsyncMock()
    handle.describe = AsyncMock()
    handle.query = AsyncMock()
    handle.cancel = AsyncMock()
    handle.result = AsyncMock()
    return handle


# =============================================================================
# GET /operations/{workflow_id} Tests
# =============================================================================


class TestGetOperationStatus:
    """Tests for GET /operations/{workflow_id}."""

    @pytest.mark.asyncio
    async def test_get_operation_status_running(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test getting status of a running workflow."""
        from datetime import datetime, timezone

        # Setup mock
        mock_desc = MagicMock()
        mock_desc.status = MagicMock()
        mock_desc.status.name = "RUNNING"
        mock_desc.start_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        mock_desc.close_time = None

        mock_workflow_handle.describe.return_value = mock_desc
        mock_workflow_handle.query.return_value = {
            "progress": 45,
            "current_step": "parse_to_parquet",
            "error": None,
        }
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        # Make request
        response = await auth_client.get("/api/v1/operations/ingest-dataset-abc123")

        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "ingest-dataset-abc123"
        assert data["status"] == "RUNNING"
        assert data["progress"] == 45
        assert data["current_step"] == "parse_to_parquet"
        assert data["entity_type"] == "dataset"
        assert data["operation_type"] == "ingest"

    @pytest.mark.asyncio
    async def test_get_operation_status_completed(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test getting status of a completed workflow."""
        from datetime import datetime, timezone

        # Setup mock
        mock_desc = MagicMock()
        mock_desc.status = MagicMock()
        mock_desc.status.name = "COMPLETED"
        mock_desc.start_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        mock_desc.close_time = datetime(2024, 1, 15, 10, 5, 0, tzinfo=timezone.utc)

        mock_workflow_handle.describe.return_value = mock_desc
        mock_workflow_handle.query.return_value = {
            "progress": 100,
            "current_step": "completed",
            "error": None,
        }
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        # Make request
        response = await auth_client.get("/api/v1/operations/ingest-dataset-abc123")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"
        assert data["progress"] == 100
        assert data["current_step"] == "completed"
        assert data["completed_at"] is not None

    @pytest.mark.asyncio
    async def test_get_operation_status_failed(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test getting status of a failed workflow."""
        from datetime import datetime, timezone

        # Setup mock
        mock_desc = MagicMock()
        mock_desc.status = MagicMock()
        mock_desc.status.name = "FAILED"
        mock_desc.start_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        mock_desc.close_time = datetime(2024, 1, 15, 10, 2, 0, tzinfo=timezone.utc)

        mock_workflow_handle.describe.return_value = mock_desc
        mock_workflow_handle.query.return_value = {
            "progress": 30,
            "current_step": "failed",
            "error": "Invalid file format",
        }
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        # Make request
        response = await auth_client.get("/api/v1/operations/ingest-dataset-abc123")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "FAILED"
        assert data["error_message"] == "Invalid file format"

    @pytest.mark.asyncio
    async def test_get_operation_status_not_found(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test getting status of a non-existent workflow."""
        # Setup mock to raise exception
        mock_workflow_handle.describe.side_effect = Exception("Workflow not found")
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        # Make request
        response = await auth_client.get("/api/v1/operations/non-existent-workflow")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_parse_workflow_id_discovery(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test parsing discovery workflow ID."""
        from datetime import datetime, timezone

        # Setup mock
        mock_desc = MagicMock()
        mock_desc.status = MagicMock()
        mock_desc.status.name = "RUNNING"
        mock_desc.start_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        mock_desc.close_time = None

        mock_workflow_handle.describe.return_value = mock_desc
        mock_workflow_handle.query.return_value = {"progress": 50, "current_step": "mine_model"}
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        # Make request
        response = await auth_client.get("/api/v1/operations/discover-abc123-inductive")

        assert response.status_code == 200
        data = response.json()
        assert data["operation_type"] == "discover"


# =============================================================================
# POST /operations/{workflow_id}/cancel Tests
# =============================================================================


class TestCancelOperation:
    """Tests for POST /operations/{workflow_id}/cancel."""

    @pytest.mark.asyncio
    async def test_cancel_running_operation(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test cancelling a running workflow."""
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        response = await auth_client.post("/api/v1/operations/ingest-dataset-abc123/cancel")

        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == "ingest-dataset-abc123"
        assert data["status"] == "cancel_requested"
        mock_workflow_handle.cancel.assert_called_once()

    @pytest.mark.asyncio
    async def test_cancel_nonexistent_operation(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test cancelling a non-existent workflow."""
        mock_workflow_handle.cancel.side_effect = Exception("Workflow not found")
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        response = await auth_client.post("/api/v1/operations/non-existent/cancel")

        assert response.status_code == 400


# =============================================================================
# GET /operations/{workflow_id}/result Tests
# =============================================================================


class TestGetOperationResult:
    """Tests for GET /operations/{workflow_id}/result."""

    @pytest.mark.asyncio
    async def test_get_completed_result(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test getting result of a completed workflow."""
        # Setup mock
        mock_desc = MagicMock()
        mock_desc.status = MagicMock()
        mock_desc.status.name = "COMPLETED"

        mock_workflow_handle.describe.return_value = mock_desc
        mock_workflow_handle.result.return_value = {
            "dataset_id": "abc123",
            "total_cases": 100,
            "total_events": 500,
        }
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        response = await auth_client.get("/api/v1/operations/ingest-dataset-abc123/result")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"
        assert data["result"]["total_cases"] == 100

    @pytest.mark.asyncio
    async def test_get_result_not_completed(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test getting result of a non-completed workflow."""
        # Setup mock
        mock_desc = MagicMock()
        mock_desc.status = MagicMock()
        mock_desc.status.name = "RUNNING"

        mock_workflow_handle.describe.return_value = mock_desc
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        response = await auth_client.get("/api/v1/operations/ingest-dataset-abc123/result")

        assert response.status_code == 400


# =============================================================================
# GET /operations Tests (List)
# =============================================================================


class TestListOperations:
    """Tests for GET /operations."""

    @pytest.mark.asyncio
    async def test_list_operations_empty(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
    ):
        """Test listing operations when none exist."""

        async def empty_generator():
            return
            yield  # Make it an async generator

        mock_temporal_client.list_workflows.return_value = empty_generator()

        response = await auth_client.get("/api/v1/operations")

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0


# =============================================================================
# SSE Stream Tests
# =============================================================================


class TestStreamOperation:
    """Tests for GET /operations/{workflow_id}/stream."""

    @pytest.mark.asyncio
    async def test_stream_returns_sse_headers(
        self,
        auth_client: AsyncClient,
        mock_temporal_client,
        mock_workflow_handle,
    ):
        """Test that SSE endpoint returns correct headers."""
        from datetime import datetime, timezone

        # Setup mock for initial state
        mock_desc = MagicMock()
        mock_desc.status = MagicMock()
        mock_desc.status.name = "COMPLETED"
        mock_desc.start_time = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        mock_desc.close_time = datetime(2024, 1, 15, 10, 5, 0, tzinfo=timezone.utc)

        mock_workflow_handle.describe.return_value = mock_desc
        mock_workflow_handle.query.return_value = {"progress": 100, "current_step": "completed"}
        mock_temporal_client.get_workflow_handle.return_value = mock_workflow_handle

        # Make request with streaming
        async with auth_client.stream(
            "GET", "/api/v1/operations/ingest-dataset-abc123/stream"
        ) as response:
            assert response.status_code == 200
            assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
            assert response.headers["cache-control"] == "no-cache, no-store, must-revalidate"


# =============================================================================
# Workflow ID Parsing Tests (Unit tests - no Temporal required)
# =============================================================================


@pytest.mark.unit
class TestWorkflowIdParsing:
    """Tests for _parse_workflow_id helper."""

    def test_parse_ingest_workflow_id(self):
        """Test parsing ingestion workflow ID."""
        from src.api.routers.operations import _parse_workflow_id

        entity_type, entity_id, operation_type = _parse_workflow_id("ingest-dataset-abc123")
        assert entity_type == "dataset"
        assert operation_type == "ingest"

    def test_parse_validate_workflow_id(self):
        """Test parsing validation workflow ID."""
        from src.api.routers.operations import _parse_workflow_id

        entity_type, entity_id, operation_type = _parse_workflow_id("validate-dataset-xyz789")
        assert entity_type == "dataset"
        assert operation_type == "validate"

    def test_parse_discover_workflow_id(self):
        """Test parsing discovery workflow ID."""
        from src.api.routers.operations import _parse_workflow_id

        entity_type, entity_id, operation_type = _parse_workflow_id(
            "discover-abc123-inductive"
        )
        assert entity_type == "dataset"
        assert operation_type == "discover"

    def test_parse_conformance_workflow_id(self):
        """Test parsing conformance workflow ID."""
        from src.api.routers.operations import _parse_workflow_id

        entity_type, entity_id, operation_type = _parse_workflow_id(
            "conformance-dataset123-model456"
        )
        assert entity_type == "dataset"
        assert operation_type == "conformance"

    def test_parse_invalid_workflow_id(self):
        """Test parsing invalid workflow ID."""
        from src.api.routers.operations import _parse_workflow_id

        entity_type, entity_id, operation_type = _parse_workflow_id("invalid")
        assert entity_type is None
        assert entity_id is None
        assert operation_type is None
