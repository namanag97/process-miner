"""Transition Service - DFG Edge Analysis using PM4Py."""

from typing import List, Dict, Any, Optional
from uuid import UUID
from collections import defaultdict

import pm4py
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery

from src.domain.entities import EventLog
from src.domain.value_objects import Transition, Gateway, GatewayType, GatewayDirection


class TransitionService:
    """
    Service for computing and analyzing DFG transitions.
    Maps to the Transition concept in the Process Mining Ontology.
    """
    
    def compute_transitions(
        self,
        event_log: EventLog,
        include_duration: bool = True,
    ) -> List[Transition]:
        """
        Compute all transitions (DFG edges) from an event log.
        
        Args:
            event_log: The event log to analyze
            include_duration: Whether to compute duration statistics
            
        Returns:
            List of Transition value objects
        """
        # Convert to PM4Py log format
        pm4py_log = self._to_pm4py_log(event_log)
        
        # Compute DFG with frequency
        dfg = dfg_discovery.apply(pm4py_log)
        
        # Calculate total outgoing frequency for each activity (for probability)
        outgoing_totals: Dict[str, int] = defaultdict(int)
        for (source, target), freq in dfg.items():
            outgoing_totals[source] += freq
        
        # Compute duration statistics if requested
        duration_stats = {}
        if include_duration:
            duration_stats = self._compute_duration_statistics(event_log)
        
        # Build Transition objects
        transitions = []
        for (source, target), frequency in dfg.items():
            probability = frequency / outgoing_totals[source] if outgoing_totals[source] > 0 else 0.0
            
            duration_key = f"{source} -> {target}"
            durations = duration_stats.get(duration_key, {})
            
            transition = Transition(
                source_activity=source,
                target_activity=target,
                frequency=frequency,
                probability=round(probability, 4),
                avg_duration_seconds=durations.get("avg", 0.0),
                min_duration_seconds=durations.get("min", 0.0),
                max_duration_seconds=durations.get("max", 0.0),
            )
            transitions.append(transition)
        
        # Sort by frequency descending
        transitions.sort(key=lambda t: t.frequency, reverse=True)
        return transitions
    
    def get_start_activities(self, event_log: EventLog) -> Dict[str, int]:
        """Get activities that start cases with their frequencies."""
        pm4py_log = self._to_pm4py_log(event_log)
        return dict(pm4py.get_start_activities(pm4py_log))
    
    def get_end_activities(self, event_log: EventLog) -> Dict[str, int]:
        """Get activities that end cases with their frequencies."""
        pm4py_log = self._to_pm4py_log(event_log)
        return dict(pm4py.get_end_activities(pm4py_log))
    
    def detect_gateways(
        self,
        transitions: List[Transition],
        threshold: int = 2,
    ) -> List[Gateway]:
        """
        Detect gateways (splits and joins) from transitions.
        
        Args:
            transitions: List of computed transitions
            threshold: Minimum branches to consider a gateway
            
        Returns:
            List of Gateway value objects
        """
        # Count incoming and outgoing edges per activity
        outgoing: Dict[str, List[str]] = defaultdict(list)
        incoming: Dict[str, List[str]] = defaultdict(list)
        
        for t in transitions:
            outgoing[t.source_activity].append(t.target_activity)
            incoming[t.target_activity].append(t.source_activity)
        
        gateways = []
        
        # Detect splits (one activity with multiple outgoing)
        for activity, targets in outgoing.items():
            if len(targets) >= threshold:
                gateway = Gateway(
                    activity=activity,
                    gateway_type=GatewayType.XOR,  # Default to XOR, can be refined
                    direction=GatewayDirection.SPLIT,
                    branches=tuple(targets),
                )
                gateways.append(gateway)
        
        # Detect joins (one activity with multiple incoming)
        for activity, sources in incoming.items():
            if len(sources) >= threshold:
                gateway = Gateway(
                    activity=activity,
                    gateway_type=GatewayType.XOR,  # Default to XOR
                    direction=GatewayDirection.JOIN,
                    branches=tuple(sources),
                )
                gateways.append(gateway)
        
        return gateways
    
    def get_transition_statistics(
        self,
        transitions: List[Transition],
    ) -> Dict[str, Any]:
        """
        Get summary statistics for transitions.
        """
        if not transitions:
            return {
                "total_transitions": 0,
                "total_frequency": 0,
                "unique_activities": 0,
            }
        
        total_freq = sum(t.frequency for t in transitions)
        activities = set()
        for t in transitions:
            activities.add(t.source_activity)
            activities.add(t.target_activity)
        
        avg_freq = total_freq / len(transitions)
        avg_prob = sum(t.probability for t in transitions) / len(transitions)
        
        # Find most frequent transitions
        top_transitions = transitions[:5]
        
        return {
            "total_transitions": len(transitions),
            "total_frequency": total_freq,
            "unique_activities": len(activities),
            "avg_frequency": round(avg_freq, 2),
            "avg_probability": round(avg_prob, 4),
            "top_transitions": [t.to_dict() for t in top_transitions],
        }
    
    def _compute_duration_statistics(
        self,
        event_log: EventLog,
    ) -> Dict[str, Dict[str, float]]:
        """
        Compute duration statistics for each transition.
        
        Returns:
            Dict mapping "source -> target" to {"avg", "min", "max"} durations
        """
        durations: Dict[str, List[float]] = defaultdict(list)
        
        for case in event_log.cases:
            events = sorted(case.events, key=lambda e: e.timestamp.value)
            
            for i in range(len(events) - 1):
                source = str(events[i].activity)
                target = str(events[i + 1].activity)
                key = f"{source} -> {target}"
                
                duration = (events[i + 1].timestamp.value - events[i].timestamp.value).total_seconds()
                if duration >= 0:  # Skip negative durations (data quality issue)
                    durations[key].append(duration)
        
        # Compute statistics
        stats = {}
        for key, duration_list in durations.items():
            if duration_list:
                stats[key] = {
                    "avg": sum(duration_list) / len(duration_list),
                    "min": min(duration_list),
                    "max": max(duration_list),
                }
        
        return stats
    
    def _to_pm4py_log(self, event_log: EventLog):
        """Convert domain EventLog to PM4Py EventLog."""
        from pm4py.objects.log.obj import EventLog as PM4PyEventLog, Trace, Event
        
        pm4py_log = PM4PyEventLog()
        
        for case in event_log.cases:
            trace = Trace()
            trace.attributes["concept:name"] = case.case_id
            
            for event in case.events:
                pm4py_event = Event()
                pm4py_event["concept:name"] = str(event.activity)
                pm4py_event["time:timestamp"] = event.timestamp.value
                if event.resource:
                    pm4py_event["org:resource"] = str(event.resource)
                trace.append(pm4py_event)
            
            pm4py_log.append(trace)
        
        return pm4py_log


# Singleton instance
transition_service = TransitionService()
