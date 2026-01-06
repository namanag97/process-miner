
import pytest
from test_config import API_V1, context

@pytest.fixture(autouse=True)
def check_auth():
    if not context.access_token:
        pytest.skip("Skipping protected tests due to missing access token")

def test_create_project(api_client):
    """Test creating a project"""
    if not context.workspace_id:
        pytest.skip("No workspace ID available")
        
    url = f"{API_V1}/projects/"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    payload = {
        "name": "Test Project",
        "workspace_id": context.workspace_id,
        "description": "Created by automated tests"
    }
    response = api_client.post(url, json=payload, headers=headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    context.project_id = data["id"]

def test_list_projects(api_client):
    """Test listing projects"""
    url = f"{API_V1}/projects/"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    params = {"workspace_id": context.workspace_id} if context.workspace_id else {}
    response = api_client.get(url, headers=headers, params=params)
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) > 0
    
    found = False
    for proj in data["items"]:
        if proj["id"] == context.project_id:
            found = True
            break
    assert found

def test_get_project(api_client):
    """Test getting project details"""
    if not context.project_id:
        pytest.skip("No project ID available")
        
    url = f"{API_V1}/projects/{context.project_id}"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == context.project_id
