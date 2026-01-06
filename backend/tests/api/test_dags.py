"""Tests for DAG API endpoints.

Tests workflow orchestration endpoints including:
- Template listing
- Definition CRUD
- Run triggering and management
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_templates(auth_client: AsyncClient):
    """Test listing predefined DAG templates."""
    response = await auth_client.get("/api/v1/dags/templates")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 5  # Should have at least 5 predefined templates
    
    # Check template structure
    template = data[0]
    assert "name" in template
    assert "display_name" in template
    assert "description" in template
    assert "step_count" in template
    assert "edge_count" in template


@pytest.mark.asyncio
async def test_list_templates_includes_data_ingestion(auth_client: AsyncClient):
    """Test that data_ingestion template is present."""
    response = await auth_client.get("/api/v1/dags/templates")
    assert response.status_code == 200
    
    data = response.json()
    template_names = [t["name"] for t in data]
    assert "data_ingestion" in template_names


@pytest.mark.asyncio
async def test_create_definition(auth_client: AsyncClient):
    """Test creating a custom DAG definition."""
    payload = {
        "name": "Test Custom DAG",
        "description": "A test workflow",
        "steps": [
            {"name": "step_a", "task_name": "validate_file", "default_params": {}},
            {"name": "step_b", "task_name": "detect_columns", "default_params": {}},
        ],
        "edges": [
            {"from_step": "step_a", "to_step": "step_b"}
        ]
    }
    
    response = await auth_client.post("/api/v1/dags/definitions", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == "Test Custom DAG"
    assert data["is_active"] is True
    assert len(data["steps"]) == 2
    assert len(data["edges"]) == 1


@pytest.mark.asyncio
async def test_create_definition_invalid_cycle(auth_client: AsyncClient):
    """Test that cyclic DAG definitions are rejected."""
    payload = {
        "name": "Cyclic DAG",
        "steps": [
            {"name": "step_a", "task_name": "validate_file"},
            {"name": "step_b", "task_name": "detect_columns"},
            {"name": "step_c", "task_name": "ingest_dataset"},
        ],
        "edges": [
            {"from_step": "step_a", "to_step": "step_b"},
            {"from_step": "step_b", "to_step": "step_c"},
            {"from_step": "step_c", "to_step": "step_a"},  # Creates cycle
        ]
    }
    
    response = await auth_client.post("/api/v1/dags/definitions", json=payload)
    assert response.status_code == 400
    assert "cycle" in response.json().get("detail", "").lower()


@pytest.mark.asyncio
async def test_create_definition_empty_steps_fails(auth_client: AsyncClient):
    """Test that DAG with no steps is rejected."""
    payload = {
        "name": "Empty DAG",
        "steps": [],
        "edges": []
    }
    
    response = await auth_client.post("/api/v1/dags/definitions", json=payload)
    # Should fail validation - Pydantic min_length=1
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_definitions(auth_client: AsyncClient):
    """Test listing DAG definitions."""
    # First create a definition
    payload = {
        "name": "List Test DAG",
        "steps": [{"name": "step_a", "task_name": "validate_file"}],
        "edges": []
    }
    await auth_client.post("/api/v1/dags/definitions", json=payload)
    
    # List definitions
    response = await auth_client.get("/api/v1/dags/definitions")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_definition(auth_client: AsyncClient):
    """Test getting a single DAG definition by ID."""
    # Create a definition
    payload = {
        "name": "Get Test DAG",
        "steps": [{"name": "step_a", "task_name": "validate_file"}],
        "edges": []
    }
    create_response = await auth_client.post("/api/v1/dags/definitions", json=payload)
    definition_id = create_response.json()["id"]
    
    # Get by ID
    response = await auth_client.get(f"/api/v1/dags/definitions/{definition_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == definition_id
    assert data["name"] == "Get Test DAG"


@pytest.mark.asyncio
async def test_get_definition_not_found(auth_client: AsyncClient):
    """Test getting a non-existent definition."""
    response = await auth_client.get("/api/v1/dags/definitions/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_trigger_run(auth_client: AsyncClient):
    """Test triggering a DAG run."""
    # Create a definition first
    payload = {
        "name": "Run Test DAG",
        "steps": [{"name": "step_a", "task_name": "validate_file"}],
        "edges": []
    }
    create_response = await auth_client.post("/api/v1/dags/definitions", json=payload)
    definition_id = create_response.json()["id"]
    
    # Trigger a run
    run_payload = {
        "definition_id": definition_id,
        "context": {"dataset_id": "test-dataset"},
        "step_params": {}
    }
    
    response = await auth_client.post("/api/v1/dags/runs", json=run_payload)
    assert response.status_code == 202
    
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"
    assert len(data["steps"]) == 1


@pytest.mark.asyncio
async def test_trigger_run_by_template_name(auth_client: AsyncClient):
    """Test triggering a DAG run using template name."""
    run_payload = {
        "definition_name": "discovery_only",
        "context": {"dataset_id": "test-dataset"},
        "step_params": {}
    }
    
    response = await auth_client.post("/api/v1/dags/runs", json=run_payload)
    assert response.status_code == 202
    
    data = response.json()
    assert "id" in data
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_list_runs(auth_client: AsyncClient):
    """Test listing DAG runs."""
    # Trigger a run first
    run_payload = {
        "definition_name": "discovery_only",
        "context": {}
    }
    await auth_client.post("/api/v1/dags/runs", json=run_payload)
    
    # List runs
    response = await auth_client.get("/api/v1/dags/runs")
    assert response.status_code == 200
    
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data


@pytest.mark.asyncio
async def test_get_run_status(auth_client: AsyncClient):
    """Test getting DAG run status with step details."""
    # Trigger a run
    run_payload = {"definition_name": "discovery_only", "context": {}}
    create_response = await auth_client.post("/api/v1/dags/runs", json=run_payload)
    run_id = create_response.json()["id"]
    
    # Get run status
    response = await auth_client.get(f"/api/v1/dags/runs/{run_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == run_id
    assert "status" in data
    assert "steps" in data
    assert isinstance(data["steps"], list)


@pytest.mark.asyncio
async def test_get_run_not_found(auth_client: AsyncClient):
    """Test getting a non-existent run."""
    response = await auth_client.get("/api/v1/dags/runs/nonexistent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_cancel_run(auth_client: AsyncClient):
    """Test cancelling a DAG run."""
    # Trigger a run first
    run_payload = {"definition_name": "data_ingestion", "context": {}}
    create_response = await auth_client.post("/api/v1/dags/runs", json=run_payload)
    run_id = create_response.json()["id"]
    
    # Cancel the run
    response = await auth_client.post(f"/api/v1/dags/runs/{run_id}/cancel")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "cancelled"
    assert data["run_id"] == run_id


@pytest.mark.asyncio
async def test_cancel_run_not_found(auth_client: AsyncClient):
    """Test cancelling a non-existent run."""
    response = await auth_client.post("/api/v1/dags/runs/nonexistent-id/cancel")
    assert response.status_code == 404
