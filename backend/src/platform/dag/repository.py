"""DAG Repository.

Database CRUD operations for DAG entities using SQLAlchemy async sessions.
"""

import json
from datetime import datetime
from typing import Sequence
from uuid import uuid4

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.platform.dag.models import (
    DAGDefinition,
    DAGDefinitionEdge,
    DAGDefinitionStep,
    DAGRun,
    DAGRunStatus,
    DAGRunStep,
    DAGStepStatus,
)


class DAGRepository:
    """Repository for DAG database operations."""

    def __init__(self, session: AsyncSession):
        self._session = session

    # =========================================================================
    # DAG Definitions
    # =========================================================================

    async def create_definition(
        self,
        name: str,
        steps: list[dict],
        edges: list[dict],
        description: str | None = None,
    ) -> DAGDefinition:
        """Create a new DAG definition with steps and edges.

        Args:
            name: Human-readable name for the DAG
            steps: List of step dicts with keys: name, task_name, default_params, retry_policy, timeout_seconds
            edges: List of edge dicts with keys: from_step, to_step, condition
            description: Optional description

        Returns:
            Created DAGDefinition
        """
        dag_def = DAGDefinition(
            id=str(uuid4()),
            name=name,
            description=description,
            version=1,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        self._session.add(dag_def)
        await self._session.flush()

        # Create step name to ID mapping for edge creation
        step_name_to_id: dict[str, str] = {}

        for position, step_data in enumerate(steps):
            step = DAGDefinitionStep(
                id=str(uuid4()),
                dag_definition_id=dag_def.id,
                name=step_data["name"],
                task_name=step_data["task_name"],
                default_params_json=json.dumps(step_data.get("default_params")) if step_data.get("default_params") else None,
                retry_policy_json=json.dumps(step_data.get("retry_policy")) if step_data.get("retry_policy") else None,
                timeout_seconds=step_data.get("timeout_seconds", 3600),
                position=position,
                created_at=datetime.utcnow(),
            )
            self._session.add(step)
            step_name_to_id[step.name] = step.id

        await self._session.flush()

        # Create edges
        for edge_data in edges:
            from_step_name = edge_data["from_step"]
            to_step_name = edge_data["to_step"]

            if from_step_name not in step_name_to_id:
                raise ValueError(f"Edge references unknown step: {from_step_name}")
            if to_step_name not in step_name_to_id:
                raise ValueError(f"Edge references unknown step: {to_step_name}")

            edge = DAGDefinitionEdge(
                id=str(uuid4()),
                dag_definition_id=dag_def.id,
                from_step_id=step_name_to_id[from_step_name],
                to_step_id=step_name_to_id[to_step_name],
                condition_json=json.dumps(edge_data.get("condition")) if edge_data.get("condition") else None,
            )
            self._session.add(edge)

        await self._session.flush()
        await self._session.refresh(dag_def)

        return dag_def

    async def get_definition(self, definition_id: str) -> DAGDefinition | None:
        """Get a DAG definition by ID with steps and edges."""
        result = await self._session.execute(
            select(DAGDefinition)
            .options(
                selectinload(DAGDefinition.steps),
                selectinload(DAGDefinition.edges),
            )
            .where(DAGDefinition.id == definition_id)
        )
        return result.scalar_one_or_none()

    async def get_definition_by_name(self, name: str) -> DAGDefinition | None:
        """Get a DAG definition by name (returns latest active version)."""
        result = await self._session.execute(
            select(DAGDefinition)
            .options(
                selectinload(DAGDefinition.steps),
                selectinload(DAGDefinition.edges),
            )
            .where(
                and_(
                    DAGDefinition.name == name,
                    DAGDefinition.is_active == True,
                )
            )
            .order_by(DAGDefinition.version.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_definitions(self, active_only: bool = True) -> Sequence[DAGDefinition]:
        """List all DAG definitions."""
        query = select(DAGDefinition)
        if active_only:
            query = query.where(DAGDefinition.is_active == True)
        query = query.order_by(DAGDefinition.name, DAGDefinition.version.desc())

        result = await self._session.execute(query)
        return result.scalars().all()

    async def deactivate_definition(self, definition_id: str) -> bool:
        """Deactivate a DAG definition (soft delete)."""
        dag_def = await self.get_definition(definition_id)
        if not dag_def:
            return False

        dag_def.is_active = False
        dag_def.updated_at = datetime.utcnow()
        await self._session.flush()
        return True

    # =========================================================================
    # DAG Runs
    # =========================================================================

    async def create_run(
        self,
        dag_definition: DAGDefinition,
        user_id: str | None = None,
        trigger_type: str = "api",
        context: dict | None = None,
        step_params: dict[str, dict] | None = None,
    ) -> DAGRun:
        """Create a new DAG run from a definition.

        Args:
            dag_definition: DAGDefinition to instantiate
            user_id: User who triggered the run
            trigger_type: How the run was triggered (api, scheduled, webhook)
            context: Shared context passed to all steps
            step_params: Override parameters per step (step_name -> params dict)

        Returns:
            Created DAGRun with all steps initialized
        """
        step_params = step_params or {}

        dag_run = DAGRun(
            id=str(uuid4()),
            dag_definition_id=dag_definition.id,
            user_id=user_id,
            status=DAGRunStatus.PENDING.value,
            trigger_type=trigger_type,
            context_json=json.dumps(context) if context else None,
            created_at=datetime.utcnow(),
        )
        self._session.add(dag_run)
        await self._session.flush()

        # Create run steps from definition steps
        for def_step in dag_definition.steps:
            # Merge default params with override params
            params = {}
            if def_step.default_params_json:
                params.update(json.loads(def_step.default_params_json))
            if def_step.name in step_params:
                params.update(step_params[def_step.name])

            run_step = DAGRunStep(
                id=str(uuid4()),
                dag_run_id=dag_run.id,
                definition_step_id=def_step.id,
                step_name=def_step.name,
                task_name=def_step.task_name,
                status=DAGStepStatus.PENDING.value,
                parameters_json=json.dumps(params) if params else None,
                retry_count=0,
                created_at=datetime.utcnow(),
            )
            self._session.add(run_step)

        await self._session.flush()
        await self._session.refresh(dag_run)

        return dag_run

    async def get_run(self, run_id: str) -> DAGRun | None:
        """Get a DAG run by ID with all steps."""
        result = await self._session.execute(
            select(DAGRun)
            .options(selectinload(DAGRun.steps))
            .where(DAGRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def list_runs(
        self,
        user_id: str | None = None,
        status: str | None = None,
        dag_definition_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[DAGRun]:
        """List DAG runs with optional filtering."""
        query = select(DAGRun).options(selectinload(DAGRun.steps))

        if user_id:
            query = query.where(DAGRun.user_id == user_id)
        if status:
            query = query.where(DAGRun.status == status)
        if dag_definition_id:
            query = query.where(DAGRun.dag_definition_id == dag_definition_id)

        query = query.order_by(DAGRun.created_at.desc()).limit(limit).offset(offset)

        result = await self._session.execute(query)
        return result.scalars().all()

    async def start_run(self, run_id: str) -> bool:
        """Mark a DAG run as started."""
        dag_run = await self.get_run(run_id)
        if not dag_run:
            return False

        dag_run.status = DAGRunStatus.RUNNING.value
        dag_run.started_at = datetime.utcnow()
        await self._session.flush()
        return True

    async def complete_run(self, run_id: str, status: DAGRunStatus = DAGRunStatus.COMPLETED) -> bool:
        """Mark a DAG run as completed/failed/cancelled."""
        dag_run = await self.get_run(run_id)
        if not dag_run:
            return False

        dag_run.status = status.value
        dag_run.completed_at = datetime.utcnow()
        await self._session.flush()
        return True

    async def fail_run(self, run_id: str, error_message: str) -> bool:
        """Mark a DAG run as failed with error message."""
        dag_run = await self.get_run(run_id)
        if not dag_run:
            return False

        dag_run.status = DAGRunStatus.FAILED.value
        dag_run.error_message = error_message
        dag_run.completed_at = datetime.utcnow()
        await self._session.flush()
        return True

    # =========================================================================
    # DAG Run Steps
    # =========================================================================

    async def get_run_step(self, step_id: str) -> DAGRunStep | None:
        """Get a DAG run step by ID."""
        result = await self._session.execute(
            select(DAGRunStep).where(DAGRunStep.id == step_id)
        )
        return result.scalar_one_or_none()

    async def get_run_step_by_name(self, run_id: str, step_name: str) -> DAGRunStep | None:
        """Get a DAG run step by run ID and step name."""
        result = await self._session.execute(
            select(DAGRunStep).where(
                and_(
                    DAGRunStep.dag_run_id == run_id,
                    DAGRunStep.step_name == step_name,
                )
            )
        )
        return result.scalar_one_or_none()

    async def queue_step(self, step_id: str, celery_task_id: str) -> bool:
        """Mark a step as queued with Celery task ID."""
        step = await self.get_run_step(step_id)
        if not step:
            return False

        step.status = DAGStepStatus.QUEUED.value
        step.celery_task_id = celery_task_id
        await self._session.flush()
        return True

    async def start_step(self, step_id: str) -> bool:
        """Mark a step as running."""
        step = await self.get_run_step(step_id)
        if not step:
            return False

        step.status = DAGStepStatus.RUNNING.value
        step.started_at = datetime.utcnow()
        await self._session.flush()
        return True

    async def complete_step(self, step_id: str, result: dict | None = None) -> bool:
        """Mark a step as completed with optional result."""
        step = await self.get_run_step(step_id)
        if not step:
            return False

        step.status = DAGStepStatus.COMPLETED.value
        step.result_json = json.dumps(result) if result else None
        step.completed_at = datetime.utcnow()
        await self._session.flush()
        return True

    async def fail_step(self, step_id: str, error_message: str) -> bool:
        """Mark a step as failed with error message."""
        step = await self.get_run_step(step_id)
        if not step:
            return False

        step.status = DAGStepStatus.FAILED.value
        step.error_message = error_message
        step.completed_at = datetime.utcnow()
        await self._session.flush()
        return True

    async def skip_step(self, step_id: str, reason: str = "upstream_failed") -> bool:
        """Mark a step as skipped."""
        step = await self.get_run_step(step_id)
        if not step:
            return False

        step.status = DAGStepStatus.SKIPPED.value
        step.error_message = reason
        step.completed_at = datetime.utcnow()
        await self._session.flush()
        return True

    async def increment_retry(self, step_id: str) -> int:
        """Increment retry count for a step, return new count."""
        step = await self.get_run_step(step_id)
        if not step:
            return -1

        step.retry_count += 1
        step.status = DAGStepStatus.PENDING.value  # Reset to pending for retry
        await self._session.flush()
        return step.retry_count

    async def get_pending_steps(self, run_id: str) -> Sequence[DAGRunStep]:
        """Get all pending steps for a run."""
        result = await self._session.execute(
            select(DAGRunStep).where(
                and_(
                    DAGRunStep.dag_run_id == run_id,
                    DAGRunStep.status == DAGStepStatus.PENDING.value,
                )
            )
        )
        return result.scalars().all()

    async def get_completed_step_names(self, run_id: str) -> set[str]:
        """Get names of all completed steps for a run."""
        result = await self._session.execute(
            select(DAGRunStep.step_name).where(
                and_(
                    DAGRunStep.dag_run_id == run_id,
                    DAGRunStep.status == DAGStepStatus.COMPLETED.value,
                )
            )
        )
        return {row[0] for row in result.all()}

    async def get_failed_step_names(self, run_id: str) -> set[str]:
        """Get names of all failed steps for a run."""
        result = await self._session.execute(
            select(DAGRunStep.step_name).where(
                and_(
                    DAGRunStep.dag_run_id == run_id,
                    DAGRunStep.status == DAGStepStatus.FAILED.value,
                )
            )
        )
        return {row[0] for row in result.all()}
