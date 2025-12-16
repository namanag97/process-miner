"""
Mappings endpoint tests.
"""

import pytest
from httpx import AsyncClient
import json


async def create_test_upload(client: AsyncClient) -> tuple[str, str]:
    """Helper to create a user and upload for testing."""
    # Create user
    user_response = await client.post("/api/users")
    user_id = user_response.json()["id"]
    
    # Upload file
    file_content = b"case_id,activity,timestamp,resource\n1,Start,2023-01-01T10:00:00,John\n1,End,2023-01-01T11:00:00,Jane"
    files = {"file": ("test.csv", file_content, "text/csv")}
    headers = {"X-User-ID": user_id}
    
    upload_response = await client.post("/api/uploads", files=files, headers=headers)
    upload_id = upload_response.json()["upload_id"]
    
    return user_id, upload_id


@pytest.mark.asyncio
async def test_create_mapping(client: AsyncClient):
    """Test creating a column mapping."""
    user_id, upload_id = await create_test_upload(client)
    
    mapping_data = {
        "case_id_column": "case_id",
        "activity_column": "activity",
        "timestamp_column": "timestamp",
        "resource_column": "resource",
    }
    
    response = await client.post(
        f"/api/mappings/uploads/{upload_id}/mappings",
        json=mapping_data,
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "mapping_id" in data
    assert data["upload_id"] == upload_id
    assert data["case_id_column"] == "case_id"
    assert data["activity_column"] == "activity"


@pytest.mark.asyncio
async def test_get_mapping(client: AsyncClient):
    """Test retrieving a mapping by ID."""
    user_id, upload_id = await create_test_upload(client)
    
    # Create mapping first
    mapping_data = {
        "case_id_column": "case_id",
        "activity_column": "activity",
        "timestamp_column": "timestamp",
    }
    create_response = await client.post(
        f"/api/mappings/uploads/{upload_id}/mappings",
        json=mapping_data,
    )
    mapping_id = create_response.json()["mapping_id"]
    
    # Get mapping
    response = await client.get(f"/api/mappings/{mapping_id}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["mapping_id"] == mapping_id
    assert data["case_id_column"] == "case_id"


@pytest.mark.asyncio
async def test_create_mapping_invalid_column(client: AsyncClient):
    """Test creating mapping with non-existent column."""
    user_id, upload_id = await create_test_upload(client)
    
    mapping_data = {
        "case_id_column": "nonexistent_column",
        "activity_column": "activity",
        "timestamp_column": "timestamp",
    }
    
    response = await client.post(
        f"/api/mappings/uploads/{upload_id}/mappings",
        json=mapping_data,
    )
    
    assert response.status_code == 400
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_mapping_not_found(client: AsyncClient):
    """Test getting a non-existent mapping."""
    response = await client.get("/api/mappings/nonexistent-id")
    assert response.status_code == 404
