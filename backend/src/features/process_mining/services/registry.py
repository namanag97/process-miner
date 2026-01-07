"""Analysis Registry - Central registry for all PM4Py analysis types.

This solves BUG-007 by making the analysis system generic and extensible.
Instead of hardcoding analysis logic in the API router, we define a registry
that maps analysis types to their configuration schemas and worker functions.

Adding a new analysis type is now as simple as adding one entry to this registry.
The UI will automatically discover it and generate the appropriate form.
"""

from typing import Any

from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)


class AnalysisDefinition:
    """Definition of a single analysis type."""

    def __init__(
        self,
        name: str,
        category: str,
        description: str,
        worker_func: str,
        result_type: str = "json",
        config_schema: dict[str, Any] | None = None,
    ):
        """Initialize analysis definition.

        Args:
            name: Human-readable name
            category: Category (Discovery, Organizational, Performance, etc.)
            description: Brief description of what this analysis does
            worker_func: Path to the worker function (e.g., "mining_service.get_dfg_fast")
            result_type: Type of result (graph, table, chart, json)
            config_schema: JSON schema defining configuration parameters
        """
        self.name = name
        self.category = category
        self.description = description
        self.worker_func = worker_func
        self.result_type = result_type
        self.config_schema = config_schema or {}


# =============================================================================
# Analysis Registry
# =============================================================================

