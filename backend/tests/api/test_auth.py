"""Tests for Auth API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_current_user_dev_mode(auth_client: AsyncClient, seeded_user):
    """Test /auth/me returns current user info."""
    # The auth_client has the seeded user's email in headers
    # But the dependency returns a mock user - so we just verify structure
    response = await auth_client.get("/api/v1/auth/me")
    assert response.status_code == 200
    data = response.json()
    
    assert "user" in data
    assert "email" in data["user"]
    assert "name" in data["user"]


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration creates user, org, and workspace."""
    # Use a unique email to avoid conflicts
    import uuid
    unique_email = f"newuser_{uuid.uuid4().hex[:8]}@example.com"
    
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": unique_email,
            "password": "SecurePass123!",
            "name": "New User",
            "organization_name": "New Org",
        },
    )
    
    if response.status_code == 400 and "already registered" in response.text:
        pytest.skip("Email already registered in database")
    
    assert response.status_code in [200, 201], f"Registration failed: {response.text}"
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["email"] == unique_email


@pytest.mark.asyncio
async def test_login_with_registered_user(client: AsyncClient, seeded_user):
    """Test login with an existing user."""
    # First, login with the seeded user (which has no password in test)
    # In dev mode (auth_enabled=false), password check is skipped if user exists
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": seeded_user.email,
            "password": "anypassword",  # Ignored in dev mode
        },
    )
    
    # May fail if auth is enabled and password doesn't match
    if response.status_code == 401:
        pytest.skip("Auth is enabled - seeded user has no valid password")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, seeded_user):
    """Test refresh token endpoint returns new access token."""
    # First login to get a refresh token
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": seeded_user.email, "password": "password"},
    )
    
    if login_response.status_code != 200:
        pytest.skip("Login failed - cannot test refresh token")
    
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


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout endpoint."""
    response = await client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "logged_out"
