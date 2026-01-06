"""Tests for Auth API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_current_user_dev_mode(auth_client: AsyncClient, seeded_user):
    """Test /auth/me returns current user info in dev mode."""
    response = await auth_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    
    assert "user" in data
    assert data["user"]["email"] == seeded_user.email
    assert data["user"]["name"] == seeded_user.name


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration creates user, org, and workspace."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "name": "New User",
            "organization_name": "New Org",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["email"] == "newuser@example.com"
    assert data["user"]["name"] == "New User"


@pytest.mark.asyncio
async def test_login_dev_mode(client: AsyncClient, seeded_user):
    """Test login in dev mode accepts any credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "any@example.com",
            "password": "anypassword",
        },
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    """Test refresh token endpoint returns new access token."""
    # First login to get a refresh token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "password"},
    )
    assert login_response.status_code == 200
    refresh_token = login_response.json()["refresh_token"]
    
    # Use refresh token to get new access token
    response = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data
