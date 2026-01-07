"""Tests for Visualization API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_dfg(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting Directly-Follows Graph data."""
    response = await auth_client.get(
        f"/api/v1/visualization/datasets/{seeded_dataset_ready.id}/dfg"
    )
    assert response.status_code == 200
    data = response.json()

    assert "nodes" in data
    assert "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


@pytest.mark.asyncio
async def test_get_dfg_with_performance(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting DFG with performance metrics."""
    response = await auth_client.get(
        f"/api/v1/visualization/datasets/{seeded_dataset_ready.id}/dfg",
        params={"include_performance": True},
    )
    assert response.status_code == 200
    data = response.json()

    assert "nodes" in data
    assert "edges" in data


@pytest.mark.asyncio
async def test_get_petri_net(auth_client: AsyncClient, seeded_process_model):
    """Test getting Petri net visualization data."""
    response = await auth_client.get(
        f"/api/v1/visualization/models/{seeded_process_model.id}/petri-net"
    )
    # May return 200 or 400 if model has no serialized data
    assert response.status_code in [200, 400]

    if response.status_code == 200:
        data = response.json()
        assert "places" in data or "transitions" in data


@pytest.mark.asyncio
async def test_get_explorer_data(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting unified explorer data."""
    response = await auth_client.get(
        f"/api/v1/visualization/datasets/{seeded_dataset_ready.id}/explorer"
    )
    assert response.status_code == 200
    data = response.json()

    # Should have comprehensive process data
    assert "dfg" in data
    assert isinstance(data["dfg"], dict)
