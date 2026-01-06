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
    TaskResult,
    TaskRegistry,
    dag_task,
    task_registry,
)
from src.platform.dag.templates import (
    TEMPLATES,
    get_template,
    list_templates,
)
from src.platform.dag.executor import DAGExecutor

__all__ = [
    # Models
    "DAGDefinition",
    "DAGDefinitionStep",
    "DAGDefinitionEdge",
    "DAGRun",
    "DAGRunStep",
    "DAGRunStatus",
    "DAGStepStatus",
    # Registry
    "DAGContext",
    "TaskResult",
    "TaskRegistry",
    "dag_task",
    "task_registry",
    # Templates
    "TEMPLATES",
    "get_template",
    "list_templates",
    # Executor
    "DAGExecutor",
]

