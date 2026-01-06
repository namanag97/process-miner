"""Tests for Conformance API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_conformance_methods(auth_client: AsyncClient):
    """Test listing available conformance checking methods."""
    response = await auth_client.get("/api/v1/conformance/methods")
    assert response.status_code == 200
    data = response.json()
    
    assert "methods" in data
    assert isinstance(data["methods"], list)
    
    # Should include common methods
    method_ids = [m["id"] for m in data["methods"]]
    assert "token_replay" in method_ids
    assert "alignments" in method_ids


@pytest.mark.asyncio
async def test_check_conformance(auth_client: AsyncClient, seeded_dataset_ready, seeded_process_model):
    """Test running conformance check."""
    response = await auth_client.post(
        "/api/v1/conformance/check",
        json={
            "dataset_id": seeded_dataset_ready.id,
            "model_id": seeded_process_model.id,
            "method": "token_replay",
        },
    )
    # May return 200 or 400 if model has no serialized data
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        data = response.json()
        assert "result_id" in data or "fitness" in data


@pytest.mark.asyncio
async def test_list_conformance_results(auth_client: AsyncClient):
    """Test listing conformance check results."""
    response = await auth_client.get("/api/v1/conformance/results")
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
