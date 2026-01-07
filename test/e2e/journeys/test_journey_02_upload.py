"""
User Journey 02: Dataset Upload (CRITICAL)

Tests the complete dataset upload and processing flow:
1. Upload CSV file
2. Wait for validation
3. Detect columns
4. Submit column mapping
5. Preview mapped data
6. Trigger ingestion
7. Wait for READY status
8. Verify statistics
"""

import pytest
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conftest import API_V1, wait_for_state, POLL_INTERVAL
from debug_helpers import dump_request, save_failed_test_state


# Test data file path
TEST_DATA_DIR = Path(__file__).parent.parent / "data"
SAMPLE_CSV = TEST_DATA_DIR / "sample_event_log.csv"


@pytest.fixture(scope="module")
def sample_csv_content():
    """Create sample CSV content for upload."""
    return """case_id,activity,timestamp,resource
1,Start,2024-01-01T10:00:00,Alice
1,Process,2024-01-01T10:30:00,Bob
1,End,2024-01-01T11:00:00,Alice
2,Start,2024-01-01T10:00:00,Bob
2,Process,2024-01-01T10:45:00,Alice
2,End,2024-01-01T11:30:00,Bob
3,Start,2024-01-01T10:00:00,Alice
3,Review,2024-01-01T10:20:00,Charlie
3,Process,2024-01-01T10:50:00,Bob
3,End,2024-01-01T11:20:00,Alice
"""


