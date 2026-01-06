
import pytest
from test_config import API_V1, context

@pytest.fixture(autouse=True)
def check_auth():
    if not context.access_token:
        pytest.skip("Skipping protected tests due to missing access token")

def test_conformance_check(api_client):
    """Test standard conformance checking"""
    if not context.dataset_id or not context.dataset_ingested or not context.model_id:
        pytest.skip("Prerequisites (dataset, model) not met")
        
    url = f"{API_V1}/conformance/check"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    payload = {
        "dataset_id": context.dataset_id,
        "model_id": context.model_id
    }
    
    response = api_client.post(url, json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "fitness" in data
    assert "precision" in data
