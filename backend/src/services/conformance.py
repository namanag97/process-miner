"""Conformance Checking Service - PM4Py Integration.

Ported from: src/application/core/conformance_service.py
Simplified: No aggregates, no domain entities - direct PM4Py usage.
"""

from typing import Any

import pm4py
from pm4py.objects.petri_net.obj import Marking, PetriNet

from src.core.enums import ConformanceMethod, ModelFormat
from src.models.orm import EventLog, ProcessModel
from src.services.mining import mining_service


class ConformanceService:
    """
    Conformance Checking Service using PM4Py.
    Supports token-based replay and alignment-based conformance.
    """

    def check_conformance(
        self,
        event_log: EventLog,
        model: ProcessModel,
        method: ConformanceMethod = ConformanceMethod.TOKEN_REPLAY,
    ) -> dict[str, Any]:
        """
        Check conformance between an event log and a process model.

        Returns:
            Dictionary with fitness, precision, method, and diagnostics
        """
        pm4py_log = mining_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)

        if method == ConformanceMethod.TOKEN_REPLAY:
            result = self._token_replay(pm4py_log, net, im, fm)
        else:
            result = self._alignment_based(pm4py_log, net, im, fm)

        return result

    def calculate_fitness(
        self,
        event_log: EventLog,
        model: ProcessModel,
    ) -> float:
        """Calculate fitness score for log-model pair."""
        pm4py_log = mining_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)

        fitness = pm4py.fitness_token_based_replay(pm4py_log, net, im, fm)
        return fitness.get("average_trace_fitness", 0.0)

    def calculate_precision(
        self,
        event_log: EventLog,
        model: ProcessModel,
    ) -> float:
        """Calculate precision score for log-model pair."""
        pm4py_log = mining_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)

        precision = pm4py.precision_token_based_replay(pm4py_log, net, im, fm)
        return precision

    def calculate_generalization(
        self,
        event_log: EventLog,
        model: ProcessModel,
    ) -> float:
        """Calculate generalization score for log-model pair.
        
        Generalization measures how well the model generalizes beyond
        the observed behavior in the log.
        """
        pm4py_log = mining_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)
        
        try:
            # PM4py's generalization function
            generalization = pm4py.generalization_tbr(pm4py_log, net, im, fm)
            return generalization
        except Exception:
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
            simplicity = pm4py.simplicity_petri_net(net, im, fm)
            return simplicity
        except Exception:
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
        event_log: EventLog,
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
        event_log: EventLog,
        model: ProcessModel,
    ) -> dict[str, Any]:
        """Get detailed conformance diagnostics."""
        pm4py_log = mining_service._to_pm4py_log(event_log)
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
        event_log: EventLog,
        model: ProcessModel,
        threshold: float = 0.8,
    ) -> list[dict[str, Any]]:
        """Detect specific deviations from the model."""
        pm4py_log = mining_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)

        diagnostics = pm4py.conformance_diagnostics_token_based_replay(pm4py_log, net, im, fm)

        deviations = []
        for i, (trace, diag) in enumerate(zip(pm4py_log, diagnostics)):
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
        event_log: EventLog,
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
        pm4py_log = mining_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)

        # Get alignment diagnostics using PM4Py
        alignments = pm4py.conformance_diagnostics_alignments(pm4py_log, net, im, fm)

        case_alignments = []
        total_fitness = 0.0
        fitting_count = 0

        for i, (trace, alignment) in enumerate(zip(pm4py_log, alignments)):
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
        except Exception:
            precision = None

        # Get diagnostics for fitting trace count
        diagnostics = pm4py.conformance_diagnostics_token_based_replay(log, net, im, fm)
        fitting_traces = sum(1 for r in diagnostics if r.get("trace_is_fit", False))

        return {
            "fitness": fitness,
            "precision": precision,
            "method": "token_replay",
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
        """Perform alignment-based conformance checking."""
        try:
            fitness_result = pm4py.fitness_alignments(log, net, im, fm)
            precision = pm4py.precision_alignments(log, net, im, fm)

            fitness = fitness_result.get("average_trace_fitness", 0.0)

            return {
                "fitness": fitness,
                "precision": precision,
                "method": "alignment",
                "fitting_traces": int(len(log) * fitness),
                "total_traces": len(log),
                "is_conformant": fitness >= 0.8,
            }
        except Exception:
            # Fall back to token replay if alignment fails
            return self._token_replay(log, net, im, fm)

    def _get_petri_net(
        self,
        model: ProcessModel,
    ) -> tuple[PetriNet, Marking, Marking]:
        """Get Petri net from model, converting if necessary."""
        model_data = mining_service.deserialize_model(model.serialized_model)

        if model.model_format == ModelFormat.PETRI_NET.value:
            return model_data
        elif model.model_format == ModelFormat.PROCESS_TREE.value:
            return pm4py.convert_to_petri_net(model_data)
        elif model.model_format == ModelFormat.BPMN.value:
            return pm4py.convert_to_petri_net(model_data)
        else:
            raise ValueError(f"Cannot convert {model.model_format} to Petri net")


# Singleton instance
conformance_service = ConformanceService()
