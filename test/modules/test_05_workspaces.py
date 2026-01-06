
import pytest
from test_config import API_V1, context

@pytest.fixture(autouse=True)
def check_auth():
    if not context.access_token:
        pytest.skip("Skipping protected tests due to missing access token")

def test_create_workspace(api_client):
    """Test creating a workspace"""
    if not context.org_id:
        pytest.skip("No organization ID available")
        
    url = f"{API_V1}/workspaces"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    payload = {
        "name": "Test Workspace",
        "description": "Created by automated tests"
    }
    params = {"org_id": context.org_id}
    response = api_client.post(url, json=payload, headers=headers, params=params)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Workspace"
    context.workspace_id = data["id"]

def test_list_workspaces(api_client):
    """Test listing workspaces"""
    url = f"{API_V1}/workspaces"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    params = {"organization_id": context.org_id} if context.org_id else {}
    response = api_client.get(url, headers=headers, params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    
    found = False
    for ws in data["items"]:
        if ws["id"] == context.workspace_id:
            found = True
            break
    assert found

def test_get_workspace(api_client):
    """Test getting workspace details"""
    if not context.workspace_id:
        pytest.skip("No workspace ID available")
        
    url = f"{API_V1}/workspaces/{context.workspace_id}"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == context.workspace_id
