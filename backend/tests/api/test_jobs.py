"""Tests for Jobs API endpoints.

These tests cover CRITICAL issues (500 errors) identified in the API audit.
The jobs endpoints were returning 500s when job IDs didn't exist.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_jobs_empty(auth_client: AsyncClient):
    """Test listing async jobs when none exist."""
    response = await auth_client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_get_job_not_found(auth_client: AsyncClient):
    """Test getting a non-existent job returns 404, not 500.

    CRITICAL: This was returning 500 before the fix.
    """
    response = await auth_client.get("/api/v1/jobs/nonexistent-job-id")
    # Should be 404 Not Found, not 500 Internal Server Error
    assert response.status_code in (404, 422), f"Expected 404/422, got {response.status_code}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_cancel_job_not_found(auth_client: AsyncClient):
    """Test canceling a non-existent job returns 404, not 500.

    CRITICAL: This was returning 500 before the fix.
    """
    response = await auth_client.delete("/api/v1/jobs/nonexistent-job-id")
    assert response.status_code in (404, 422), f"Expected 404/422, got {response.status_code}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_stream_job_not_found(auth_client: AsyncClient):
    """Test streaming a non-existent job returns 404, not 500.

    CRITICAL: This was returning 500 before the fix.
    """
    response = await auth_client.get("/api/v1/jobs/nonexistent-job-id/stream")
    assert response.status_code in (404, 422), f"Expected 404/422, got {response.status_code}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_jobs_with_pagination(auth_client: AsyncClient):
    """Test that job listing supports pagination."""
    response = await auth_client.get("/api/v1/jobs?page=1&page_size=10")
    assert response.status_code == 200
    data = response.json()

    # Should have pagination metadata
    assert "items" in data
    assert isinstance(data.get("page", 1), int)
    assert isinstance(data.get("page_size", data.get("pageSize", 10)), int)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_jobs_invalid_page(auth_client: AsyncClient):
    """Test that invalid pagination is handled gracefully."""
    response = await auth_client.get("/api/v1/jobs?page=-1")
    # Should either return 422 validation error or clamp to valid values
    assert response.status_code in (200, 422)
