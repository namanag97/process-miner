
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
        # Already exists
        pass
    elif response.status_code == 422 and "already exists" in response.text:
        # Slug collision also returns 422
        pass
    else:
        if response.status_code == 422:
            print(f"Validation Error: {response.json()}")
        assert response.status_code == 201
        data = response.json()
        
    # If we are here, we might need to fetch the org_id if we didn't create it
    if not context.org_id:
        # Minimal fetch to get ID
        list_url = f"{API_V1}/organizations/"
        resp = api_client.get(list_url, headers=headers)
        if resp.status_code == 200:
            items = resp.json().get("items", [])
            for item in items:
                if item["slug"] == "test-org":
                    context.org_id = item["id"]
                    break

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
