#!/usr/bin/env python
"""E2E Test: Upload Flow

Tests the complete upload → validate → map → ingest flow via API.
"""

import os
import sys
import time
import requests
import tempfile

API_BASE = "http://localhost:8001/api/v1"
PROJECT_ID = "36bffd5f-bdce-4ebd-9b2d-fe00f89f2487"  # Test Project Fix

# Test CSV content
TEST_CSV = """case_id,activity,timestamp,resource
CASE-001,Order Received,2024-01-01 09:00:00,Alice
CASE-001,Validate Order,2024-01-01 09:15:00,Bob
CASE-001,Ship Order,2024-01-01 10:00:00,Charlie
CASE-001,Deliver Order,2024-01-02 14:00:00,David
CASE-002,Order Received,2024-01-01 10:00:00,Alice
CASE-002,Validate Order,2024-01-01 10:30:00,Eve
CASE-002,Reject Order,2024-01-01 11:00:00,Frank
CASE-003,Order Received,2024-01-02 08:00:00,Grace
CASE-003,Validate Order,2024-01-02 08:30:00,Alice
CASE-003,Ship Order,2024-01-02 09:00:00,Bob
CASE-003,Deliver Order,2024-01-03 16:00:00,Charlie
"""

def log(step: str, msg: str, data: dict = None):
    print(f"\n{'='*60}")
    print(f"📍 STEP {step}: {msg}")
    if data:
        for k, v in data.items():
            print(f"   {k}: {v}")
    print('='*60)

def log_error(msg: str, response=None):
    print(f"\n❌ ERROR: {msg}")
    if response is not None:
        print(f"   Status: {response.status_code}")
        try:
            print(f"   Body: {response.json()}")
        except:
            print(f"   Body: {response.text[:500]}")

def log_success(msg: str):
    print(f"✅ {msg}")

def main():
    print("\n" + "="*60)
    print("🚀 E2E UPLOAD FLOW TEST")
    print("="*60)
    
    # Step 1: Create temp CSV file
    log("1", "Creating test CSV file")
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write(TEST_CSV)
        csv_path = f.name
    log_success(f"Created: {csv_path}")
    
    try:
        # Step 2: Direct Upload
        log("2", "Uploading file via POST /datasets/")
        with open(csv_path, 'rb') as f:
            files = {'file': ('test_order_process.csv', f, 'text/csv')}
            data = {'project_id': PROJECT_ID}
            response = requests.post(f"{API_BASE}/datasets/", files=files, data=data)
        
        if response.status_code != 200:
            log_error("Upload failed", response)
            return 1
        
        result = response.json()
        dataset_id = result.get('id')
        log_success(f"Uploaded! Dataset ID: {dataset_id}")
        print(f"   Status: {result.get('status')}")
        
        # Step 3: Poll for validation to complete
        log("3", "Polling dataset status (waiting for validation)")
        max_wait = 30
        for i in range(max_wait):
            response = requests.get(f"{API_BASE}/datasets/{dataset_id}")
            if response.status_code != 200:
                log_error("Failed to get dataset", response)
                return 1
            
            status = response.json().get('status')
            print(f"   [{i+1}/{max_wait}] Status: {status}")
            
            if status == 'awaiting_mapping':
                log_success("Validation complete - ready for mapping!")
                break
            elif status == 'error':
                log_error("Dataset validation failed")
                print(f"   Error: {response.json().get('error_message')}")
                return 1
            elif status in ('ready', 'analyzing'):
                log_success(f"Dataset is {status}")
                break
            
            time.sleep(1)
        else:
            log_error(f"Timeout waiting for validation. Final status: {status}")
            # Continue anyway for debugging
        
        # Step 4: Get column preview
        log("4", "Fetching column preview")
        response = requests.get(f"{API_BASE}/datasets/{dataset_id}/preview?rows=5")
        if response.status_code == 200:
            preview = response.json()
            print(f"   Columns: {preview.get('columns', [])}")
            print(f"   Rows: {len(preview.get('rows', []))}")
            log_success("Preview fetched")
        else:
            log_error("Preview fetch failed (may not be ready)", response)
        
        # Step 5: Get column mapping suggestions
        log("5", "Getting column mapping suggestions")
        response = requests.get(f"{API_BASE}/datasets/{dataset_id}/columns")
        if response.status_code == 200:
            columns = response.json()
            print(f"   Detected columns: {[c.get('name') for c in columns.get('columns', [])]}")
            log_success("Columns detected")
        else:
            log_error("Column detection failed", response)
        
        # Step 6: Submit mapping and start ingestion
        log("6", "Submitting column mapping and starting ingestion")
        mapping = {
            "case_id_column": "case_id",
            "activity_column": "activity", 
            "timestamp_column": "timestamp",
            "resource_column": "resource"
        }
        response = requests.post(
            f"{API_BASE}/datasets/{dataset_id}/ingest",
            json=mapping
        )
        
        if response.status_code == 200:
            ingest_result = response.json()
            print(f"   Job ID: {ingest_result.get('id')}")
            log_success("Ingestion started!")
        else:
            log_error("Ingestion failed", response)
            # Try to see current status
            response = requests.get(f"{API_BASE}/datasets/{dataset_id}")
            if response.status_code == 200:
                print(f"   Current dataset status: {response.json().get('status')}")
        
        # Step 7: Poll for ingestion to complete
        log("7", "Polling for ingestion completion")
        for i in range(30):
            response = requests.get(f"{API_BASE}/datasets/{dataset_id}")
            if response.status_code != 200:
                log_error("Failed to get dataset", response)
                break
            
            data = response.json()
            status = data.get('status')
            print(f"   [{i+1}/30] Status: {status}")
            
            if status == 'ready':
                log_success("🎉 INGESTION COMPLETE!")
                print(f"   Total cases: {data.get('total_cases')}")
                print(f"   Total events: {data.get('total_events')}")
                print(f"   Total activities: {data.get('total_activities')}")
                break
            elif status == 'error':
                log_error("Ingestion failed")
                print(f"   Error: {data.get('error_message')}")
                break
            
            time.sleep(1)
        else:
            print(f"   Final status: {status}")
        
        # Step 8: Test explorer API
        log("8", "Testing explorer data endpoint")
        response = requests.get(f"{API_BASE}/visualization/{dataset_id}/explorer-data")
        if response.status_code == 200:
            explorer_data = response.json()
            print(f"   DFG nodes: {len(explorer_data.get('dfg', {}).get('nodes', []))}")
            print(f"   Variants: {len(explorer_data.get('variants', []))}")
            log_success("Explorer data accessible!")
        elif response.status_code == 409:
            print("   Dataset not ready for explorer yet")
        else:
            log_error("Explorer data failed", response)
        
        print("\n" + "="*60)
        print("🏁 E2E TEST COMPLETE")
        print("="*60 + "\n")
        return 0
        
    finally:
        # Cleanup
        os.unlink(csv_path)

if __name__ == "__main__":
    sys.exit(main())
