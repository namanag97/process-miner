"""Unit tests for DAG Engine.

Tests core DAG execution logic including topological sort,
ready-step detection, and cycle validation.
"""

from src.infra.dag.engine import DAGEngine


class TestDAGEngineValidation:
    """Tests for DAG validation logic."""

    def setup_method(self):
        self.engine = DAGEngine()

    def test_validate_empty_dag_fails(self):
        """Empty DAG should fail validation."""
        is_valid, error = self.engine.validate_dag([], [])
        assert not is_valid
        assert "at least one step" in error

    def test_validate_simple_dag_passes(self):
        """Simple valid DAG should pass."""
        steps = [
            {"name": "step_a", "task_name": "task_a"},
            {"name": "step_b", "task_name": "task_b"},
        ]
        edges = [{"from_step": "step_a", "to_step": "step_b"}]

        is_valid, error = self.engine.validate_dag(steps, edges)
        assert is_valid
        assert error == "OK"

    def test_validate_parallel_dag_passes(self):
        """DAG with parallel steps should pass."""
        steps = [
            {"name": "start", "task_name": "start_task"},
            {"name": "parallel_a", "task_name": "task_a"},
            {"name": "parallel_b", "task_name": "task_b"},
            {"name": "end", "task_name": "end_task"},
        ]
        edges = [
            {"from_step": "start", "to_step": "parallel_a"},
            {"from_step": "start", "to_step": "parallel_b"},
            {"from_step": "parallel_a", "to_step": "end"},
            {"from_step": "parallel_b", "to_step": "end"},
        ]

        is_valid, _error = self.engine.validate_dag(steps, edges)
        assert is_valid

    def test_validate_duplicate_step_names_fails(self):
        """Duplicate step names should fail."""
        steps = [
            {"name": "step_a", "task_name": "task_a"},
            {"name": "step_a", "task_name": "task_b"},  # Duplicate
        ]
        edges = []

        is_valid, error = self.engine.validate_dag(steps, edges)
        assert not is_valid
        assert "Duplicate" in error

    def test_validate_unknown_step_in_edge_fails(self):
        """Edge referencing unknown step should fail."""
        steps = [{"name": "step_a", "task_name": "task_a"}]
        edges = [{"from_step": "step_a", "to_step": "nonexistent"}]

        is_valid, error = self.engine.validate_dag(steps, edges)
        assert not is_valid
        assert "unknown step" in error

    def test_validate_self_referencing_edge_fails(self):
        """Self-referencing edge should fail."""
        steps = [{"name": "step_a", "task_name": "task_a"}]
        edges = [{"from_step": "step_a", "to_step": "step_a"}]

        is_valid, error = self.engine.validate_dag(steps, edges)
        assert not is_valid
        assert "Self-referencing" in error

    def test_validate_cycle_fails(self):
        """Cycle in DAG should fail."""
        steps = [
            {"name": "step_a", "task_name": "task_a"},
            {"name": "step_b", "task_name": "task_b"},
            {"name": "step_c", "task_name": "task_c"},
        ]
        edges = [
            {"from_step": "step_a", "to_step": "step_b"},
            {"from_step": "step_b", "to_step": "step_c"},
            {"from_step": "step_c", "to_step": "step_a"},  # Creates cycle
        ]

        is_valid, error = self.engine.validate_dag(steps, edges)
        assert not is_valid
        assert "cycle" in error.lower()


