"""
State machine definitions for tracking dataset and workflow states during E2E tests.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any


class DatasetStatus(str, Enum):
    """Dataset lifecycle states matching backend."""
    PENDING = "pending"
    VALIDATING = "validating"
    AWAITING_MAPPING = "awaiting_mapping"
    MAPPED = "mapped"
    INGESTING = "ingesting"
    READY = "ready"
    ERROR = "error"
    
    @classmethod
    def terminal_states(cls) -> list:
        return [cls.READY, cls.ERROR]
    
    @classmethod
    def success_states(cls) -> list:
        return [cls.READY]


class WorkflowStatus(str, Enum):
    """Workflow lifecycle states."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    
    @classmethod
    def terminal_states(cls) -> list:
        return [cls.COMPLETED, cls.FAILED, cls.CANCELLED]


class JobStatus(str, Enum):
    """Job lifecycle states."""
    PENDING = "pending"
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class TestContext:
    """
    Shared test context for passing state between test steps.
    
    This mimics what the frontend stores in React state/context.
    """
    # Auth
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    
    # Organization
    org_id: Optional[str] = None
    org_name: Optional[str] = None
    
    # Workspace
    workspace_id: Optional[str] = None
    workspace_name: Optional[str] = None
    
    # Project
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    
    # Dataset
    dataset_id: Optional[str] = None
    dataset_status: Optional[str] = None
    dataset_columns: list = field(default_factory=list)
    
    # Model
    model_id: Optional[str] = None
    model_type: Optional[str] = None
    
    # Workflow/Job
    workflow_id: Optional[str] = None
    job_id: Optional[str] = None
    
    # Flags
    is_authenticated: bool = False
    dataset_uploaded: bool = False
    dataset_mapped: bool = False
    dataset_ingested: bool = False
    model_discovered: bool = False
    
    def reset(self):
        """Reset all context for a fresh test run."""
        self.__init__()
    
    def to_dict(self) -> dict:
        """Export context for debugging."""
        return {
            k: v for k, v in self.__dict__.items() 
            if not k.startswith('_') and v is not None
        }


# Global context instance for test sharing
context = TestContext()


def get_context() -> TestContext:
    """Get the global test context."""
    return context


def reset_context():
    """Reset the global test context."""
    global context
    context = TestContext()
