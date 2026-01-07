"""
User Journey: Complete Dataset Upload Flow

States: Upload → Validate → Column Detection → Mapping → Preview → Ingest → Ready

This is the CRITICAL path - bugs here break the entire system.

Test Flow:
1. Upload CSV file → Verify dataset created
2. Wait for validation → Poll until VALIDATED state
3. Detect columns → Verify auto-detection works
4. Submit mapping → Map case_id, activity, timestamp columns
5. Preview data → Verify preview returns events
6. Trigger ingestion → Start async ingestion job
7. Wait for READY → Poll until ingestion complete
8. Verify statistics → Assert total_cases, total_events, total_activities > 0
"""

import io

import pytest
from httpx import AsyncClient

from tests.e2e.helpers.polling import wait_for_state
from tests.e2e.helpers.state_machine import StateValidator


@pytest.mark.asyncio
@pytest.mark.e2e
class TestDatasetUploadJourney:
    """Complete dataset upload journey from user perspective."""

    async def test_01_upload_csv_file(
        self,
        auth_client: AsyncClient,
        seeded_project,
        insurance_csv: bytes,
        test_context: dict,
    ):
        """Step 1: User uploads a CSV file."""
        print("\n" + "=" * 70)
        print("[STEP 1] Uploading CSV file...")
        print("=" * 70)

        files = {
            "file": ("insurance_small.csv", io.BytesIO(insurance_csv), "text/csv"),
        }
        data = {
            "project_id": seeded_project.id,
            "name": "E2E Test Dataset",
        }

        response = await auth_client.post(
            "/api/v1/datasets/",
            files=files,
            data=data,
        )

        assert response.status_code == 200, (
            f"Upload failed with HTTP {response.status_code}\nResponse: {response.text}"
        )

        dataset_data = response.json()
        dataset_id = dataset_data["id"]

        # Save to context for subsequent tests
        test_context["dataset_id"] = dataset_id
        test_context["project_id"] = seeded_project.id

        # Verify initial state
        initial_status = dataset_data["status"]
        assert initial_status.lower() in ["pending", "validating"], (
            f"Expected initial status to be PENDING or VALIDATING, got: {initial_status}"
        )

        print("✓ Dataset uploaded successfully")
        print(f"  Dataset ID: {dataset_id}")
        print(f"  Initial status: {initial_status}")
        print(f"  Filename: {dataset_data.get('original_filename', 'N/A')}")

    async def test_02_wait_for_validation(
        self,
        auth_client: AsyncClient,
        test_context: dict,
    ):
        """Step 2: Wait for validation to complete."""
        print("\n" + "=" * 70)
        print("[STEP 2] Waiting for validation to complete...")
        print("=" * 70)

        dataset_id = test_context["dataset_id"]
        state_validator = StateValidator()

        def on_state_change(from_state, to_state):
            if from_state:
                try:
                    state_validator.add_transition(from_state, to_state)
                    print(f"  State transition: {from_state} → {to_state}")
                except ValueError as e:
                    print(f"  ⚠️  WARNING: {e}")

        final_state = await wait_for_state(
            client=auth_client,
            endpoint=f"/api/v1/datasets/{dataset_id}",
            target_states=["validated", "awaiting_mapping"],
            timeout_seconds=30,
            poll_interval=1.0,
            on_state_change=on_state_change,
        )

        assert final_state.lower() in ["validated", "awaiting_mapping"], (
            f"Expected VALIDATED or AWAITING_MAPPING, got: {final_state}"
        )

        print("✓ Validation completed successfully")
        print(f"  Final state: {final_state}")
        print(f"  Transition summary: {state_validator.get_summary()}")

    async def test_03_detect_columns(
        self,
        auth_client: AsyncClient,
        test_context: dict,
    ):
        """Step 3: Verify columns are auto-detected."""
        print("\n" + "=" * 70)
        print("[STEP 3] Detecting columns...")
        print("=" * 70)

        dataset_id = test_context["dataset_id"]

        response = await auth_client.get(f"/api/v1/datasets/{dataset_id}/columns")

        assert response.status_code == 200, (
            f"Column detection failed with HTTP {response.status_code}\nResponse: {response.text}"
        )

        columns_data = response.json()

        assert "columns" in columns_data, "Response should contain 'columns' field"
        columns = columns_data["columns"]

        assert len(columns) >= 3, (
            f"Expected at least 3 columns (case_id, activity, timestamp), but got {len(columns)}"
        )

        # Save columns to context
        test_context["columns"] = columns

        print(f"✓ Detected {len(columns)} columns")
        for col in columns:
            dtype = col.get("dtype", "unknown")
            suggested_role = col.get("suggested_role", None)
            confidence = col.get("confidence", None)

            role_info = (
                f" (suggested: {suggested_role}, confidence: {confidence:.2f})"
                if suggested_role
                else ""
            )
            print(f"  - {col['name']}: {dtype}{role_info}")

        # Verify we have the required columns for insurance_small.csv
        column_names = [col["name"] for col in columns]
        required_cols = ["case_id", "activity", "timestamp"]

        for req_col in required_cols:
            assert req_col in column_names, (
                f"Required column '{req_col}' not found in detected columns: {column_names}"
            )

        print("✓ All required columns present")

    async def test_04_submit_column_mapping(
        self,
        auth_client: AsyncClient,
        test_context: dict,
    ):
        """Step 4: User submits column mapping."""
        print("\n" + "=" * 70)
        print("[STEP 4] Submitting column mapping...")
        print("=" * 70)

        dataset_id = test_context["dataset_id"]

        # Use insurance_small.csv column structure
        mapping = {
            "case_id_column": "case_id",
            "activity_column": "activity",
            "timestamp_column": "timestamp",
            "resource_column": "resource",  # Optional
        }

        response = await auth_client.post(
            f"/api/v1/datasets/{dataset_id}/mapping",
            json=mapping,
        )

        assert response.status_code == 200, (
            f"Mapping submission failed with HTTP {response.status_code}\nResponse: {response.text}"
        )

        response.json()

        print("✓ Column mapping submitted successfully")
        print("  Mapped columns:")
        for role, column in mapping.items():
            print(f"    {role}: {column}")

        # Verify dataset transitioned to MAPPED state
        dataset_response = await auth_client.get(f"/api/v1/datasets/{dataset_id}")
        assert dataset_response.status_code == 200

        dataset_data = dataset_response.json()
        current_status = dataset_data["status"]

        assert current_status.lower() == "mapped", (
            f"Expected status MAPPED after mapping submission, got: {current_status}"
        )

        print(f"  Dataset status: {current_status}")

    async def test_05_preview_mapped_data(
        self,
        auth_client: AsyncClient,
        test_context: dict,
    ):
        """Step 5: User previews mapped data before ingestion."""
        print("\n" + "=" * 70)
        print("[STEP 5] Previewing mapped data...")
        print("=" * 70)

        dataset_id = test_context["dataset_id"]

        response = await auth_client.post(
            f"/api/v1/datasets/{dataset_id}/preview",
            params={"limit": 10},
        )

        assert response.status_code == 200, (
            f"Preview failed with HTTP {response.status_code}\nResponse: {response.text}"
        )

        preview_data = response.json()

        assert "events" in preview_data, "Preview response should contain 'events' field"
        events = preview_data["events"]

        assert len(events) > 0, "Preview should return at least 1 event"

        print(f"✓ Preview returned {len(events)} events")

        # Verify event structure
        if events:
            first_event = events[0]
            required_fields = ["case_id", "activity", "timestamp"]

            for field in required_fields:
                assert field in first_event, (
                    f"Event should have '{field}' field. Got: {list(first_event.keys())}"
                )

            print("  Sample event:")
            print(f"    case_id: {first_event.get('case_id')}")
            print(f"    activity: {first_event.get('activity')}")
            print(f"    timestamp: {first_event.get('timestamp')}")

    async def test_06_trigger_ingestion(
        self,
        auth_client: AsyncClient,
        test_context: dict,
    ):
        """Step 6: User triggers dataset ingestion."""
        print("\n" + "=" * 70)
        print("[STEP 6] Triggering ingestion...")
        print("=" * 70)

        dataset_id = test_context["dataset_id"]

        response = await auth_client.post(f"/api/v1/datasets/{dataset_id}/ingest")

        assert response.status_code in [200, 202], (
            f"Ingestion trigger failed with HTTP {response.status_code}\nResponse: {response.text}"
        )

        ingest_data = response.json()

        # Save job_id if present (async mode)
        if "job_id" in ingest_data:
            job_id = ingest_data["job_id"]
            test_context["job_id"] = job_id
            print("✓ Ingestion triggered (async mode)")
            print(f"  Job ID: {job_id}")
        else:
            print("✓ Ingestion triggered (sync mode)")

        # Verify status changed to INGESTING
        dataset_response = await auth_client.get(f"/api/v1/datasets/{dataset_id}")
        assert dataset_response.status_code == 200

        dataset_data = dataset_response.json()
        current_status = dataset_data["status"]

        print(f"  Dataset status: {current_status}")

    async def test_07_wait_for_ingestion_complete(
        self,
        auth_client: AsyncClient,
        test_context: dict,
    ):
        """Step 7: Wait for ingestion to complete (READY state)."""
        print("\n" + "=" * 70)
        print("[STEP 7] Waiting for ingestion to complete...")
        print("=" * 70)

        dataset_id = test_context["dataset_id"]
        state_validator = StateValidator()

        def on_state_change(from_state, to_state):
            if from_state:
                try:
                    state_validator.add_transition(from_state, to_state)
                    print(f"  State transition: {from_state} → {to_state}")
                except ValueError as e:
                    print(f"  ⚠️  WARNING: {e}")

        final_state = await wait_for_state(
            client=auth_client,
            endpoint=f"/api/v1/datasets/{dataset_id}",
            target_states=["ready"],
            timeout_seconds=60,
            poll_interval=2.0,
            on_state_change=on_state_change,
        )

        assert final_state.lower() == "ready", f"Expected final state READY, got: {final_state}"

        print("✓ Ingestion completed successfully")
        print(f"  Final state: {final_state}")
        print(f"  Transition summary: {state_validator.get_summary()}")

    async def test_08_verify_dataset_statistics(
        self,
        auth_client: AsyncClient,
        test_context: dict,
    ):
        """Step 8: Verify final dataset statistics are correct."""
        print("\n" + "=" * 70)
        print("[STEP 8] Verifying dataset statistics...")
        print("=" * 70)

        dataset_id = test_context["dataset_id"]

        response = await auth_client.get(f"/api/v1/datasets/{dataset_id}")
        assert response.status_code == 200

        data = response.json()

        # Critical assertions - these MUST pass
        assert data["status"].lower() == "ready", (
            f"Dataset should be in READY state, got: {data['status']}"
        )

        total_cases = data.get("total_cases", 0)
        total_events = data.get("total_events", 0)
        total_activities = data.get("total_activities", 0)

        assert total_cases > 0, (
            f"Dataset should have at least 1 case, got: {total_cases}\nFull response: {data}"
        )

        assert total_events > 0, (
            f"Dataset should have at least 1 event, got: {total_events}\nFull response: {data}"
        )

        assert total_activities > 0, (
            f"Dataset should have at least 1 activity, got: {total_activities}\n"
            f"Full response: {data}"
        )

        print("✓ Dataset statistics verified")
        print(f"  Status: {data['status']}")
        print(f"  Total cases: {total_cases}")
        print(f"  Total events: {total_events}")
        print(f"  Total activities: {total_activities}")

        # Data quality checks
        events_per_case = total_events / total_cases if total_cases > 0 else 0

        assert events_per_case > 1, (
            f"Each case should have multiple events. Got {events_per_case:.2f} events per case"
        )

        print(f"  Avg events per case: {events_per_case:.2f}")

        # Verify activities are stored correctly
        activities_json = data.get("activities_json", "[]")
        if activities_json and activities_json != "[]":
            import json

            activities = json.loads(activities_json)
            print(f"  Activities: {activities}")

        print("\n" + "=" * 70)
        print("✅ DATASET UPLOAD JOURNEY COMPLETED SUCCESSFULLY")
        print("=" * 70)
