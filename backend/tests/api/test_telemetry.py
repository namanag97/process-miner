"""Tests for Telemetry API endpoints.

CRITICAL: POST /api/v1/telemetry/traces was returning 500 in the audit.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.integration
async def test_proxy_traces_empty_body(auth_client: AsyncClient):
    """Test traces endpoint with empty body.

    CRITICAL: This was returning 500 before the fix.
    """
    response = await auth_client.post("/api/v1/telemetry/traces", json={})
    # Should return 200 or 422 validation error, not 500
    assert response.status_code in (200, 400, 422)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_proxy_traces_valid_payload(auth_client: AsyncClient):
    """Test traces endpoint with valid OTLP payload."""
    payload = {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [{"key": "service.name", "value": {"stringValue": "test"}}]
                },
                "scopeSpans": [],
            }
        ]
    }

    response = await auth_client.post("/api/v1/telemetry/traces", json=payload)
    # Should accept the payload
    assert response.status_code in (200, 202)


@pytest.mark.asyncio
@pytest.mark.integration
async def test_proxy_logs(auth_client: AsyncClient):
    """Test logs endpoint accepts log payloads."""
    payload = {"resourceLogs": []}

    response = await auth_client.post("/api/v1/telemetry/logs", json=payload)
    assert response.status_code in (200, 202, 422)
