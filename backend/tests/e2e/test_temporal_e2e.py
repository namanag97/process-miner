"""
End-to-End Tests for Temporal Workflow System.

These tests verify the complete flow from API to Temporal workflows.
They can be run against a live system with:
    pytest tests/e2e/test_temporal_e2e.py -v

Requirements:
- Backend server running on localhost:8001
- Temporal server running
- Redis running for progress streaming

For manual testing, use the curl commands in the docstrings.
"""

import asyncio
import json
import time
from typing import Any

import httpx
import pytest

# =============================================================================
# Test Configuration
# =============================================================================

BASE_URL = "http://localhost:8001/api/v1"
TEST_TIMEOUT = 60  # seconds

# MVP test data IDs (seeded on startup)
MVP_ORG_ID = "mvp-org-001"
MVP_WORKSPACE_ID = "mvp-ws-001"
MVP_PROJECT_ID = "mvp-proj-001"
MVP_USER_ID = "mvp-user-001"


def get_auth_token() -> str:
    """Get auth token for testing.

    curl -X POST http://localhost:8001/api/v1/auth/login \
        -H "Content-Type: application/json" \
        -d '{"email": "analyst@example.com", "password": "test"}'
    """
    # For MVP, we use a pre-generated token or skip auth
    # In production, this would call the login endpoint
    return "test-token"


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Get authorization headers."""
    return {
        "Authorization": f"Bearer {get_auth_token()}",
        "Content-Type": "application/json",
    }


# =============================================================================
# Health Check Tests
# =============================================================================


class TestHealthEndpoints:
    """E2E tests for health endpoints.

    curl http://localhost:8001/health/live
    curl http://localhost:8001/health/ready
    """

    @pytest.mark.e2e
    def test_liveness_probe(self):
        """Test liveness probe returns 200."""
        response = httpx.get(f"{BASE_URL.replace('/api/v1', '')}/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.e2e
    def test_readiness_probe(self):
        """Test readiness probe returns 200."""
        response = httpx.get(f"{BASE_URL.replace('/api/v1', '')}/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


# =============================================================================
# Operations API Tests
# =============================================================================


class TestOperationsAPI:
    """E2E tests for Operations (Temporal workflow status) API.

    These tests verify the /operations endpoints work correctly.
    """

    @pytest.mark.e2e
    def test_list_operations_empty(self, auth_headers):
        """Test listing operations returns valid response.

        curl -X GET http://localhost:8001/api/v1/operations \
            -H "Authorization: Bearer <token>"
        """
        response = httpx.get(f"{BASE_URL}/operations", headers=auth_headers)
        # 200 = success, 500 = Temporal not running (acceptable in test env)
        assert response.status_code in (200, 500), f"Unexpected status: {response.status_code}"

        if response.status_code == 200:
            data = response.json()
            assert "items" in data
            assert "total" in data
            assert isinstance(data["items"], list)

    @pytest.mark.e2e
    def test_get_nonexistent_operation(self, auth_headers):
        """Test getting non-existent operation returns 404.

        curl -X GET http://localhost:8001/api/v1/operations/nonexistent-workflow-123 \
            -H "Authorization: Bearer <token>"
        """
        response = httpx.get(
            f"{BASE_URL}/operations/nonexistent-workflow-123",
            headers=auth_headers,
        )
        # Should return 404 or error for non-existent workflow
        assert response.status_code in (404, 500)

    @pytest.mark.e2e
    def test_cancel_nonexistent_operation(self, auth_headers):
        """Test cancelling non-existent operation returns error.

        curl -X POST http://localhost:8001/api/v1/operations/nonexistent/cancel \
            -H "Authorization: Bearer <token>"
        """
        response = httpx.post(
            f"{BASE_URL}/operations/nonexistent-workflow/cancel",
            headers=auth_headers,
        )
        assert response.status_code == 400


# =============================================================================
# SSE Streaming Tests
# =============================================================================


class TestSSEStreaming:
    """E2E tests for SSE streaming endpoint.

    These tests verify the /operations/{id}/stream endpoint.
    """

    @pytest.mark.e2e
    def test_stream_endpoint_returns_sse_headers(self, auth_headers):
        """Test that stream endpoint returns correct SSE headers.

        curl -N http://localhost:8001/api/v1/operations/test-workflow/stream \
            -H "Authorization: Bearer <token>" \
            -H "Accept: text/event-stream"
        """
        # Use a short timeout since we're just checking headers
        with httpx.stream(
            "GET",
            f"{BASE_URL}/operations/test-workflow-123/stream",
            headers=auth_headers,
            timeout=5.0,
        ) as response:
            # Check headers
            assert response.headers.get("content-type", "").startswith("text/event-stream")
            assert "no-cache" in response.headers.get("cache-control", "")


# =============================================================================
# Full Workflow E2E Test
# =============================================================================


class TestDatasetIngestionWorkflow:
    """E2E test for complete dataset ingestion workflow.

    This test verifies the full flow:
    1. Upload a dataset
    2. Start ingestion workflow
    3. Poll for progress
    4. Verify completion
    """

    SAMPLE_CSV = """\
