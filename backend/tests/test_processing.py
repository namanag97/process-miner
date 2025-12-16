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

    # 4. Start Processing (Mock Celery task to avoid actual execution)
    mock_task = MagicMock()
    mock_task.id = "mock-celery-task-id"
    mock_task.delay.return_value = mock_task

    with patch("app.tasks.mining_tasks.run_mining_task") as mock_run:
        mock_run.delay.return_value = mock_task
        response = await client.post(f"/api/processing/mappings/{mapping_id}/process")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert "job_id" in data


@pytest.mark.asyncio
async def test_get_job_status(client: AsyncClient):
    """Test getting job status for a non-existent job returns 404."""
    response = await client.get("/api/processing/jobs/non-existent-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_processing_invalid_mapping(client: AsyncClient):
    """Test starting processing with invalid mapping returns 404."""
    with patch("app.tasks.mining_tasks.run_mining_task") as mock_run:
        response = await client.post("/api/processing/mappings/invalid-mapping-id/process")
        assert response.status_code == 404
