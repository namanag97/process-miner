"""
Mock Utilities for External Services

Provides context managers and fixtures for mocking external dependencies
like S3, Temporal, and other infrastructure services.

Usage:
    from tests.mocks import mock_s3_client, mock_temporal_client

    def test_upload():
        with mock_s3_client(content=b"test data") as mock:
            result = upload_file(...)
            mock.upload_fileobj.assert_called_once()
"""

from contextlib import contextmanager
from io import BytesIO
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

# =============================================================================
# S3/MinIO Storage Mocks
# =============================================================================


@contextmanager
def mock_s3_client(content: bytes = b"", bucket: str = "test-bucket"):
    """Mock S3/MinIO storage client.

    Args:
        content: Content to return from download operations
        bucket: Bucket name for verification

    Yields:
        Mock client object for assertions
    """
    mock_client = MagicMock()
    mock_client.download_fileobj = MagicMock(
        side_effect=lambda bucket, key, fileobj: fileobj.write(content)
    )
    mock_client.upload_fileobj = MagicMock(return_value=None)
    mock_client.head_object = MagicMock(return_value={"ContentLength": len(content)})
    mock_client.delete_object = MagicMock(return_value=None)
    mock_client.generate_presigned_url = MagicMock(
        return_value=f"https://{bucket}.s3.amazonaws.com/test-key?signed=true"
    )

    with patch(
        "src.platform.infrastructure.storage.client.get_client",
        return_value=mock_client,
    ):
        yield mock_client


@contextmanager
def mock_storage_service(files: dict[str, bytes] | None = None):
    """Mock the storage service with pre-loaded files.

    Args:
        files: Dict mapping storage keys to file contents

    Yields:
        Mock service object
    """
    files = files or {}
    mock_service = MagicMock()

    def download(key: str) -> BytesIO:
        if key in files:
            return BytesIO(files[key])
        raise FileNotFoundError(f"No such key: {key}")

    mock_service.download = MagicMock(side_effect=download)
    mock_service.upload = MagicMock(return_value=None)
    mock_service.delete = MagicMock(return_value=None)
    mock_service.exists = MagicMock(side_effect=lambda k: k in files)

    with patch(
        "src.platform.infrastructure.storage.service.StorageService",
        return_value=mock_service,
    ):
        yield mock_service


# =============================================================================
# Temporal Workflow Mocks
# =============================================================================


@contextmanager
def mock_temporal_client():
    """Mock Temporal client for workflow testing.

    Yields:
        Mock client for assertions
    """
    mock_client = AsyncMock()
    mock_client.start_workflow = AsyncMock(return_value="workflow-id-123")
    mock_client.get_workflow_handle = AsyncMock()
    mock_client.execute_workflow = AsyncMock(return_value={"status": "completed"})

    with patch(
        "src.platform.temporal.client.get_client",
        return_value=mock_client,
    ):
        yield mock_client


@contextmanager
def mock_workflow_dispatch():
    """Mock the workflow dispatch function.

    Yields:
        Mock dispatch function for assertions
    """
    mock_dispatch = AsyncMock(return_value="workflow-id-123")

    with patch(
        "src.platform.temporal.dispatch.dispatch_workflow",
        mock_dispatch,
    ):
        yield mock_dispatch


# =============================================================================
# Database Session Mocks
# =============================================================================


def create_mock_session() -> AsyncMock:
    """Create a mock async database session.

    Returns:
        AsyncMock configured as a database session
    """
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=MagicMock(scalar=MagicMock(return_value=1)))
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()
    mock_session.close = AsyncMock()
    mock_session.flush = AsyncMock()
    mock_session.refresh = AsyncMock()
    mock_session.add = MagicMock()

    # Context manager support
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)

    return mock_session


@contextmanager
def mock_session_factory():
    """Mock the session factory for database operations.

    Yields:
        Tuple of (mock_factory, mock_session)
    """
    mock_session = create_mock_session()
    mock_factory = MagicMock(return_value=mock_session)

    with patch(
        "src.platform.infrastructure.database.async_session_maker",
        mock_factory,
    ):
        yield mock_factory, mock_session


# =============================================================================
# PM4Py Mocks
# =============================================================================


@contextmanager
def mock_pm4py():
    """Mock PM4Py library functions.

    Yields:
        Dict of mock functions for assertions
    """
    mocks = {
        "read_xes": MagicMock(),
        "discover_petri_net_inductive": MagicMock(
            return_value=(MagicMock(), MagicMock(), MagicMock())
        ),
        "discover_dfg": MagicMock(return_value=({}, {}, {})),
        "conformance_diagnostics": MagicMock(return_value={}),
    }

    with patch.multiple(
        "pm4py",
        read_xes=mocks["read_xes"],
        discover_petri_net_inductive=mocks["discover_petri_net_inductive"],
    ):
        yield mocks


# =============================================================================
# HTTP Client Mocks
# =============================================================================


@contextmanager
def mock_httpx_client(responses: dict[str, Any] | None = None):
    """Mock httpx async client for external API calls.

    Args:
        responses: Dict mapping URLs to response data

    Yields:
        Mock client for assertions
    """
    responses = responses or {}
    mock_client = AsyncMock()

    async def mock_get(url: str, **kwargs):
        response = MagicMock()
        response.json = MagicMock(return_value=responses.get(url, {}))
        response.status_code = 200 if url in responses else 404
        response.raise_for_status = MagicMock()
        return response

    mock_client.get = AsyncMock(side_effect=mock_get)
    mock_client.post = AsyncMock()

    with patch("httpx.AsyncClient", return_value=mock_client):
        yield mock_client
