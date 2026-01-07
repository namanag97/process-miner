"""DAG Service.

Business logic layer for DAG orchestration including:
- Creating and managing DAG definitions
- Triggering and monitoring DAG runs
- Orchestrating step execution
"""

from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.infra.dag.engine import dag_engine
from src.infra.dag.models import (
    DAGDefinition,
    DAGRun,
    DAGRunStatus,
    DAGRunStep,
    DAGStepStatus,
)
from src.infra.dag.repository import DAGRepository

logger = structlog.get_logger(__name__)


class DAGService:
    """Service for managing DAG workflows."""

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repo = DAGRepository(session)

    # =========================================================================
    # Definition Management
    # =========================================================================

    async def create_definition(
        self,
        name: str,
        steps: list[dict],
        edges: list[dict],
        description: str | None = None,
    ) -> DAGDefinition:
        """Create a new DAG definition.

        Args:
            name: Human-readable name
            steps: List of step configs with name, task_name, default_params
            edges: List of edges with from_step, to_step names

        Returns:
            Created DAGDefinition

        Raises:
            ValueError: If DAG validation fails
        """
        # Validate before creating
        is_valid, error = dag_engine.validate_dag(steps, edges)
        if not is_valid:
            raise ValueError(f"Invalid DAG configuration: {error}")

        dag_def = await self._repo.create_definition(
            name=name,
            steps=steps,
            edges=edges,
            description=description,
        )

        logger.info(
            "dag_definition_created",
            definition_id=dag_def.id,
            name=name,
            step_count=len(steps),
            edge_count=len(edges),
        )

        return dag_def

    async def get_definition(self, definition_id: str) -> DAGDefinition | None:
        """Get a DAG definition by ID."""
        return await self._repo.get_definition(definition_id)

    async def get_definition_by_name(self, name: str) -> DAGDefinition | None:
        """Get a DAG definition by name."""
        return await self._repo.get_definition_by_name(name)

    async def list_definitions(self, active_only: bool = True) -> list[DAGDefinition]:
        """List all DAG definitions."""
        return list(await self._repo.list_definitions(active_only=active_only))

    # =========================================================================
    # Run Management
    # =========================================================================

    async def trigger_run(
        self,
        definition_id: str,
        user_id: str | None = None,
        context: dict | None = None,
        step_params: dict[str, dict] | None = None,
        trigger_type: str = "api",
    ) -> DAGRun:
        """Trigger a new DAG run.

        Args:
            definition_id: ID of the DAG definition to run
            user_id: User triggering the run
            context: Shared context for all steps
            step_params: Per-step parameter overrides
            trigger_type: How the run was triggered (api, scheduled, webhook)

        Returns:
            Created DAGRun

        Raises:
            ValueError: If definition not found
        """
        dag_def = await self._repo.get_definition(definition_id)
        if not dag_def:
            raise ValueError(f"DAG definition not found: {definition_id}")

        if not dag_def.is_active:
            raise ValueError(f"DAG definition is not active: {definition_id}")

        dag_run = await self._repo.create_run(
            dag_definition=dag_def,
            user_id=user_id,
            trigger_type=trigger_type,
            context=context,
            step_params=step_params,
        )

        logger.info(
            "dag_run_triggered",
            run_id=dag_run.id,
            definition_id=definition_id,
            user_id=user_id,
            step_count=len(dag_run.steps),
        )

        return dag_run

    async def trigger_run_by_name(
        self,
        definition_name: str,
        user_id: str | None = None,
        context: dict | None = None,
        step_params: dict[str, dict] | None = None,
    ) -> DAGRun:
        """Trigger a DAG run by definition name."""
        dag_def = await self._repo.get_definition_by_name(definition_name)
        if not dag_def:
            raise ValueError(f"DAG definition not found: {definition_name}")

        return await self.trigger_run(
            definition_id=dag_def.id,
            user_id=user_id,
            context=context,
            step_params=step_params,
        )

    async def get_run(self, run_id: str) -> DAGRun | None:
        """Get a DAG run by ID."""
        return await self._repo.get_run(run_id)

    async def list_runs(
        self,
        user_id: str | None = None,
        status: str | None = None,
        definition_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DAGRun]:
        """List DAG runs with optional filtering."""
        return list(
            await self._repo.list_runs(
                user_id=user_id,
                status=status,
                dag_definition_id=definition_id,
                limit=limit,
                offset=offset,
            )
        )

    # =========================================================================
    # Execution Orchestration
    # =========================================================================

    async def start_run(self, run_id: str) -> bool:
        """Mark a DAG run as started."""
        dag_run = await self._repo.get_run(run_id)
        if not dag_run:
            return False

        success = await self._repo.start_run(run_id)
        if success:
            logger.info("dag_run_started", run_id=run_id)

        return success

    async def get_ready_steps(self, run_id: str) -> list[DAGRunStep]:
        """Get steps that are ready to execute for a run.

        A step is ready if status is PENDING and all dependencies are COMPLETED.
        """
        dag_run = await self._repo.get_run(run_id)
        if not dag_run:
            return []

        dag_def = await self._repo.get_definition(dag_run.dag_definition_id)
        if not dag_def:
            return []

        return dag_engine.get_ready_steps(dag_run, dag_def)

    async def get_steps_to_skip(self, run_id: str) -> list[DAGRunStep]:
        """Get steps that should be skipped due to upstream failures."""
        dag_run = await self._repo.get_run(run_id)
        if not dag_run:
            return []

        dag_def = await self._repo.get_definition(dag_run.dag_definition_id)
        if not dag_def:
            return []

        return dag_engine.get_steps_to_skip(dag_run, dag_def)

    async def queue_step(
        self,
        step_id: str,
        celery_task_id: str,
    ) -> bool:
        """Mark a step as queued with Celery task ID."""
        success = await self._repo.queue_step(step_id, celery_task_id)
        if success:
            logger.debug("dag_step_queued", step_id=step_id, task_id=celery_task_id)
        return success

    async def start_step(self, step_id: str) -> bool:
        """Mark a step as running."""
        return await self._repo.start_step(step_id)

    async def complete_step(
        self,
        step_id: str,
        result: dict | None = None,
    ) -> bool:
        """Mark a step as completed."""
        success = await self._repo.complete_step(step_id, result)
        if success:
            step = await self._repo.get_run_step(step_id)
            if step:
                logger.info(
                    "dag_step_completed",
                    step_id=step_id,
                    step_name=step.step_name,
                    run_id=step.dag_run_id,
                )
                # Check if run is finished
                await self._check_run_completion(step.dag_run_id)

        return success

    async def fail_step(
        self,
        step_id: str,
        error_message: str,
    ) -> bool:
        """Mark a step as failed."""
        success = await self._repo.fail_step(step_id, error_message)
        if success:
            step = await self._repo.get_run_step(step_id)
            if step:
                logger.warning(
                    "dag_step_failed",
                    step_id=step_id,
                    step_name=step.step_name,
                    run_id=step.dag_run_id,
                    error=error_message,
                )
                # Skip downstream steps and check completion
                await self._skip_downstream_steps(step.dag_run_id)
                await self._check_run_completion(step.dag_run_id)

        return success

    async def skip_step(self, step_id: str, reason: str = "upstream_failed") -> bool:
        """Mark a step as skipped."""
        return await self._repo.skip_step(step_id, reason)

    async def cancel_run(self, run_id: str) -> bool:
        """Cancel a DAG run and all pending steps."""
        dag_run = await self._repo.get_run(run_id)
        if not dag_run:
            return False

        # Cancel all pending/queued steps
        for step in dag_run.steps:
            if step.status in (DAGStepStatus.PENDING.value, DAGStepStatus.QUEUED.value):
                await self._repo.skip_step(step.id, "cancelled")

        # Mark run as cancelled
        await self._repo.complete_run(run_id, DAGRunStatus.CANCELLED)

        logger.info("dag_run_cancelled", run_id=run_id)
        return True

    async def _skip_downstream_steps(self, run_id: str) -> None:
        """Skip all steps that have failed upstream dependencies."""
        steps_to_skip = await self.get_steps_to_skip(run_id)
        for step in steps_to_skip:
            await self._repo.skip_step(step.id, "upstream_failed")
            logger.debug(
                "dag_step_skipped",
                step_id=step.id,
                step_name=step.step_name,
            )

    async def _check_run_completion(self, run_id: str) -> None:
        """Check if a DAG run is complete and update status."""
        dag_run = await self._repo.get_run(run_id)
        if not dag_run:
            return

        if dag_engine.is_run_finished(dag_run):
            final_status = dag_engine.compute_final_status(dag_run)
            status_enum = (
                DAGRunStatus(final_status)
                if final_status in [s.value for s in DAGRunStatus]
                else DAGRunStatus.PARTIAL
            )

            await self._repo.complete_run(run_id, status_enum)
            logger.info(
                "dag_run_completed",
                run_id=run_id,
                status=final_status,
            )

    # =========================================================================
    # Utility Methods
    # =========================================================================

    async def get_run_summary(self, run_id: str) -> dict[str, Any] | None:
        """Get a summary of a DAG run for API responses."""
        dag_run = await self._repo.get_run(run_id)
        if not dag_run:
            return None

        step_summaries = []
        for step in dag_run.steps:
            step_summaries.append(
                {
                    "id": step.id,
                    "name": step.step_name,
                    "task_name": step.task_name,
                    "status": step.status,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "error_message": step.error_message,
                }
            )

        return {
            "id": dag_run.id,
            "definition_id": dag_run.dag_definition_id,
            "status": dag_run.status,
            "trigger_type": dag_run.trigger_type,
            "created_at": dag_run.created_at.isoformat(),
            "started_at": dag_run.started_at.isoformat() if dag_run.started_at else None,
            "completed_at": dag_run.completed_at.isoformat() if dag_run.completed_at else None,
            "steps": step_summaries,
        }
