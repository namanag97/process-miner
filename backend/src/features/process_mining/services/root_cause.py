"""Root Cause Analysis Service - Deviation Detection and Aggregation.

Implements Phase 11.3 - Root Cause Analysis.
Analyzes conformance deviations and identifies patterns.
"""

from collections import Counter, defaultdict
from typing import Any

from src.features.process_mining.models import Dataset, ProcessModel
from src.features.process_mining.services.conformance import conformance_service
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class RootCauseAnalyzer:
    """Service for analyzing root causes of conformance deviations."""

    def aggregate_deviations_by_activity(
        self,
        event_log: Dataset,
        model: ProcessModel,
    ) -> dict[str, Any]:
        """Aggregate deviations by activity.

        Identifies which activities cause the most conformance issues.

        Args:
            event_log: The event log
            model: The process model

        Returns:
            Dictionary with deviation counts per activity
        """
        logger.info("deviation_aggregation_by_activity_started", dataset_id=event_log.id)

        # Get diagnostics
        diagnostics = conformance_service.get_diagnostics(event_log, model)

        # Aggregate deviations by activity
        activity_deviations: dict[str, dict[str, int]] = defaultdict(
            lambda: {"missing_tokens": 0, "remaining_tokens": 0}
        )  # type: ignore[arg-type]

        for deviation in diagnostics.get("deviations", []):
            deviation_type = deviation.get("type")

            # Extract activity from tokens (tokens are strings like "Place_1")
            # In real PM4Py, these would have activity labels
            # For now, we count by deviation type
            if deviation_type == "missing_tokens":
                activity_deviations["missing"]["missing_tokens"] += 1
            elif deviation_type == "remaining_tokens":
                activity_deviations["remaining"]["remaining_tokens"] += 1

        # Convert to list format
        aggregated = []
        for activity, counts in activity_deviations.items():
            total = counts["missing_tokens"] + counts["remaining_tokens"]
            aggregated.append(
                {
                    "activity": activity,
                    "missing_token_count": counts["missing_tokens"],
                    "remaining_token_count": counts["remaining_tokens"],
                    "total_deviations": total,
                }
            )

        # Sort by total deviations descending
        aggregated.sort(key=lambda x: x["total_deviations"], reverse=True)  # type: ignore[arg-type, return-value]

        logger.info(
            "deviation_aggregation_completed",
            unique_activities_with_deviations=len(aggregated),
        )

        return {
            "aggregation_type": "by_activity",
            "total_activities_with_deviations": len(aggregated),
            "activities": aggregated[:50],  # Top 50
        }

    def aggregate_deviations_by_position(
        self,
        event_log: Dataset,
        model: ProcessModel,
    ) -> dict[str, Any]:
        """Aggregate deviations by trace position.

        Identifies at which point in the process deviations occur.

        Args:
            event_log: The event log
            model: The process model

        Returns:
            Dictionary with deviation counts per position
        """
        logger.info("deviation_aggregation_by_position_started", dataset_id=event_log.id)

        # Get alignment diagnostics for position-level analysis
        alignment_diagnostics = conformance_service.get_alignment_diagnostics(
            event_log, model, max_cases=1000
        )

        # Aggregate deviations by position
        position_deviations: dict[int, dict[str, int]] = defaultdict(
            lambda: {"log_only": 0, "model_only": 0}
        )  # type: ignore[arg-type]

        for case_alignment in alignment_diagnostics.get("case_alignments", []):
            for position, move in enumerate(case_alignment.get("alignment", [])):
                move_type = move.get("move_type")

                if move_type == "log_only":
                    position_deviations[position]["log_only"] += 1
                elif move_type == "model_only":
                    position_deviations[position]["model_only"] += 1

        # Convert to list format
        aggregated = []
        for position, counts in sorted(position_deviations.items()):
            total = counts["log_only"] + counts["model_only"]
            aggregated.append(
                {
                    "position": position,
                    "log_only_moves": counts["log_only"],
                    "model_only_moves": counts["model_only"],
                    "total_deviations": total,
                }
            )

        logger.info(
            "deviation_aggregation_by_position_completed",
            positions_with_deviations=len(aggregated),
        )

        return {
            "aggregation_type": "by_position",
            "total_positions_with_deviations": len(aggregated),
            "positions": aggregated[:100],  # Top 100 positions
        }

    def analyze_attribute_correlation(
        self,
        event_log: Dataset,
        model: ProcessModel,
        attribute: str = "resource",
    ) -> dict[str, Any]:
        """Analyze correlation between case attributes and conformance deviations.

        Identifies which attribute values (e.g., resources, departments) are
        associated with more deviations.

        Args:
            event_log: The event log
            model: The process model
            attribute: The case attribute to analyze (default: "resource")

        Returns:
            Dictionary with deviation counts per attribute value
        """
        logger.info(
            "attribute_correlation_started",
            dataset_id=event_log.id,
            attribute=attribute,
        )

        from src.features.process_mining.services.loader import event_log_loader

        # Load the PM4Py log
        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        # Get alignment diagnostics
        alignment_diagnostics = conformance_service.get_alignment_diagnostics(
            event_log, model, max_cases=1000
        )

        # Aggregate deviations by attribute value
        attribute_stats: dict[str, dict[str, int]] = defaultdict(
            lambda: {"total_cases": 0, "deviating_cases": 0, "total_deviations": 0}
        )  # type: ignore[arg-type]

        for _i, (trace, case_alignment) in enumerate(
            zip(pm4py_log, alignment_diagnostics.get("case_alignments", []), strict=False)
        ):
            # Extract attribute value from trace
            # Try case attributes first, then event attributes
            attr_value = trace.attributes.get(f"case:{attribute}")

            # If not in case attributes, try to get from events
            if attr_value is None and trace:
                # Get most common resource/attribute from events
                event_values = []
                for event in trace:
                    event_attr = event.get(attribute) or event.get(f"org:{attribute}")
                    if event_attr:
                        event_values.append(event_attr)

                if event_values:
                    # Use most common value
                    attr_value = Counter(event_values).most_common(1)[0][0]

            # Default if no attribute found
            if attr_value is None:
                attr_value = f"unknown_{attribute}"

            # Count deviations in this case
            deviation_count = sum(
                1
                for move in case_alignment.get("alignment", [])
                if move.get("move_type") in ["log_only", "model_only"]
            )

            # Update stats
            attribute_stats[str(attr_value)]["total_cases"] += 1
            if deviation_count > 0:
                attribute_stats[str(attr_value)]["deviating_cases"] += 1
                attribute_stats[str(attr_value)]["total_deviations"] += deviation_count

        # Convert to list and calculate deviation rate
        aggregated = []
        for attr_value, stats in attribute_stats.items():
            deviation_rate = (
                stats["deviating_cases"] / stats["total_cases"] if stats["total_cases"] > 0 else 0
            )
            avg_deviations_per_case = (
                stats["total_deviations"] / stats["total_cases"] if stats["total_cases"] > 0 else 0
            )

            aggregated.append(
                {
                    "attribute_value": attr_value,
                    "total_cases": stats["total_cases"],
                    "deviating_cases": stats["deviating_cases"],
                    "total_deviations": stats["total_deviations"],
                    "deviation_rate": round(deviation_rate, 3),
                    "avg_deviations_per_case": round(avg_deviations_per_case, 2),
                }
            )

        # Sort by deviation rate descending
        aggregated.sort(key=lambda x: x["deviation_rate"], reverse=True)  # type: ignore[arg-type, return-value]

        logger.info(
            "attribute_correlation_completed",
            attribute=attribute,
            unique_values=len(aggregated),
        )

        return {
            "attribute": attribute,
            "total_unique_values": len(aggregated),
            "attribute_correlations": aggregated[:50],  # Top 50
        }

    def get_comprehensive_root_cause_analysis(
        self,
        event_log: Dataset,
        model: ProcessModel,
        attributes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get comprehensive root cause analysis.

        Combines all analysis types into one report.

        Args:
            event_log: The event log
            model: The process model
            attributes: List of attributes to analyze (default: ["resource"])

        Returns:
            Comprehensive root cause analysis report
        """
        if attributes is None:
            attributes = ["resource"]

        logger.info(
            "comprehensive_root_cause_analysis_started",
            dataset_id=event_log.id,
            model_id=model.id,
        )

        # Get basic diagnostics
        diagnostics = conformance_service.get_diagnostics(event_log, model)

        # Aggregate by activity
        by_activity = self.aggregate_deviations_by_activity(event_log, model)

        # Aggregate by position
        by_position = self.aggregate_deviations_by_position(event_log, model)

        # Attribute correlation for each specified attribute
        attribute_analyses = {}
        for attribute in attributes:
            try:
                attribute_analyses[attribute] = self.analyze_attribute_correlation(
                    event_log, model, attribute
                )
            except Exception as e:
                logger.warning(
                    "attribute_correlation_failed",
                    attribute=attribute,
                    error=str(e),
                )
                attribute_analyses[attribute] = {"error": str(e)}

        logger.info("comprehensive_root_cause_analysis_completed")

        return {
            "summary": {
                "total_traces": diagnostics["total_traces"],
                "fitting_traces": diagnostics["fitting_traces"],
                "non_fitting_traces": diagnostics["non_fitting_traces"],
                "fitness_ratio": diagnostics["fitness_ratio"],
            },
            "by_activity": by_activity,
            "by_position": by_position,
            "by_attributes": attribute_analyses,
        }


# Singleton instance
root_cause_analyzer = RootCauseAnalyzer()
