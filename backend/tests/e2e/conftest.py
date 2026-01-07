"""
E2E Test Fixtures and Configuration.

This module provides fixtures for E2E tests that run against a live backend server.
These tests verify the complete business flows work correctly.

Inherits from parent conftest.py:
- event_loop
- test_engine, db_session
- client, auth_client
- seeded_org, seeded_user, seeded_workspace, seeded_project
- sample_csv_bytes

E2E-Specific Fixtures:
- live_client: HTTP client for live server
- auth_headers: Real auth token from login
- test_context: Shared state across test journey
- cleanup_resources: Track resources for cleanup
"""

import pathlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import httpx
import pytest


# =============================================================================
# Configuration
# =============================================================================

BASE_URL = "http://localhost:8001"
API_URL = f"{BASE_URL}/api/v1"

# MVP data (seeded on backend startup)
MVP_USER_EMAIL = "analyst@example.com"
MVP_USER_PASSWORD = "password123"  # Any password works for MVP user
MVP_ORG_ID = "mvp-org-001"
MVP_WORKSPACE_ID = "mvp-ws-001"
MVP_PROJECT_ID = "mvp-proj-001"


# =============================================================================
# Test Context & Cleanup Tracking
# =============================================================================


@dataclass
class _TestContext:
    """Shared context for tracking state across test functions."""

    __test__ = False  # Tell pytest this is not a test class

    user_id: str | None = None
    org_id: str | None = None
    workspace_id: str | None = None
    project_id: str | None = None
    dataset_id: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    state_history: list = field(default_factory=list)
    request_history: list = field(default_factory=list)

    # Created resources for cleanup
    created_datasets: list = field(default_factory=list)
    created_projects: list = field(default_factory=list)
    created_workspaces: list = field(default_factory=list)

    def track(self, resource_type: str, resource_id: str):
        """Track a created resource for cleanup."""
        if resource_type == "dataset":
            self.created_datasets.append(resource_id)
        elif resource_type == "project":
            self.created_projects.append(resource_id)
        elif resource_type == "workspace":
            self.created_workspaces.append(resource_id)

    def record_request(self, method: str, url: str, status: int, response: Any = None):
        """Record a request for debugging."""
        self.request_history.append({
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "url": url,
            "status": status,
            "response": response[:500] if isinstance(response, str) else str(response)[:500],
        })


# Expose as TestContext for imports (underscore prefix avoids pytest collection)
TestContext = _TestContext


@pytest.fixture
def test_context() -> _TestContext:
    """
    Shared context for tracking state across test functions.
    Use this to pass data between test steps in a journey.
    """
    return _TestContext()


# =============================================================================
# Live Server Fixtures
# =============================================================================


@pytest.fixture(scope="session")
def live_client() -> httpx.Client:
    """Create HTTP client for live server testing."""
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)
    yield client
    client.close()


@pytest.fixture(scope="session")
def async_live_client() -> httpx.AsyncClient:
    """Create async HTTP client for live server testing."""
    return httpx.AsyncClient(base_url=BASE_URL, timeout=30.0)


@pytest.fixture(scope="function")
def auth_headers(live_client: httpx.Client) -> dict[str, str]:
    """Get real auth headers by logging in.

    Returns authorization headers with a valid JWT token.
    """
    response = live_client.post(
        f"{API_URL}/auth/login",
        json={"email": MVP_USER_EMAIL, "password": MVP_USER_PASSWORD},
    )

    if response.status_code != 200:
        pytest.skip(f"Cannot authenticate: {response.status_code} - {response.text}")

    data = response.json()
    access_token = data.get("access_token")

    if not access_token:
        pytest.skip("No access token in login response")

    return {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }


@pytest.fixture(scope="function")
def auth_token(live_client: httpx.Client) -> str:
    """Get just the auth token."""
    response = live_client.post(
        f"{API_URL}/auth/login",
        json={"email": MVP_USER_EMAIL, "password": MVP_USER_PASSWORD},
    )

    if response.status_code != 200:
        pytest.skip(f"Cannot authenticate: {response.status_code}")

    return response.json().get("access_token", "")


# =============================================================================
# Cleanup Fixture
# =============================================================================


