"""Tests for Filtering API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_filter_options(auth_client: AsyncClient, seeded_dataset_ready):
    """Test getting available filter options for a dataset."""
    response = await auth_client.get(
        f"/api/v1/filtering/datasets/{seeded_dataset_ready.id}/options"
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "activities" in data or "time_range" in data


@pytest.mark.asyncio
async def test_preview_filter(auth_client: AsyncClient, seeded_dataset_ready):
    """Test previewing filter impact."""
    response = await auth_client.post(
        f"/api/v1/filtering/datasets/{seeded_dataset_ready.id}/preview",
        json={
            "filters": {
                "activities": {
                    "included": ["Start", "End"],
                    "excluded": [],
                }
            }
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "cases_retained" in data or "events_retained" in data


@pytest.mark.asyncio
async def test_apply_filter(auth_client: AsyncClient, seeded_dataset_ready):
    """Test applying a filter to create filtered log."""
    response = await auth_client.post(
        f"/api/v1/filtering/datasets/{seeded_dataset_ready.id}/apply",
        json={
            "name": "Filtered Log",
            "filters": {
                "activities": {
                    "included": ["Start", "Process", "End"],
                    "excluded": [],
                }
            },
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "id" in data or "filtered_dataset_id" in data


@pytest.mark.asyncio
async def test_get_filter_templates(auth_client: AsyncClient):
    """Test getting predefined filter templates."""
    response = await auth_client.get("/api/v1/filtering/templates")
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list) or isinstance(data, dict)
