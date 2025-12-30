"""OCPM Service - Object-Centric Process Mining using PM4Py.

Ported from: src/application/core/ocpm_service.py
Simplified: Direct PM4Py calls without domain layer ceremony.

Provides OCEL 2.0 support for Object-Centric Process Mining including:
- OCEL file reading (JSON, SQLite formats)
- Object-Centric Petri Net discovery
- Object-Centric DFG discovery
- Object graph analysis
- Flattening to traditional event logs
"""

import os
import pickle
import tempfile
from typing import Any

import pm4py


class OCPMService:
    """Service for Object-Centric Process Mining operations using PM4Py."""

    def read_ocel(self, file_path: str):
        """Read an OCEL file (JSON, SQLite, or XML format).

        Args:
            file_path: Path to the OCEL file

        Returns:
            PM4Py OCEL object
        """
        return pm4py.read_ocel(file_path)

    def read_ocel_from_bytes(self, content: bytes, source_format: str = "jsonocel"):
        """Read OCEL from bytes content.

        Args:
            content: Raw bytes of the OCEL file
            source_format: File format (jsonocel, sqlite, xmlocel)

        Returns:
            PM4Py OCEL object
        """
        suffix = self._get_suffix_for_format(source_format)

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        try:
            return pm4py.read_ocel(tmp_path)
        finally:
            os.unlink(tmp_path)

    def _get_suffix_for_format(self, source_format: str) -> str:
        """Get file suffix for OCEL format.

        Args:
            source_format: File format (jsonocel, sqlite, xmlocel)

        Returns:
            File suffix including dot
        """
        if source_format == "sqlite":
            return ".sqlite"
        elif source_format == "xmlocel":
            return ".xmlocel"
        return ".jsonocel"

    def get_object_types(self, ocel) -> list[str]:
        """Get all object types from an OCEL.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            List of object type names
        """
        return list(pm4py.ocel_get_object_types(ocel))

    def get_objects_by_type(self, ocel, object_type: str) -> list[str]:
        """Get all object IDs of a specific type.

        Args:
            ocel: PM4Py OCEL object
            object_type: Name of the object type

        Returns:
            List of object identifiers
        """
        objects = pm4py.ocel_get_objects_of_type(ocel, object_type)
        return list(objects) if objects else []

    def get_activities(self, ocel) -> list[str]:
        """Get all activities from an OCEL.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            List of activity names
        """
        return list(pm4py.ocel_get_activity_names(ocel))

    def get_events(self, ocel) -> list[dict]:
        """Get all events from an OCEL.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            List of event dictionaries
        """
        events_df = ocel.events
        if hasattr(events_df, "to_dict"):
            return events_df.to_dict("records")
        return []

    def discover_oc_petri_net(self, ocel):
        """Discover Object-Centric Petri Net from OCEL.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Object-Centric Petri Net
        """
        return pm4py.discover_oc_petri_net(ocel)

    def get_object_centric_dfg(self, ocel) -> dict:
        """Get object-centric DFG (Directly-Follows Graph).

        This returns a DFG for each object type.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Object-centric DFG dictionary
        """
        return pm4py.ocel_discover_ocdfg(ocel)

    def get_object_graph(self, ocel) -> dict:
        """Get object-to-object interaction graph.

        Shows which objects interact with each other.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Object interaction graph
        """
        return pm4py.ocel_o2o_graph(ocel)

    def flatten_to_traditional_log(self, ocel, object_type: str):
        """Flatten OCEL to traditional event log for a specific object type.

        This creates a case-centric view where each object becomes a case.
        Useful for applying traditional process mining techniques.

        Args:
            ocel: PM4Py OCEL object
            object_type: Object type to flatten by

        Returns:
            Traditional PM4Py EventLog
        """
        return pm4py.ocel_flattening(ocel, object_type)

    def get_ocel_statistics(self, ocel) -> dict[str, Any]:
        """Get statistics about an OCEL.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Dictionary with OCEL statistics
        """
        object_types = self.get_object_types(ocel)
        activities = self.get_activities(ocel)

        # Count objects per type
        objects_per_type = {}
        total_objects = 0
        for ot in object_types:
            count = len(self.get_objects_by_type(ocel, ot))
            objects_per_type[ot] = count
            total_objects += count

        # Get event count
        events = ocel.events if hasattr(ocel, "events") else None
        total_events = len(events) if events is not None else 0

        return {
            "object_types": object_types,
            "total_object_types": len(object_types),
            "total_events": total_events,
            "total_objects": total_objects,
            "objects_per_type": objects_per_type,
            "activities": activities,
            "total_activities": len(activities),
        }

    def serialize_oc_petri_net(self, oc_pn) -> bytes:
        """Serialize an Object-Centric Petri Net for storage.

        Args:
            oc_pn: Object-Centric Petri Net

        Returns:
            Pickled bytes
        """
        return pickle.dumps(oc_pn)

    def deserialize_oc_petri_net(self, data: bytes):
        """Deserialize an Object-Centric Petri Net from storage.

        Args:
            data: Pickled bytes

        Returns:
            Object-Centric Petri Net
        """
        return pickle.loads(data)

    def get_ocdfg_graph_data(self, ocel) -> dict[str, Any]:
        """Get OC-DFG as structured data for visualization.

        Returns graph data organized by object type for React frontend.

        The PM4Py ocel_discover_ocdfg returns a dictionary with keys:
        - 'edges': dict mapping (source, target, object_type) to frequency
        - 'activities_ot': dict mapping object_type to set of activities
        - 'start_activities': dict mapping object_type to dict of start activities
        - 'end_activities': dict mapping object_type to dict of end activities
        """
        try:
            ocdfg = self.get_object_centric_dfg(ocel)
            object_types = self.get_object_types(ocel)
            activities = self.get_activities(ocel)

            result = {
                "object_types": object_types,
                "activities": activities,
                "graphs_by_type": {},
            }

            # Extract edges dictionary
            edges_dict = ocdfg.get("edges", {}) if isinstance(ocdfg, dict) else {}
            start_activities = ocdfg.get("start_activities", {}) if isinstance(ocdfg, dict) else {}
            end_activities = ocdfg.get("end_activities", {}) if isinstance(ocdfg, dict) else {}
            activities_ot = ocdfg.get("activities_ot", {}) if isinstance(ocdfg, dict) else {}

            # Build graph per object type
            for ot in object_types:
                # Get activities for this object type
                ot_activities = list(activities_ot.get(ot, set())) if activities_ot else activities

                # Build nodes
                nodes = []
                activity_freq: dict[str, int] = {}
                for (src, tgt, edge_ot), freq in edges_dict.items():
                    if edge_ot == ot:
                        activity_freq[src] = activity_freq.get(src, 0) + freq
                        activity_freq[tgt] = activity_freq.get(tgt, 0) + freq

                for act in ot_activities:
                    nodes.append({
                        "id": f"{ot}_{act}",
                        "name": act,
                        "object_type": ot,
                        "frequency": activity_freq.get(act, 0),
                    })

                # Build edges
                edges = []
                for (src, tgt, edge_ot), freq in edges_dict.items():
                    if edge_ot == ot:
                        edges.append({
                            "source": src,
                            "target": tgt,
                            "object_type": ot,
                            "frequency": freq,
                        })

                # Get start/end activities for this object type
                ot_start = list(start_activities.get(ot, {}).keys()) if start_activities else []
                ot_end = list(end_activities.get(ot, {}).keys()) if end_activities else []

                result["graphs_by_type"][ot] = {
                    "object_type": ot,
                    "nodes": nodes,
                    "edges": edges,
                    "start_activities": ot_start,
                    "end_activities": ot_end,
                }

            return result
        except Exception as e:
            return {"error": str(e), "object_types": [], "activities": [], "graphs_by_type": {}}

    def get_objects_events_relationship(self, ocel) -> dict[str, Any]:
        """Get the event-object relationship summary.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Dictionary mapping object types to their event participation
        """
        object_types = self.get_object_types(ocel)
        result = {}

        for ot in object_types:
            try:
                # Flatten to see how many events relate to this object type
                flattened = self.flatten_to_traditional_log(ocel, ot)
                event_count = sum(len(trace) for trace in flattened)
                case_count = len(flattened)
                result[ot] = {
                    "event_count": event_count,
                    "case_count": case_count,
                }
            except Exception:
                result[ot] = {
                    "event_count": 0,
                    "case_count": 0,
                    "error": "Could not flatten",
                }

        return result


# Singleton instance
ocpm_service = OCPMService()
