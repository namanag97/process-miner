"""Conformance Checking Service - PM4Py Integration."""

from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from dataclasses import dataclass

import pm4py
from pm4py.objects.petri_net.obj import PetriNet, Marking

from src.domain.entities import EventLog, ProcessModel, ConformanceResult
from src.domain.aggregates import AnalysisAggregate
from src.domain.value_objects import ConformanceMethod, ModelFormat
from src.application.core.discovery_service import discovery_service


@dataclass
class DeviationInfo:
    """Information about a conformance deviation."""
    case_id: str
    activity: str
    deviation_type: str
    details: str


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
    ) -> AnalysisAggregate:
        """
        Check conformance between an event log and a process model.
        
        Args:
            event_log: The event log to check
            model: The process model to check against
            method: Conformance checking method
            
        Returns:
            AnalysisAggregate with conformance results
        """
        # Convert to PM4Py formats
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)
        
        # Calculate conformance
        if method == ConformanceMethod.TOKEN_REPLAY:
            result = self._token_replay(pm4py_log, net, im, fm)
        else:
            result = self._alignment_based(pm4py_log, net, im, fm)
        
        # Create analysis aggregate
        aggregate = AnalysisAggregate.create(
            log_id=event_log.id,
            model_id=model.id,
        )
        
        conformance_result = ConformanceResult.create(
            log_id=event_log.id,
            model_id=model.id,
            fitness=result["fitness"],
        )
        conformance_result.precision = result.get("precision")
        conformance_result.deviations = result.get("deviations", [])
        
        aggregate.set_conformance_result(conformance_result)
        
        return aggregate
    
    def calculate_fitness(
        self,
        event_log: EventLog,
        model: ProcessModel,
    ) -> float:
        """Calculate fitness score for log-model pair."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)
        
        fitness = pm4py.fitness_token_based_replay(pm4py_log, net, im, fm)
        return fitness.get("average_trace_fitness", 0.0)
    
    def calculate_precision(
        self,
        event_log: EventLog,
        model: ProcessModel,
    ) -> float:
        """Calculate precision score for log-model pair."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)
        
        precision = pm4py.precision_token_based_replay(pm4py_log, net, im, fm)
        return precision
    
    def get_diagnostics(
        self,
        event_log: EventLog,
        model: ProcessModel,
    ) -> Dict[str, Any]:
        """Get detailed conformance diagnostics."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)
        
        # Token replay diagnostics
        replay_result = pm4py.conformance_diagnostics_token_based_replay(
            pm4py_log, net, im, fm
        )
        
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
                    deviations.append({
                        "trace_index": i,
                        "type": "missing_tokens",
                        "tokens": [str(t) for t in missing[:5]],  # Limit for readability
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
            "trace_fitness_ratio": fitting_traces / total_traces if total_traces > 0 else 0,
            "deviations": deviations[:50],  # Limit deviations
        }
    
    def detect_deviations(
        self,
        event_log: EventLog,
        model: ProcessModel,
        threshold: float = 0.8,
    ) -> List[DeviationInfo]:
        """Detect specific deviations from the model."""
        pm4py_log = discovery_service._to_pm4py_log(event_log)
        net, im, fm = self._get_petri_net(model)
        
        diagnostics = pm4py.conformance_diagnostics_token_based_replay(
            pm4py_log, net, im, fm
        )
        
        deviations = []
        for i, (trace, diag) in enumerate(zip(pm4py_log, diagnostics)):
            if not diag.get("trace_is_fit", True):
                case_id = trace.attributes.get("concept:name", f"trace_{i}")
                
                # Analyze deviation types
                if diag.get("missing_tokens"):
                    deviations.append(DeviationInfo(
                        case_id=case_id,
                        activity="",
                        deviation_type="missing_token",
                        details=f"Missing tokens: {len(diag['missing_tokens'])}",
                    ))
                
                if diag.get("remaining_tokens"):
                    deviations.append(DeviationInfo(
                        case_id=case_id,
                        activity="",
                        deviation_type="remaining_token",
                        details=f"Remaining tokens: {len(diag['remaining_tokens'])}",
                    ))
        
        return deviations
    
    def _token_replay(
        self,
        log,
        net: PetriNet,
        im: Marking,
        fm: Marking,
    ) -> Dict[str, Any]:
        """Perform token-based replay conformance checking."""
        fitness = pm4py.fitness_token_based_replay(log, net, im, fm)
        
        try:
            precision = pm4py.precision_token_based_replay(log, net, im, fm)
        except Exception:
            precision = None
        
        return {
            "fitness": fitness.get("average_trace_fitness", 0.0),
            "precision": precision,
            "method": "token_replay",
        }
    
    def _alignment_based(
        self,
        log,
        net: PetriNet,
        im: Marking,
        fm: Marking,
    ) -> Dict[str, Any]:
        """Perform alignment-based conformance checking."""
        try:
            fitness = pm4py.fitness_alignments(log, net, im, fm)
            precision = pm4py.precision_alignments(log, net, im, fm)
            
            return {
                "fitness": fitness.get("average_trace_fitness", 0.0),
                "precision": precision,
                "method": "alignment",
            }
        except Exception as e:
            # Fall back to token replay if alignment fails
            return self._token_replay(log, net, im, fm)
    
    def _get_petri_net(
        self,
        model: ProcessModel,
    ) -> Tuple[PetriNet, Marking, Marking]:
        """Get Petri net from model, converting if necessary."""
        if model.model_data is None and model.serialized:
            import pickle
            model.model_data = pickle.loads(model.serialized)
        
        if model.format == ModelFormat.PETRI_NET:
            return model.model_data
        elif model.format == ModelFormat.PROCESS_TREE:
            return pm4py.convert_to_petri_net(model.model_data)
        elif model.format == ModelFormat.BPMN:
            return pm4py.convert_to_petri_net(model.model_data)
        else:
            raise ValueError(f"Cannot convert {model.format} to Petri net")


# Singleton instance
conformance_service = ConformanceService()
