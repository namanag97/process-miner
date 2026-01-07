"""
E2E test fixtures.

Inherits from parent conftest.py:
- event_loop
- test_engine, db_session
- client, auth_client
- seeded_org, seeded_user, seeded_workspace, seeded_project
- sample_csv_bytes
"""

import pathlib
from typing import Dict
import pytest


@pytest.fixture
def test_context() -> Dict:
    """
    Shared context for tracking state across test functions.
    
    Use this to pass data between test steps in a journey.
    """
    return {
        "user_id": None,
        "org_id": None,
        "workspace_id": None,
        "project_id": None,
        "dataset_id": None,
        "access_token": None,
        "state_history": [],  # Track state transitions
        "request_history": [],  # Debug failed assertions
    }


@pytest.fixture
def insurance_csv() -> bytes:
    """Load insurance_small.csv for testing."""
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "insurance_small.csv"
    return csv_path.read_bytes()


@pytest.fixture
def rework_csv() -> bytes:
    """Load rework_cases.csv for testing."""
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "rework_cases.csv"
    return csv_path.read_bytes()


@pytest.fixture
def bottleneck_csv() -> bytes:
    """Load bottleneck_cases.csv for testing."""
    csv_path = pathlib.Path(__file__).parent.parent / "data" / "bottleneck_cases.csv"
    return csv_path.read_bytes()
