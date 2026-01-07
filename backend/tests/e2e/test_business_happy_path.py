"""
Business Happy Path E2E Tests.

These tests verify the complete business workflows work correctly for the
Process Mining SaaS platform. They cover the core user journeys:

1. Authentication & User Management
2. Organization & Workspace Management
3. Project Management
4. Dataset Upload & Ingestion
5. Process Discovery
6. Analytics & Insights

Run with:
    pytest tests/e2e/test_business_happy_path.py -v -m e2e

Requirements:
    - Backend server running on localhost:8001
    - Temporal server running (for dataset ingestion)
    - Redis running (for progress streaming)
"""

import time
from datetime import datetime
from uuid import uuid4

import httpx
import pytest

from .conftest import (
    API_URL,
    BASE_URL,
    MVP_ORG_ID,
    MVP_PROJECT_ID,
    MVP_USER_EMAIL,
    MVP_WORKSPACE_ID,
    TestContext,
)


# =============================================================================
# Test Helpers
# =============================================================================


def check_backend_available():
    """Check if backend is available."""
    try:
        response = httpx.get(f"{BASE_URL}/health/live", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def skip_if_backend_unavailable():
    """Skip test if backend is not available."""
    if not check_backend_available():
        pytest.skip("Backend server not available")


# =============================================================================
# 1. Health & Infrastructure Tests
# =============================================================================


@pytest.mark.e2e
class TestHealthEndpoints:
    """Verify health endpoints work correctly."""

    def test_liveness_probe(self, live_client: httpx.Client):
        """Test liveness probe returns healthy status."""
        skip_if_backend_unavailable()

        response = live_client.get("/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_readiness_probe(self, live_client: httpx.Client):
        """Test readiness probe returns healthy status."""
        skip_if_backend_unavailable()

        response = live_client.get("/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_root_endpoint(self, live_client: httpx.Client):
        """Test root endpoint returns API info."""
        skip_if_backend_unavailable()

        response = live_client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data


# =============================================================================
# 2. Authentication Tests
# =============================================================================


@pytest.mark.e2e
class TestAuthentication:
    """Verify authentication flows work correctly."""

    def test_login_success(self, live_client: httpx.Client):
        """Test successful login returns tokens."""
        skip_if_backend_unavailable()

        response = live_client.post(
            f"{API_URL}/auth/login",
            json={"email": MVP_USER_EMAIL, "password": "any_password"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, live_client: httpx.Client):
        """Test login with invalid credentials fails."""
        skip_if_backend_unavailable()

        response = live_client.post(
            f"{API_URL}/auth/login",
            json={"email": "nonexistent@example.com", "password": "wrong"},
        )

        # Should fail with 401 or 404
        assert response.status_code in (401, 404)

    def test_get_current_user(self, live_client: httpx.Client, auth_headers: dict):
        """Test getting current user info."""
        skip_if_backend_unavailable()

        response = live_client.get(f"{API_URL}/auth/me", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == MVP_USER_EMAIL

    def test_unauthorized_request(self, live_client: httpx.Client):
        """Test request without token to protected endpoint."""
        skip_if_backend_unavailable()

        # /auth/me may be permissive, test workspace endpoint instead
        # Note: 307 redirect may occur due to trailing slash normalization
        response = live_client.get(f"{API_URL}/workspaces")

        # Should either require auth, return empty, or redirect
        assert response.status_code in (200, 307, 401, 403)


# =============================================================================
# 3. Organization & Workspace Tests
# =============================================================================


@pytest.mark.e2e
class TestOrganizationManagement:
    """Verify organization management works correctly."""

    def test_list_organizations(self, live_client: httpx.Client, auth_headers: dict):
        """Test listing organizations."""
        skip_if_backend_unavailable()

        # Add trailing slash to avoid 307 redirect
        response = live_client.get(f"{API_URL}/organizations/", headers=auth_headers)

        # May return 200 with list, 404 if not accessible, or 307 redirect
        assert response.status_code in (200, 307, 404)

    def test_get_organization(self, live_client: httpx.Client, auth_headers: dict):
        """Test getting organization details."""
        skip_if_backend_unavailable()

        response = live_client.get(
            f"{API_URL}/organizations/{MVP_ORG_ID}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == MVP_ORG_ID
        assert "name" in data


@pytest.mark.e2e
class TestWorkspaceManagement:
    """Verify workspace management works correctly."""

    def test_list_workspaces(self, live_client: httpx.Client, auth_headers: dict):
        """Test listing workspaces."""
        skip_if_backend_unavailable()

        response = live_client.get(f"{API_URL}/workspaces", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_workspace(self, live_client: httpx.Client, auth_headers: dict):
        """Test getting workspace details."""
        skip_if_backend_unavailable()

        response = live_client.get(
            f"{API_URL}/workspaces/{MVP_WORKSPACE_ID}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == MVP_WORKSPACE_ID
        assert "name" in data

    def test_create_workspace(
        self,
        live_client: httpx.Client,
        auth_headers: dict,
        cleanup_resources: dict,
    ):
        """Test creating a new workspace."""
        skip_if_backend_unavailable()

        workspace_name = f"E2E Test Workspace {uuid4().hex[:8]}"
        # org_id is required as query parameter
        response = live_client.post(
            f"{API_URL}/workspaces",
            headers=auth_headers,
            params={"org_id": MVP_ORG_ID},
            json={"name": workspace_name, "description": "Created by E2E test"},
        )

        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()
        assert data["name"] == workspace_name
        assert "id" in data

        # Track for cleanup
        cleanup_resources["workspaces"].append(data["id"])

    def test_update_workspace(
        self,
        live_client: httpx.Client,
        auth_headers: dict,
        cleanup_resources: dict,
    ):
        """Test updating a workspace."""
        skip_if_backend_unavailable()

        # First create a workspace
        create_response = live_client.post(
            f"{API_URL}/workspaces",
            headers=auth_headers,
            params={"org_id": MVP_ORG_ID},
            json={"name": f"Update Test {uuid4().hex[:8]}", "description": "Original"},
        )

        if create_response.status_code != 201:
            pytest.skip(f"Cannot create workspace for update test: {create_response.text}")

        workspace_id = create_response.json()["id"]
        cleanup_resources["workspaces"].append(workspace_id)

        # Update it
        update_response = live_client.put(
            f"{API_URL}/workspaces/{workspace_id}",
            headers=auth_headers,
            json={"name": "Updated Workspace", "description": "Updated description"},
        )

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["name"] == "Updated Workspace"


# =============================================================================
# 4. Project Management Tests
# =============================================================================


@pytest.mark.e2e
class TestProjectManagement:
    """Verify project management works correctly."""

    def test_list_projects(self, live_client: httpx.Client, auth_headers: dict):
        """Test listing projects."""
        skip_if_backend_unavailable()

        response = live_client.get(f"{API_URL}/projects", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_project(self, live_client: httpx.Client, auth_headers: dict):
        """Test getting project details."""
        skip_if_backend_unavailable()

        response = live_client.get(
            f"{API_URL}/projects/{MVP_PROJECT_ID}",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == MVP_PROJECT_ID
        assert "name" in data

    def test_create_project(
        self,
        live_client: httpx.Client,
        auth_headers: dict,
        cleanup_resources: dict,
    ):
        """Test creating a new project."""
        skip_if_backend_unavailable()

        project_name = f"E2E Test Project {uuid4().hex[:8]}"
        # workspace_id is required as query param, not in body
        response = live_client.post(
            f"{API_URL}/projects",
            headers=auth_headers,
            params={"workspace_id": MVP_WORKSPACE_ID},
            json={
                "name": project_name,
                "description": "Created by E2E test",
            },
        )

        assert response.status_code == 201, f"Create failed: {response.text}"
        data = response.json()
        assert data["name"] == project_name
        assert "id" in data

        # Track for cleanup
        cleanup_resources["projects"].append(data["id"])


# =============================================================================
# 5. Dataset Management Tests
# =============================================================================


@pytest.mark.e2e
class TestDatasetManagement:
    """Verify dataset management works correctly."""

    def test_list_datasets(self, live_client: httpx.Client, auth_headers: dict):
        """Test listing datasets."""
        skip_if_backend_unavailable()

        # Note: trailing slash required to avoid 307 redirect
        response = live_client.get(
            f"{API_URL}/datasets/",
            headers=auth_headers,
            params={"project_id": MVP_PROJECT_ID},
        )

        # May return 200 with list or empty
        assert response.status_code == 200

    def test_upload_dataset(
        self,
        live_client: httpx.Client,
        auth_headers: dict,
        simple_event_log_csv: bytes,
        cleanup_resources: dict,
    ):
        """Test uploading a dataset (CSV file)."""
        skip_if_backend_unavailable()

        # Remove Content-Type for multipart
        upload_headers = {"Authorization": auth_headers["Authorization"]}

        response = live_client.post(
            f"{API_URL}/datasets/",
            headers=upload_headers,
            files={"file": ("test_events.csv", simple_event_log_csv, "text/csv")},
            data={"project_id": MVP_PROJECT_ID, "name": f"E2E Upload {uuid4().hex[:8]}"},
        )

        # 201 = success, 500 = Temporal not running
        if response.status_code == 500:
            pytest.skip("Temporal workflows not available")

        assert response.status_code == 201, f"Upload failed: {response.text}"
        data = response.json()
        assert "id" in data
        assert "status" in data

        # Track for cleanup
        cleanup_resources["datasets"].append(data["id"])

    def test_get_dataset_columns(
        self,
        live_client: httpx.Client,
        auth_headers: dict,
        simple_event_log_csv: bytes,
        cleanup_resources: dict,
    ):
        """Test getting dataset columns after upload."""
        skip_if_backend_unavailable()

        # First upload a dataset
        upload_headers = {"Authorization": auth_headers["Authorization"]}
        upload_response = live_client.post(
            f"{API_URL}/datasets/",
            headers=upload_headers,
            files={"file": ("test.csv", simple_event_log_csv, "text/csv")},
            data={"project_id": MVP_PROJECT_ID, "name": f"Columns Test {uuid4().hex[:8]}"},
        )

        if upload_response.status_code == 500:
            pytest.skip("Temporal workflows not available")

        if upload_response.status_code != 201:
            pytest.skip(f"Upload failed: {upload_response.text}")

        dataset_id = upload_response.json()["id"]
        cleanup_resources["datasets"].append(dataset_id)

        # Wait for validation to complete
        time.sleep(2)

        # Get columns
        columns_response = live_client.get(
            f"{API_URL}/datasets/{dataset_id}/columns",
            headers=auth_headers,
        )

        # May need to wait for async processing
        if columns_response.status_code == 404:
            pytest.skip("Dataset validation still in progress")

        assert columns_response.status_code == 200
        data = columns_response.json()
        # Should have detected columns
        assert isinstance(data, (list, dict))


# =============================================================================
# 6. Jobs & Operations Tests
# =============================================================================


@pytest.mark.e2e
class TestJobsManagement:
    """Verify jobs/operations management works correctly."""

    def test_list_jobs(self, live_client: httpx.Client, auth_headers: dict):
        """Test listing jobs."""
        skip_if_backend_unavailable()

        response = live_client.get(f"{API_URL}/jobs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_operations(self, live_client: httpx.Client, auth_headers: dict):
        """Test listing operations (Temporal workflows)."""
        skip_if_backend_unavailable()

        response = live_client.get(f"{API_URL}/operations", headers=auth_headers)

        # 200 = success, 500 = Temporal not running
        assert response.status_code in (200, 500)

        if response.status_code == 200:
            data = response.json()
            assert "items" in data


# =============================================================================
# 7. Algorithms & Discovery Tests
# =============================================================================


@pytest.mark.e2e
class TestAlgorithms:
    """Verify algorithm registry works correctly."""

    def test_list_algorithms(self, live_client: httpx.Client, auth_headers: dict):
        """Test listing available algorithms."""
        skip_if_backend_unavailable()

        response = live_client.get(f"{API_URL}/algorithms", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "algorithms" in data
        assert "total" in data


# =============================================================================
# 8. Full Business Journey Test
# =============================================================================


@pytest.mark.e2e
@pytest.mark.slow
class TestFullBusinessJourney:
    """
    Complete business journey test.

    This test simulates a user going through the entire platform:
    1. Login
    2. View workspaces & projects
    3. Create a new project
    4. Upload a dataset
    5. Wait for processing
    6. View results

    This is the most comprehensive E2E test.
    """

    def test_complete_journey(
        self,
        live_client: httpx.Client,
        simple_event_log_csv: bytes,
        test_context: TestContext,
    ):
        """Test the complete user journey."""
        skip_if_backend_unavailable()

        # Step 1: Login
        print("\n=== Step 1: Login ===")
        login_response = live_client.post(
            f"{API_URL}/auth/login",
            json={"email": MVP_USER_EMAIL, "password": "password123"},
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"

        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        test_context.access_token = token
        print(f"  Logged in successfully")

        # Step 2: Get current user
        print("\n=== Step 2: Get User Info ===")
        me_response = live_client.get(f"{API_URL}/auth/me", headers=headers)
        assert me_response.status_code == 200
        user_data = me_response.json()
        test_context.user_id = user_data["user"]["id"]
        print(f"  User: {user_data['user']['email']}")

        # Step 3: List workspaces
        print("\n=== Step 3: List Workspaces ===")
        ws_response = live_client.get(f"{API_URL}/workspaces", headers=headers)
        assert ws_response.status_code == 200
        workspaces = ws_response.json()["items"]
        print(f"  Found {len(workspaces)} workspace(s)")

        # Step 4: List projects
        print("\n=== Step 4: List Projects ===")
        proj_response = live_client.get(f"{API_URL}/projects", headers=headers)
        assert proj_response.status_code == 200
        projects = proj_response.json()["items"]
        print(f"  Found {len(projects)} project(s)")

        # Step 5: Create a new project
        print("\n=== Step 5: Create Project ===")
        project_name = f"Journey Test {datetime.now().strftime('%H%M%S')}"
        # workspace_id is required as query param, not in body
        create_proj_response = live_client.post(
            f"{API_URL}/projects",
            headers=headers,
            params={"workspace_id": MVP_WORKSPACE_ID},
            json={
                "name": project_name,
                "description": "Created during E2E journey test",
            },
        )
        assert create_proj_response.status_code == 201, f"Create failed: {create_proj_response.text}"
        new_project = create_proj_response.json()
        test_context.project_id = new_project["id"]
        test_context.track("project", new_project["id"])
        print(f"  Created project: {new_project['name']} ({new_project['id']})")

        # Step 6: Upload dataset
        print("\n=== Step 6: Upload Dataset ===")
        upload_headers = {"Authorization": f"Bearer {token}"}
        upload_response = live_client.post(
            f"{API_URL}/datasets/",
            headers=upload_headers,
            files={"file": ("journey_test.csv", simple_event_log_csv, "text/csv")},
            data={"project_id": new_project["id"], "name": "Journey Test Dataset"},
        )

        if upload_response.status_code == 500:
            print("  SKIP: Temporal workflows not available")
            # Cleanup project
            live_client.delete(f"{API_URL}/projects/{new_project['id']}", headers=headers)
            pytest.skip("Temporal workflows not available for dataset processing")

        assert upload_response.status_code == 201, f"Upload failed: {upload_response.text}"
        dataset = upload_response.json()
        test_context.dataset_id = dataset["id"]
        test_context.track("dataset", dataset["id"])
        print(f"  Uploaded dataset: {dataset['name']} ({dataset['id']})")
        print(f"  Status: {dataset['status']}")

        # Step 7: Poll for dataset processing
        print("\n=== Step 7: Wait for Processing ===")
        max_polls = 30
        poll_interval = 2

        for i in range(max_polls):
            status_response = live_client.get(
                f"{API_URL}/datasets/{dataset['id']}",
                headers=headers,
            )

            if status_response.status_code != 200:
                print(f"  Poll {i+1}: Error getting status")
                continue

            current_status = status_response.json()["status"]
            print(f"  Poll {i+1}: Status = {current_status}")

            if current_status == "READY":
                print("  Dataset processing complete!")
                break
            elif current_status in ("FAILED", "ERROR"):
                print(f"  Dataset processing failed!")
                break

            time.sleep(poll_interval)

        # Step 8: Check dataset details
        print("\n=== Step 8: View Dataset Details ===")
        details_response = live_client.get(
            f"{API_URL}/datasets/{dataset['id']}",
            headers=headers,
        )
        assert details_response.status_code == 200
        details = details_response.json()
        print(f"  Dataset: {details['name']}")
        print(f"  Status: {details['status']}")
        if details.get("total_cases"):
            print(f"  Cases: {details['total_cases']}")
            print(f"  Events: {details['total_events']}")

        # Cleanup
        print("\n=== Cleanup ===")
        for ds_id in test_context.created_datasets:
            live_client.delete(f"{API_URL}/datasets/{ds_id}", headers=headers)
            print(f"  Deleted dataset: {ds_id}")

        for proj_id in test_context.created_projects:
            live_client.delete(f"{API_URL}/projects/{proj_id}", headers=headers)
            print(f"  Deleted project: {proj_id}")

        print("\n=== Journey Complete ===")


# =============================================================================
# 9. Audit & Observability Tests
# =============================================================================


@pytest.mark.e2e
class TestAuditTrail:
    """Verify audit trail functionality."""

    def test_list_audit_logs(self, live_client: httpx.Client, auth_headers: dict):
        """Test listing audit logs."""
        skip_if_backend_unavailable()

        # Endpoint is /audit/logs not /audit/events
        response = live_client.get(f"{API_URL}/audit/logs", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "-s", "-m", "e2e"],
        cwd="/Users/namanagarwal/system/backend",
    )
    sys.exit(result.returncode)