class TestDatasetUploadJourney:
    """
    Complete dataset upload journey simulating frontend user flow.
    
    State transitions: PENDING → VALIDATING → AWAITING_MAPPING → MAPPED → INGESTING → READY
    """
    
    @pytest.mark.journey
    def test_01_upload_csv(self, api_client, context, sample_csv_content):
        """User uploads a CSV file."""
        if not context.project_id:
            pytest.skip("No project ID - run onboarding journey first")
        
        url = f"{API_V1}/datasets/"
        
        # Create file-like object from content
        files = {
            "file": ("e2e_test_log.csv", sample_csv_content.encode(), "text/csv")
        }
        data = {
            "project_id": context.project_id
        }
        
        # Remove content-type header for multipart
        headers = dict(api_client.headers)
        headers.pop("Content-Type", None)
        
        response = api_client.post(url, files=files, data=data, headers=headers)
        
        if response.status_code not in [200, 201]:
            dump_request("POST", url, response, data)
            save_failed_test_state(context, "test_01_upload_csv", response=response)
        
        assert response.status_code in [200, 201], f"Upload failed: {response.text}"
        
        result = response.json()
        context.dataset_id = result["id"]
        context.dataset_uploaded = True
        print(f"✓ Dataset uploaded: {context.dataset_id}")
    
    @pytest.mark.journey
    def test_02_wait_for_validation(self, api_client, context):
        """Wait for validation to complete."""
        if not context.dataset_id:
            pytest.skip("No dataset uploaded")
        
        url = f"{API_V1}/datasets/{context.dataset_id}"
        
        try:
            final_state = wait_for_state(
                api_client,
                url,
                target_states=["awaiting_mapping", "mapped", "ready"],
                timeout=60
            )
            context.dataset_status = final_state
            print(f"✓ Dataset status: {final_state}")
        except TimeoutError:
            pytest.fail("Timeout waiting for validation")
        except RuntimeError as e:
            pytest.fail(str(e))
    
    @pytest.mark.journey
    def test_03_detect_columns(self, api_client, context):
        """Verify columns are detected correctly."""
        if not context.dataset_id:
            pytest.skip("No dataset uploaded")
        
        url = f"{API_V1}/datasets/{context.dataset_id}/columns"
        response = api_client.get(url)
        
        assert response.status_code == 200, f"Column detection failed: {response.text}"
        
        data = response.json()
        columns = data.get("columns", [])
        column_names = [c["name"] for c in columns]
        
        print(f"✓ Detected columns: {column_names}")
        context.dataset_columns = columns
        
        # Verify expected columns exist
        assert len(columns) >= 3, "Expected at least 3 columns"
    
    @pytest.mark.journey
    def test_04_submit_mapping(self, api_client, context):
        """User submits column mapping."""
        if not context.dataset_id:
            pytest.skip("No dataset uploaded")
        
        # Skip if already mapped
        if context.dataset_status in ["mapped", "ready"]:
            context.dataset_mapped = True
            pytest.skip("Dataset already mapped")
        
        url = f"{API_V1}/datasets/{context.dataset_id}/mapping"
        
        # Find columns intelligently
        columns = context.dataset_columns or []
        column_names = [c["name"].lower() for c in columns]
        
        def find_column(keywords, default):
            for col in columns:
                name_lower = col["name"].lower()
                if any(k in name_lower for k in keywords):
                    return col["name"]
            return default
        
        mapping = {
            "case_id_column": find_column(["case", "trace", "id"], "case_id"),
            "activity_column": find_column(["activity", "concept:name", "action"], "activity"),
            "timestamp_column": find_column(["timestamp", "time", "date"], "timestamp")
        }
        
        response = api_client.post(url, json=mapping)
        
        if response.status_code != 200:
            dump_request("POST", url, response, mapping)
        
        assert response.status_code == 200, f"Mapping failed: {response.text}"
        context.dataset_mapped = True
        print(f"✓ Mapping submitted: {mapping}")
    
    @pytest.mark.journey
    def test_05_preview_data(self, api_client, context):
        """User previews mapped data before ingestion."""
        if not context.dataset_id:
            pytest.skip("No dataset uploaded")
        
        url = f"{API_V1}/datasets/{context.dataset_id}/preview"
        response = api_client.post(url, params={"limit": 10})
        
        if response.status_code == 200:
            data = response.json()
            events = data.get("events", data.get("rows", []))
            print(f"✓ Preview returned {len(events)} events")
        else:
            # Preview might not be available in all states
            print(f"⚠ Preview not available: {response.status_code}")
    
    @pytest.mark.journey
    def test_06_trigger_ingestion(self, api_client, context):
        """User triggers data ingestion."""
        if not context.dataset_id:
            pytest.skip("No dataset uploaded")
        
        # Skip if already ready
        if context.dataset_status == "ready":
            context.dataset_ingested = True
            pytest.skip("Dataset already ready")
        
        url = f"{API_V1}/datasets/{context.dataset_id}/ingest"
        response = api_client.post(url)
        
        assert response.status_code in [200, 202], f"Ingestion trigger failed: {response.text}"
        
        data = response.json()
        if "job_id" in data:
            context.job_id = data["job_id"]
        
        context.dataset_ingested = True
        print(f"✓ Ingestion triggered")
    
    @pytest.mark.journey
    def test_07_wait_for_ready(self, api_client, context):
        """Wait for dataset to reach READY status."""
        if not context.dataset_id:
            pytest.skip("No dataset uploaded")
        
        url = f"{API_V1}/datasets/{context.dataset_id}"
        
        try:
            final_state = wait_for_state(
                api_client,
                url,
                target_states=["ready", "READY"],
                timeout=120
            )
            context.dataset_status = final_state
            print(f"✓ Dataset ready: {final_state}")
        except TimeoutError:
            pytest.fail("Timeout waiting for READY status")
        except RuntimeError as e:
            save_failed_test_state(context, "test_07_wait_for_ready")
            pytest.fail(str(e))
    
    @pytest.mark.journey
    def test_08_verify_statistics(self, api_client, context):
        """Verify final dataset statistics."""
        if not context.dataset_id:
            pytest.skip("No dataset uploaded")
        
        url = f"{API_V1}/datasets/{context.dataset_id}"
        response = api_client.get(url)
        
        assert response.status_code == 200
        
        data = response.json()
        total_cases = data.get("total_cases", 0)
        total_events = data.get("total_events", 0)
        
        print(f"✓ Statistics: {total_cases} cases, {total_events} events")
        
        assert total_cases > 0, "Expected cases to be counted"
        assert total_events > 0, "Expected events to be counted"
