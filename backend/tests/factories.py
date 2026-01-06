"""
Test Data Factories

Provides factory functions and dataclasses for creating consistent test data.
Use these instead of manually constructing model instances in tests.

Usage:
    from tests.factories import create_dataset, create_user
    
    dataset = create_dataset(name="My Test", status="ready")
    user = create_user(email="custom@test.com")
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


# =============================================================================
# Organization Factory
# =============================================================================

@dataclass
class OrganizationData:
    """Test data for Organization model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Test Organization"
    slug: str = "test-org"
    plan: str = "free"


def create_organization(**overrides) -> dict[str, Any]:
    """Create organization data dict with optional overrides."""
    data = OrganizationData(**{k: v for k, v in overrides.items() if hasattr(OrganizationData, k)})
    return asdict(data)


# =============================================================================
# User Factory
# =============================================================================

@dataclass
class UserData:
    """Test data for User model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    org_id: str = field(default_factory=lambda: str(uuid4()))
    email: str = "test@example.com"
    name: str = "Test User"
    role: str = "admin"


def create_user(**overrides) -> dict[str, Any]:
    """Create user data dict with optional overrides."""
    data = UserData(**{k: v for k, v in overrides.items() if hasattr(UserData, k)})
    return asdict(data)


# =============================================================================
# Workspace Factory
# =============================================================================

@dataclass
class WorkspaceData:
    """Test data for Workspace model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    org_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Test Workspace"
    description: str = "Workspace for testing"


def create_workspace(**overrides) -> dict[str, Any]:
    """Create workspace data dict with optional overrides."""
    data = WorkspaceData(**{k: v for k, v in overrides.items() if hasattr(WorkspaceData, k)})
    return asdict(data)


# =============================================================================
# Project Factory
# =============================================================================

@dataclass
class ProjectData:
    """Test data for Project model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    workspace_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Test Project"
    description: str = "Project for testing"


def create_project(**overrides) -> dict[str, Any]:
    """Create project data dict with optional overrides."""
    data = ProjectData(**{k: v for k, v in overrides.items() if hasattr(ProjectData, k)})
    return asdict(data)


# =============================================================================
# Dataset Factory
# =============================================================================

@dataclass
class DatasetData:
    """Test data for Dataset model."""
    id: str = field(default_factory=lambda: str(uuid4()))
    project_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Test Dataset"
    status: str = "pending"
    source_format: str = "csv"
    original_filename: str = "test.csv"
    case_id_column: str = "case_id"
    activity_column: str = "activity"
    timestamp_column: str = "timestamp"
    total_cases: int = 0
    total_events: int = 0
    total_activities: int = 0


def create_dataset(**overrides) -> dict[str, Any]:
    """Create dataset data dict with optional overrides."""
    data = DatasetData(**{k: v for k, v in overrides.items() if hasattr(DatasetData, k)})
    return asdict(data)


# =============================================================================
# Process Model Factory
# =============================================================================

@dataclass
class ProcessModelData:
    """Test data for ProcessModel."""
    id: str = field(default_factory=lambda: str(uuid4()))
    dataset_id: str = field(default_factory=lambda: str(uuid4()))
    name: str = "Test Model"
    algorithm: str = "inductive"
    model_format: str = "petri_net"


def create_process_model(**overrides) -> dict[str, Any]:
    """Create process model data dict with optional overrides."""
    data = ProcessModelData(**{k: v for k, v in overrides.items() if hasattr(ProcessModelData, k)})
    return asdict(data)


# =============================================================================
# Event Log Factories
# =============================================================================

def create_event_log_csv(
    num_cases: int = 3,
    activities: list[str] | None = None,
    resources: list[str] | None = None,
) -> str:
    """Generate a sample event log CSV string.
    
    Args:
        num_cases: Number of cases to generate
        activities: List of activities (default: Start, Process, End)
        resources: List of resources (default: Alice, Bob, Charlie)
    
    Returns:
        CSV content as string
    """
    if activities is None:
        activities = ["Start", "Process", "End"]
    if resources is None:
        resources = ["Alice", "Bob", "Charlie"]
    
    lines = ["case_id,activity,timestamp,resource"]
    base_time = datetime(2024, 1, 1, 9, 0, 0, tzinfo=timezone.utc)
    
    for case_num in range(1, num_cases + 1):
        for i, activity in enumerate(activities):
            ts = base_time.replace(
                hour=9 + (case_num - 1),
                minute=i * 15
            )
            resource = resources[i % len(resources)]
            lines.append(f"{case_num},{activity},{ts.strftime('%Y-%m-%d %H:%M:%S')},{resource}")
    
    return "\n".join(lines)
