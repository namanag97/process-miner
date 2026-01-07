"""Tests for Datasets API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_datasets(auth_client: AsyncClient, seeded_dataset_ready):
    """Test listing datasets returns user's datasets."""
    response = await auth_client.get("/api/v1/datasets")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1

    # Should contain our seeded dataset
    dataset_ids = [d["id"] for d in data["items"]]
    assert seeded_dataset_ready.id in dataset_ids


@pytest.mark.asyncio
async def test_get_dataset(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting a dataset returns full details."""
    response = await auth_client.get(f"/api/v1/datasets/{seeded_dataset_ready.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == seeded_dataset_ready.id
    assert data["name"] == seeded_dataset_ready.name
    assert data["status"] == seeded_dataset_ready.status
    assert data["total_cases"] == 3
    assert data["total_events"] == 9
    assert data["total_activities"] == 3


@pytest.mark.asyncio
async def test_get_dataset_statistics(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting dataset statistics."""
    response = await auth_client.get(f"/api/v1/datasets/{seeded_dataset_ready.id}/statistics")
    assert response.status_code == 200
    data = response.json()

    assert "total_cases" in data
    assert "total_events" in data
    assert "total_activities" in data
    assert data["total_cases"] == 3
    assert data["total_events"] == 9


@pytest.mark.asyncio
async def test_get_dataset_cases(auth_client: AsyncClient, seeded_dataset_ready):
    """Test listing cases in a dataset."""
    response = await auth_client.get(f"/api/v1/datasets/{seeded_dataset_ready.id}/cases")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] == 3
    assert len(data["items"]) == 3


@pytest.mark.asyncio
async def test_get_dataset_events(auth_client: AsyncClient, seeded_dataset_ready):
    """Test listing events in a dataset."""
    response = await auth_client.get(f"/api/v1/datasets/{seeded_dataset_ready.id}/events")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] == 9


@pytest.mark.asyncio
async def test_get_dataset_activities(auth_client: AsyncClient, seeded_dataset_ready):
    """Test listing activities in a dataset."""
    response = await auth_client.get(f"/api/v1/datasets/{seeded_dataset_ready.id}/activities")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    # Should have Start, Process, End
    assert len(data["items"]) >= 3


@pytest.mark.asyncio
async def test_get_dataset_variants(auth_client: AsyncClient, seeded_dataset_ready):
    """Test listing process variants in a dataset."""
    response = await auth_client.get(f"/api/v1/datasets/{seeded_dataset_ready.id}/variants")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_delete_dataset(auth_client: AsyncClient, seeded_project, db_session):
    """Test deleting a dataset."""
    from src.features.process_mining.models import Dataset, DatasetStatus

    # Create a dataset to delete
    dataset = Dataset(
        project_id=seeded_project.id,
        name="To Delete",
        source_format="csv",
        source_file="test.csv",
        status=DatasetStatus.PENDING.value,
    )
    db_session.add(dataset)
    await db_session.commit()
    await db_session.refresh(dataset)

    # Delete it
    response = await auth_client.delete(f"/api/v1/datasets/{dataset.id}")
    assert response.status_code == 200

    # Verify it's gone
    get_response = await auth_client.get(f"/api/v1/datasets/{dataset.id}")
    assert get_response.status_code == 404
