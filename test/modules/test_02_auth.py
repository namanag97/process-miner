
import pytest
from test_config import BASE_URL, API_V1, TEST_USER, context

def test_register(api_client):
    """Test user registration"""
    url = f"{API_V1}/auth/register"
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
        "name": TEST_USER["name"]
    }
    response = api_client.post(url, json=payload)
    # 201 Created or 400/409 if already exists (idempotency for tests)
    if response.status_code == 400 and "already registered" in response.text:
        # User exists, that's fine for subsequent tests
        assert True
    elif response.status_code == 409: # Conflict
        assert True
    else:
        assert response.status_code in [201, 200]
        data = response.json()
        # Save tokens if returned on register
        if "access_token" in data:
            context.access_token = data["access_token"]
            context.refresh_token = data.get("refresh_token")

def test_login(api_client):
    """Test user login"""
    url = f"{API_V1}/auth/login"
    payload = {
        "email": TEST_USER["email"],
        "password": TEST_USER["password"]
    }
    # Using JSON for login
    response = api_client.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    
    # Store in context
    context.access_token = data["access_token"]
    context.refresh_token = data.get("refresh_token")

def test_get_me(api_client):
    """Test get current user profile"""
    url = f"{API_V1}/auth/me"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["email"] == TEST_USER["email"]
    
    # Store IDs for hierarchy tests
    context.user_id = data["user"]["id"]
    # If user has organizations/workspaces, grab the first one
    if "organizations" in data and data["organizations"] and len(data["organizations"]) > 0:
        context.org_id = data["organizations"][0]["id"]
    
    # We might need to check other fields if the API returns them nested or separate

def test_refresh_token(api_client):
    """Test token refresh"""
    if not context.refresh_token:
        pytest.skip("No refresh token available")
        
    url = f"{API_V1}/auth/refresh"
    payload = {"refresh_token": context.refresh_token}
    response = api_client.post(url, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    # Update context
    context.access_token = data["access_token"]
