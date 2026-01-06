
import pytest
import time
from test_config import API_V1, context

@pytest.fixture(autouse=True)
def check_auth():
    if not context.access_token:
        pytest.skip("Skipping protected tests due to missing access token")

def test_list_miners(api_client):
    """Test listing available miners"""
    url = f"{API_V1}/discovery/miners"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_discover_process(api_client):
    """Test discovering a process model"""
    if not context.dataset_id or not context.dataset_ingested:
        pytest.skip("No ingested dataset available")
        
    url = f"{API_V1}/discovery/discover"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    payload = {
        "dataset_id": context.dataset_id,
        "miner_type": "inductive" # Default miner
    }
    
    response = api_client.post(url, json=payload, headers=headers)
    assert response.status_code in [200, 202]
    data = response.json()
    
    if response.status_code == 200 and "model_id" in data:
        context.model_id = data["model_id"]
    elif response.status_code == 202 and "job_id" in data:
        # Need to poll job
        job_id = data["job_id"]
        # Poll code...
        pass
    else:
        # Check if model object returned directly
        if "id" in data:
            context.model_id = data["id"]

def test_get_model(api_client):
    """Test getting a discovered model"""
    if not context.model_id:
        pytest.skip("No model ID available")
        
    url = f"{API_V1}/discovery/models/{context.model_id}"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == context.model_id
