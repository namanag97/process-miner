"""DAG Engine.

Core DAG execution logic including:
- Topological sort for execution order
- Ready-to-run step detection
- Dependency graph traversal
"""

from collections import defaultdict
from dataclasses import dataclass, field

from src.platform.dag.models import (
    DAGDefinition,
    DAGRun,
    DAGRunStep,
    DAGStepStatus,
)


@dataclass
class DAGNode:
    """Represents a node in the DAG execution graph."""

    step_id: str
    step_name: str
    task_name: str
    status: DAGStepStatus
    dependencies: set[str] = field(default_factory=set)  # Set of step names this depends on
    dependents: set[str] = field(default_factory=set)  # Set of step names that depend on this


class DAGEngine:
    """Engine for DAG execution logic.

    Handles:
    - Building execution graphs from definitions
    - Determining which steps are ready to run
    - Topological sorting for execution order
    - Dependency resolution
    """

    def build_dependency_graph(
        self,
        dag_definition: DAGDefinition,
    ) -> dict[str, DAGNode]:
        """Build a dependency graph from a DAG definition.

        Args:
            dag_definition: The DAG definition with steps and edges

        Returns:
            Dict mapping step_name to DAGNode
        """
        graph: dict[str, DAGNode] = {}

        # Create nodes for each step
        for step in dag_definition.steps:
            graph[step.name] = DAGNode(
                step_id=step.id,
                step_name=step.name,
                task_name=step.task_name,
                status=DAGStepStatus.PENDING,
                dependencies=set(),
                dependents=set(),
            )

        # Add edges
        for edge in dag_definition.edges:
            from_step_name = next(
                (s.name for s in dag_definition.steps if s.id == edge.from_step_id), None
            )
            to_step_name = next(
                (s.name for s in dag_definition.steps if s.id == edge.to_step_id), None
            )

            if from_step_name and to_step_name:
                graph[to_step_name].dependencies.add(from_step_name)
                graph[from_step_name].dependents.add(to_step_name)

        return graph

    def build_runtime_graph(
        self,
        dag_run: DAGRun,
        dag_definition: DAGDefinition,
    ) -> dict[str, DAGNode]:
        """Build a runtime execution graph with current step statuses.

        Args:
            dag_run: The DAG run with current step states
            dag_definition: The DAG definition with edges

        Returns:
            Dict mapping step_name to DAGNode with current statuses
        """
        # Start with definition graph
        graph = self.build_dependency_graph(dag_definition)

        # Update with runtime statuses
        for run_step in dag_run.steps:
            if run_step.step_name in graph:
                graph[run_step.step_name].step_id = run_step.id
                graph[run_step.step_name].status = DAGStepStatus(run_step.status)

        return graph

    def get_ready_steps(
        self,
        dag_run: DAGRun,
        dag_definition: DAGDefinition,
    ) -> list[DAGRunStep]:
        """Get steps that are ready to execute.

        A step is ready if:
        1. Its status is PENDING
        2. All its dependencies are COMPLETED

        Args:
            dag_run: The DAG run to check
            dag_definition: The DAG definition with dependencies

        Returns:
            List of DAGRunStep objects ready to execute
        """
        graph = self.build_runtime_graph(dag_run, dag_definition)

        # Build step_name -> DAGRunStep mapping
        step_by_name: dict[str, DAGRunStep] = {step.step_name: step for step in dag_run.steps}

        ready_steps: list[DAGRunStep] = []

        for step_name, node in graph.items():
            # Skip if not pending
            if node.status != DAGStepStatus.PENDING:
                continue

            # Check if all dependencies are completed
            all_deps_completed = all(
                graph[dep_name].status == DAGStepStatus.COMPLETED for dep_name in node.dependencies
            )

            if all_deps_completed:
                if step_name in step_by_name:
                    ready_steps.append(step_by_name[step_name])

        return ready_steps

    def get_steps_to_skip(
        self,
        dag_run: DAGRun,
        dag_definition: DAGDefinition,
    ) -> list[DAGRunStep]:
        """Get steps that should be skipped due to upstream failures.

        A step should be skipped if:
        1. Its status is PENDING
        2. Any of its dependencies is FAILED or SKIPPED

        Args:
            dag_run: The DAG run to check
            dag_definition: The DAG definition with dependencies

        Returns:
            List of DAGRunStep objects that should be skipped
        """
        graph = self.build_runtime_graph(dag_run, dag_definition)
        step_by_name: dict[str, DAGRunStep] = {step.step_name: step for step in dag_run.steps}

        skip_steps: list[DAGRunStep] = []

        for step_name, node in graph.items():
            if node.status != DAGStepStatus.PENDING:
                continue

            # Check if any dependency failed or was skipped
            has_failed_dep = any(
                graph[dep_name].status in (DAGStepStatus.FAILED, DAGStepStatus.SKIPPED)
                for dep_name in node.dependencies
            )

            if has_failed_dep:
                if step_name in step_by_name:
                    skip_steps.append(step_by_name[step_name])

        return skip_steps

    def topological_sort(
        self,
        dag_definition: DAGDefinition,
    ) -> list[str]:
        """Return step names in topological order.

        Uses Kahn's algorithm for topological sorting.

        Args:
            dag_definition: The DAG definition to sort

        Returns:
            List of step names in execution order

        Raises:
            ValueError: If the graph contains a cycle
        """
        graph = self.build_dependency_graph(dag_definition)

        # Calculate in-degrees
        in_degree: dict[str, int] = {name: len(node.dependencies) for name, node in graph.items()}

        # Start with nodes that have no dependencies
        queue: list[str] = [name for name, degree in in_degree.items() if degree == 0]
        result: list[str] = []

        while queue:
            # Pop from front (FIFO for stable ordering)
            current = queue.pop(0)
            result.append(current)

            # Decrease in-degree for all dependents
            for dependent in graph[current].dependents:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        # Check for cycle
        if len(result) != len(graph):
            remaining = set(graph.keys()) - set(result)
            raise ValueError(f"DAG contains a cycle involving: {remaining}")

        return result

    def validate_dag(
        self,
        steps: list[dict],
        edges: list[dict],
    ) -> tuple[bool, str]:
        """Validate a DAG configuration before creating.

        Args:
            steps: List of step configurations
            edges: List of edge configurations

        Returns:
            (is_valid, error_message)
        """
        if not steps:
            return False, "DAG must have at least one step"

        step_names = {step["name"] for step in steps}

        # Check for duplicate step names
        if len(step_names) != len(steps):
            return False, "Duplicate step names found"

        # Validate edges reference valid steps
        for edge in edges:
            if edge["from_step"] not in step_names:
                return False, f"Edge references unknown step: {edge['from_step']}"
            if edge["to_step"] not in step_names:
                return False, f"Edge references unknown step: {edge['to_step']}"
            if edge["from_step"] == edge["to_step"]:
                return False, f"Self-referencing edge: {edge['from_step']}"

        # Build temporary graph to check for cycles
        graph: dict[str, set[str]] = defaultdict(set)
        for edge in edges:
            graph[edge["to_step"]].add(edge["from_step"])

        # Check for cycles using DFS
        visited: set[str] = set()
        rec_stack: set[str] = set()

        def has_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)

            for dep in graph[node]:
                if dep not in visited:
                    if has_cycle(dep):
                        return True
                elif dep in rec_stack:
                    return True

            rec_stack.remove(node)
            return False

        for step_name in step_names:
            if step_name not in visited:
                if has_cycle(step_name):
                    return False, "DAG contains a cycle"

        return True, "OK"

    def is_run_finished(self, dag_run: DAGRun) -> bool:
        """Check if a DAG run has finished (all steps terminal)."""
        terminal_statuses = {
            DAGStepStatus.COMPLETED.value,
            DAGStepStatus.FAILED.value,
            DAGStepStatus.SKIPPED.value,
            DAGStepStatus.CANCELLED.value,
        }

        return all(step.status in terminal_statuses for step in dag_run.steps)

    def compute_final_status(self, dag_run: DAGRun) -> str:
        """Compute the final status of a DAG run based on step statuses.

        Returns:
            - COMPLETED if all steps completed successfully
            - FAILED if any step failed
            - PARTIAL if some steps failed but others completed
            - CANCELLED if any step was cancelled
        """
        statuses = {step.status for step in dag_run.steps}

        if DAGStepStatus.CANCELLED.value in statuses:
            return DAGStepStatus.CANCELLED.value

        if DAGStepStatus.FAILED.value in statuses:
            if DAGStepStatus.COMPLETED.value in statuses:
                return "partial"  # Some failed, some completed
            return DAGStepStatus.FAILED.value

        if all(step.status == DAGStepStatus.COMPLETED.value for step in dag_run.steps):
            return DAGStepStatus.COMPLETED.value

        return "partial"


# Singleton instance
dag_engine = DAGEngine()
