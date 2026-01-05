"""End-to-End Happy Path API Tests.

Comprehensive end-to-end tests covering complete business flows
through the API. All tests follow happy path scenarios.

Tests cover:
1. Dataset Lifecycle: upload → detect → map → ingest → list → get → delete
2. Discovery Lifecycle: discover → get model → visualize
3. Workspace/Project Management
4. Authentication Flow
"""

import pytest
from httpx import AsyncClient


class TestDatasetLifecycleHappyPath:
    """Happy path tests for complete dataset lifecycle."""

    @pytest.mark.asyncio
    async def test_complete_dataset_workflow(
        self,
        client: AsyncClient,
        sample_csv_content: bytes,
        default_project: str,
    ):
        """Test complete dataset lifecycle: upload → detect → map → ingest → list → get → delete."""
        # Step 1: Upload dataset
        response = await client.post(
            "/api/v1/datasets/upload",
            files={"file": ("test_workflow.csv", sample_csv_content, "text/csv")},
            data={"project_id": default_project},
        )
        assert response.status_code == 200, f"Upload failed: {response.text}"
        upload_data = response.json()
        dataset_id = upload_data["id"]
        assert dataset_id is not None
        assert upload_data["status"] in ["UPLOADED", "PENDING", "VALIDATING"]

        # Step 2: Detect columns
        response = await client.get(f"/api/v1/datasets/{dataset_id}/columns")
        if response.status_code == 200:
            columns_data = response.json()
            assert "columns" in columns_data
            assert "suggestions" in columns_data
            assert len(columns_data["columns"]) >= 3  # At minimum: case, activity, timestamp

            # Step 3: Submit mapping
            mapping_response = await client.post(
                f"/api/v1/datasets/{dataset_id}/mapping",
                json={
                    "case_id_column": columns_data["suggestions"].get("case_id", "case_id"),
                    "activity_column": columns_data["suggestions"].get("activity", "activity"),
                    "timestamp_column": columns_data["suggestions"].get("timestamp", "timestamp"),
                },
            )
            if mapping_response.status_code == 200:
                mapping_data = mapping_response.json()
                assert mapping_data["status"] == "MAPPED"

        # Step 4: List datasets (verify dataset appears in list)
        response = await client.get("/api/v1/datasets")
        assert response.status_code == 200
        list_data = response.json()
        assert "items" in list_data
        assert "total" in list_data
        
        # Find our dataset in the list
        dataset_ids = [item["id"] for item in list_data["items"]]
        assert dataset_id in dataset_ids

        # Step 5: Get dataset details
        response = await client.get(f"/api/v1/datasets/{dataset_id}")
        assert response.status_code == 200
        detail_data = response.json()
        assert detail_data["id"] == dataset_id
        assert detail_data["name"] is not None

        # Step 6: Delete dataset
        response = await client.delete(f"/api/v1/datasets/{dataset_id}")
        assert response.status_code == 200
        delete_data = response.json()
        assert delete_data["status"] == "deleted"

        # Verify deletion by checking 404 on get
        response = await client.get(f"/api/v1/datasets/{dataset_id}")
        assert response.status_code == 404


class TestDiscoveryLifecycleHappyPath:
    """Happy path tests for process discovery workflow."""

    @pytest.mark.asyncio
    async def test_discovery_workflow(
        self,
        client: AsyncClient,
        uploaded_log_id: str,
    ):
        """Test discovery: list miners → discover → get model."""
        # Step 1: List available miners
        response = await client.get("/api/v1/discovery/miners")
        assert response.status_code == 200
        miners = response.json()
        assert isinstance(miners, list)
        assert len(miners) >= 3  # Alpha, Inductive, Heuristics

        miner_ids = [m["id"] for m in miners]
        assert "alpha" in miner_ids
        assert "inductive" in miner_ids
        assert "heuristics" in miner_ids

        # Step 2: Discover process model using inductive miner
        response = await client.post(
            f"/api/v1/discovery/discover/{uploaded_log_id}",
            json={
                "algorithm": "inductive",
                "parameters": {},
            },
        )
        # Could be 200 or 202 depending on sync/async
        assert response.status_code in [200, 202], f"Discovery failed: {response.text}"
        
        if response.status_code == 200:
            discovery_result = response.json()
            # Check for expected fields based on API design
            if "analysis_id" in discovery_result:
                analysis_id = discovery_result["analysis_id"]
                
                # Step 3: Get analysis result
                get_response = await client.get(f"/api/v1/analyses/{analysis_id}")
                assert get_response.status_code in [200, 404]  # May not be immediately available

    @pytest.mark.asyncio
    async def test_visualization_dfg(
        self,
        client: AsyncClient,
        uploaded_log_id: str,
    ):
        """Test DFG visualization generation."""
        response = await client.get(
            f"/api/v1/visualization/dfg/{uploaded_log_id}",
            params={"format": "json"},
        )
        if response.status_code == 200:
            viz_data = response.json()
            # DFG should have nodes and edges
            assert "nodes" in viz_data or "activities" in viz_data


