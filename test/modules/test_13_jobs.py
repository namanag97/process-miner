
import pytest
from test_config import API_V1, context

@pytest.fixture(autouse=True)
def check_auth():
    if not context.access_token:
        pytest.skip("Skipping protected tests due to missing access token")

def test_list_jobs(api_client):
    """Test listing jobs"""
    url = f"{API_V1}/jobs"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data["items"], list)

def test_get_job(api_client):
    """Test getting a specific job"""
    if not context.job_id:
        # Try to find one from list if context is empty
        url_list = f"{API_V1}/jobs"
        headers = {"Authorization": f"Bearer {context.access_token}"}
        resp = api_client.get(url_list, headers=headers)
        if resp.status_code == 200 and len(resp.json()["items"]) > 0:
            context.job_id = resp.json()["items"][0]["id"]
    
    if not context.job_id:
        pytest.skip("No job ID available")
        
    url = f"{API_V1}/jobs/{context.job_id}"
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == context.job_id