@pytest.fixture
def cleanup_resources(live_client: httpx.Client, auth_headers: dict):
    """Fixture that cleans up resources after test."""
    created = {"datasets": [], "projects": [], "workspaces": []}

    yield created

    # Cleanup in reverse dependency order
    for dataset_id in created["datasets"]:
        try:
            live_client.delete(f"{API_URL}/datasets/{dataset_id}", headers=auth_headers)
        except Exception:
            pass

    for project_id in created["projects"]:
        try:
            live_client.delete(f"{API_URL}/projects/{project_id}", headers=auth_headers)
        except Exception:
            pass

    for workspace_id in created["workspaces"]:
        try:
            live_client.delete(f"{API_URL}/workspaces/{workspace_id}", headers=auth_headers)
        except Exception:
            pass


# =============================================================================
# Sample Data Fixtures
# =============================================================================


@pytest.fixture
def insurance_csv() -> bytes:
    """Load insurance_small.csv for testing."""
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "insurance_small.csv"
    if csv_path.exists():
        return csv_path.read_bytes()
    # Fallback sample data
    return b"case_id,activity,timestamp,resource\n1,Start,2024-01-01 10:00:00,Alice\n"


@pytest.fixture
def rework_csv() -> bytes:
    """Load rework_cases.csv for testing."""
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "rework_cases.csv"
    if csv_path.exists():
        return csv_path.read_bytes()
    return b"case_id,activity,timestamp,resource\n1,Start,2024-01-01 10:00:00,Alice\n"


@pytest.fixture
def bottleneck_csv() -> bytes:
    """Load bottleneck_cases.csv for testing."""
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "bottleneck_cases.csv"
    if csv_path.exists():
        return csv_path.read_bytes()
    return b"case_id,activity,timestamp,resource\n1,Start,2024-01-01 10:00:00,Alice\n"


@pytest.fixture
def simple_event_log_csv() -> bytes:
    """Generate a simple event log CSV for testing."""
    csv = """case_id,activity,timestamp,resource
1,Start,2024-01-01 09:00:00,Alice
1,Process,2024-01-01 10:00:00,Bob
1,Complete,2024-01-01 11:00:00,Alice
2,Start,2024-01-01 09:30:00,Bob
2,Process,2024-01-01 10:30:00,Alice
2,Complete,2024-01-01 11:30:00,Bob
3,Start,2024-01-01 10:00:00,Alice
3,Review,2024-01-01 11:00:00,Charlie
3,Process,2024-01-01 12:00:00,Bob
3,Complete,2024-01-01 13:00:00,Alice
"""
    return csv.encode("utf-8")


# =============================================================================
# Test Data Generators
# =============================================================================


class TestDataGenerator:
    """Generate test data for various scenarios."""

    __test__ = False  # Tell pytest this is not a test class

    @staticmethod
    def event_log(num_cases: int = 5, activities: list[str] | None = None) -> bytes:
        """Generate a test event log CSV."""
        if activities is None:
            activities = ["Start", "Process", "Review", "Approve", "Complete"]

        resources = ["Alice", "Bob", "Charlie", "Diana"]
        lines = ["case_id,activity,timestamp,resource"]

        for case_id in range(1, num_cases + 1):
            hour = 9
            for i, activity in enumerate(activities):
                resource = resources[i % len(resources)]
                lines.append(f"{case_id},{activity},2024-01-01 {hour:02d}:00:00,{resource}")
                hour += 1

        return "\n".join(lines).encode("utf-8")

    @staticmethod
    def workspace_data(name: str | None = None) -> dict:
        """Generate workspace creation data."""
        from uuid import uuid4
        return {
            "name": name or f"Test Workspace {uuid4().hex[:8]}",
            "description": "Created by E2E test",
        }

    @staticmethod
    def project_data(workspace_id: str, name: str | None = None) -> dict:
        """Generate project creation data."""
        from uuid import uuid4
        return {
            "workspace_id": workspace_id,
            "name": name or f"Test Project {uuid4().hex[:8]}",
            "description": "Created by E2E test",
        }


@pytest.fixture
def test_data() -> TestDataGenerator:
    """Provide test data generator."""
    return TestDataGenerator()