ANALYSIS_REGISTRY: dict[str, AnalysisDefinition] = {
    # Discovery Algorithms
    "dfg_discovery": AnalysisDefinition(
        name="Directly-Follows Graph (DFG)",
        category="Discovery",
        description="Discover the directly-follows graph showing activity transitions and frequencies",
        worker_func="mining_service.get_dfg_fast",
        result_type="graph",
        config_schema={
            "min_frequency": {
                "type": "integer",
                "default": 1,
                "min": 1,
                "description": "Minimum edge frequency to include",
            },
        },
    ),
    "alpha_miner": AnalysisDefinition(
        name="Alpha Miner",
        category="Discovery",
        description="Classic Alpha algorithm for discovering Petri nets from event logs",
        worker_func="mining_service.discover_alpha",
        result_type="graph",
        config_schema={},
    ),
    "inductive_miner": AnalysisDefinition(
        name="Inductive Miner",
        category="Discovery",
        description="Inductive mining algorithm that guarantees sound process models",
        worker_func="mining_service.discover_inductive",
        result_type="graph",
        config_schema={
            "noise_threshold": {
                "type": "float",
                "default": 0.2,
                "min": 0.0,
                "max": 1.0,
                "description": "Noise filtering threshold (0=no filtering, 1=max filtering)",
            },
        },
    ),
    "heuristic_miner": AnalysisDefinition(
        name="Heuristics Miner",
        category="Discovery",
        description="Heuristics-based miner that handles noise and incomplete logs",
        worker_func="mining_service.discover_heuristic",
        result_type="graph",
        config_schema={
            "dependency_threshold": {
                "type": "float",
                "default": 0.5,
                "min": 0.0,
                "max": 1.0,
                "description": "Dependency threshold for edge inclusion",
            },
            "relative_to_best_threshold": {
                "type": "float",
                "default": 0.05,
                "min": 0.0,
                "max": 1.0,
                "description": "Relative-to-best threshold",
            },
        },
    ),
    # Alpha+ Miner - handles loops better than Alpha
    "alpha_plus_miner": AnalysisDefinition(
        name="Alpha+ Miner",
        category="Discovery",
        description="Improved Alpha algorithm with loop handling (length 1 and 2)",
        worker_func="mining_service._discover_alpha_plus",
        result_type="graph",
        config_schema={},
    ),
    # Inductive Miner Infrequent - aggressive noise filtering
    "inductive_infrequent": AnalysisDefinition(
        name="Inductive Miner (Infrequent)",
        category="Discovery",
        description="Inductive miner with aggressive noise filtering for highly variable logs",
        worker_func="mining_service._discover_inductive_infrequent",
        result_type="graph",
        config_schema={
            "noise_threshold": {
                "type": "float",
                "default": 0.2,
                "min": 0.0,
                "max": 1.0,
                "description": "Noise filtering threshold (higher = more filtering)",
            },
        },
    ),
    # Performance DFG - DFG with timing information
    "performance_dfg": AnalysisDefinition(
        name="Performance DFG",
        category="Discovery",
        description="Directly-Follows Graph with performance metrics (durations between activities)",
        worker_func="mining_service._discover_performance_dfg",
        result_type="graph",
        config_schema={},
    ),
    # ILP Miner - Integer Linear Programming
    "ilp_miner": AnalysisDefinition(
        name="ILP Miner",
        category="Discovery",
        description="Integer Linear Programming miner for optimal Petri net discovery",
        worker_func="mining_service.discover_ilp",
        result_type="graph",
        config_schema={
            "alpha": {
                "type": "float",
                "default": 1.0,
                "min": 0.0,
                "max": 1.0,
                "description": "Noise filtering parameter (0=max filtering, 1=no filtering)",
            },
        },
    ),
    # POWL - Partially Ordered Workflow Language
    "powl_miner": AnalysisDefinition(
        name="POWL Discovery",
        category="Discovery",
        description="Partially Ordered Workflow Language - discovers models with partial order semantics",
        worker_func="mining_service.discover_powl",
        result_type="graph",
        config_schema={},
    ),
    # BPMN Discovery - Direct BPMN 2.0 output
    "bpmn_discovery": AnalysisDefinition(
        name="BPMN Discovery",
        category="Discovery",
        description="Discover BPMN 2.0 compliant models directly (using Inductive Miner)",
        worker_func="mining_service.discover_bpmn",
        result_type="bpmn",
        config_schema={},
    ),
    # Declare Miner - Declarative constraints
    "declare_miner": AnalysisDefinition(
        name="Declare Miner",
        category="Discovery",
        description="Discover declarative constraints (LTL) instead of procedural control-flow",
        worker_func="mining_service.discover_declare",
        result_type="declare",
        config_schema={},
    ),
    # Log Skeleton - Declarative constraints from activity patterns
    "log_skeleton": AnalysisDefinition(
        name="Log Skeleton",
        category="Discovery",
        description="Discover declarative constraints based on activity occurrences and ordering",
        worker_func="mining_service.discover_log_skeleton",
        result_type="json",
        config_schema={
            "noise_threshold": {
                "type": "float",
                "default": 0.0,
                "min": 0.0,
                "max": 1.0,
                "description": "Fraction of traces that can violate constraints",
            },
        },
    ),
    # Temporal Profile - Time-based constraints
    "temporal_profile": AnalysisDefinition(
        name="Temporal Profile",
        category="Discovery",
        description="Discover temporal constraints (avg/stdev time between activities)",
        worker_func="mining_service.discover_temporal_profile",
        result_type="json",
        config_schema={},
    ),
    # Prefix Tree - Trie of all trace prefixes
    "prefix_tree": AnalysisDefinition(
        name="Prefix Tree",
        category="Discovery",
        description="Build prefix automaton for all unique trace prefixes (useful for prediction)",
        worker_func="mining_service.discover_prefix_tree",
        result_type="graph",
        config_schema={},
    ),
    # Transition System - State-based model
    "transition_system": AnalysisDefinition(
        name="Transition System",
        category="Discovery",
        description="Discover state-based model where states are defined by activity sequences",
        worker_func="mining_service.discover_transition_system",
        result_type="graph",
        config_schema={
            "direction": {
                "type": "string",
                "default": "forward",
                "enum": ["forward", "backward", "both"],
                "description": "Direction for state construction",
            },
            "window": {
                "type": "integer",
                "default": 2,
                "min": 1,
                "max": 10,
                "description": "Window size for state definition",
            },
        },
    ),
    # Variants Analysis
    "variant_analysis": AnalysisDefinition(
        name="Process Variants",
        category="Variants",
        description="Analyze unique process execution paths (variants) and their frequencies",
        worker_func="mining_service.get_variants_fast",
        result_type="table",
        config_schema={
            "top_n": {
                "type": "integer",
                "default": 20,
                "min": 1,
                "max": 100,
                "description": "Number of top variants to return",
            },
            "top_k_percent": {
                "type": "float",
                "default": None,
                "min": 0.0,
                "max": 100.0,
                "description": "Return variants covering top K% of cases (optional)",
            },
        },
    ),
    # Statistics
    "basic_statistics": AnalysisDefinition(
        name="Basic Statistics",
        category="Statistics",
        description="Compute basic process statistics (events, cases, activities, durations)",
        worker_func="mining_service.get_statistics_fast",
        result_type="json",
        config_schema={},
    ),
    # Organizational Mining
    "social_network_handover": AnalysisDefinition(
        name="Social Network: Handover of Work",
        category="Organizational",
        description="Discover handover-of-work social network between resources",
        worker_func="mining_service.get_social_network_handover",
        result_type="graph",
        config_schema={
            "beta": {
                "type": "float",
                "default": 0.5,
                "min": 0.0,
                "max": 1.0,
                "description": "Beta parameter for causality (0=strict, 1=lenient)",
            },
        },
    ),
    "social_network_working_together": AnalysisDefinition(
        name="Social Network: Working Together",
        category="Organizational",
        description="Discover working-together social network between resources",
        worker_func="mining_service.get_social_network_working_together",
        result_type="graph",
        config_schema={},
    ),
    "resource_utilization": AnalysisDefinition(
        name="Resource Utilization",
        category="Organizational",
        description="Analyze resource workload and activity distribution",
        worker_func="mining_service.get_resource_utilization",
        result_type="table",
        config_schema={},
    ),
    # Performance Analysis
    "bottleneck_analysis": AnalysisDefinition(
        name="Bottleneck Analysis",
        category="Performance",
        description="Identify process bottlenecks based on activity durations",
        worker_func="mining_service.get_bottlenecks",
        result_type="table",
        config_schema={
            "top_n": {
                "type": "integer",
                "default": 10,
                "min": 1,
                "max": 50,
                "description": "Number of top bottlenecks to return",
            },
        },
    ),
    # Conformance Checking
    "token_replay": AnalysisDefinition(
        name="Token-Based Replay",
        category="Conformance",
        description="Check conformance using token-based replay on Petri net",
        worker_func="mining_service.check_conformance_token_replay",
        result_type="json",
        config_schema={
            "model_id": {
                "type": "string",
                "description": "ID of the process model to check against (required)",
            },
        },
    ),
    "alignments": AnalysisDefinition(
        name="Alignments",
        category="Conformance",
        description="Compute optimal alignments between log and model",
        worker_func="mining_service.check_conformance_alignments",
        result_type="json",
        config_schema={
            "model_id": {
                "type": "string",
                "description": "ID of the process model to check against (required)",
            },
        },
    ),
}


