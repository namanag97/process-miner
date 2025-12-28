"""API integration tests."""

import pytest
from httpx import AsyncClient


class TestHealthEndpoints:
    """Tests for health check endpoints."""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """Test root health endpoint."""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "app" in data
        assert "version" in data
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """Test detailed health endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "database" in data


class TestDiscoveryEndpoints:
    """Tests for process discovery endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_miners(self, client: AsyncClient):
        """Test listing available miners."""
        response = await client.get("/api/v1/discovery/miners")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 4
        
        # Check miner structure
        miner_ids = [m["id"] for m in data]
        assert "alpha" in miner_ids
        assert "inductive" in miner_ids
        assert "heuristics" in miner_ids


class TestAuthEndpoints:
    """Tests for authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_login(self, client: AsyncClient):
        """Test login endpoint."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "user@example.com", "password": "test"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_get_me(self, client: AsyncClient):
        """Test get current user endpoint."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "email" in data


class TestLogEndpoints:
    """Tests for event log endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_logs_empty(self, client: AsyncClient):
        """Test listing logs when empty."""
        response = await client.get("/api/v1/logs/")
        assert response.status_code == 200
        data = response.json()
        # Paginated response format
        assert data["items"] == []
        assert data["total"] == 0
        assert "page" in data
        assert "page_size" in data
    
    @pytest.mark.asyncio
    async def test_upload_log(self, client: AsyncClient, sample_csv_content: bytes):
        """Test uploading an event log."""
        response = await client.post(
            "/api/v1/logs/upload",
            files={"file": ("test.csv", sample_csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["total_cases"] >= 1
        assert data["total_events"] >= 1
    
    @pytest.mark.asyncio
    async def test_detect_columns(self, client: AsyncClient, sample_csv_content: bytes):
        """Test column detection for CSV."""
        response = await client.post(
            "/api/v1/logs/detect-columns",
            files={"file": ("test.csv", sample_csv_content, "text/csv")},
        )
        assert response.status_code == 200
        data = response.json()
        assert "columns" in data
        assert "suggestions" in data
        assert len(data["columns"]) >= 3


class TestWorkflowEndpoints:
    """Tests for workflow endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_pipelines(self, client: AsyncClient):
        """Test listing available pipelines."""
        response = await client.get("/api/v1/workflows/pipelines")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check pipeline structure
        pipeline_names = [p["name"] for p in data]
        assert "full_analysis" in pipeline_names


class TestNotificationEndpoints:
    """Tests for notification endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_channels(self, client: AsyncClient):
        """Test listing notification channels."""
        response = await client.get("/api/v1/notifications/channels")
        assert response.status_code == 200
        data = response.json()
        assert "channels" in data
        assert len(data["channels"]) >= 3
    
    @pytest.mark.asyncio
    async def test_send_notification(self, client: AsyncClient):
        """Test sending a notification."""
        response = await client.post(
            "/api/v1/notifications/send",
            json={
                "channel": "email",
                "recipient": "test@example.com",
                "subject": "Test Notification",
                "body": "This is a test.",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sent"


class TestIntegrationEndpoints:
    """Tests for integration endpoints."""
    
    @pytest.mark.asyncio
    async def test_list_connector_types(self, client: AsyncClient):
        """Test listing connector types."""
        response = await client.get("/api/v1/integrations/connector-types")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 4
        
        # Check connector types
        types = [c["type"] for c in data]
        assert "sap" in types
        assert "salesforce" in types
    
    @pytest.mark.asyncio
    async def test_create_connector(self, client: AsyncClient):
        """Test creating a connector."""
        response = await client.post(
            "/api/v1/integrations/connectors",
            json={
                "name": "Test SAP",
                "connector_type": "sap",
                "settings": {"host": "localhost"},
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test SAP"
        assert data["status"] == "disconnected"


class TestEnhancementEndpoints:
    """Tests for enhancement endpoints."""
    
    @pytest.mark.asyncio
    async def test_performance_not_found(self, client: AsyncClient):
        """Test performance endpoint with non-existent log."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/enhancement/performance/{fake_id}")
        assert response.status_code == 404


class TestAnalyticsEndpoints:
    """Tests for analytics endpoints."""
    
    @pytest.mark.asyncio
    async def test_dashboard_not_found(self, client: AsyncClient):
        """Test dashboard endpoint with non-existent log."""
        import uuid
        fake_id = str(uuid.uuid4())
        response = await client.get(f"/api/v1/analytics/dashboard/{fake_id}")
        assert response.status_code == 404
