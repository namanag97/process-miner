"""Conformance Checking Service - PM4Py Integration.

Ported from: src/application/core/conformance_service.py
Simplified: No aggregates, no domain entities - direct PM4Py usage.
"""

from typing import Any

import pm4py
from pm4py.objects.petri_net.obj import Marking, PetriNet

from src.features.process_mining.discovery.service import mining_service
from src.features.process_mining.enums import ConformanceMethod, ModelFormat
from src.features.process_mining.models import Dataset, ProcessModel
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class ConformanceService:
    """
    Conformance Checking Service using PM4Py.
    Supports token-based replay and alignment-based conformance.
    """

    def check_conformance(
        self,
        event_log: Dataset,
        model: ProcessModel,
        method: ConformanceMethod = ConformanceMethod.TOKEN_REPLAY,
    ) -> dict[str, Any]:
        """
        Check conformance between an event log and a process model.

        Returns:
            Dictionary with fitness, precision, method, and diagnostics
        """
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        net, im, fm = self._get_petri_net(model)

        if method == ConformanceMethod.TOKEN_REPLAY:
            result = self._token_replay(pm4py_log, net, im, fm)
        else:
            result = self._alignment_based(pm4py_log, net, im, fm)

        return result

    def calculate_fitness(
        self,
        event_log: Dataset,
        model: ProcessModel,
    ) -> float:
        """Calculate fitness score for log-model pair."""
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        net, im, fm = self._get_petri_net(model)

        fitness = pm4py.fitness_token_based_replay(pm4py_log, net, im, fm)
        return fitness.get("average_trace_fitness", 0.0)

    def calculate_precision(
        self,
        event_log: Dataset,
        model: ProcessModel,
    ) -> float:
        """Calculate precision score for log-model pair."""
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        net, im, fm = self._get_petri_net(model)

        return pm4py.precision_token_based_replay(pm4py_log, net, im, fm)

    def calculate_generalization(
        self,
        event_log: Dataset,
        model: ProcessModel,
    ) -> float:
        """Calculate generalization score for log-model pair.

        Generalization measures how well the model generalizes beyond
        the observed behavior in the log.
        """
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        net, im, fm = self._get_petri_net(model)

        try:
            # PM4py's generalization function
            return pm4py.generalization_tbr(pm4py_log, net, im, fm)
        except Exception as e:
            logger.warning(
                "generalization_calculation_failed",
                error=str(e),
                msg="Returning None for generalization",
            )
            return None

    def calculate_simplicity(
        self,
        model: ProcessModel,
    ) -> float:
        """Calculate simplicity score for a process model.

        Simplicity measures how simple/understandable the model is,
        typically based on the number of elements.
        """
        net, im, fm = self._get_petri_net(model)

        try:
            # PM4py's simplicity function for Petri nets
            return pm4py.simplicity_petri_net(net, im, fm)
        except Exception as e:
            logger.warning(
                "simplicity_calculation_failed",
                error=str(e),
                msg="Returning None for simplicity",
            )
            return None

    def calculate_f_score(
        self,
        fitness: float,
        precision: float,
    ) -> float:
        """Calculate F-score (harmonic mean of fitness and precision).

        F-score balances fitness and precision into a single quality metric.
        """
        if fitness is None or precision is None:
            return None
        if fitness + precision == 0:
            return 0.0
        return 2 * (fitness * precision) / (fitness + precision)

    def get_full_quality_metrics(
        self,
        event_log: Dataset,
        model: ProcessModel,
    ) -> dict[str, Any]:
        """Get all 4 quality dimensions: fitness, precision, generalization, simplicity.

        Plus computed f_score.
        """
        fitness = self.calculate_fitness(event_log, model)
        precision = self.calculate_precision(event_log, model)
        generalization = self.calculate_generalization(event_log, model)
        simplicity = self.calculate_simplicity(model)
        f_score = self.calculate_f_score(fitness, precision)

        return {
            "fitness": fitness,
            "precision": precision,
            "generalization": generalization,
            "simplicity": simplicity,
            "f_score": f_score,
        }

    def get_diagnostics(
        self,
        event_log: Dataset,
        model: ProcessModel,
    ) -> dict[str, Any]:
        """Get detailed conformance diagnostics."""
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        net, im, fm = self._get_petri_net(model)

        # Token replay diagnostics
        replay_result = pm4py.conformance_diagnostics_token_based_replay(pm4py_log, net, im, fm)

        # Calculate aggregate metrics
        fitting_traces = sum(1 for r in replay_result if r.get("trace_is_fit", False))
        total_traces = len(replay_result)

        # Collect deviations
        deviations = []
        for i, result in enumerate(replay_result):
            if not result.get("trace_is_fit", True):
                missing = result.get("missing_tokens", [])
                remaining = result.get("remaining_tokens", [])

                if missing:
                    deviations.append(
                        {
                            "trace_index": i,
                            "type": "missing_tokens",
                            "tokens": [str(t) for t in missing[:5]],
                        }
                    )
                if remaining:
                    deviations.append(
                        {
                            "trace_index": i,
                            "type": "remaining_tokens",
                            "tokens": [str(t) for t in remaining[:5]],
                        }
                    )

        return {
            "total_traces": total_traces,
            "fitting_traces": fitting_traces,
            "non_fitting_traces": total_traces - fitting_traces,
            "fitness_ratio": fitting_traces / total_traces if total_traces > 0 else 0,
            "deviations": deviations[:50],  # Limit deviations
        }

    def detect_deviations(
        self,
        event_log: Dataset,
        model: ProcessModel,
        threshold: float = 0.8,
    ) -> list[dict[str, Any]]:
        """Detect specific deviations from the model."""
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        net, im, fm = self._get_petri_net(model)

        diagnostics = pm4py.conformance_diagnostics_token_based_replay(pm4py_log, net, im, fm)

        deviations = []
        for i, (trace, diag) in enumerate(zip(pm4py_log, diagnostics, strict=False)):
            if not diag.get("trace_is_fit", True):
                case_id = trace.attributes.get("concept:name", f"trace_{i}")

                if diag.get("missing_tokens"):
                    deviations.append(
                        {
                            "case_id": case_id,
                            "activity": "",
                            "deviation_type": "missing_token",
                            "details": f"Missing tokens: {len(diag['missing_tokens'])}",
                        }
                    )

                if diag.get("remaining_tokens"):
                    deviations.append(
                        {
                            "case_id": case_id,
                            "activity": "",
                            "deviation_type": "remaining_token",
                            "details": f"Remaining tokens: {len(diag['remaining_tokens'])}",
                        }
                    )

        return deviations

    def get_alignment_diagnostics(
        self,
        event_log: Dataset,
        model: ProcessModel,
        max_cases: int = 100,
    ) -> dict[str, Any]:
        """Get detailed alignment diagnostics using PM4Py alignments.

        Uses pm4py.conformance_diagnostics_alignments() to compute optimal
        alignments between the log and model. This is more precise but slower
        than token replay.

        Args:
            event_log: The event log to check
            model: The process model to check against
            max_cases: Maximum number of cases to include in response

        Returns:
            Dictionary with alignment diagnostics per case
        """
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        net, im, fm = self._get_petri_net(model)

        # Get alignment diagnostics using PM4Py
        alignments = pm4py.conformance_diagnostics_alignments(pm4py_log, net, im, fm)

        case_alignments = []
        total_fitness = 0.0
        fitting_count = 0

        for i, (trace, alignment) in enumerate(zip(pm4py_log, alignments, strict=False)):
            if i >= max_cases:
                break

            case_id = trace.attributes.get("concept:name", f"trace_{i}")

            # Extract alignment moves
            moves = []
            alignment_seq = alignment.get("alignment", [])
            for move in alignment_seq:
                # Each move is ((log_label, model_label), (log_move, model_move))
                if isinstance(move, tuple) and len(move) >= 2:
                    labels = move[0] if len(move) > 0 else (None, None)
                    log_label = labels[0] if isinstance(labels, tuple) and len(labels) > 0 else None
                    model_label = (
                        labels[1] if isinstance(labels, tuple) and len(labels) > 1 else None
                    )

                    # Determine move type
                    if log_label == ">>" or log_label is None:
                        move_type = "model_only"
                        log_move = None
                        model_move = str(model_label) if model_label else None
                    elif model_label == ">>" or model_label is None:
                        move_type = "log_only"
                        log_move = str(log_label) if log_label else None
                        model_move = None
                    else:
                        move_type = "sync"
                        log_move = str(log_label) if log_label else None
                        model_move = str(model_label) if model_label else None

                    moves.append(
                        {
                            "log_move": log_move,
                            "model_move": model_move,
                            "move_type": move_type,
                        }
                    )

            # Calculate fitness for this case
            fitness = alignment.get("fitness", 1.0)
            cost = alignment.get("cost", 0)
            is_fit = cost == 0

            total_fitness += fitness
            if is_fit:
                fitting_count += 1

            case_alignments.append(
                {
                    "case_id": case_id,
                    "fitness": fitness,
                    "cost": cost,
                    "alignment": moves,
                    "is_fit": is_fit,
                }
            )

        avg_fitness = total_fitness / len(case_alignments) if case_alignments else 0.0

        return {
            "total_cases": len(pm4py_log),
            "fitting_cases": fitting_count,
            "average_fitness": avg_fitness,
            "case_alignments": case_alignments,
        }

    # =========================================================================
    # Declarative Conformance (Phase 2 PM4py Integration)
    # =========================================================================

    def check_declare_conformance(
        self,
        event_log: Dataset,
        declare_model: dict | None = None,
    ) -> dict[str, Any]:
        """
        Check conformance against DECLARE constraints.

        If no model is provided, discovers one from the log first.

        Args:
            event_log: The event log to check
            declare_model: Optional DECLARE model (discovered if not provided)

        Returns:
            Dictionary with constraint conformance details
        """
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        # Discover DECLARE model if not provided
        if declare_model is None:
            declare_model = pm4py.discover_declare(pm4py_log)

        # Check conformance
        conformance = pm4py.conformance_declare(pm4py_log, declare_model)

        # Aggregate results
        total_traces = len(conformance)
        conforming_traces = sum(1 for c in conformance if c.get("is_conformant", False))

        # Extract constraint violations
        violations = []
        for i, trace_conf in enumerate(conformance[:50]):  # Limit to 50 traces
            if not trace_conf.get("is_conformant", True):
                violations.append(
                    {
                        "trace_index": i,
                        "violated_constraints": list(trace_conf.get("violated_constraints", []))[
                            :5
                        ],
                    }
                )

        return {
            "method": "declare",
            "total_traces": total_traces,
            "conforming_traces": conforming_traces,
            "conformance_ratio": conforming_traces / total_traces if total_traces > 0 else 0,
            "violations": violations,
            "is_conformant": conforming_traces == total_traces,
        }

    def check_log_skeleton_conformance(
        self,
        event_log: Dataset,
        log_skeleton: dict | None = None,
        noise_threshold: float = 0.0,
    ) -> dict[str, Any]:
        """
        Check conformance against a Log Skeleton model.

        Log Skeleton captures activity occurrence and ordering constraints.

        Args:
            event_log: The event log to check
            log_skeleton: Optional log skeleton model (discovered if not provided)
            noise_threshold: Fraction of traces allowed to violate constraints

        Returns:
            Dictionary with conformance details
        """
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        # Discover log skeleton if not provided
        if log_skeleton is None:
            log_skeleton = pm4py.discover_log_skeleton(pm4py_log, noise_threshold=noise_threshold)

        # Check conformance
        conformance = pm4py.conformance_log_skeleton(pm4py_log, log_skeleton)

        # Analyze results
        total_traces = len(conformance)
        deviations = []
        conforming_count = 0

        for i, (is_fit, details) in enumerate(conformance):
            if is_fit:
                conforming_count += 1
            elif i < 50:  # Limit deviation details
                deviations.append(
                    {
                        "trace_index": i,
                        "deviation_details": str(details)[:200] if details else None,
                    }
                )

        return {
            "method": "log_skeleton",
            "total_traces": total_traces,
            "conforming_traces": conforming_count,
            "conformance_ratio": conforming_count / total_traces if total_traces > 0 else 0,
            "deviations": deviations,
            "is_conformant": conforming_count == total_traces,
        }

    def check_temporal_profile_conformance(
        self,
        event_log: Dataset,
        temporal_profile: dict | None = None,
        zeta: float = 2.0,
    ) -> dict[str, Any]:
        """
        Check conformance against temporal constraints.

        Detects activities with unusual time intervals (anomalies).

        Args:
            event_log: The event log to check
            temporal_profile: Optional temporal profile (discovered if not provided)
            zeta: Number of standard deviations for anomaly threshold

        Returns:
            Dictionary with temporal conformance and detected anomalies
        """
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        # Discover temporal profile if not provided
        if temporal_profile is None:
            temporal_profile = pm4py.discover_temporal_profile(pm4py_log)

        # Check conformance
        conformance = pm4py.conformance_temporal_profile(pm4py_log, temporal_profile, zeta=zeta)

        # Collect anomalies
        anomalies = []
        traces_with_anomalies = 0

        for i, trace_anomalies in enumerate(conformance):
            if trace_anomalies:  # Has anomalies
                traces_with_anomalies += 1
                if i < 50:  # Limit output
                    for anomaly in trace_anomalies[:3]:  # Max 3 per trace
                        anomalies.append(
                            {
                                "trace_index": i,
                                "activity_pair": anomaly[0] if len(anomaly) > 0 else None,
                                "expected_avg": anomaly[1] if len(anomaly) > 1 else None,
                                "expected_std": anomaly[2] if len(anomaly) > 2 else None,
                                "actual_duration": anomaly[3] if len(anomaly) > 3 else None,
                            }
                        )

        total_traces = len(conformance)

        return {
            "method": "temporal_profile",
            "total_traces": total_traces,
            "traces_with_anomalies": traces_with_anomalies,
            "conformance_ratio": 1 - (traces_with_anomalies / total_traces)
            if total_traces > 0
            else 1,
            "zeta_threshold": zeta,
            "anomalies": anomalies[:100],  # Cap anomalies
            "is_conformant": traces_with_anomalies == 0,
        }

    # =========================================================================
    # Model Quality Analysis (Phase 2 PM4py Integration)
    # =========================================================================

    def check_soundness(
        self,
        model: ProcessModel,
    ) -> dict[str, Any]:
        """
        Check if a Petri net is sound (proper completion, no deadlocks).

        A sound workflow net guarantees that every started case can
        complete properly.

        Returns:
            Dictionary with soundness verdict and diagnostics
        """
        net, im, fm = self._get_petri_net(model)

        try:
            is_sound = pm4py.check_soundness(net, im, fm)

            return {
                "is_sound": is_sound[0] if isinstance(is_sound, tuple) else is_sound,
                "diagnostics": is_sound[1]
                if isinstance(is_sound, tuple) and len(is_sound) > 1
                else None,
            }
        except Exception as e:
            return {
                "is_sound": None,
                "error": str(e),
            }

    def calculate_earth_movers_distance(
        self,
        event_log: Dataset,
        model: ProcessModel,
    ) -> dict[str, float]:
        """
        Calculate Earth Mover's Distance between log and model.

        EMD measures the effort required to transform the log language
        into the model language. Lower is better.

        Returns:
            Dictionary with EMD value
        """
        # Use fast path: event_log_loader instead of ORM iteration
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(event_log.id)

        net, im, fm = self._get_petri_net(model)

        try:
            emd = pm4py.compute_emd(pm4py_log, net, im, fm)
            return {
                "earth_movers_distance": emd,
                "interpretation": "Lower EMD indicates better model fit",
            }
        except Exception as e:
            return {
                "earth_movers_distance": None,
                "error": str(e),
            }

    def calculate_model_similarity(
        self,
        model1: ProcessModel,
        model2: ProcessModel,
    ) -> dict[str, Any]:
        """
        Calculate behavioral and structural similarity between two models.

        Returns:
            Dictionary with similarity scores
        """
        net1, im1, fm1 = self._get_petri_net(model1)
        net2, im2, fm2 = self._get_petri_net(model2)

        result = {}

        # Structural similarity (based on edit distance)
        try:
            structural_sim = pm4py.structural_similarity((net1, im1, fm1), (net2, im2, fm2))
            result["structural_similarity"] = structural_sim
        except Exception as e:
            result["structural_similarity"] = None
            result["structural_error"] = str(e)

        # Behavioral similarity (based on language)
        try:
            behavioral_sim = pm4py.behavioral_similarity((net1, im1, fm1), (net2, im2, fm2))
            result["behavioral_similarity"] = behavioral_sim
        except Exception as e:
            result["behavioral_similarity"] = None
            result["behavioral_error"] = str(e)

        return result

    def _token_replay(
        self,
        log,
        net: PetriNet,
        im: Marking,
        fm: Marking,
    ) -> dict[str, Any]:
        """Perform token-based replay conformance checking."""
        fitness_result = pm4py.fitness_token_based_replay(log, net, im, fm)
        fitness = fitness_result.get("average_trace_fitness", 0.0)

        try:
            precision = pm4py.precision_token_based_replay(log, net, im, fm)
        except Exception as e:
            logger.warning(
                "precision_calculation_failed",
                error=str(e),
                msg="Returning None for precision",
            )
            precision = None

        # Get diagnostics for fitting trace count
        diagnostics = pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)
        fitting_traces = sum(1 for r in diagnostics if r.get("trace_is_fit", False))

        return {
            "fitness": fitness,
            "precision": precision,
            "method": "token_replay",
            "algorithm_used": "token_replay",  # Explicit tracking (same as method when no fallback)
            "fallback_reason": None,
            "fitting_traces": fitting_traces,
            "total_traces": len(log),
            "is_conformant": fitness >= 0.8,
        }

    def _alignment_based(
        self,
        log,
        net: PetriNet,
        im: Marking,
        fm: Marking,
    ) -> dict[str, Any]:
        """Perform alignment-based conformance checking.

        Now includes explicit algorithm tracking to address silent fallback anti-pattern.
        Returns algorithm_used and fallback_reason fields.
        """
        from src.platform.core.logging_config import get_logger

        logger = get_logger(__name__)

        try:
            fitness_result = pm4py.fitness_alignments(log, net, im, fm)
            precision = pm4py.precision_alignments(log, net, im, fm)

            fitness = fitness_result.get("average_trace_fitness", 0.0)

            return {
                "fitness": fitness,
                "precision": precision,
                "method": "alignment",
                "algorithm_used": "alignment",  # Explicit tracking
                "fallback_reason": None,
                "fitting_traces": int(len(log) * fitness),
                "total_traces": len(log),
                "is_conformant": fitness >= 0.8,
            }
        except Exception as e:
            # Log the fallback with reason - no longer silent!
            fallback_reason = f"Alignment failed: {str(e)[:200]}"
            logger.warning(
                "conformance_algorithm_fallback",
                requested_method="alignment",
                fallback_to="token_replay",
                reason=fallback_reason,
            )

            # Fall back to token replay, but explicitly track it
            result = self._token_replay(log, net, im, fm)
            result["method"] = "alignment"  # What was requested
            result["algorithm_used"] = "token_replay"  # What actually ran
            result["fallback_reason"] = fallback_reason
            return result

    def _get_petri_net(
        self,
        model: ProcessModel,
    ) -> tuple[PetriNet, Marking, Marking]:
        """Get Petri net from model, converting if necessary."""
        model_data = mining_service.deserialize_model(model.serialized_model)

        if model.model_format == ModelFormat.PETRI_NET.value:
            return model_data
        if (
            model.model_format == ModelFormat.PROCESS_TREE.value
            or model.model_format == ModelFormat.BPMN.value
        ):
            return pm4py.convert_to_petri_net(model_data)
        raise ValueError(f"Cannot convert {model.model_format} to Petri net")


# Singleton instance for backward compatibility
conformance_service = ConformanceService()
