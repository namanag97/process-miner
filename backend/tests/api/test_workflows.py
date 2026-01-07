"""Tests for Workflows API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_workflow_templates(auth_client: AsyncClient):
    """Test listing workflow templates."""
    response = await auth_client.get("/api/v1/workflows/templates")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_workflow(auth_client: AsyncClient):
    """Test creating a workflow."""
    response = await auth_client.post(
        "/api/v1/workflows",
        json={
            "name": "Test Workflow",
            "steps": [
                {
                    "name": "discovery",
                    "type": "discovery",
                    "params": {"algorithm": "inductive"},
                }
            ],
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert "id" in data
    assert data["name"] == "Test Workflow"


@pytest.mark.asyncio
async def test_list_workflows(auth_client: AsyncClient):
    """Test listing workflows."""
    response = await auth_client.get("/api/v1/workflows")
    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
