import pytest
from httpx import AsyncClient
import io

@pytest.mark.asyncio
async def test_upload_file(client: AsyncClient):
    # 1. Create User
    create_response = await client.post("/api/users")
    user_id = create_response.json()["id"]

    # 2. Upload File
    file_content = b"case_id,activity,timestamp\n1,A,2023-01-01T10:00:00\n1,B,2023-01-01T11:00:00"
    files = {"file": ("test.csv", file_content, "text/csv")}
    headers = {"X-User-ID": user_id}
    
    response = await client.post("/api/uploads", files=files, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "upload_id" in data
    assert data["filename"] == "test.csv"
    assert "columns" in data

@pytest.mark.asyncio
async def test_upload_without_user_header(client: AsyncClient):
    file_content = b"header\ndata"
    files = {"file": ("test.csv", file_content, "text/csv")}
    
    response = await client.post("/api/uploads", files=files)
    # Depending on implementation, it might be 403 or 422 if header is missing
    # In uploads.py: x_user_id: Annotated[str | None, Header()] = None
    # If None, it raises HTTPException(400, "User ID required") or similar logic
    # Let's check impl: 
    # if not x_user_id: raise HTTPException(status_code=401, detail="Missing X-User-ID header")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_upload(client: AsyncClient):
    """Test getting an upload by ID."""
    # Create user and upload
    create_response = await client.post("/api/users")
    user_id = create_response.json()["id"]
    
    file_content = b"case_id,activity,timestamp\n1,A,2023-01-01T10:00:00"
    files = {"file": ("test.csv", file_content, "text/csv")}
    headers = {"X-User-ID": user_id}
    
    upload_response = await client.post("/api/uploads", files=files, headers=headers)
    upload_id = upload_response.json()["upload_id"]
    
    # Get the upload
    response = await client.get(f"/api/uploads/{upload_id}", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["upload_id"] == upload_id
    assert data["filename"] == "test.csv"


@pytest.mark.asyncio
async def test_get_upload_columns(client: AsyncClient):
    """Test getting columns for an upload."""
    # Create user and upload
    create_response = await client.post("/api/users")
    user_id = create_response.json()["id"]
    
    file_content = b"case_id,activity,timestamp\n1,A,2023-01-01T10:00:00"
    files = {"file": ("test.csv", file_content, "text/csv")}
    headers = {"X-User-ID": user_id}
    
    upload_response = await client.post("/api/uploads", files=files, headers=headers)
    upload_id = upload_response.json()["upload_id"]
    
    # Get columns
    response = await client.get(f"/api/uploads/{upload_id}/columns", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "columns" in data
    assert len(data["columns"]) == 3  # case_id, activity, timestamp


@pytest.mark.asyncio 
async def test_delete_upload(client: AsyncClient):
    """Test deleting an upload."""
    # Create user and upload
    create_response = await client.post("/api/users")
    user_id = create_response.json()["id"]
    
    file_content = b"case_id,activity,timestamp\n1,A,2023-01-01T10:00:00"
    files = {"file": ("test.csv", file_content, "text/csv")}
    headers = {"X-User-ID": user_id}
    
    upload_response = await client.post("/api/uploads", files=files, headers=headers)
    upload_id = upload_response.json()["upload_id"]
    
    # Delete the upload
    response = await client.delete(f"/api/uploads/{upload_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"
    
    # Verify it's gone
    get_response = await client.get(f"/api/uploads/{upload_id}", headers=headers)
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_upload_unsupported_file_type(client: AsyncClient):
    """Test uploading unsupported file type."""
    create_response = await client.post("/api/users")
    user_id = create_response.json()["id"]
    
    file_content = b"some content"
    files = {"file": ("test.txt", file_content, "text/plain")}
    headers = {"X-User-ID": user_id}
    
    response = await client.post("/api/uploads", files=files, headers=headers)
    assert response.status_code == 400
