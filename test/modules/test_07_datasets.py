
import pytest
import time
import os
from test_config import API_V1, context

@pytest.fixture(autouse=True)
def check_auth():
    if not context.access_token:
        pytest.skip("Skipping protected tests due to missing access token")

def test_upload_dataset(api_client):
    """Test uploading a dataset file"""
    if not context.project_id:
        pytest.skip("No project ID available")
        
    url = f"{API_V1}/datasets/"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    
    # Use the sample log file if it exists, otherwise create a dummy one
    sample_file = "/Users/namanagarwal/system/backend/sample_log.csv"
    if not os.path.exists(sample_file):
        with open("dummy_log.csv", "w") as f:
            f.write("case_id,activity,timestamp\n1,A,2023-01-01T10:00:00\n1,B,2023-01-01T11:00:00")
        sample_file = "dummy_log.csv"
        
    files = {
        "file": ("test_log.csv", open(sample_file, "rb"), "text/csv")
    }
    data = {
        "project_id": context.project_id,
        "description": "Test Dataset"
    }
    
    response = api_client.post(url, headers=headers, files=files, data=data)
    if response.status_code not in [200, 201]:
        print(f"Dataset Upload Failed: {response.status_code} - {response.text}")
    assert response.status_code in [200, 201]
    data = response.json()
    context.dataset_id = data["id"]
    context.dataset_uploaded = True

def test_get_dataset_columns(api_client):
    """Test getting dataset columns for mapping"""
    if not context.dataset_id:
        pytest.skip("No dataset ID available")
        
    url = f"{API_V1}/datasets/{context.dataset_id}/columns"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    
    # Wait for initial processing if needed (checking if job completed)
    # Ideally we should poll the job, but for simplicitly we assume sync or fast async
    time.sleep(2) 
    
    response = api_client.get(url, headers=headers)
    assert response.status_code == 200
    data = response.json()
    print(f"Detected Columns: {[c['name'] for c in data['columns']]}")
    assert len(data["columns"]) >= 3

def test_map_dataset(api_client):
    """Test mapping dataset columns"""
    if not context.dataset_id:
        pytest.skip("No dataset ID available")
        
    url_get = f"{API_V1}/datasets/{context.dataset_id}"
    headers = {"Authorization": f"Bearer {context.access_token}"}

    # Wait for dataset to be processed (columnd detection) and ready for mapping
    import time
    max_retries = 30
    for _ in range(max_retries):
        resp = api_client.get(url_get, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        print(f"Dataset Status: {data['status']}")
        if data["status"] in ["awaiting_mapping", "error"]:
            if data["status"] == "error":
                pytest.fail(f"Dataset processing failed: {data.get('error_message')}")
            break
        time.sleep(1)
    else:
        pytest.fail("Timeout waiting for dataset to be ready for mapping")

    url = f"{API_V1}/datasets/{context.dataset_id}/mapping"

    # Get available columns to map correctly (sample_log.csv vs dummy_log.csv)
    url_cols = f"{API_V1}/datasets/{context.dataset_id}/columns"
    resp_cols = api_client.get(url_cols, headers=headers)
    assert resp_cols.status_code == 200
    available_cols = [c['name'] for c in resp_cols.json()['columns']]
    print(f"Mapping using columns: {available_cols}")

    # Helper to find column case-insensitive
    def find_col(keywords, default):
        for col in available_cols:
            if any(k in col.lower() for k in keywords):
                return col
        return default

    # Basic mapping based on standard names or XES standard
    payload = {
        "case_id_column": find_col(["case", "trace", "id"], "case_id"),
        "activity_column": find_col(["concept:name", "activity", "action"], "activity"),
        "timestamp_column": find_col(["time:timestamp", "timestamp", "date"], "timestamp")
    }
    
    response = api_client.post(url, json=payload, headers=headers)
    if response.status_code != 200:
        print(f"Mapping Failed: {response.status_code} - {response.text}")
    assert response.status_code == 200
    context.dataset_mapped = True

def test_ingest_dataset(api_client):
    """Test triggering ingestion"""
    if not context.dataset_id or not context.dataset_mapped:
        pytest.skip("Dataset not ready for ingestion")
        
    url = f"{API_V1}/datasets/{context.dataset_id}/ingest"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    
    response = api_client.post(url, headers=headers)
    assert response.status_code in [200, 202]
    
    # Store job ID if returned, to poll
    data = response.json()
    if "job_id" in data:
        context.job_id = data["job_id"]
    
    context.dataset_ingested = True

def test_poll_ingestion(api_client):
    """Poll for ingestion completion"""
    if not context.dataset_id:
        pytest.skip("No dataset ID available")
        
    # Poll dataset status until READY or failed
    url = f"{API_V1}/datasets/{context.dataset_id}"
    headers = {"Authorization": f"Bearer {context.access_token}"}
    
    max_retries = 30
    for _ in range(max_retries):
        response = api_client.get(url, headers=headers)
        assert response.status_code == 200
        data = response.json()
        if data["status"] == "READY":
            break
        if data["status"] == "FAILED":
            pytest.fail(f"Ingestion failed: {data.get('error_message')}")
        time.sleep(1)
    else:
        pytest.fail("Ingestion timed out")
