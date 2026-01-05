"""Business Use Cases - P2P, O2C, Supply Chain, Customer Journey.

Implements Phase 9 - Business Use Cases Layer.
Domain-specific process mining features for common business scenarios.
"""

import random
from typing import Any

import pm4py

from src.features.process_mining.models import Dataset, ProcessModel
from src.features.process_mining.services.conformance import conformance_service
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class BusinessUseCases:
    """Service for business-specific process mining use cases."""

    # =========================================================================
    # 9.1 Procure-to-Pay (P2P) Audit
    # =========================================================================

    def detect_mavericks(
        self,
        event_log: Dataset,
        reference_model: ProcessModel,
        threshold: float = 0.8,
    ) -> dict[str, Any]:
        """Detect maverick purchasing behavior (non-conformant cases).

        In P2P, mavericks are purchases that don't follow the approved process.

        Args:
            event_log: The purchase order event log
            reference_model: The approved P2P process model
            threshold: Fitness threshold below which a case is considered maverick

        Returns:
            Dictionary with maverick cases and statistics
        """
        logger.info(
            "maverick_detection_started",
            log_id=event_log.id,
            model_id=reference_model.id,
            threshold=threshold,
        )

        from src.features.process_mining.services.loader import event_log_loader

        # Load the PM4Py log
        event_log_loader.load_as_pm4py_log(event_log.id)

        # Get alignment diagnostics for each case
        alignment_diagnostics = conformance_service.get_alignment_diagnostics(
            event_log, reference_model, max_cases=10000
        )

        # Identify mavericks
        mavericks = []
        conforming_cases = []

        for case_data in alignment_diagnostics.get("case_alignments", []):
            case_id = case_data.get("case_id")
            fitness = case_data.get("fitness", 1.0)
            cost = case_data.get("cost", 0)

            if fitness < threshold:
                # This is a maverick
                mavericks.append(
                    {
                        "case_id": case_id,
                        "fitness": round(fitness, 3),
                        "deviation_cost": cost,
                        "severity": "high"
                        if fitness < 0.5
                        else "medium"
                        if fitness < threshold
                        else "low",
                    }
                )
            else:
                conforming_cases.append(case_id)

        # Calculate statistics
        total_cases = len(mavericks) + len(conforming_cases)
        maverick_rate = len(mavericks) / total_cases if total_cases > 0 else 0

        logger.info(
            "maverick_detection_completed",
            total_cases=total_cases,
            mavericks=len(mavericks),
            maverick_rate=round(maverick_rate, 3),
        )

        return {
            "total_cases": total_cases,
            "conforming_cases": len(conforming_cases),
            "maverick_cases": len(mavericks),
            "maverick_rate": round(maverick_rate, 3),
            "threshold": threshold,
            "mavericks": mavericks[:100],  # Limit to 100 for response size
        }

    def generate_p2p_audit_report(
        self,
        event_log: Dataset,
        reference_model: ProcessModel,
    ) -> dict[str, Any]:
        """Generate comprehensive P2P audit report.

        Args:
            event_log: The purchase order event log
            reference_model: The approved P2P process model

        Returns:
            Comprehensive audit report
        """
        logger.info(
            "p2p_audit_report_started",
            log_id=event_log.id,
            model_id=reference_model.id,
        )

        # Get conformance metrics
        quality_metrics = conformance_service.get_full_quality_metrics(event_log, reference_model)

        # Detect mavericks
        maverick_analysis = self.detect_mavericks(event_log, reference_model, threshold=0.8)

        # Get root cause analysis (if available)
        from src.features.process_mining.services.root_cause import root_cause_analyzer

        root_cause = root_cause_analyzer.get_comprehensive_root_cause_analysis(
            event_log, reference_model, attributes=["resource", "department", "vendor"]
        )

        logger.info("p2p_audit_report_completed")

        return {
            "report_type": "p2p_audit",
            "conformance_overview": {
                "fitness": quality_metrics.get("fitness"),
                "precision": quality_metrics.get("precision"),
                "is_compliant": quality_metrics.get("fitness", 0) >= 0.9,
            },
            "maverick_analysis": maverick_analysis,
            "root_causes": {
                "by_activity": root_cause.get("by_activity", {}).get("activities", [])[:10],
                "by_attributes": root_cause.get("by_attributes", {}),
            },
            "recommendations": self._generate_p2p_recommendations(
                quality_metrics, maverick_analysis
            ),
        }

    def _generate_p2p_recommendations(
        self, quality_metrics: dict, maverick_analysis: dict
    ) -> list[str]:
        """Generate recommendations based on P2P audit findings."""
        recommendations = []

        fitness = quality_metrics.get("fitness", 1.0)
        maverick_rate = maverick_analysis.get("maverick_rate", 0)

        if fitness < 0.7:
            recommendations.append(
                "CRITICAL: Process compliance is below 70%. Review and update P2P policy."
            )

        if maverick_rate > 0.2:
            recommendations.append(
                f"HIGH: {maverick_rate * 100:.1f}% of purchases are non-compliant. "
                "Implement automated purchase order validation."
            )

        if maverick_rate > 0.1:
            recommendations.append(
                "MEDIUM: Provide additional training to procurement team on approved process."
            )

        if not recommendations:
            recommendations.append("Process is compliant. Continue monitoring for process drift.")

        return recommendations

    # =========================================================================
    # 9.2 Order-to-Cash (O2C) Optimization
    # =========================================================================

    def split_log_by_attribute(
        self,
        event_log: Dataset,
        attribute: str,
        value: str,
    ) -> dict[str, Any]:
        """Split event log by attribute value for comparative analysis.

        Args:
            event_log: The event log to split
            attribute: The attribute to split on (e.g., "region", "product_category")
            value: The specific value to filter for

        Returns:
            Statistics about the filtered subset
        """
        logger.info(
            "log_split_started",
            log_id=event_log.id,
            attribute=attribute,
            value=value,
        )

        from src.features.process_mining.services.loader import event_log_loader

        # Load the PM4Py log
        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        # Filter log by attribute
        filtered_cases = []
        for trace in pm4py_log:
            # Check case attribute
            if trace.attributes.get(f"case:{attribute}") == value:
                filtered_cases.append(trace.attributes.get("concept:name"))

        logger.info(
            "log_split_completed",
            total_cases=len(pm4py_log),
            filtered_cases=len(filtered_cases),
        )

        return {
            "attribute": attribute,
            "value": value,
            "total_cases": len(pm4py_log),
            "filtered_cases": len(filtered_cases),
            "percentage": round(len(filtered_cases) / len(pm4py_log) * 100, 2) if pm4py_log else 0,
            "case_ids": filtered_cases[:100],  # Sample
        }

    def compare_process_variants(
        self,
        event_log1: Dataset,
        event_log2: Dataset,
        log1_name: str = "Group A",
        log2_name: str = "Group B",
    ) -> dict[str, Any]:
        """Compare process variants between two logs (e.g., regions, products).

        Args:
            event_log1: First event log
            event_log2: Second event log
            log1_name: Display name for first log
            log2_name: Display name for second log

        Returns:
            Comparison metrics
        """
        logger.info(
            "process_comparison_started",
            log1_id=event_log1.id,
            log2_id=event_log2.id,
        )

        from src.features.process_mining.services.loader import event_log_loader

        # Load both logs
        log1 = event_log_loader.load_as_pm4py_log(event_log1.id)
        log2 = event_log_loader.load_as_pm4py_log(event_log2.id)

        # Get variant statistics for each
        variants1 = pm4py.get_variants_as_tuples(log1)
        variants2 = pm4py.get_variants_as_tuples(log2)

        # Calculate performance for each

        durations1 = [
            (trace[-1]["time:timestamp"] - trace[0]["time:timestamp"]).total_seconds() / 3600
            for trace in log1
            if len(trace) > 0 and "time:timestamp" in trace[0] and "time:timestamp" in trace[-1]
        ]

        durations2 = [
            (trace[-1]["time:timestamp"] - trace[0]["time:timestamp"]).total_seconds() / 3600
            for trace in log2
            if len(trace) > 0 and "time:timestamp" in trace[0] and "time:timestamp" in trace[-1]
        ]

        avg_duration1 = sum(durations1) / len(durations1) if durations1 else 0
        avg_duration2 = sum(durations2) / len(durations2) if durations2 else 0

        logger.info("process_comparison_completed")

        return {
            "comparison": {
                log1_name: {
                    "total_cases": len(log1),
                    "unique_variants": len(variants1),
                    "avg_duration_hours": round(avg_duration1, 2),
                },
                log2_name: {
                    "total_cases": len(log2),
                    "unique_variants": len(variants2),
                    "avg_duration_hours": round(avg_duration2, 2),
                },
            },
            "differences": {
                "duration_difference_hours": round(avg_duration2 - avg_duration1, 2),
                "duration_difference_pct": round(
                    ((avg_duration2 - avg_duration1) / avg_duration1 * 100)
                    if avg_duration1 > 0
                    else 0,
                    2,
                ),
                "variant_complexity_diff": len(variants2) - len(variants1),
            },
        }

    # =========================================================================
    # 9.3 Supply Chain Simulation
    # =========================================================================

    def simulate_process_changes(
        self,
        event_log: Dataset,
        parameter_changes: dict[str, float],
        num_simulations: int = 1000,
    ) -> dict[str, Any]:
        """Simulate process changes using Monte Carlo simulation.

        Args:
            event_log: Historical event log
            parameter_changes: Dictionary of parameters to change
                             (e.g., {"activity_duration_reduction": 0.2} for 20% faster)
            num_simulations: Number of Monte Carlo iterations

        Returns:
            Simulation results with impact analysis
        """
        logger.info(
            "simulation_started",
            log_id=event_log.id,
            num_simulations=num_simulations,
            parameter_changes=parameter_changes,
        )

        from src.features.process_mining.services.loader import event_log_loader

        # Load the PM4Py log
        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        # Calculate baseline metrics
        baseline_durations = []
        for trace in pm4py_log:
            if len(trace) > 0 and "time:timestamp" in trace[0] and "time:timestamp" in trace[-1]:
                duration = (
                    trace[-1]["time:timestamp"] - trace[0]["time:timestamp"]
                ).total_seconds() / 3600
                baseline_durations.append(duration)

        baseline_avg = (
            sum(baseline_durations) / len(baseline_durations) if baseline_durations else 0
        )

        # Run Monte Carlo simulations
        duration_reduction = parameter_changes.get("activity_duration_reduction", 0)
        parameter_changes.get("capacity_increase", 0)

        simulated_durations = []
        for _sim in range(num_simulations):
            # Apply parameter changes with random variation
            variation = random.gauss(1.0, 0.1)  # 10% standard deviation
            reduction_factor = 1 - (duration_reduction * variation)

            # Simulate duration for a random baseline case
            if baseline_durations:
                baseline_duration = random.choice(baseline_durations)
                simulated_duration = baseline_duration * reduction_factor
                simulated_durations.append(simulated_duration)

        simulated_avg = (
            sum(simulated_durations) / len(simulated_durations) if simulated_durations else 0
        )
        simulated_p50 = (
            sorted(simulated_durations)[len(simulated_durations) // 2] if simulated_durations else 0
        )
        simulated_p95 = (
            sorted(simulated_durations)[int(len(simulated_durations) * 0.95)]
            if simulated_durations
            else 0
        )

        logger.info(
            "simulation_completed",
            baseline_avg=round(baseline_avg, 2),
            simulated_avg=round(simulated_avg, 2),
        )

        return {
            "simulation_type": "monte_carlo",
            "num_simulations": num_simulations,
            "parameter_changes": parameter_changes,
            "baseline_metrics": {
                "avg_duration_hours": round(baseline_avg, 2),
                "num_cases": len(baseline_durations),
            },
            "simulated_metrics": {
                "avg_duration_hours": round(simulated_avg, 2),
                "p50_duration_hours": round(simulated_p50, 2),
                "p95_duration_hours": round(simulated_p95, 2),
            },
            "impact_analysis": {
                "duration_reduction_hours": round(baseline_avg - simulated_avg, 2),
                "duration_reduction_pct": round(
                    ((baseline_avg - simulated_avg) / baseline_avg * 100)
                    if baseline_avg > 0
                    else 0,
                    2,
                ),
                "potential_cost_savings_pct": round(
                    ((baseline_avg - simulated_avg) / baseline_avg * 100) * 0.7
                    if baseline_avg > 0
                    else 0,
                    2,
                ),  # Assume 70% of time savings = cost savings
            },
        }

    # =========================================================================
    # 9.4 Customer Journey Mapping
    # =========================================================================

    def detect_journey_dropoffs(
        self,
        event_log: Dataset,
        expected_path: list[str] | None = None,
    ) -> dict[str, Any]:
        """Detect drop-offs in customer journey funnel.

        Args:
            event_log: Customer journey event log
            expected_path: Expected journey path (list of activity names)
                          If None, uses most common path

        Returns:
            Drop-off analysis by stage
        """
        logger.info("journey_dropoff_detection_started", log_id=event_log.id)

        from src.features.process_mining.services.loader import event_log_loader

        # Load the PM4Py log
        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        # If no expected path, find the most common variant
        if expected_path is None:
            variants = pm4py.get_variants_as_tuples(pm4py_log)
            if variants:
                # Get most common variant
                most_common = sorted(variants.items(), key=lambda x: len(x[1]), reverse=True)[0]
                expected_path = list(most_common[0])

        if not expected_path:
            return {"error": "Could not determine expected path"}

        # Analyze drop-offs at each stage
        stage_completion = {}
        for i, stage in enumerate(expected_path):
            completed = 0
            for trace in pm4py_log:
                # Check if trace completed this stage
                trace_activities = [event["concept:name"] for event in trace]
                if i < len(trace_activities) and stage in trace_activities:
                    completed += 1

            stage_completion[stage] = {
                "stage_index": i,
                "completed_cases": completed,
                "completion_rate": round(completed / len(pm4py_log), 3) if pm4py_log else 0,
            }

        # Calculate drop-offs between stages
        drop_offs = []
        for i in range(len(expected_path) - 1):
            current_stage = expected_path[i]
            next_stage = expected_path[i + 1]

            current_completed = stage_completion[current_stage]["completed_cases"]
            next_completed = stage_completion[next_stage]["completed_cases"]

            drop_off_count = current_completed - next_completed
            drop_off_rate = drop_off_count / current_completed if current_completed > 0 else 0

            drop_offs.append(
                {
                    "from_stage": current_stage,
                    "to_stage": next_stage,
                    "drop_off_count": drop_off_count,
                    "drop_off_rate": round(drop_off_rate, 3),
                }
            )

        logger.info("journey_dropoff_detection_completed", total_stages=len(expected_path))

        return {
            "expected_journey": expected_path,
            "total_cases": len(pm4py_log),
            "stage_completion": stage_completion,
            "drop_offs": drop_offs,
        }


# Singleton instance
business_use_cases = BusinessUseCases()
