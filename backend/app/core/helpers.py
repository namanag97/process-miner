"""
Helper functions for common operations.

Reduces duplication across routers and services.
"""

import json
from typing import Any

from ..models import (
    DFGResponse,
    DFGNode,
    DFGEdge,
    DFGSummary,
    NodePosition,
    ActivityNodeData,
    EdgeData,
    VariantsResponse,
    VariantItem,
    ProcessStats,
    Deviation,
)


def deserialize_dfg(dfg_data: dict[str, Any]) -> DFGResponse:
    """
    Deserialize stored DFG JSON to DFGResponse.
    
    Extracts duplicate code from analysis.py that was converting
    JSON dict back to Pydantic models.
    """
    return DFGResponse(
        nodes=[
            DFGNode(
                id=n["id"],
                type=n["type"],
                position=NodePosition(**n["position"]),
                data=ActivityNodeData(**n["data"]),
            )
            for n in dfg_data["nodes"]
        ],
        edges=[
            DFGEdge(
                id=e["id"],
                source=e["source"],
                target=e["target"],
                type=e["type"],
                data=EdgeData(**e["data"]),
            )
            for e in dfg_data["edges"]
        ],
        summary=DFGSummary(**dfg_data["summary"]),
    )


def deserialize_variants(variants_data: dict[str, Any]) -> VariantsResponse:
    """Deserialize stored variants JSON to VariantsResponse."""
    return VariantsResponse(
        total=variants_data["total"],
        variants=[VariantItem(**v) for v in variants_data["variants"]],
    )


def deserialize_stats(stats_data: dict[str, Any]) -> ProcessStats:
    """Deserialize stored stats JSON to ProcessStats."""
    return ProcessStats(
        total_cases=stats_data["total_cases"],
        total_events=stats_data["total_events"],
        total_activities=stats_data["total_activities"],
        total_variants=stats_data["total_variants"],
        avg_case_duration_ms=stats_data["avg_case_duration_ms"],
        median_case_duration_ms=stats_data["median_case_duration_ms"],
        start_activities=stats_data["start_activities"],
        end_activities=stats_data["end_activities"],
    )


def deserialize_deviations(deviations_data: list[dict[str, Any]]) -> list[Deviation]:
    """Deserialize stored deviations JSON to list of Deviation."""
    return [Deviation(**d) for d in deviations_data]


def parse_dataset_json(dataset) -> dict[str, Any]:
    """
    Parse all JSON fields from a Dataset model.
    
    Returns:
        Dict with parsed dfg, variants, stats, activity_stats, deviations
    """
    return {
        "dfg": json.loads(dataset.dfg_json) if dataset.dfg_json else None,
        "variants": json.loads(dataset.variants_json) if dataset.variants_json else None,
        "stats": json.loads(dataset.stats_json) if dataset.stats_json else None,
        "activity_stats": json.loads(dataset.activity_stats_json) if dataset.activity_stats_json else None,
        "deviations": json.loads(dataset.deviations_json) if dataset.deviations_json else [],
        "created_at": dataset.created_at,
    }
