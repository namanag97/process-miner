"""Tests for Workspaces API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_workspaces(auth_client: AsyncClient, seeded_workspace):
    """Test listing workspaces returns user's workspaces."""
    response = await auth_client.get("/api/v1/workspaces")
    assert response.status_code == 200
    data = response.json()
    
    assert "items" in data
    assert "total" in data
    assert data["total"] >= 1
    
    # Should contain our seeded workspace
    workspace_ids = [w["id"] for w in data["items"]]
    assert seeded_workspace.id in workspace_ids


@pytest.mark.asyncio
async def test_get_workspace(auth_client: AsyncClient, seeded_workspace, seeded_project):
    """Test getting a workspace returns details with projects."""
    response = await auth_client.get(f"/api/v1/workspaces/{seeded_workspace.id}")
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == seeded_workspace.id
    assert data["name"] == seeded_workspace.name
    assert "projects" in data
    
    # Should contain our seeded project
    project_ids = [p["id"] for p in data["projects"]]
    assert seeded_project.id in project_ids


@pytest.mark.asyncio
async def test_create_workspace(auth_client: AsyncClient, seeded_org):
    """Test creating a new workspace."""
    response = await auth_client.post(
        f"/api/v1/workspaces?org_id={seeded_org.id}",
        json={
            "name": "New Test Workspace",
            "description": "Created in test",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["name"] == "New Test Workspace"
    assert data["description"] == "Created in test"
    assert "id" in data


@pytest.mark.asyncio
async def test_update_workspace(auth_client: AsyncClient, seeded_workspace):
    """Test updating a workspace."""
    response = await auth_client.put(
        f"/api/v1/workspaces/{seeded_workspace.id}",
        json={
            "name": "Updated Workspace Name",
            "description": "Updated description",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == seeded_workspace.id
    assert data["name"] == "Updated Workspace Name"
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_workspace(auth_client: AsyncClient, seeded_org, seeded_user, db_session):
    """Test deleting a workspace."""
    from src.platform.models import Workspace, WorkspaceMember
    
    # Create a workspace to delete
    workspace = Workspace(
        org_id=seeded_org.id,
        name="To Delete",
        description="Will be deleted",
    )
    db_session.add(workspace)
    await db_session.flush()
    
    membership = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=seeded_user.id,
        role="owner",
    )
    db_session.add(membership)
    await db_session.commit()
    await db_session.refresh(workspace)
    
    # Delete it
    response = await auth_client.delete(f"/api/v1/workspaces/{workspace.id}")
    assert response.status_code == 200
    
    # Verify it's gone
    get_response = await auth_client.get(f"/api/v1/workspaces/{workspace.id}")
    assert get_response.status_code == 404
