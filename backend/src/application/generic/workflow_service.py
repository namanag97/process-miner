"""Workflow Orchestration Service."""

from typing import Optional, Dict, Any, List, Callable
from uuid import UUID, uuid4
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import logging

from src.infrastructure.workers.task_queue import task_queue, enqueue_job, get_job_status, Job

logger = logging.getLogger(__name__)


class PipelineStatus(str, Enum):
    """Status of a pipeline execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    """Status of a pipeline step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PipelineStep:
    """Definition of a pipeline step."""
    name: str
    job_type: str
    params: Dict[str, Any] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    condition: Optional[str] = None  # Expression to evaluate


@dataclass
class PipelineExecution:
    """Execution state of a pipeline."""
    id: UUID
    pipeline_name: str
    status: PipelineStatus = PipelineStatus.PENDING
    steps: Dict[str, StepStatus] = field(default_factory=dict)
    step_results: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "pipeline_name": self.pipeline_name,
            "status": self.status.value,
            "steps": {k: v.value for k, v in self.steps.items()},
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
        }


class WorkflowService:
    """
    Workflow Orchestration Service.
    Manages complex multi-step pipelines for process mining.
    """
    
    def __init__(self):
        self._pipelines: Dict[str, List[PipelineStep]] = {}
        self._executions: Dict[UUID, PipelineExecution] = {}
        self._step_handlers: Dict[str, Callable] = {}
        
        # Register built-in pipelines
        self._register_builtin_pipelines()
    
    def _register_builtin_pipelines(self):
        """Register standard process mining pipelines."""
        
        # Full Analysis Pipeline
        self._pipelines["full_analysis"] = [
            PipelineStep("ingest", "ingest_log", {"validate": True}),
            PipelineStep("discover", "discover_model", {"miner_type": "inductive"}, depends_on=["ingest"]),
            PipelineStep("conformance", "check_conformance", {}, depends_on=["discover"]),
            PipelineStep("performance", "analyze_performance", {}, depends_on=["ingest"]),
            PipelineStep("report", "generate_report", {}, depends_on=["conformance", "performance"]),
        ]
        
        # Discovery Only Pipeline
        self._pipelines["discovery_only"] = [
            PipelineStep("ingest", "ingest_log", {}),
            PipelineStep("alpha", "discover_model", {"miner_type": "alpha"}, depends_on=["ingest"]),
            PipelineStep("inductive", "discover_model", {"miner_type": "inductive"}, depends_on=["ingest"]),
            PipelineStep("heuristics", "discover_model", {"miner_type": "heuristics"}, depends_on=["ingest"]),
        ]
        
        # Conformance Analysis Pipeline
        self._pipelines["conformance_analysis"] = [
            PipelineStep("fitness", "calculate_fitness", {}),
            PipelineStep("precision", "calculate_precision", {}, depends_on=["fitness"]),
            PipelineStep("deviations", "detect_deviations", {}, depends_on=["fitness"]),
        ]
        
        # Batch Analysis Pipeline
        self._pipelines["batch_analysis"] = [
            PipelineStep("load_logs", "load_multiple_logs", {}),
            PipelineStep("compare", "compare_logs", {}, depends_on=["load_logs"]),
            PipelineStep("trends", "analyze_trends", {}, depends_on=["compare"]),
        ]
    
    def register_pipeline(self, name: str, steps: List[PipelineStep]) -> None:
        """Register a custom pipeline."""
        self._pipelines[name] = steps
        logger.info(f"Pipeline registered: {name} with {len(steps)} steps")
    
    def register_step_handler(self, job_type: str, handler: Callable) -> None:
        """Register a handler for a step type."""
        self._step_handlers[job_type] = handler
        task_queue.register_handler(job_type, handler)
    
    def get_available_pipelines(self) -> List[Dict[str, Any]]:
        """Get list of available pipelines."""
        return [
            {
                "name": name,
                "steps": [
                    {"name": step.name, "job_type": step.job_type, "depends_on": step.depends_on}
                    for step in steps
                ],
            }
            for name, steps in self._pipelines.items()
        ]
    
    async def start_pipeline(
        self,
        pipeline_name: str,
        params: Dict[str, Any] = None,
    ) -> PipelineExecution:
        """
        Start a pipeline execution.
        
        Args:
            pipeline_name: Name of the pipeline to execute
            params: Parameters to pass to pipeline steps
            
        Returns:
            PipelineExecution tracking the execution
        """
        if pipeline_name not in self._pipelines:
            raise ValueError(f"Unknown pipeline: {pipeline_name}")
        
        steps = self._pipelines[pipeline_name]
        
        execution = PipelineExecution(
            id=uuid4(),
            pipeline_name=pipeline_name,
            status=PipelineStatus.RUNNING,
            steps={step.name: StepStatus.PENDING for step in steps},
            started_at=datetime.utcnow(),
        )
        
        self._executions[execution.id] = execution
        
        # Start execution in background
        asyncio.create_task(self._execute_pipeline(execution, steps, params or {}))
        
        return execution
    
    async def _execute_pipeline(
        self,
        execution: PipelineExecution,
        steps: List[PipelineStep],
        params: Dict[str, Any],
    ) -> None:
        """Execute pipeline steps in order respecting dependencies."""
        try:
            completed = set()
            
            while len(completed) < len(steps):
                # Find steps that can run
                runnable = []
                for step in steps:
                    if step.name in completed:
                        continue
                    if execution.steps[step.name] == StepStatus.FAILED:
                        continue
                    if all(dep in completed for dep in step.depends_on):
                        runnable.append(step)
                
                if not runnable:
                    # No progress possible - check for failures
                    if any(s == StepStatus.FAILED for s in execution.steps.values()):
                        break
                    # Deadlock
                    raise RuntimeError("Pipeline deadlock detected")
                
                # Execute runnable steps in parallel
                tasks = []
                for step in runnable:
                    execution.steps[step.name] = StepStatus.RUNNING
                    task = asyncio.create_task(self._execute_step(step, params, execution))
                    tasks.append((step.name, task))
                
                # Wait for all to complete
                for step_name, task in tasks:
                    try:
                        result = await task
                        execution.steps[step_name] = StepStatus.COMPLETED
                        execution.step_results[step_name] = result
                        completed.add(step_name)
                    except Exception as e:
                        execution.steps[step_name] = StepStatus.FAILED
                        execution.error = f"Step {step_name} failed: {str(e)}"
                        logger.error(f"Pipeline step failed: {step_name} - {e}")
            
            # Determine final status
            if all(s == StepStatus.COMPLETED for s in execution.steps.values()):
                execution.status = PipelineStatus.COMPLETED
            else:
                execution.status = PipelineStatus.FAILED
                
        except Exception as e:
            execution.status = PipelineStatus.FAILED
            execution.error = str(e)
            logger.error(f"Pipeline execution failed: {e}")
        finally:
            execution.completed_at = datetime.utcnow()
    
    async def _execute_step(
        self,
        step: PipelineStep,
        params: Dict[str, Any],
        execution: PipelineExecution,
    ) -> Any:
        """Execute a single pipeline step."""
        # Merge step params with execution params
        step_params = {**params, **step.params}
        step_params["execution_id"] = str(execution.id)
        step_params["step_name"] = step.name
        
        # Add results from previous steps
        step_params["previous_results"] = execution.step_results.copy()
        
        # Enqueue job
        job_id = await enqueue_job(step.job_type, step_params)
        
        # Wait for completion (poll)
        while True:
            job = get_job_status(job_id)
            if job is None:
                raise RuntimeError(f"Job not found: {job_id}")
            
            if job.status.value == "completed":
                return job.result
            elif job.status.value == "failed":
                raise RuntimeError(job.error or "Job failed")
            
            await asyncio.sleep(0.1)
    
    def get_execution(self, execution_id: UUID) -> Optional[PipelineExecution]:
        """Get execution status by ID."""
        return self._executions.get(execution_id)
    
    def get_execution_status(self, execution_id: UUID) -> Optional[Dict[str, Any]]:
        """Get execution status as dict."""
        execution = self._executions.get(execution_id)
        return execution.to_dict() if execution else None
    
    def cancel_execution(self, execution_id: UUID) -> bool:
        """Cancel a running execution."""
        execution = self._executions.get(execution_id)
        if not execution:
            return False
        
        if execution.status == PipelineStatus.RUNNING:
            execution.status = PipelineStatus.CANCELLED
            execution.completed_at = datetime.utcnow()
            return True
        
        return False
    
    def list_executions(
        self,
        status: Optional[PipelineStatus] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """List pipeline executions."""
        executions = list(self._executions.values())
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        executions.sort(key=lambda e: e.started_at or datetime.min, reverse=True)
        
        return [e.to_dict() for e in executions[:limit]]


# Singleton instance
workflow_service = WorkflowService()
