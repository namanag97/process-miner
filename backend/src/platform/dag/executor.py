"""DAG Executor.

Executes DAG steps using the TaskRegistry, handling:
- Task function lookup and invocation
- Context propagation between steps
- Celery integration for async execution
- Error handling and retries
"""

import json
import time
from datetime import datetime
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.platform.dag.models import DAGRun, DAGRunStep, DAGStepStatus
from src.platform.dag.registry import DAGContext, TaskResult, task_registry
from src.platform.dag.repository import DAGRepository
from src.platform.dag.service import DAGService

logger = structlog.get_logger(__name__)


class DAGExecutor:
    """Executor for running DAG steps.

    Handles step execution using registered task functions from TaskRegistry.
    Manages context propagation and result storage.
    """

    def __init__(self, session: AsyncSession):
        self._session = session
        self._repo = DAGRepository(session)
        self._service = DAGService(session)

    async def execute_step(
        self,
        step_id: str,
        override_params: dict[str, Any] | None = None,
    ) -> TaskResult:
        """Execute a single DAG step.

        Looks up the task function from TaskRegistry and executes it
        with the appropriate context and parameters.

        Args:
            step_id: ID of the DAGRunStep to execute
            override_params: Optional parameter overrides

        Returns:
            TaskResult from the task function
        """
        step = await self._repo.get_run_step(step_id)
        if not step:
            return TaskResult.fail(f"Step not found: {step_id}")

        dag_run = await self._repo.get_run(step.dag_run_id)
        if not dag_run:
            return TaskResult.fail(f"DAG run not found: {step.dag_run_id}")

        task_fn = task_registry.get(step.task_name)
        if not task_fn:
            error_msg = f"Task not registered: {step.task_name}"
            await self._service.fail_step(step_id, error_msg)
            return TaskResult.fail(error_msg)

        # Mark step as started
        await self._service.start_step(step_id)

        # Build context from run and previous steps
        ctx = await self._build_context(dag_run, step)

        # Merge parameters: default < stored < override
        params = {}
        if step.parameters_json:
            params.update(json.loads(step.parameters_json))
        if override_params:
            params.update(override_params)

        logger.info(
            "executing_dag_step",
            step_id=step_id,
            step_name=step.step_name,
            task_name=step.task_name,
            run_id=dag_run.id,
        )

        try:
            start = time.perf_counter()
            result = await task_fn(ctx, params)
            duration_ms = (time.perf_counter() - start) * 1000

            if result.success:
                await self._service.complete_step(step_id, result.data)
                logger.info(
                    "dag_step_executed",
                    step_id=step_id,
                    step_name=step.step_name,
                    success=True,
                    duration_ms=round(duration_ms, 2),
                )
            else:
                await self._service.fail_step(step_id, result.error or "Task failed")
                logger.warning(
                    "dag_step_executed",
                    step_id=step_id,
                    step_name=step.step_name,
                    success=False,
                    error=result.error,
                )

            return result

        except Exception as e:
            error_msg = str(e)
            await self._service.fail_step(step_id, error_msg)
            logger.error(
                "dag_step_execution_error",
                step_id=step_id,
                step_name=step.step_name,
                error=error_msg,
                exc_info=True,
            )
            return TaskResult.fail(error_msg)

    async def execute_ready_steps(self, run_id: str) -> list[TaskResult]:
        """Execute all ready steps for a DAG run.

        Gets all steps that are ready to execute (dependencies met)
        and executes them. This can be called repeatedly to progress
        through the DAG.

        Args:
            run_id: ID of the DAG run

        Returns:
            List of TaskResults from executed steps
        """
        ready_steps = await self._service.get_ready_steps(run_id)
        results = []

        for step in ready_steps:
            result = await self.execute_step(step.id)
            results.append(result)

        return results

    async def run_to_completion(
        self,
        run_id: str,
        max_iterations: int = 100,
    ) -> dict[str, Any]:
        """Run a DAG to completion synchronously.

        Keeps executing ready steps until the run is finished.
        Useful for testing or synchronous execution contexts.

        Args:
            run_id: ID of the DAG run
            max_iterations: Safety limit to prevent infinite loops

        Returns:
            Summary dict with final status and step results
        """
        dag_run = await self._repo.get_run(run_id)
        if not dag_run:
            return {"error": f"DAG run not found: {run_id}"}

        # Start the run
        await self._service.start_run(run_id)

        iteration = 0
        all_results = []

        while iteration < max_iterations:
            iteration += 1

            # Skip steps that should be skipped due to upstream failures
            steps_to_skip = await self._service.get_steps_to_skip(run_id)
            for step in steps_to_skip:
                await self._service.skip_step(step.id, "upstream_failed")

            # Execute ready steps
            ready_steps = await self._service.get_ready_steps(run_id)
            if not ready_steps:
                # No more steps to execute
                break

            for step in ready_steps:
                result = await self.execute_step(step.id)
                all_results.append({
                    "step_id": step.id,
                    "step_name": step.step_name,
                    "success": result.success,
                    "error": result.error,
                })

        # Get final status
        dag_run = await self._repo.get_run(run_id)
        return {
            "run_id": run_id,
            "status": dag_run.status if dag_run else "unknown",
            "iterations": iteration,
            "step_results": all_results,
        }

    async def _build_context(
        self,
        dag_run: DAGRun,
        current_step: DAGRunStep,
    ) -> DAGContext:
        """Build execution context from run and previous step results.

        Aggregates shared_data from all completed upstream steps
        to provide context for the current step.
        """
        # Parse run context
        run_context = {}
        if dag_run.context_json:
            run_context = json.loads(dag_run.context_json)

        # Aggregate results from completed steps
        shared_data = dict(run_context)
        for step in dag_run.steps:
            if step.status == DAGStepStatus.COMPLETED.value and step.result_json:
                step_result = json.loads(step.result_json)
                # Namespace by step name to avoid collisions
                shared_data[f"_step_{step.step_name}"] = step_result
                # Also merge top-level keys for convenience
                shared_data.update(step_result)

        return DAGContext(
            run_id=dag_run.id,
            user_id=dag_run.user_id,
            dataset_id=run_context.get("dataset_id"),
            model_id=run_context.get("model_id"),
            shared_data=shared_data,
            step_id=current_step.id,
        )


# Celery task for async step execution
def create_celery_step_task():
    """Create a Celery task for async DAG step execution.

    This allows steps to be executed asynchronously via Celery workers.
    """
    try:
        from src.platform.infrastructure.tasks.base import AsyncTask, celery_app, AsyncSessionLocal

        @celery_app.task(
            bind=True,
            base=AsyncTask,
            name="execute_dag_step",
            autoretry_for=(),
            retry_kwargs={"max_retries": 3},
        )
        async def execute_dag_step_task(self, step_id: str) -> dict[str, Any]:
            """Celery task for executing a DAG step."""
            async with AsyncSessionLocal() as session:
                executor = DAGExecutor(session)
                result = await executor.execute_step(step_id)
                await session.commit()
                return {
                    "success": result.success,
                    "data": result.data,
                    "error": result.error,
                }

        return execute_dag_step_task

    except ImportError:
        logger.warning("celery_not_available", msg="Celery task not created")
        return None


# Try to create the Celery task at module load
execute_dag_step_task = create_celery_step_task()
