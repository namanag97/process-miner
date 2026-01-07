"""
Pytest fixtures for E2E user journey tests.
"""

import os
import time
import pytest
import requests
from typing import Optional

from state_machine import TestContext, get_context, reset_context, DatasetStatus

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8001")
API_V1 = f"{BASE_URL}/api/v1"

# Timeouts
DEFAULT_TIMEOUT = 30  # seconds
POLL_INTERVAL = 1.0  # seconds
MAX_POLL_RETRIES = 60

# Test credentials
TEST_EMAIL = "e2e-test@example.com"
TEST_PASSWORD = "TestPassword123!"


@pytest.fixture(scope="session")
def api_client():
    """Session-scoped API client."""
    session = requests.Session()
    session.headers["Content-Type"] = "application/json"
    session.timeout = DEFAULT_TIMEOUT
    return session


@pytest.fixture(scope="session")
def context():
    """Shared test context for the entire session."""
    reset_context()
    return get_context()


@pytest.fixture(scope="session", autouse=True)
def setup_auth(api_client, context):
    """
    Setup authentication before running tests.
    
    1. Try to login with existing user
    2. If fails, register new user
    3. Store tokens in context
    """
    # Try login first
    login_resp = api_client.post(
        f"{API_V1}/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD}
    )
    
    if login_resp.status_code == 200:
        data = login_resp.json()
        context.access_token = data.get("access_token")
        context.refresh_token = data.get("refresh_token")
        context.is_authenticated = True
    else:
        # Register new user
        register_resp = api_client.post(
            f"{API_V1}/auth/register",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": "E2E Test User"
            }
        )
        
        if register_resp.status_code in [200, 201]:
            data = register_resp.json()
            context.access_token = data.get("access_token")
            context.refresh_token = data.get("refresh_token")
            context.is_authenticated = True
        else:
            # Auth might be disabled in dev mode, try without
            print(f"Auth setup failed: {register_resp.status_code}")
            context.is_authenticated = False
    
    # Set auth header for all subsequent requests
    if context.access_token:
        api_client.headers["Authorization"] = f"Bearer {context.access_token}"
    
    yield context
    
    # Cleanup could go here


@pytest.fixture
def auth_headers(context):
    """Get authorization headers."""
    if context.access_token:
        return {"Authorization": f"Bearer {context.access_token}"}
    return {}


def wait_for_state(
    client: requests.Session,
    url: str,
    target_states: list[str],
    timeout: int = DEFAULT_TIMEOUT,
    poll_interval: float = POLL_INTERVAL,
    status_key: str = "status",
    headers: Optional[dict] = None
) -> str:
    """
    Poll an endpoint until it reaches one of the target states.
    
    Args:
        client: HTTP client
        url: Endpoint to poll
        target_states: States to wait for (case-insensitive)
        timeout: Max seconds to wait
        poll_interval: Seconds between polls
        status_key: Key in response containing status
        headers: Optional headers
    
    Returns:
        Final status string
    
    Raises:
        TimeoutError: If timeout exceeded
    """
    target_lower = [s.lower() for s in target_states]
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        response = client.get(url, headers=headers)
        
        if response.status_code != 200:
            time.sleep(poll_interval)
            continue
        
        data = response.json()
        current_status = data.get(status_key, "").lower()
        
        if current_status in target_lower:
            return current_status
        
        if current_status == "error":
            error_msg = data.get("error_message", "Unknown error")
            raise RuntimeError(f"Resource entered error state: {error_msg}")
        
        time.sleep(poll_interval)
    
    raise TimeoutError(f"Timeout waiting for states: {target_states}")


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "journey: User journey tests")
    config.addinivalue_line("markers", "smoke: Quick smoke tests")
    config.addinivalue_line("markers", "slow: Slow tests (>30s)")


def generate_curl(method: str, url: str, headers: dict = None, data: dict = None) -> str:
    """Generate curl command for debugging."""
    cmd = f"curl -X {method}"
    
    if headers:
        for k, v in headers.items():
            cmd += f" -H '{k}: {v}'"
    
    if data:
        import json
        cmd += f" -d '{json.dumps(data)}'"
    
    cmd += f" '{url}'"
    return cmd
