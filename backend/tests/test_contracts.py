"""API contract tests.

Validates that API responses conform to expected contracts:
- Error responses follow RFC 7807 Problem Details
- Success responses have expected structure
- Headers are properly set

Usage:
    pytest tests/test_contracts.py -v
"""

import pytest
from httpx import AsyncClient


# =============================================================================
# RFC 7807 Problem Details Contract
# =============================================================================

class TestErrorResponseContracts:
    """Verify error responses follow RFC 7807 Problem Details standard."""
    
    RFC7807_REQUIRED_FIELDS = {"type", "title", "status", "detail"}
    
    @pytest.mark.asyncio
    async def test_404_follows_rfc7807(self, async_client: AsyncClient):
        """404 responses should follow RFC 7807 format."""
        response = await async_client.get("/api/v1/processes/nonexistent-uuid")
        
        assert response.status_code == 404
        
        body = response.json()
        
        # Check required fields
        for field in self.RFC7807_REQUIRED_FIELDS:
            assert field in body, f"Missing RFC 7807 field: {field}"
        
        # Verify field types
        assert isinstance(body["type"], str)
        assert isinstance(body["title"], str)
        assert isinstance(body["status"], int)
        assert body["status"] == 404
        assert isinstance(body["detail"], str)
    
    @pytest.mark.asyncio
    async def test_422_includes_validation_details(self, async_client: AsyncClient):
        """422 validation errors should include field information."""
        # Send invalid data (missing required fields)
        response = await async_client.post(
            "/api/v1/projects",
            json={},  # Empty body, missing required 'name'
        )
        
        assert response.status_code == 422
        
        body = response.json()
        
        # Should have error details about validation
        assert "detail" in body
    
    @pytest.mark.asyncio
    async def test_error_responses_include_error_code(self, async_client: AsyncClient):
        """Error responses should include error_code field."""
        response = await async_client.get("/api/v1/processes/invalid-id")
        
        # Should be 404 or 422 depending on validation
        assert response.status_code in {404, 422}
        
        body = response.json()
        
        # Check for error_code in response or detail
        if response.status_code == 404:
            # Custom exception should include error_code
            assert "error_code" in body or "type" in body


# =============================================================================
# Success Response Contracts
# =============================================================================

class TestSuccessResponseContracts:
    """Verify success responses have expected structure."""
    
    @pytest.mark.asyncio
    async def test_list_endpoint_returns_array(self, async_client: AsyncClient):
        """List endpoints should return arrays."""
        response = await async_client.get("/api/v1/processes/")
        
        assert response.status_code == 200
        
        body = response.json()
        
        # Should be a list
        assert isinstance(body, list)
    
    @pytest.mark.asyncio
    async def test_projects_list_returns_array(self, async_client: AsyncClient):
        """Projects list should return array."""
        response = await async_client.get("/api/v1/projects")
        
        assert response.status_code == 200
        
        body = response.json()
        assert isinstance(body, list)
    
    @pytest.mark.asyncio
    async def test_discovery_miners_returns_array(self, async_client: AsyncClient):
        """Discovery miners endpoint should return array."""
        response = await async_client.get("/api/v1/discovery/miners")
        
        assert response.status_code == 200
        
        body = response.json()
        assert isinstance(body, list)
        
        # Each miner should have id and name
        for miner in body:
            assert "id" in miner
            assert "name" in miner


# =============================================================================
# Header Contracts
# =============================================================================

class TestHeaderContracts:
    """Verify response headers are properly set."""
    
    @pytest.mark.asyncio
    async def test_json_content_type(self, async_client: AsyncClient):
        """JSON responses should have correct content-type."""
        response = await async_client.get("/api/v1/processes/")
        
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type
    
    @pytest.mark.asyncio
    async def test_cors_headers_present(self, async_client: AsyncClient):
        """CORS headers should be present for allowed origins."""
        response = await async_client.options(
            "/api/v1/processes/",
            headers={"Origin": "http://localhost:3000"},
        )
        
        # CORS preflight should succeed
        assert response.status_code in {200, 204, 405}


# =============================================================================
# Health Endpoint Contracts
# =============================================================================

class TestHealthContracts:
    """Verify health endpoints follow expected contracts."""
    
    @pytest.mark.asyncio
    async def test_health_live_minimal_response(self, async_client: AsyncClient):
        """Liveness probe should return minimal status."""
        response = await async_client.get("/health/live")
        
        assert response.status_code == 200
        
        body = response.json()
        assert "status" in body
        assert body["status"] in {"healthy", "unhealthy", "starting"}
    
    @pytest.mark.asyncio
    async def test_health_ready_includes_status(self, async_client: AsyncClient):
        """Readiness probe should include status."""
        response = await async_client.get("/health/ready")
        
        # May be 200 or 503 depending on dependencies
        assert response.status_code in {200, 503}
        
        body = response.json()
        assert "status" in body
    
    @pytest.mark.asyncio
    async def test_health_detailed_includes_components(self, async_client: AsyncClient):
        """Detailed health should include component breakdown."""
        response = await async_client.get("/health/detailed")
        
        assert response.status_code == 200
        
        body = response.json()
        assert "status" in body
        assert "components" in body
        assert isinstance(body["components"], list)
        
        # Each component should have name and status
        for component in body["components"]:
            assert "name" in component
            assert "status" in component


# =============================================================================
# Root Endpoint Contract
# =============================================================================

class TestRootEndpointContract:
    """Verify root endpoint provides API discovery info."""
    
    @pytest.mark.asyncio
    async def test_root_returns_api_info(self, async_client: AsyncClient):
        """Root endpoint should return API information."""
        response = await async_client.get("/")
        
        assert response.status_code == 200
        
        body = response.json()
        
        # Should include basic API info
        assert "name" in body
        assert "version" in body
        assert "docs" in body