class TestDAGEngineTopologicalSort:
    """Tests for topological sorting."""

    def setup_method(self):
        self.engine = DAGEngine()

    def test_topological_sort_linear(self):
        """Linear DAG should sort correctly."""
        from src.infra.dag.models import DAGDefinition, DAGDefinitionEdge, DAGDefinitionStep

        # Create mock definition
        dag_def = DAGDefinition(id="test-1", name="test")
        dag_def.steps = [
            DAGDefinitionStep(
                id="s1", name="first", task_name="t1", position=0, dag_definition_id="test-1"
            ),
            DAGDefinitionStep(
                id="s2", name="second", task_name="t2", position=1, dag_definition_id="test-1"
            ),
            DAGDefinitionStep(
                id="s3", name="third", task_name="t3", position=2, dag_definition_id="test-1"
            ),
        ]
        dag_def.edges = [
            DAGDefinitionEdge(
                id="e1", dag_definition_id="test-1", from_step_id="s1", to_step_id="s2"
            ),
            DAGDefinitionEdge(
                id="e2", dag_definition_id="test-1", from_step_id="s2", to_step_id="s3"
            ),
        ]

        result = self.engine.topological_sort(dag_def)

        assert result == ["first", "second", "third"]

    def test_topological_sort_diamond(self):
        """Diamond DAG (A -> B,C -> D) should sort with B,C before D."""
        from src.infra.dag.models import DAGDefinition, DAGDefinitionEdge, DAGDefinitionStep

        dag_def = DAGDefinition(id="test-2", name="test")
        dag_def.steps = [
            DAGDefinitionStep(
                id="s1", name="start", task_name="t1", position=0, dag_definition_id="test-2"
            ),
            DAGDefinitionStep(
                id="s2", name="branch_a", task_name="t2", position=1, dag_definition_id="test-2"
            ),
            DAGDefinitionStep(
                id="s3", name="branch_b", task_name="t3", position=2, dag_definition_id="test-2"
            ),
            DAGDefinitionStep(
                id="s4", name="join", task_name="t4", position=3, dag_definition_id="test-2"
            ),
        ]
        dag_def.edges = [
            DAGDefinitionEdge(
                id="e1", dag_definition_id="test-2", from_step_id="s1", to_step_id="s2"
            ),
            DAGDefinitionEdge(
                id="e2", dag_definition_id="test-2", from_step_id="s1", to_step_id="s3"
            ),
            DAGDefinitionEdge(
                id="e3", dag_definition_id="test-2", from_step_id="s2", to_step_id="s4"
            ),
            DAGDefinitionEdge(
                id="e4", dag_definition_id="test-2", from_step_id="s3", to_step_id="s4"
            ),
        ]

        result = self.engine.topological_sort(dag_def)

        # Start must be first, join must be last
        assert result[0] == "start"
        assert result[-1] == "join"
        # branch_a and branch_b must come before join
        assert result.index("branch_a") < result.index("join")
        assert result.index("branch_b") < result.index("join")