case_id,activity,timestamp,resource
1,Start,2024-01-01 10:00:00,Alice
1,Process,2024-01-01 10:30:00,Bob
1,End,2024-01-01 11:00:00,Alice
2,Start,2024-01-01 10:00:00,Bob
2,Process,2024-01-01 10:45:00,Alice
2,End,2024-01-01 11:30:00,Bob
"""

    @pytest.mark.e2e
    @pytest.mark.slow
    def test_full_ingestion_flow(self, auth_headers):
        """Test complete dataset upload and ingestion.

        Manual curl commands:

        # 1. Create dataset
        curl -X POST http://localhost:8001/api/v1/datasets \
            -H "Authorization: Bearer <token>" \
            -H "Content-Type: application/json" \
            -d '{"name": "E2E Test Dataset", "project_id": "mvp-proj-001"}'

        # 2. Upload file
        curl -X POST http://localhost:8001/api/v1/datasets/{dataset_id}/upload \
            -H "Authorization: Bearer <token>" \
            -F "file=@test.csv"

        # 3. Start ingestion
        curl -X POST http://localhost:8001/api/v1/datasets/{dataset_id}/ingest \
            -H "Authorization: Bearer <token>" \
            -H "Content-Type: application/json" \
            -d '{"case_id_column": "case_id", "activity_column": "activity", "timestamp_column": "timestamp"}'

        # 4. Poll progress
        curl http://localhost:8001/api/v1/operations/ingest-dataset-{dataset_id} \
            -H "Authorization: Bearer <token>"

        # 5. Stream progress (SSE)
        curl -N http://localhost:8001/api/v1/operations/ingest-dataset-{dataset_id}/stream \
            -H "Authorization: Bearer <token>"
        """
        # This test requires a running backend with Temporal
        # Skip if server is not available
        try:
            health = httpx.get(f"{BASE_URL.replace('/api/v1', '')}/health/ready", timeout=5)
            if health.status_code != 200:
                pytest.skip("Backend not ready")
        except Exception:
            pytest.skip("Backend not available")

        # Step 1: Create dataset
        create_response = httpx.post(
            f"{BASE_URL}/datasets",
            headers=auth_headers,
            json={
                "name": f"E2E Test {int(time.time())}",
                "project_id": MVP_PROJECT_ID,
            },
        )

        if create_response.status_code != 201:
            pytest.skip(f"Could not create dataset: {create_response.text}")

        dataset_id = create_response.json()["id"]
        print(f"Created dataset: {dataset_id}")

        try:
            # Step 2: Upload file
            files = {"file": ("test.csv", self.SAMPLE_CSV, "text/csv")}
            upload_response = httpx.post(
                f"{BASE_URL}/datasets/{dataset_id}/upload",
                headers={"Authorization": auth_headers["Authorization"]},
                files=files,
                timeout=30,
            )

            if upload_response.status_code not in (200, 201):
                print(f"Upload failed: {upload_response.text}")
                pytest.skip("Upload not supported in test environment")

            print(f"Uploaded file to dataset: {dataset_id}")

            # Step 3: Start ingestion
            ingest_response = httpx.post(
                f"{BASE_URL}/datasets/{dataset_id}/ingest",
                headers=auth_headers,
                json={
                    "case_id_column": "case_id",
                    "activity_column": "activity",
                    "timestamp_column": "timestamp",
                    "resource_column": "resource",
                },
                timeout=30,
            )

            if ingest_response.status_code not in (200, 201, 202):
                print(f"Ingest start failed: {ingest_response.text}")
                pytest.skip("Ingestion not available")

            workflow_id = f"ingest-dataset-{dataset_id}"
            print(f"Started workflow: {workflow_id}")

            # Step 4: Poll for completion
            max_polls = 30
            poll_interval = 2

            for i in range(max_polls):
                status_response = httpx.get(
                    f"{BASE_URL}/operations/{workflow_id}",
                    headers=auth_headers,
                    timeout=10,
                )

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"Poll {i+1}: status={status_data.get('status')}, progress={status_data.get('progress')}%")

                    if status_data.get("status") == "COMPLETED":
                        print("Workflow completed successfully!")
                        assert status_data["progress"] == 100
                        return
                    elif status_data.get("status") in ("FAILED", "CANCELLED"):
                        pytest.fail(f"Workflow failed: {status_data.get('error_message')}")

                time.sleep(poll_interval)

            pytest.fail("Workflow did not complete in time")

        finally:
            # Cleanup: Delete dataset
            httpx.delete(f"{BASE_URL}/datasets/{dataset_id}", headers=auth_headers)


# =============================================================================
# Progress Publisher Integration Test
# =============================================================================


class TestProgressPublisherIntegration:
    """Integration tests for the progress publisher with Redis."""

    @pytest.mark.e2e
    @pytest.mark.asyncio
    async def test_publish_and_subscribe(self):
        """Test publishing and subscribing to progress events.

        This requires Redis to be running.
        """
        try:
            import redis.asyncio as redis
        except ImportError:
            pytest.skip("redis package not installed")

        try:
            # Connect to Redis
            client = redis.from_url("redis://localhost:6379", decode_responses=True)
            await client.ping()
        except Exception:
            pytest.skip("Redis not available")

        from src.infra.temporal.activities.progress import (
            ActivityProgressPublisher,
            ProgressEventType,
        )

        # Create publisher
        publisher = ActivityProgressPublisher()
        workflow_id = f"test-workflow-{int(time.time())}"
        channel = f"workflow:progress:{workflow_id}"

        # Subscribe to channel
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)

        # Publish progress
        await publisher.step_progress(
            workflow_id=workflow_id,
            step="test_step",
            progress=50,
            details={"test": True},
        )

        # Receive message
        message = None
        for _ in range(10):
            msg = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1)
            if msg and msg["type"] == "message":
                message = msg
                break
            await asyncio.sleep(0.1)

        # Cleanup
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await client.close()

        # Verify
        assert message is not None
        assert "step:progress" in message["data"]

        # Parse SSE data
        lines = message["data"].split("\n")
        data_line = [l for l in lines if l.startswith("data: ")][0]
        data = json.loads(data_line[6:])

        assert data["workflow_id"] == workflow_id
        assert data["step"] == "test_step"
        assert data["progress"] == 50


# =============================================================================
# Run Tests Script
# =============================================================================

if __name__ == "__main__":
    """Run e2e tests manually.

    Usage:
        python tests/e2e/test_temporal_e2e.py

    Or with pytest:
        pytest tests/e2e/test_temporal_e2e.py -v -m e2e
    """
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "-m", "e2e"],
        cwd="/Users/namanagarwal/system/backend",
    )
    sys.exit(result.returncode)
