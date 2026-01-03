#!/usr/bin/env python3
"""Test script to verify schema migration and upload flow."""

import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:8001/api/v1"

def test_health():
    """Test if backend is responding."""
    try:
        response = requests.get(f"{BASE_URL}/../health", timeout=5)
        print(f"✅ Health check: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_upload():
    """Test file upload."""
    csv_path = Path(__file__).parent.parent / "sample_event_log.csv"
    
    if not csv_path.exists():
        print(f"❌ Test file not found: {csv_path}")
        return False
    
    try:
        with open(csv_path, 'rb') as f:
            files = {'file': ('test_upload.csv', f, 'text/csv')}
            response = requests.post(
                f"{BASE_URL}/datasets/upload",
                files=files,
                timeout=30
            )
        
        print(f"Upload response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful! Dataset ID: {data.get('id')}")
            return True, data.get('id')
        else:
            print(f"❌ Upload failed: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Upload exception: {e}")
        return False, None

def test_get_dataset(dataset_id):
    """Test retrieving dataset."""
    try:
        response = requests.get(f"{BASE_URL}/datasets/{dataset_id}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Retrieved dataset: {data.get('name')}")
            print(f"   Cases: {data.get('total_cases')}, Events: {data.get('total_events')}")
            return True
        else:
            print(f"❌ Get dataset failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Get dataset exception: {e}")
        return False

def main():
    print("=" * 60)
    print("SCHEMA MIGRATION VERIFICATION TEST")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n[1/3] Testing backend health...")
    if not test_health():
        print("\n❌ Backend is not responding. Please start it first.")
        sys.exit(1)
    
    # Test 2: Upload
    print("\n[2/3] Testing upload endpoint...")
    success, dataset_id = test_upload()
    if not success:
        print("\n❌ Upload test failed!")
        sys.exit(1)
    
    # Test 3: Retrieve
    print("\n[3/3] Testing retrieval...")
    if not test_get_dataset(dataset_id):
        print("\n❌ Retrieval test failed!")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED! Schema migration successful.")
    print("=" * 60)
    sys.exit(0)

if __name__ == "__main__":
    main()
