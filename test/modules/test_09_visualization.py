
import pytest
from test_config import API_V1, context

@pytest.fixture(autouse=True)
def check_auth():
    if not context.access_token:
        pytest.skip("Skipping protected tests due to missing access token")

def test_get_dfg(api_client):
    """Test getting Directly-Follows Graph"""
    if not context.dataset_id or not context.dataset_ingested:
        pytest.skip("No ingested dataset available")
        
    url = f"{API_V1}/visualization/{context.dataset_id}/dfg"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "edges" in data

def test_get_model_svg(api_client):
    """Test getting SVG for model"""
    if not context.model_id:
        pytest.skip("No model ID available")
        
    url = f"{API_V1}/visualization/models/{context.model_id}/svg"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    # Check 200 OK. Content might be SVG string
    assert response.status_code == 200
    assert "<svg" in response.text
