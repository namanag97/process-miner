"""Workflow Service - Pipeline Orchestration.

Simple workflow execution for process mining pipelines.
"""

from typing import Any


class WorkflowService:
    """Service for workflow/pipeline orchestration."""

    def get_templates(self) -> list[dict[str, Any]]:
        """Get predefined workflow templates."""
        return [
            {
                "id": "discovery_basic",
                "name": "Basic Discovery",
                "description": "Upload log → Discover model → Get statistics",
                "steps": [
                    {"name": "discover", "type": "discover", "params": {"miner": "inductive"}},
                    {"name": "statistics", "type": "statistics", "params": {}},
                ],
            },
            {
                "id": "conformance_check",
                "name": "Conformance Check",
                "description": "Discover model → Check conformance → Get diagnostics",
                "steps": [
                    {"name": "discover", "type": "discover", "params": {"miner": "inductive"}},
                    {"name": "conformance", "type": "conformance", "params": {"method": "token_replay"}},
                ],
            },
            {
                "id": "full_analysis",
                "name": "Full Analysis",
                "description": "Complete analysis: discovery, conformance, variants",
                "steps": [
                    {"name": "discover", "type": "discover", "params": {"miner": "inductive"}},
                    {"name": "conformance", "type": "conformance", "params": {"method": "token_replay"}},
                    {"name": "variants", "type": "variants", "params": {"top_n": 20}},
                    {"name": "statistics", "type": "statistics", "params": {}},
                ],
            },
        ]

    async def execute_step(
        self,
        step_type: str,
        params: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute a single workflow step."""
        # This is a simplified execution - in production would call actual services
        if step_type == "discover":
            return {"status": "completed", "model_id": context.get("model_id")}
        elif step_type == "conformance":
            return {"status": "completed", "fitness": 0.95}
        elif step_type == "variants":
            return {"status": "completed", "variant_count": 10}
        elif step_type == "statistics":
            return {"status": "completed"}
        else:
            return {"status": "skipped", "reason": f"Unknown step type: {step_type}"}

    def validate_workflow(self, steps: list[dict]) -> tuple[bool, str]:
        """Validate workflow definition."""
        if not steps:
            return False, "Workflow must have at least one step"

        valid_types = {"discover", "conformance", "variants", "statistics", "export"}
        for i, step in enumerate(steps):
            if "type" not in step:
                return False, f"Step {i} missing 'type'"
            if step["type"] not in valid_types:
                return False, f"Step {i} has invalid type: {step['type']}"

        return True, "OK"


workflow_service = WorkflowService()
