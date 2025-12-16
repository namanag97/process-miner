import pytest
from httpx import AsyncClient
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_start_processing(client: AsyncClient):
    # 1. Create User
    user_res = await client.post("/api/users")
    user_id = user_res.json()["id"]

    # 2. Upload File
    file_content = b"case_id,activity,timestamp\n1,A,2023-01-01T10:00:00"
    files = {"file": ("test.csv", file_content, "text/csv")}
    upload_res = await client.post("/api/uploads", files=files, headers={"X-User-ID": user_id})
    upload_id = upload_res.json()["upload_id"]

    # 3. Create Mapping
    mapping_payload = {
        "case_id_column": "case_id",
        "activity_column": "activity",
        "timestamp_column": "timestamp",
        "timestamp_format": "ISO8601"
    }
    mapping_res = await client.post(f"/api/mappings/uploads/{upload_id}/mappings", json=mapping_payload)
    mapping_id = mapping_res.json()["mapping_id"]

    # 4. Start Processing (Mock background task to avoid actual execution)
    # We patch the BACKGROUND TASK adds, but for integration test we want to ensure endpoint returns 200
    # The actual background task execution is hard to test in simple async tests without widespread mocking
    # or waiting. Here we just test the endpoint response.
    
    with patch("app.routers.processing.run_mining_job") as mock_run:
        response = await client.post(f"/api/processing/mappings/{mapping_id}/process")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "job_id" in data
