"""Conformance Checking Service - PM4Py Integration.

Ported from: src/application/core/conformance_service.py
Simplified: No aggregates, no domain entities - direct PM4Py usage.
"""

from typing import Any, Optional

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

    def get_diagnostics(
        self,
        event_log: EventLog,
        model: ProcessModel,
    ) -> dict[str, Any]:
        """Get detailed conformance diagnostics."""
        pm4py_log = mining_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)

        # Token replay diagnostics
        replay_result = pm4py.conformance_diagnostics_token_based_replay(
            pm4py_log, net, im, fm
        )

        # Calculate aggregate metrics
        fitting_traces = sum(
            1 for r in replay_result if r.get("trace_is_fit", False)
        )
        total_traces = len(replay_result)

        # Collect deviations
        deviations = []
        for i, result in enumerate(replay_result):
            if not result.get("trace_is_fit", True):
                missing = result.get("missing_tokens", [])
                remaining = result.get("remaining_tokens", [])

                if missing:
                    deviations.append({
                        "trace_index": i,
                        "type": "missing_tokens",
                        "tokens": [str(t) for t in missing[:5]],
                    })
                if remaining:
                    deviations.append({
                        "trace_index": i,
                        "type": "remaining_tokens",
                        "tokens": [str(t) for t in remaining[:5]],
                    })

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

        diagnostics = pm4py.conformance_diagnostics_token_based_replay(
            pm4py_log, net, im, fm
        )

        deviations = []
        for i, (trace, diag) in enumerate(zip(pm4py_log, diagnostics)):
            if not diag.get("trace_is_fit", True):
                case_id = trace.attributes.get("concept:name", f"trace_{i}")

                if diag.get("missing_tokens"):
                    deviations.append({
                        "case_id": case_id,
                        "activity": "",
                        "deviation_type": "missing_token",
                        "details": f"Missing tokens: {len(diag['missing_tokens'])}",
                    })

                if diag.get("remaining_tokens"):
                    deviations.append({
                        "case_id": case_id,
                        "activity": "",
                        "deviation_type": "remaining_token",
                        "details": f"Remaining tokens: {len(diag['remaining_tokens'])}",
                    })

        return deviations

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
        percentage_fit = fitness_result.get("percentage_of_fitting_traces", 0.0)

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