class TestDAGEngineReadySteps:
    """Tests for ready step detection."""

    def setup_method(self):
        self.engine = DAGEngine()

    def test_get_ready_steps_initial(self):
        """Initially, only steps with no dependencies should be ready."""
        from src.infra.dag.models import (
            DAGDefinition,
            DAGDefinitionEdge,
            DAGDefinitionStep,
            DAGRun,
            DAGRunStep,
            DAGStepStatus,
        )

        # Definition with start -> middle -> end
        dag_def = DAGDefinition(id="d1", name="test")
        dag_def.steps = [
            DAGDefinitionStep(
                id="ds1", name="start", task_name="t1", position=0, dag_definition_id="d1"
            ),
            DAGDefinitionStep(
                id="ds2", name="middle", task_name="t2", position=1, dag_definition_id="d1"
            ),
            DAGDefinitionStep(
                id="ds3", name="end", task_name="t3", position=2, dag_definition_id="d1"
            ),
        ]
        dag_def.edges = [
            DAGDefinitionEdge(
                id="e1", dag_definition_id="d1", from_step_id="ds1", to_step_id="ds2"
            ),
            DAGDefinitionEdge(
                id="e2", dag_definition_id="d1", from_step_id="ds2", to_step_id="ds3"
            ),
        ]

        # Run with all pending
        dag_run = DAGRun(id="r1", dag_definition_id="d1")
        dag_run.steps = [
            DAGRunStep(
                id="rs1",
                dag_run_id="r1",
                step_name="start",
                task_name="t1",
                status=DAGStepStatus.PENDING.value,
            ),
            DAGRunStep(
                id="rs2",
                dag_run_id="r1",
                step_name="middle",
                task_name="t2",
                status=DAGStepStatus.PENDING.value,
            ),
            DAGRunStep(
                id="rs3",
                dag_run_id="r1",
                step_name="end",
                task_name="t3",
                status=DAGStepStatus.PENDING.value,
            ),
        ]

        ready = self.engine.get_ready_steps(dag_run, dag_def)

        assert len(ready) == 1
        assert ready[0].step_name == "start"

    def test_get_ready_steps_after_completion(self):
        """After start completes, middle should be ready."""
        from src.infra.dag.models import (
            DAGDefinition,
            DAGDefinitionEdge,
            DAGDefinitionStep,
            DAGRun,
            DAGRunStep,
            DAGStepStatus,
        )

        dag_def = DAGDefinition(id="d1", name="test")
        dag_def.steps = [
            DAGDefinitionStep(
                id="ds1", name="start", task_name="t1", position=0, dag_definition_id="d1"
            ),
            DAGDefinitionStep(
                id="ds2", name="middle", task_name="t2", position=1, dag_definition_id="d1"
            ),
        ]
        dag_def.edges = [
            DAGDefinitionEdge(
                id="e1", dag_definition_id="d1", from_step_id="ds1", to_step_id="ds2"
            ),
        ]

        dag_run = DAGRun(id="r1", dag_definition_id="d1")
        dag_run.steps = [
            DAGRunStep(
                id="rs1",
                dag_run_id="r1",
                step_name="start",
                task_name="t1",
                status=DAGStepStatus.COMPLETED.value,
            ),
            DAGRunStep(
                id="rs2",
                dag_run_id="r1",
                step_name="middle",
                task_name="t2",
                status=DAGStepStatus.PENDING.value,
            ),
        ]

        ready = self.engine.get_ready_steps(dag_run, dag_def)

        assert len(ready) == 1
        assert ready[0].step_name == "middle"

    def test_get_ready_steps_parallel(self):
        """Multiple parallel steps should all be ready."""
        from src.infra.dag.models import (
            DAGDefinition,
            DAGDefinitionEdge,
            DAGDefinitionStep,
            DAGRun,
            DAGRunStep,
            DAGStepStatus,
        )

        dag_def = DAGDefinition(id="d1", name="test")
        dag_def.steps = [
            DAGDefinitionStep(
                id="ds1", name="start", task_name="t1", position=0, dag_definition_id="d1"
            ),
            DAGDefinitionStep(
                id="ds2", name="parallel_a", task_name="t2", position=1, dag_definition_id="d1"
            ),
            DAGDefinitionStep(
                id="ds3", name="parallel_b", task_name="t3", position=2, dag_definition_id="d1"
            ),
        ]
        dag_def.edges = [
            DAGDefinitionEdge(
                id="e1", dag_definition_id="d1", from_step_id="ds1", to_step_id="ds2"
            ),
            DAGDefinitionEdge(
                id="e2", dag_definition_id="d1", from_step_id="ds1", to_step_id="ds3"
            ),
        ]

        dag_run = DAGRun(id="r1", dag_definition_id="d1")
        dag_run.steps = [
            DAGRunStep(
                id="rs1",
                dag_run_id="r1",
                step_name="start",
                task_name="t1",
                status=DAGStepStatus.COMPLETED.value,
            ),
            DAGRunStep(
                id="rs2",
                dag_run_id="r1",
                step_name="parallel_a",
                task_name="t2",
                status=DAGStepStatus.PENDING.value,
            ),
            DAGRunStep(
                id="rs3",
                dag_run_id="r1",
                step_name="parallel_b",
                task_name="t3",
                status=DAGStepStatus.PENDING.value,
            ),
        ]

        ready = self.engine.get_ready_steps(dag_run, dag_def)

        assert len(ready) == 2
        names = {s.step_name for s in ready}
        assert names == {"parallel_a", "parallel_b"}


class TestDAGEngineStepsToSkip:
    """Tests for skip detection due to upstream failures."""

    def setup_method(self):
        self.engine = DAGEngine()

    def test_steps_to_skip_on_failure(self):
        """Downstream steps should be skipped if upstream fails."""
        from src.infra.dag.models import (
            DAGDefinition,
            DAGDefinitionEdge,
            DAGDefinitionStep,
            DAGRun,
            DAGRunStep,
            DAGStepStatus,
        )

        dag_def = DAGDefinition(id="d1", name="test")
        dag_def.steps = [
            DAGDefinitionStep(
                id="ds1", name="start", task_name="t1", position=0, dag_definition_id="d1"
            ),
            DAGDefinitionStep(
                id="ds2", name="end", task_name="t2", position=1, dag_definition_id="d1"
            ),
        ]
        dag_def.edges = [
            DAGDefinitionEdge(
                id="e1", dag_definition_id="d1", from_step_id="ds1", to_step_id="ds2"
            ),
        ]

        dag_run = DAGRun(id="r1", dag_definition_id="d1")
        dag_run.steps = [
            DAGRunStep(
                id="rs1",
                dag_run_id="r1",
                step_name="start",
                task_name="t1",
                status=DAGStepStatus.FAILED.value,
            ),
            DAGRunStep(
                id="rs2",
                dag_run_id="r1",
                step_name="end",
                task_name="t2",
                status=DAGStepStatus.PENDING.value,
            ),
        ]

        to_skip = self.engine.get_steps_to_skip(dag_run, dag_def)

        assert len(to_skip) == 1
        assert to_skip[0].step_name == "end"


