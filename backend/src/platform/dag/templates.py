"""Predefined DAG Templates.

Common workflow templates that can be registered with the DAGService.
Each template defines a reusable workflow pattern.
"""

from typing import Any

# =============================================================================
# Template Definitions
# =============================================================================

TEMPLATES: dict[str, dict[str, Any]] = {
    # -------------------------------------------------------------------------
    # Data Ingestion Pipeline
    # -------------------------------------------------------------------------
    "data_ingestion": {
        "name": "Data Ingestion Pipeline",
        "description": "Validate, detect columns, and ingest a dataset",
        "steps": [
            {
                "name": "validate",
                "task_name": "validate_file",
                "default_params": {},
            },
            {
                "name": "detect",
                "task_name": "detect_columns",
                "default_params": {},
            },
            {
                "name": "ingest",
                "task_name": "ingest_dataset",
                "default_params": {},
            },
        ],
        "edges": [
            {"from_step": "validate", "to_step": "detect"},
            {"from_step": "detect", "to_step": "ingest"},
        ],
    },
    # -------------------------------------------------------------------------
    # Full Analysis Pipeline
    # -------------------------------------------------------------------------
    "full_analysis": {
        "name": "Full Analysis Pipeline",
        "description": "Discover process model and perform conformance checking",
        "steps": [
            {
                "name": "discover",
                "task_name": "discover_model",
                "default_params": {"miner_type": "inductive"},
            },
            {
                "name": "conformance",
                "task_name": "check_conformance",
                "default_params": {"method": "token_replay"},
            },
            {
                "name": "statistics",
                "task_name": "compute_statistics",
                "default_params": {"analysis_type": "statistics"},
            },
        ],
        "edges": [
            {"from_step": "discover", "to_step": "conformance"},
            # Statistics can run in parallel with discover since it only needs the dataset
        ],
    },
    # -------------------------------------------------------------------------
    # Discovery Only Pipeline
    # -------------------------------------------------------------------------
    "discovery_only": {
        "name": "Discovery Pipeline",
        "description": "Discover process model and compute statistics",
        "steps": [
            {
                "name": "discover",
                "task_name": "discover_model",
                "default_params": {"miner_type": "inductive"},
            },
            {
                "name": "statistics",
                "task_name": "compute_statistics",
                "default_params": {"analysis_type": "discovery"},
            },
        ],
        "edges": [
            # Both can run in parallel - no edges needed
        ],
    },
    # -------------------------------------------------------------------------
    # Prediction Training Pipeline
    # -------------------------------------------------------------------------
    "prediction_training": {
        "name": "Prediction Training Pipeline",
        "description": "Train ML prediction models after ingestion",
        "steps": [
            {
                "name": "train_activity",
                "task_name": "train_predictor",
                "default_params": {
                    "target_type": "next_activity",
                    "algorithm": "random_forest",
                },
            },
            {
                "name": "train_time",
                "task_name": "train_predictor",
                "default_params": {
                    "target_type": "remaining_time",
                    "algorithm": "random_forest",
                },
            },
        ],
        "edges": [
            # Both can run in parallel
        ],
    },
    # -------------------------------------------------------------------------
    # Complete Pipeline (End-to-End)
    # -------------------------------------------------------------------------
    "complete_pipeline": {
        "name": "Complete Process Mining Pipeline",
        "description": "Full workflow from ingestion through analysis",
        "steps": [
            {"name": "validate", "task_name": "validate_file", "default_params": {}},
            {"name": "detect", "task_name": "detect_columns", "default_params": {}},
            {"name": "ingest", "task_name": "ingest_dataset", "default_params": {}},
            {"name": "discover", "task_name": "discover_model", "default_params": {}},
            {"name": "conformance", "task_name": "check_conformance", "default_params": {}},
            {"name": "statistics", "task_name": "compute_statistics", "default_params": {}},
        ],
        "edges": [
            {"from_step": "validate", "to_step": "detect"},
            {"from_step": "detect", "to_step": "ingest"},
            {"from_step": "ingest", "to_step": "discover"},
            {"from_step": "ingest", "to_step": "statistics"},  # Parallel
            {"from_step": "discover", "to_step": "conformance"},
        ],
    },
}


def get_template(name: str) -> dict[str, Any] | None:
    """Get a template by name."""
    return TEMPLATES.get(name)


def list_templates() -> list[str]:
    """List all available template names."""
    return list(TEMPLATES.keys())


def get_template_steps(name: str) -> list[dict] | None:
    """Get steps for a template."""
    template = TEMPLATES.get(name)
    return template.get("steps") if template else None


def get_template_edges(name: str) -> list[dict] | None:
    """Get edges for a template."""
    template = TEMPLATES.get(name)
    return template.get("edges") if template else None
