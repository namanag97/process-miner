"""Tests for Health API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_liveness_probe(client: AsyncClient):
    """Test liveness probe returns 200."""
    response = await client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_readiness_probe(client: AsyncClient):
    """Test readiness probe returns 200 when DB is connected."""
    response = await client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_startup_probe(client: AsyncClient):
    """Test startup probe returns 200 once app is ready."""
    response = await client.get("/health/startup")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_detailed_health(client: AsyncClient):
    """Test detailed health endpoint returns component breakdown."""
    response = await client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "version" in data
    assert "uptime_seconds" in data
    assert "components" in data
    assert isinstance(data["components"], list)
    
    # Should have at least database component
    component_names = [c["name"] for c in data["components"]]
    assert "database" in component_names


@pytest.mark.asyncio
async def test_basic_health_check(client: AsyncClient):
    """Test basic health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