class AnalysisRegistry:
    """Registry manager for analysis types."""

    def __init__(self):
        self.registry = ANALYSIS_REGISTRY

    def get(self, analysis_type: str) -> AnalysisDefinition | None:
        """Get analysis definition by type.

        Args:
            analysis_type: Analysis type key

        Returns:
            AnalysisDefinition or None if not found
        """
        return self.registry.get(analysis_type)

    def list_all(self) -> dict[str, AnalysisDefinition]:
        """Get all registered analysis types.

        Returns:
            dict mapping analysis_type to AnalysisDefinition
        """
        return self.registry.copy()

    def list_by_category(self, category: str) -> dict[str, AnalysisDefinition]:
        """Get all analysis types in a category.

        Args:
            category: Category name (Discovery, Organizational, etc.)

        Returns:
            dict of analysis types in this category
        """
        return {
            key: definition
            for key, definition in self.registry.items()
            if definition.category == category
        }

    def get_categories(self) -> list[str]:
        """Get list of all categories.

        Returns:
            Sorted list of unique category names
        """
        categories = {definition.category for definition in self.registry.values()}
        return sorted(categories)

    def get_metadata(self) -> dict[str, Any]:
        """Get metadata for all analysis types (for frontend consumption).

        Returns:
            dict with categories, analysis types, and their schemas
        """
        metadata = {
            "categories": self.get_categories(),
            "analysis_types": {},
        }

        for analysis_type, definition in self.registry.items():
            metadata["analysis_types"][analysis_type] = {
                "name": definition.name,
                "category": definition.category,
                "description": definition.description,
                "result_type": definition.result_type,
                "config_schema": definition.config_schema,
            }

        return metadata


# Singleton instance
analysis_registry = AnalysisRegistry()
