
import pytest
from test_config import API_V1, context

# Skip all if no auth
@pytest.fixture(autouse=True)
def check_auth():
    if not context.access_token:
        pytest.skip("Skipping protected tests due to missing access token")

def test_list_organizations(api_client):
    """Test listing user organizations"""
    url = f"{API_V1}/organizations/"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)
    
    # If we have an org from login/profile, it should be here
    ids = [org["id"] for org in data["items"]]
    if context.org_id:
        assert context.org_id in ids
    elif len(ids) > 0:
        context.org_id = ids[0]

def test_create_organization(api_client):
    """Test creating a new organization"""
    url = f"{API_V1}/organizations/"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    payload = {"name": "Test Organization", "slug": "test-org"}
    response = api_client.post(url, json=payload, headers=headers)
    
    if response.status_code == 409:
        # Already exists, fetch and use
        # Logic to find it? For now assume list_organizations set it
        pass
    else:
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Organization"
        context.org_id = data["id"]

def test_get_organization(api_client):
    """Test getting organization details"""
    if not context.org_id:
        pytest.skip("No organization ID available")
        
    url = f"{API_V1}/organizations/{context.org_id}"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == context.org_id
