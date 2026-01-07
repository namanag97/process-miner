"""DAG Orchestration Package.

Provides DAG-based workflow orchestration for process mining tasks.

Components:
- models: SQLAlchemy ORM models for DAG entities
- repository: Database CRUD operations
- engine: DAG execution logic (topological sort, ready check)
- service: Business logic layer
- registry: Task function registration
- executor: Step execution engine
- templates: Predefined workflow templates
- tasks: DAG-compatible task functions
"""

from src.platform.dag.executor import DAGExecutor
from src.platform.dag.models import (
    DAGDefinition,
    DAGDefinitionEdge,
    DAGDefinitionStep,
    DAGRun,
    DAGRunStatus,
    DAGRunStep,
    DAGStepStatus,
)
from src.platform.dag.registry import (
    DAGContext,
    TaskRegistry,
    TaskResult,
    dag_task,
    task_registry,
)
from src.platform.dag.service import DAGService
from src.platform.dag.templates import (
    TEMPLATES,
    get_template,
    list_templates,
)

__all__ = [
    # Templates
    "TEMPLATES",
    # Registry
    "DAGContext",
    # Models
    "DAGDefinition",
    "DAGDefinitionEdge",
    "DAGDefinitionStep",
    # Executor
    "DAGExecutor",
    "DAGRun",
    "DAGRunStatus",
    "DAGRunStep",
    # Service
    "DAGService",
    "DAGStepStatus",
    "TaskRegistry",
    "TaskResult",
    "dag_task",
    "get_template",
    "list_templates",
    "task_registry",
]
