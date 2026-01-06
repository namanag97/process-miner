"""Tests for Jobs API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_jobs(auth_client: AsyncClient):
    """Test listing async jobs."""
    response = await auth_client.get("/api/v1/jobs")
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
