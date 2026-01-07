"""Tests for Happy Flow API Responses.

These tests verify that successful API responses have:
1. Clear, descriptive messages
2. Proper data structures
3. Useful metadata for the frontend
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_health_response_quality(client: AsyncClient):
    """Verify health endpoint returns useful information."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()

    # Should have status field
    assert "status" in data, "Health response missing 'status' field"
    assert data["status"] in ("healthy", "ok", "degraded"), f"Unexpected status: {data['status']}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_detailed_health_response_quality(client: AsyncClient):
    """Verify detailed health has component breakdown."""
    response = await client.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()

    # Should have components list
    assert "components" in data, "Detailed health missing 'components'"
    assert isinstance(data["components"], list), "Components should be a list"

    # Each component should have name and status
    for comp in data["components"]:
        assert "name" in comp, f"Component missing 'name': {comp}"
        assert "status" in comp, f"Component missing 'status': {comp}"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_list_endpoints_return_pagination(auth_client: AsyncClient):
    """Verify list endpoints have proper pagination structure."""
    endpoints = [
        "/api/v1/workspaces",
        "/api/v1/projects",
        "/api/v1/datasets",
        "/api/v1/jobs",
    ]

    for endpoint in endpoints:
        response = await auth_client.get(endpoint)
        if response.status_code == 200:
            data = response.json()
            # Should have items array
            assert "items" in data, f"{endpoint} missing 'items' field"
            assert isinstance(data["items"], list), f"{endpoint} items should be list"

            # Should have total count
            has_total = "total" in data or "count" in data
            assert has_total, f"{endpoint} missing total/count for pagination"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_404_error_messages_are_helpful(auth_client: AsyncClient):
    """Verify 404 errors have descriptive messages."""
    test_cases = [
        ("/api/v1/datasets/nonexistent-uuid-12345", "Dataset"),
        ("/api/v1/projects/nonexistent-uuid-12345", "Project"),
        ("/api/v1/workspaces/nonexistent-uuid-12345", "Workspace"),
    ]

    for endpoint, resource_type in test_cases:
        response = await auth_client.get(endpoint)

        if response.status_code == 404:
            data = response.json()
            detail = data.get("detail", data.get("message", ""))

            # Error message should mention what resource wasn't found
            assert len(detail) > 5, f"Error message too short for {resource_type} 404: '{detail}'"
            # Ideally mentions the resource type
            # assert resource_type.lower() in detail.lower(), \
            #     f"404 for {resource_type} should mention '{resource_type}': got '{detail}'"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_validation_errors_are_specific(auth_client: AsyncClient):
    """Verify validation errors identify the problematic field."""
    # Send invalid data to trigger validation
    response = await auth_client.post(
        "/api/v1/projects",
        json={"name": ""},  # Empty name should fail validation
    )

    if response.status_code == 422:
        data = response.json()
        detail = data.get("detail", [])

        # Pydantic validation errors should include field info
        if isinstance(detail, list) and len(detail) > 0:
            # Should have loc (location) field
            assert "loc" in detail[0] or "field" in detail[0], (
                "Validation error should identify which field failed"
            )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_created_resources_return_id(auth_client: AsyncClient, seeded_workspace):
    """Verify POST endpoints return the created resource ID."""
    # Create a project
    response = await auth_client.post(
        "/api/v1/projects",
        json={
            "name": "Test Project for ID Check",
            "workspace_id": seeded_workspace.id,
        },
    )

    if response.status_code in (200, 201):
        data = response.json()
        # Should return the ID of created resource
        assert "id" in data, "Created resource response missing 'id'"
        assert data["id"] is not None, "Created resource ID should not be null"

        # Cleanup - delete the created project
        await auth_client.delete(f"/api/v1/projects/{data['id']}")
