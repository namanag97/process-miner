"""Tests for Projects API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_projects(auth_client: AsyncClient, seeded_project):
    """Test listing projects returns user's projects."""
    response = await auth_client.get("/api/v1/projects")
    assert response.status_code == 200
    data = response.json()

    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1

    # Should contain our seeded project
    project_ids = [p["id"] for p in data["items"]]
    assert seeded_project.id in project_ids


@pytest.mark.asyncio
async def test_get_project(auth_client: AsyncClient, seeded_project, seeded_dataset_ready):
    """Test getting a project returns details with datasets."""
    response = await auth_client.get(f"/api/v1/projects/{seeded_project.id}")
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == seeded_project.id
    assert data["name"] == seeded_project.name
    assert "datasets" in data


@pytest.mark.asyncio
async def test_create_project(auth_client: AsyncClient, seeded_workspace):
    """Test creating a new project."""
    response = await auth_client.post(
        f"/api/v1/projects?workspace_id={seeded_workspace.id}",
        json={
            "name": "New Test Project",
            "description": "Created in test",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["name"] == "New Test Project"
    assert data["description"] == "Created in test"
    assert "id" in data


@pytest.mark.asyncio
async def test_update_project(auth_client: AsyncClient, seeded_project):
    """Test updating a project."""
    response = await auth_client.put(
        f"/api/v1/projects/{seeded_project.id}",
        json={
            "name": "Updated Project Name",
            "description": "Updated description",
        },
    )
    assert response.status_code == 200
    data = response.json()

    assert data["id"] == seeded_project.id
    assert data["name"] == "Updated Project Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_project(auth_client: AsyncClient, seeded_workspace, db_session):
    """Test deleting a project."""
    from src.infra.models import Project

    # Create a project to delete
    project = Project(
        workspace_id=seeded_workspace.id,
        name="To Delete",
        description="Will be deleted",
    )
    db_session.add(project)
    await db_session.commit()
    await db_session.refresh(project)

    # Delete it
    response = await auth_client.delete(f"/api/v1/projects/{project.id}")
    assert response.status_code == 200

    # Verify it's gone
    get_response = await auth_client.get(f"/api/v1/projects/{project.id}")
    assert get_response.status_code == 404