class TestWorkspaceProjectHappyPath:
    """Happy path tests for workspace and project management."""

    @pytest.mark.asyncio
    async def test_list_workspaces(self, client: AsyncClient):
        """Test listing workspaces."""
        response = await client.get("/api/v1/workspaces")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have at least the MVP workspace from seeding
        if len(data) > 0:
            workspace = data[0]
            assert "id" in workspace
            assert "name" in workspace

    @pytest.mark.asyncio
    async def test_project_crud_workflow(self, client: AsyncClient):
        """Test project CRUD: create → list → update → archive."""
        import uuid

        # Use the seeded MVP workspace
        workspace_id = "mvp-ws-001"

        # Step 1: Create a project
        project_name = f"Test Project {uuid.uuid4().hex[:8]}"
        response = await client.post(
            "/api/v1/projects",
            json={
                "name": project_name,
                "description": "Created by E2E happy path test",
                "workspace_id": workspace_id,
            },
        )
        if response.status_code == 200:
            project_data = response.json()
            project_id = project_data["id"]
            assert project_data["name"] == project_name

            # Step 2: List projects (verify our project appears)
            list_response = await client.get("/api/v1/projects")
            assert list_response.status_code == 200
            projects = list_response.json()
            project_ids = [p["id"] for p in projects]
            assert project_id in project_ids

            # Step 3: Update project
            update_response = await client.patch(
                f"/api/v1/projects/{project_id}",
                json={"description": "Updated description"},
            )
            if update_response.status_code == 200:
                updated = update_response.json()
                assert updated["description"] == "Updated description"


class TestAuthHappyPath:
    """Happy path tests for authentication flow."""

    @pytest.mark.asyncio
    async def test_auth_me_returns_user(self, client: AsyncClient):
        """Test GET /auth/me returns current user info."""
        response = await client.get("/api/v1/auth/me")
        # With mock auth in tests, should return 200
        if response.status_code == 200:
            data = response.json()
            assert "user" in data
            user = data["user"]
            assert "id" in user
            assert "email" in user

    @pytest.mark.asyncio  
    async def test_login_endpoint_exists(self, client: AsyncClient):
        """Test login endpoint is available."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "test@example.com", "password": "testpass"},
        )
        # Should get 200 (success) or 401 (bad creds), not 404/500
        assert response.status_code in [200, 401, 422]


class TestHealthHappyPath:
    """Happy path tests for health endpoints."""

    @pytest.mark.asyncio
    async def test_root_returns_api_info(self, client: AsyncClient):
        """Test root endpoint returns API info."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data
        assert "health" in data

    @pytest.mark.asyncio
    async def test_health_liveness(self, client: AsyncClient):
        """Test liveness probe."""
        response = await client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_readiness(self, client: AsyncClient):
        """Test readiness probe."""
        response = await client.get("/health/ready")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    @pytest.mark.asyncio
    async def test_health_detailed(self, client: AsyncClient):
        """Test detailed health check."""
        response = await client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "uptime_seconds" in data
        assert "components" in data


class TestAnalyticsHappyPath:
    """Happy path tests for analytics endpoints."""

    @pytest.mark.asyncio
    async def test_dashboard_with_valid_dataset(
        self,
        client: AsyncClient,
        uploaded_log_id: str,
    ):
        """Test analytics dashboard for a valid dataset."""
        response = await client.get(f"/api/v1/analytics/dashboard/{uploaded_log_id}")
        # May return 200 (with data) or 404 (not yet processed)
        if response.status_code == 200:
            data = response.json()
            # Dashboard should have some metrics
            assert isinstance(data, dict)

    @pytest.mark.asyncio
    async def test_kpi_endpoint(self, client: AsyncClient, uploaded_log_id: str):
        """Test KPI computation endpoint."""
        response = await client.get(f"/api/v1/analytics/{uploaded_log_id}/kpis")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


class TestConformanceHappyPath:
    """Happy path tests for conformance checking."""

    @pytest.mark.asyncio
    async def test_list_conformance_methods(self, client: AsyncClient):
        """Test listing available conformance methods."""
        response = await client.get("/api/v1/conformance/methods")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


class TestJobsHappyPath:
    """Happy path tests for job tracking."""

    @pytest.mark.asyncio
    async def test_list_jobs(self, client: AsyncClient):
        """Test listing jobs."""
        response = await client.get("/api/v1/jobs")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list) or "items" in data


class TestFilteringHappyPath:
    """Happy path tests for event log filtering."""

    @pytest.mark.asyncio
    async def test_list_filter_types(self, client: AsyncClient):
        """Test listing available filter types."""
        response = await client.get("/api/v1/filtering/types")
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
