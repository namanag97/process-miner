"""Process Discovery Service - PM4Py Integration."""

import pickle
from typing import Any, Dict, Optional, Tuple

import pm4py
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.process_tree.obj import ProcessTree
from pm4py.visualization.dfg import visualizer as dfg_visualizer
from pm4py.visualization.petri_net import visualizer as pn_visualizer

from src.domain.aggregates import ProcessModelAggregate
from src.domain.entities import EventLog, ProcessModel
from src.domain.value_objects import MinerType, ModelFormat


class DiscoveryService:
    """
    Process Discovery Service using PM4Py.
    Supports Alpha, Inductive, Heuristics miners, and DFG discovery.
    """

    def discover_process_model(
        self,
        event_log: EventLog,
        miner_type: MinerType = MinerType.INDUCTIVE,
        model_name: Optional[str] = None,
    ) -> ProcessModelAggregate:
        """
        Discover a process model from an event log.

        Args:
            event_log: The event log to mine
            miner_type: Type of mining algorithm to use
            model_name: Optional name for the model

        Returns:
            ProcessModelAggregate with the discovered model
        """
        # Convert domain EventLog to PM4Py format
        pm4py_log = self._to_pm4py_log(event_log)

        # Discover model based on miner type
        if miner_type == MinerType.ALPHA:
            model_data = self._discover_alpha(pm4py_log)
            model_format = ModelFormat.PETRI_NET
        elif miner_type == MinerType.ALPHA_PLUS:
            model_data = self._discover_alpha_plus(pm4py_log)
            model_format = ModelFormat.PETRI_NET
        elif miner_type == MinerType.INDUCTIVE:
            model_data = self._discover_inductive(pm4py_log)
            model_format = ModelFormat.PROCESS_TREE
        elif miner_type == MinerType.INDUCTIVE_INFREQUENT:
            model_data = self._discover_inductive_infrequent(pm4py_log)
            model_format = ModelFormat.PROCESS_TREE
        elif miner_type == MinerType.HEURISTICS:
            model_data = self._discover_heuristics(pm4py_log)
            model_format = ModelFormat.PETRI_NET
        elif miner_type == MinerType.DFG:
            model_data = self._discover_dfg(pm4py_log)
            model_format = ModelFormat.DFG
        else:
            raise ValueError(f"Unknown miner type: {miner_type}")

        # Create model aggregate
        name = model_name or f"{event_log.name}_{miner_type.value}"
        aggregate = ProcessModelAggregate.create_from_discovery(
            name=name,
            source_log_id=event_log.id,
            miner_type=miner_type,
            model_format=model_format,
            model_data=model_data,
        )

        # Serialize model for storage
        aggregate.model.serialized = self._serialize_model(model_data, model_format)

        return aggregate

    def get_petri_net(
        self,
        event_log: EventLog,
        miner_type: MinerType = MinerType.INDUCTIVE,
    ) -> Tuple[PetriNet, Marking, Marking]:
        """
        Get Petri net directly from process discovery.
        Converts process tree to Petri net if needed.
        """
        pm4py_log = self._to_pm4py_log(event_log)

        if miner_type == MinerType.ALPHA:
            net, im, fm = self._discover_alpha(pm4py_log)
        elif miner_type == MinerType.INDUCTIVE:
            tree = self._discover_inductive(pm4py_log)
            net, im, fm = pm4py.convert_to_petri_net(tree)
        elif miner_type == MinerType.HEURISTICS:
            net, im, fm = self._discover_heuristics(pm4py_log)
        else:
            # Default to inductive
            tree = self._discover_inductive(pm4py_log)
            net, im, fm = pm4py.convert_to_petri_net(tree)

        return net, im, fm

    def visualize_model(
        self,
        model: ProcessModel,
        format: str = "svg",
    ) -> bytes:
        """Generate visualization of a process model."""
        if not model.model_data:
            if model.serialized:
                model.model_data = self._deserialize_model(model.serialized, model.format)
            else:
                raise ValueError("Model has no data to visualize")

        if model.format == ModelFormat.PETRI_NET:
            net, im, fm = model.model_data
            gviz = pn_visualizer.apply(net, im, fm)
            return pn_visualizer.serialize(gviz)
        elif model.format == ModelFormat.PROCESS_TREE:
            # Convert to Petri net for visualization
            net, im, fm = pm4py.convert_to_petri_net(model.model_data)
            gviz = pn_visualizer.apply(net, im, fm)
            return pn_visualizer.serialize(gviz)
        elif model.format == ModelFormat.DFG:
            dfg, start_activities, end_activities = model.model_data
            gviz = dfg_visualizer.apply(dfg, activities_count=start_activities)
            return dfg_visualizer.serialize(gviz)
        else:
            raise ValueError(f"Visualization not supported for format: {model.format}")

    def get_available_miners(self) -> list[Dict[str, Any]]:
        """Get list of available mining algorithms."""
        return [
            {
                "id": MinerType.ALPHA.value,
                "name": "Alpha Miner",
                "description": "Classic process discovery algorithm, produces Petri nets",
                "output_format": ModelFormat.PETRI_NET.value,
            },
            {
                "id": MinerType.INDUCTIVE.value,
                "name": "Inductive Miner",
                "description": "Produces sound and fitting process trees, recommended for most cases",
                "output_format": ModelFormat.PROCESS_TREE.value,
            },
            {
                "id": MinerType.INDUCTIVE_INFREQUENT.value,
                "name": "Inductive Miner Infrequent",
                "description": "Handles infrequent behavior, filters noise",
                "output_format": ModelFormat.PROCESS_TREE.value,
            },
            {
                "id": MinerType.HEURISTICS.value,
                "name": "Heuristics Miner",
                "description": "Handles noise well, frequency-based discovery",
                "output_format": ModelFormat.PETRI_NET.value,
            },
            {
                "id": MinerType.DFG.value,
                "name": "Directly-Follows Graph",
                "description": "Simple visualization of activity sequences",
                "output_format": ModelFormat.DFG.value,
            },
        ]

    def _to_pm4py_log(self, event_log: EventLog) -> pm4py.objects.log.obj.EventLog:
        """Convert domain EventLog to PM4Py EventLog."""
        from pm4py.objects.log.obj import Event
        from pm4py.objects.log.obj import EventLog as PM4PyLog
        from pm4py.objects.log.obj import Trace

        pm4py_log = PM4PyLog()

        for case in event_log.cases:
            trace = Trace()
            trace.attributes["concept:name"] = case.case_id

            for event in case.events:
                pm4py_event = Event()
                pm4py_event["concept:name"] = str(event.activity)
                pm4py_event["time:timestamp"] = event.timestamp.value
                if event.resource:
                    pm4py_event["org:resource"] = str(event.resource)

                # Add any additional attributes
                for key, value in event.attributes.items():
                    pm4py_event[key] = value

                trace.append(pm4py_event)

            pm4py_log.append(trace)

        return pm4py_log

    def _discover_alpha(self, log) -> Tuple[PetriNet, Marking, Marking]:
        """Discover using Alpha miner."""
        return pm4py.discover_petri_net_alpha(log)

    def _discover_alpha_plus(self, log) -> Tuple[PetriNet, Marking, Marking]:
        """Discover using Alpha+ miner."""
        return pm4py.discover_petri_net_alpha_plus(log)

    def _discover_inductive(self, log) -> ProcessTree:
        """Discover using Inductive miner."""
        return pm4py.discover_process_tree_inductive(log)

    def _discover_inductive_infrequent(self, log) -> ProcessTree:
        """Discover using Inductive miner with infrequent handling."""
        return pm4py.discover_process_tree_inductive(log, noise_threshold=0.2)

    def _discover_heuristics(self, log) -> Tuple[PetriNet, Marking, Marking]:
        """Discover using Heuristics miner."""
        return pm4py.discover_petri_net_heuristics(log)

    def _discover_dfg(self, log) -> Tuple[dict, dict, dict]:
        """Discover Directly-Follows Graph."""
        dfg, start_activities, end_activities = pm4py.discover_dfg(log)
        return dfg, start_activities, end_activities

    def _serialize_model(self, model_data: Any, format: ModelFormat) -> bytes:
        """Serialize a model for storage."""
        return pickle.dumps(model_data)

    def _deserialize_model(self, data: bytes, format: ModelFormat) -> Any:
        """Deserialize a model from storage."""
        return pickle.loads(data)


# Singleton instance
discovery_service = DiscoveryService()
