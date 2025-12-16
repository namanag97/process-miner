import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    response = await client.post("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert isinstance(data["id"], str)

@pytest.mark.asyncio
async def test_get_current_user_info(client: AsyncClient):
    # 1. Create User
    create_response = await client.post("/api/users")
    user_id = create_response.json()["id"]

    # 2. Get Info
    response = await client.get(f"/api/users/me?user_id={user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert "created_at" in data

@pytest.mark.asyncio
async def test_get_non_existent_user(client: AsyncClient):
    response = await client.get("/api/users/me?user_id=non-existent-uuid")
    assert response.status_code == 404
