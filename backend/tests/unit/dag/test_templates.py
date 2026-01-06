"""Unit tests for DAG Templates."""

import pytest

from src.platform.dag.engine import dag_engine
from src.platform.dag.templates import (
    TEMPLATES,
    get_template,
    get_template_edges,
    get_template_steps,
    list_templates,
)


class TestTemplateConfiguration:
    """Tests for template structure and helpers."""

    def test_list_templates(self):
        """Test listing all available templates."""
        templates = list_templates()

        assert "data_ingestion" in templates
        assert "full_analysis" in templates
        assert "discovery_only" in templates
        assert "prediction_training" in templates
        assert "complete_pipeline" in templates

    def test_get_template(self):
        """Test getting a template by name."""
        template = get_template("data_ingestion")

        assert template is not None
        assert "steps" in template
        assert "edges" in template
        assert template.get("name") is not None

    def test_get_nonexistent_template(self):
        """Test getting a template that doesn't exist."""
        template = get_template("nonexistent")
        assert template is None

    def test_get_template_steps(self):
        """Test getting just the steps from a template."""
        steps = get_template_steps("data_ingestion")

        assert steps is not None
        assert len(steps) == 3  # validate, detect, ingest

    def test_get_template_edges(self):
        """Test getting just the edges from a template."""
        edges = get_template_edges("data_ingestion")

        assert edges is not None
        assert len(edges) == 2  # validate->detect, detect->ingest


class TestTemplateValidation:
    """Test that all templates pass DAG validation."""

    @pytest.mark.parametrize("template_name", list_templates())
    def test_template_is_valid_dag(self, template_name: str):
        """Test that each template is a valid DAG structure."""
        template = get_template(template_name)
        assert template is not None

        steps = template["steps"]
        edges = template["edges"]

        is_valid, error = dag_engine.validate_dag(steps, edges)
        assert is_valid, f"Template '{template_name}' failed validation: {error}"

    @pytest.mark.parametrize("template_name", list_templates())
    def test_template_has_required_fields(self, template_name: str):
        """Test that each template has required top-level fields."""
        template = get_template(template_name)

        assert "name" in template, f"{template_name} missing 'name'"
        assert "description" in template, f"{template_name} missing 'description'"
        assert "steps" in template, f"{template_name} missing 'steps'"
        assert "edges" in template, f"{template_name} missing 'edges'"

    @pytest.mark.parametrize("template_name", list_templates())
    def test_steps_have_required_fields(self, template_name: str):
        """Test that each step has required fields."""
        template = get_template(template_name)

        for step in template["steps"]:
            assert "name" in step, f"Step missing 'name' in {template_name}"
            assert "task_name" in step, f"Step missing 'task_name' in {template_name}"


class TestDataIngestionTemplate:
    """Tests specific to the data_ingestion template."""

    def test_step_sequence(self):
        """Test data ingestion has correct step sequence."""
        template = get_template("data_ingestion")
        steps = template["steps"]

        step_names = [s["name"] for s in steps]
        assert step_names == ["validate", "detect", "ingest"]

    def test_linear_dependency_chain(self):
        """Test data ingestion has linear dependencies."""
        template = get_template("data_ingestion")
        edges = template["edges"]

        # Should be: validate -> detect -> ingest
        assert {"from_step": "validate", "to_step": "detect"} in edges
        assert {"from_step": "detect", "to_step": "ingest"} in edges


class TestFullAnalysisTemplate:
    """Tests specific to the full_analysis template."""

    def test_contains_discovery_and_conformance(self):
        """Test full analysis includes discovery and conformance steps."""
        template = get_template("full_analysis")
        step_names = [s["name"] for s in template["steps"]]

        assert "discover" in step_names
        assert "conformance" in step_names
        assert "statistics" in step_names

    def test_conformance_depends_on_discover(self):
        """Test conformance step depends on discover."""
        template = get_template("full_analysis")
        edges = template["edges"]

        assert {"from_step": "discover", "to_step": "conformance"} in edges


class TestCompletePipelineTemplate:
    """Tests specific to the complete_pipeline template."""

    def test_full_workflow_coverage(self):
        """Test complete pipeline covers all major steps."""
        template = get_template("complete_pipeline")
        step_names = {s["name"] for s in template["steps"]}

        expected = {"validate", "detect", "ingest", "discover", "conformance", "statistics"}
        assert step_names == expected

    def test_parallel_execution_possible(self):
        """Test that some steps can run in parallel."""
        template = get_template("complete_pipeline")
        edges = template["edges"]

        # Both discover and statistics depend on ingest, so they can run in parallel
        assert {"from_step": "ingest", "to_step": "discover"} in edges
        assert {"from_step": "ingest", "to_step": "statistics"} in edges
