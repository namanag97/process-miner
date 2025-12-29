"""Process Mining Service - PM4Py Integration.

Ported from:
- src/application/core/discovery_service.py
- src/application/core/pm4py_service.py

Simplified: Removed aggregates, domain entities - works directly with ORM models.
"""

import pickle
import time
import warnings
from typing import Any, Optional

warnings.filterwarnings("ignore")

import pm4py
from pm4py.objects.log.obj import Event as PM4PyEvent
from pm4py.objects.log.obj import EventLog as PM4PyLog
from pm4py.objects.log.obj import Trace
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.statistics.traces.generic.log import case_arrival, case_statistics
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from pm4py.visualization.petri_net import visualizer as pn_visualizer

from src.core.enums import MinerType, ModelFormat
from src.core.logging_config import get_logger
from src.models.orm import EventLog

logger = get_logger(__name__)


class MiningService:
    """
    Process Mining Service using PM4Py.
    Supports discovery, conformance, analysis, and visualization.
    """

    # =========================================================================
    # Discovery Algorithms
    # =========================================================================

    def discover(
        self,
        event_log: EventLog,
        miner_type: MinerType = MinerType.INDUCTIVE,
    ) -> tuple[Any, ModelFormat]:
        """
        Discover a process model from an event log.

        Returns:
            Tuple of (model_data, model_format)
        """
        logger.info(
            "discovery_algorithm_started",
            log_id=event_log.id,
            miner_type=miner_type.value,
            total_cases=event_log.total_cases,
            total_events=event_log.total_events,
        )
        start_time = time.perf_counter()

        pm4py_log = self._to_pm4py_log(event_log)
        conversion_ms = (time.perf_counter() - start_time) * 1000
        logger.debug("pm4py_log_conversion", duration_ms=round(conversion_ms, 2))

        mining_start = time.perf_counter()
        if miner_type == MinerType.ALPHA:
            result = self._discover_alpha(pm4py_log), ModelFormat.PETRI_NET
        elif miner_type == MinerType.ALPHA_PLUS:
            result = self._discover_alpha_plus(pm4py_log), ModelFormat.PETRI_NET
        elif miner_type == MinerType.INDUCTIVE:
            result = self._discover_inductive(pm4py_log), ModelFormat.PROCESS_TREE
        elif miner_type == MinerType.INDUCTIVE_INFREQUENT:
            result = self._discover_inductive_infrequent(pm4py_log), ModelFormat.PROCESS_TREE
        elif miner_type == MinerType.HEURISTICS:
            result = self._discover_heuristics(pm4py_log), ModelFormat.PETRI_NET
        elif miner_type == MinerType.DFG:
            result = self._discover_dfg(pm4py_log), ModelFormat.DFG
        else:
            raise ValueError(f"Unknown miner type: {miner_type}")

        mining_ms = (time.perf_counter() - mining_start) * 1000
        total_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "discovery_algorithm_completed",
            miner_type=miner_type.value,
            model_format=result[1].value,
            mining_duration_ms=round(mining_ms, 2),
            total_duration_ms=round(total_ms, 2),
        )
        return result

    def _discover_alpha(self, log: PM4PyLog) -> tuple[PetriNet, Marking, Marking]:
        """Alpha miner - classic algorithm."""
        return pm4py.discover_petri_net_alpha(log)

    def _discover_alpha_plus(self, log: PM4PyLog) -> tuple[PetriNet, Marking, Marking]:
        """Alpha+ miner - handles short loops."""
        return pm4py.discover_petri_net_alpha_plus(log)

    def _discover_inductive(self, log: PM4PyLog) -> ProcessTree:
        """Inductive miner - recommended, produces sound process trees."""
        return pm4py.discover_process_tree_inductive(log)

    def _discover_inductive_infrequent(self, log: PM4PyLog) -> ProcessTree:
        """Inductive miner with noise filtering."""
        return pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)

    def _discover_heuristics(self, log: PM4PyLog) -> tuple[PetriNet, Marking, Marking]:
        """Heuristics miner - handles noise well."""
        return pm4py.discover_petri_net_heuristics(log)

    def _discover_dfg(self, log: PM4PyLog) -> tuple[dict, dict, dict]:
        """Directly-Follows Graph - simple visualization."""
        return pm4py.discover_dfg(log)

    # =========================================================================
    # Petri Net Operations
    # =========================================================================

    def get_petri_net(
        self,
        event_log: EventLog,
        miner_type: MinerType = MinerType.INDUCTIVE,
    ) -> tuple[PetriNet, Marking, Marking]:
        """Get Petri net from discovery (converts process tree if needed)."""
        pm4py_log = self._to_pm4py_log(event_log)

        if miner_type in [MinerType.ALPHA, MinerType.ALPHA_PLUS, MinerType.HEURISTICS]:
            model_data, _ = self.discover(event_log, miner_type)
            return model_data
        else:
            # Inductive miners return process tree, convert to Petri net
            tree = self._discover_inductive(pm4py_log)
            return pm4py.convert_to_petri_net(tree)

    def tree_to_petri_net(self, tree: ProcessTree) -> tuple[PetriNet, Marking, Marking]:
        """Convert process tree to Petri net."""
        return pm4py.convert_to_petri_net(tree)

    # =========================================================================
    # Visualization
    # =========================================================================

    def visualize_petri_net(
        self,
        net: PetriNet,
        im: Marking,
        fm: Marking,
    ) -> bytes:
        """Generate SVG visualization of Petri net."""
        gviz = pn_visualizer.apply(net, im, fm)
        return pn_visualizer.serialize(gviz)

    def visualize_dfg(
        self,
        dfg: dict,
        start_activities: dict,
        end_activities: dict,
    ) -> bytes:
        """Generate SVG visualization of DFG."""
        gviz = dfg_visualizer.apply(dfg, activities_count=start_activities)
        return dfg_visualizer.serialize(gviz)

    def visualize_model(
        self,
        model_data: Any,
        model_format: ModelFormat,
    ) -> bytes:
        """Generate visualization for any model type."""
        if model_format == ModelFormat.PETRI_NET:
            net, im, fm = model_data
            return self.visualize_petri_net(net, im, fm)
        elif model_format == ModelFormat.PROCESS_TREE:
            net, im, fm = pm4py.convert_to_petri_net(model_data)
            return self.visualize_petri_net(net, im, fm)
        elif model_format == ModelFormat.DFG:
            dfg, start, end = model_data
            return self.visualize_dfg(dfg, start, end)
        else:
            raise ValueError(f"Visualization not supported for: {model_format}")

    # =========================================================================
    # Analysis Functions
    # =========================================================================

    def get_start_activities(self, event_log: EventLog) -> dict[str, int]:
        """Get start activities with frequencies."""
        pm4py_log = self._to_pm4py_log(event_log)
        return dict(pm4py.get_start_activities(pm4py_log))

    def get_end_activities(self, event_log: EventLog) -> dict[str, int]:
        """Get end activities with frequencies."""
        pm4py_log = self._to_pm4py_log(event_log)
        return dict(pm4py.get_end_activities(pm4py_log))

    def get_variants(self, event_log: EventLog, top_n: int = 20) -> dict[str, Any]:
        """Get process variants with counts."""
        pm4py_log = self._to_pm4py_log(event_log)
        variants = pm4py.get_variants(pm4py_log)

        def get_count(v):
            return len(v) if isinstance(v, (list, tuple)) else v

        variant_list = [
            {
                "variant": " -> ".join(k) if isinstance(k, tuple) else str(k),
                "count": get_count(v),
            }
            for k, v in sorted(variants.items(), key=lambda x: -get_count(x[1]))[:top_n]
        ]

        return {
            "top_variants": variant_list,
            "total_variants": len(variants),
        }

    def get_dfg_data(self, event_log: EventLog) -> dict[str, Any]:
        """Get DFG as structured data for visualization."""
        pm4py_log = self._to_pm4py_log(event_log)
        dfg, start_activities, end_activities = pm4py.discover_dfg(pm4py_log)

        # Build nodes (unique activities)
        all_activities = set()
        for (source, target), _ in dfg.items():
            all_activities.add(source)
            all_activities.add(target)

        # Calculate frequencies
        activity_freq = {}
        for (source, target), freq in dfg.items():
            activity_freq[source] = activity_freq.get(source, 0) + freq
            activity_freq[target] = activity_freq.get(target, 0) + freq

        total_freq = sum(dfg.values())

        nodes = [
            {
                "id": act,
                "name": act,
                "frequency": activity_freq.get(act, 0),
                "is_start": act in start_activities,
                "is_end": act in end_activities,
            }
            for act in all_activities
        ]

        edges = [
            {
                "source": source,
                "target": target,
                "frequency": freq,
                "probability": round(freq / total_freq, 4) if total_freq > 0 else 0,
            }
            for (source, target), freq in dfg.items()
        ]

        return {
            "nodes": nodes,
            "edges": edges,
            "start_activities": dict(start_activities),
            "end_activities": dict(end_activities),
            "total_frequency": total_freq,
        }

    def get_footprints(self, event_log: EventLog) -> dict[str, Any]:
        """Compute behavioral footprints (sequence/parallel relations)."""
        pm4py_log = self._to_pm4py_log(event_log)

        try:
            from pm4py.algo.discovery.footprints import algorithm as footprints_discovery

            fp_result = footprints_discovery.apply(pm4py_log)

            if isinstance(fp_result, list):
                # Merge trace footprints
                sequence, parallel, activities = set(), set(), set()
                start_acts, end_acts = set(), set()

                for fp in fp_result:
                    if isinstance(fp, dict):
                        sequence.update(fp.get("sequence", set()))
                        parallel.update(fp.get("parallel", set()))
                        activities.update(fp.get("activities", set()))
                        start_acts.update(fp.get("start_activities", set()))
                        end_acts.update(fp.get("end_activities", set()))

                return {
                    "sequence": [f"{k[0]} -> {k[1]}" for k in list(sequence)[:50]],
                    "parallel": [f"{k[0]} || {k[1]}" for k in list(parallel)[:50]],
                    "activities": list(activities),
                    "start_activities": list(start_acts),
                    "end_activities": list(end_acts),
                }
            elif isinstance(fp_result, dict):
                return {
                    "sequence": [f"{k[0]} -> {k[1]}" for k in list(fp_result.get("sequence", set()))[:50]],
                    "parallel": [f"{k[0]} || {k[1]}" for k in list(fp_result.get("parallel", set()))[:50]],
                    "activities": list(fp_result.get("activities", set())),
                    "start_activities": list(fp_result.get("start_activities", set())),
                    "end_activities": list(fp_result.get("end_activities", set())),
                }
        except Exception as e:
            return {"error": str(e)}

    def get_case_statistics(self, event_log: EventLog) -> dict[str, Any]:
        """Get case duration statistics."""
        pm4py_log = self._to_pm4py_log(event_log)

        try:
            durations = case_statistics.get_all_case_durations(pm4py_log)

            if not durations:
                return {"note": "No case durations available"}

            sorted_durations = sorted(durations)
            return {
                "min_duration_seconds": min(durations),
                "max_duration_seconds": max(durations),
                "avg_duration_seconds": sum(durations) / len(durations),
                "median_duration_seconds": sorted_durations[len(durations) // 2],
                "total_cases": len(durations),
            }
        except Exception as e:
            return {"error": str(e)}



    # =========================================================================
    # Model Quality Evaluation
    # =========================================================================

    def evaluate_fitness(
        self,
        event_log: EventLog,
        net: PetriNet,
        im: Marking,
        fm: Marking,
    ) -> dict[str, float]:
        """Evaluate model fitness using token replay."""
        pm4py_log = self._to_pm4py_log(event_log)
        result = pm4py.fitness_token_based_replay(pm4py_log, net, im, fm)
        return {
            "fitness": result.get("average_trace_fitness", 0.0),
            "percentage_fit_traces": result.get("percentage_of_fitting_traces", 0.0),
        }

    def evaluate_precision(
        self,
        event_log: EventLog,
        net: PetriNet,
        im: Marking,
        fm: Marking,
    ) -> float:
        """Evaluate model precision."""
        pm4py_log = self._to_pm4py_log(event_log)
        return pm4py.precision_token_based_replay(pm4py_log, net, im, fm)



    # =========================================================================
    # Serialization
    # =========================================================================

    def serialize_model(self, model_data: Any) -> bytes:
        """Serialize model for storage."""
        return pickle.dumps(model_data)

    def deserialize_model(self, data: bytes) -> Any:
        """Deserialize model from storage."""
        return pickle.loads(data)

    # =========================================================================
    # Helpers
    # =========================================================================

    def get_available_miners(self) -> list[dict[str, str]]:
        """Get list of available mining algorithms."""
        return [
            {
                "id": MinerType.INDUCTIVE.value,
                "name": "Inductive Miner",
                "description": "Recommended - produces sound, fitting process trees",
                "output_format": ModelFormat.PROCESS_TREE.value,
            },
            {
                "id": MinerType.ALPHA.value,
                "name": "Alpha Miner",
                "description": "Classic algorithm, produces Petri nets",
                "output_format": ModelFormat.PETRI_NET.value,
            },
            {
                "id": MinerType.ALPHA_PLUS.value,
                "name": "Alpha+ Miner",
                "description": "Enhanced Alpha, handles short loops",
                "output_format": ModelFormat.PETRI_NET.value,
            },
            {
                "id": MinerType.INDUCTIVE_INFREQUENT.value,
                "name": "Inductive Miner (Infrequent)",
                "description": "Handles noise, filters infrequent behavior",
                "output_format": ModelFormat.PROCESS_TREE.value,
            },
            {
                "id": MinerType.HEURISTICS.value,
                "name": "Heuristics Miner",
                "description": "Frequency-based, handles noise well",
                "output_format": ModelFormat.PETRI_NET.value,
            },
            {
                "id": MinerType.DFG.value,
                "name": "Directly-Follows Graph",
                "description": "Simple activity flow visualization",
                "output_format": ModelFormat.DFG.value,
            },
        ]

    def _to_pm4py_log(self, event_log: EventLog) -> PM4PyLog:
        """Convert ORM EventLog to PM4Py EventLog."""
        pm4py_log = PM4PyLog()

        for case in event_log.cases:
            trace = Trace()
            trace.attributes["concept:name"] = case.case_id

            for event in case.events:
                pm4py_event = PM4PyEvent()
                pm4py_event["concept:name"] = event.activity
                pm4py_event["time:timestamp"] = event.timestamp

                if event.resource:
                    pm4py_event["org:resource"] = event.resource

                # Add any additional attributes from JSON
                if event.attributes_json:
                    import json
                    try:
                        attrs = json.loads(event.attributes_json)
                        for key, value in attrs.items():
                            pm4py_event[key] = value
                    except Exception:
                        pass

                trace.append(pm4py_event)

            pm4py_log.append(trace)

        return pm4py_log


# Singleton instance
mining_service = MiningService()
