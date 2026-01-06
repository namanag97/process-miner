"""Tests for Analytics API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_bottlenecks(auth_client: AsyncClient, seeded_dataset_ready):
    """Test detecting bottlenecks in a process."""
    response = await auth_client.get(
        f"/api/v1/analytics/datasets/{seeded_dataset_ready.id}/bottlenecks"
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "bottlenecks" in data
    assert isinstance(data["bottlenecks"], list)


@pytest.mark.asyncio
async def test_get_rework(auth_client: AsyncClient, seeded_dataset_ready):
    """Test analyzing rework patterns."""
    response = await auth_client.get(
        f"/api/v1/analytics/datasets/{seeded_dataset_ready.id}/rework"
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "rework_cases" in data or "total_rework" in data


@pytest.mark.asyncio
async def test_get_service_times(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting service time statistics."""
    response = await auth_client.get(
        f"/api/v1/analytics/datasets/{seeded_dataset_ready.id}/service-times"
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "activities" in data or "service_times" in data


@pytest.mark.asyncio
async def test_get_cycle_time(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting cycle time statistics."""
    response = await auth_client.get(
        f"/api/v1/analytics/datasets/{seeded_dataset_ready.id}/cycle-time"
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "mean" in data or "median" in data


@pytest.mark.asyncio
async def test_get_throughput(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting throughput metrics."""
    response = await auth_client.get(
        f"/api/v1/analytics/datasets/{seeded_dataset_ready.id}/throughput"
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "throughput" in data or "cases_per_day" in data


@pytest.mark.asyncio
async def test_get_performance_dashboard(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting comprehensive performance dashboard."""
    response = await auth_client.get(
        f"/api/v1/analytics/datasets/{seeded_dataset_ready.id}/performance"
    )
    assert response.status_code == 200
    data = response.json()
    
    # Should have multiple performance metrics
    assert isinstance(data, dict)
    assert len(data) > 0
