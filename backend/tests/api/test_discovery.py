"""Tests for Discovery API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_miners(auth_client: AsyncClient):
    """Test listing available mining algorithms."""
    response = await auth_client.get("/api/v1/discovery/miners")
    assert response.status_code == 200
    data = response.json()

    assert "algorithms" in data
    assert isinstance(data["algorithms"], list)
    assert len(data["algorithms"]) > 0

    # Should include common algorithms
    algorithm_names = [a["id"] for a in data["algorithms"]]
    assert "inductive" in algorithm_names
    assert "alpha" in algorithm_names


@pytest.mark.asyncio
async def test_discover_model_sync(auth_client: AsyncClient, seeded_dataset_ready):
    """Test discovering a process model in sync mode."""
    response = await auth_client.post(
        "/api/v1/discovery/discover",
        json={
            "dataset_id": seeded_dataset_ready.id,
            "algorithm": "inductive",
            "parameters": {},
        },
        params={"async_mode": False},
    )
    assert response.status_code == 200
    data = response.json()

    assert "model_id" in data
    assert data["algorithm"] == "inductive"
    assert "format" in data


@pytest.mark.asyncio
async def test_list_models(auth_client: AsyncClient, seeded_process_model):
    """Test listing discovered process models."""
    response = await auth_client.get("/api/v1/discovery/models")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1

    # Should contain our seeded model
    model_ids = [m["id"] for m in data["items"]]
    assert seeded_process_model.id in model_ids


@pytest.mark.asyncio
async def test_get_model(auth_client: AsyncClient, seeded_process_model):
    """Test getting a process model's details."""
    response = await auth_client.get(f"/api/v1/discovery/models/{seeded_process_model.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == seeded_process_model.id
    assert data["name"] == seeded_process_model.name
    assert data["algorithm"] == seeded_process_model.algorithm
    assert data["model_format"] == seeded_process_model.model_format


@pytest.mark.asyncio
async def test_delete_model(auth_client: AsyncClient, seeded_dataset_ready, db_session):
    """Test deleting a process model."""
    from src.features.process_mining.models import ProcessModel

    # Create a model to delete
    model = ProcessModel(
        dataset_id=seeded_dataset_ready.id,
        name="To Delete",
        algorithm="inductive",
        model_format="petri_net",
    )
    db_session.add(model)
    await db_session.commit()
    await db_session.refresh(model)

    # Delete it
    response = await auth_client.delete(f"/api/v1/discovery/models/{model.id}")
    assert response.status_code == 200

    # Verify it's gone
    get_response = await auth_client.get(f"/api/v1/discovery/models/{model.id}")
    assert get_response.status_code == 404