class TestDAGEngineRunCompletion:
    """Tests for run completion detection."""

    def setup_method(self):
        self.engine = DAGEngine()

    def test_is_run_finished_all_completed(self):
        """Run should be finished when all steps complete."""
        from src.infra.dag.models import DAGRun, DAGRunStep, DAGStepStatus

        dag_run = DAGRun(id="r1")
        dag_run.steps = [
            DAGRunStep(
                id="rs1",
                dag_run_id="r1",
                step_name="a",
                task_name="t1",
                status=DAGStepStatus.COMPLETED.value,
            ),
            DAGRunStep(
                id="rs2",
                dag_run_id="r1",
                step_name="b",
                task_name="t2",
                status=DAGStepStatus.COMPLETED.value,
            ),
        ]

        assert self.engine.is_run_finished(dag_run) is True

    def test_is_run_finished_with_pending(self):
        """Run should not be finished with pending steps."""
        from src.infra.dag.models import DAGRun, DAGRunStep, DAGStepStatus

        dag_run = DAGRun(id="r1")
        dag_run.steps = [
            DAGRunStep(
                id="rs1",
                dag_run_id="r1",
                step_name="a",
                task_name="t1",
                status=DAGStepStatus.COMPLETED.value,
            ),
            DAGRunStep(
                id="rs2",
                dag_run_id="r1",
                step_name="b",
                task_name="t2",
                status=DAGStepStatus.PENDING.value,
            ),
        ]

        assert self.engine.is_run_finished(dag_run) is False

    def test_compute_final_status_all_completed(self):
        """Final status should be COMPLETED if all steps completed."""
        from src.infra.dag.models import DAGRun, DAGRunStep, DAGStepStatus

        dag_run = DAGRun(id="r1")
        dag_run.steps = [
            DAGRunStep(
                id="rs1",
                dag_run_id="r1",
                step_name="a",
                task_name="t1",
                status=DAGStepStatus.COMPLETED.value,
            ),
            DAGRunStep(
                id="rs2",
                dag_run_id="r1",
                step_name="b",
                task_name="t2",
                status=DAGStepStatus.COMPLETED.value,
            ),
        ]

        assert self.engine.compute_final_status(dag_run) == DAGStepStatus.COMPLETED.value

    def test_compute_final_status_with_failure(self):
        """Final status should be FAILED if any step failed."""
        from src.infra.dag.models import DAGRun, DAGRunStep, DAGStepStatus

        dag_run = DAGRun(id="r1")
        dag_run.steps = [
            DAGRunStep(
                id="rs1",
                dag_run_id="r1",
                step_name="a",
                task_name="t1",
                status=DAGStepStatus.FAILED.value,
            ),
            DAGRunStep(
                id="rs2",
                dag_run_id="r1",
                step_name="b",
                task_name="t2",
                status=DAGStepStatus.SKIPPED.value,
            ),
        ]

        assert self.engine.compute_final_status(dag_run) == DAGStepStatus.FAILED.value

    def test_compute_final_status_partial(self):
        """Final status should be PARTIAL if some failed and some completed."""
        from src.infra.dag.models import DAGRun, DAGRunStep, DAGStepStatus

        dag_run = DAGRun(id="r1")
        dag_run.steps = [
            DAGRunStep(
                id="rs1",
                dag_run_id="r1",
                step_name="a",
                task_name="t1",
                status=DAGStepStatus.COMPLETED.value,
            ),
            DAGRunStep(
                id="rs2",
                dag_run_id="r1",
                step_name="b",
                task_name="t2",
                status=DAGStepStatus.FAILED.value,
            ),
        ]

        assert self.engine.compute_final_status(dag_run) == "partial"
