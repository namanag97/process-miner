import pytest
from httpx import AsyncClient
from fastapi import status

@pytest.mark.asyncio
async def test_operations_require_auth(client: AsyncClient):
    """Verify that operations endpoints now require authentication."""
    response = await client.get("/api/v1/operations/test-workflow")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

@pytest.mark.asyncio
async def test_legacy_auth_removed(client: AsyncClient):
    """Verify that the legacy MVP auth endpoint has been removed."""
    response = await client.get("/api/v1/auth/me/legacy")
    # Even if auth is disabled in settings, the route itself should be gone or 404
    assert response.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_405_METHOD_NOT_ALLOWED)

@pytest.mark.asyncio
async def test_operations_list_require_auth(client: AsyncClient):
    """Verify that listing operations require authentication."""
    response = await client.get("/api/v1/operations")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
