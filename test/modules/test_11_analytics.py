
import pytest
from test_config import API_V1, context

@pytest.fixture(autouse=True)
def check_auth():
    if not context.access_token:
        pytest.skip("Skipping protected tests due to missing access token")

def test_get_bottlenecks(api_client):
    """Test bottleneck detection"""
    if not context.dataset_id or not context.dataset_ingested:
        pytest.skip("No ingested dataset available")
        
    url = f"{API_V1}/analytics/datasets/{context.dataset_id}/bottlenecks"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_rework(api_client):
    """Test rework analysis"""
    if not context.dataset_id or not context.dataset_ingested:
        pytest.skip("No ingested dataset available")
        
    url = f"{API_V1}/analytics/datasets/{context.dataset_id}/rework"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200

def test_get_statistics(api_client):
    """Test dataset statistics"""
    if not context.dataset_id or not context.dataset_ingested:
        pytest.skip("No ingested dataset available")
        
    url = f"{API_V1}/datasets/{context.dataset_id}/statistics"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "cases" in data
    assert "events" in data
