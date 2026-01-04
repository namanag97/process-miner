"""OCPM Service - Object-Centric Process Mining using PM4Py.

Ported from: src/application/core/ocpm_service.py
Simplified: Direct PM4Py calls without domain layer ceremony.

Provides OCEL 2.0 support for Object-Centric Process Mining including:
- OCEL file reading (JSON, SQLite formats)
- Object-Centric Petri Net discovery
- Object-Centric DFG discovery
- Object graph analysis
- Flattening to traditional event logs

Serialization: Uses joblib for OC-PN persistence (safer than pickle).
Note: Consider removing OC-PN storage and re-discovering on-demand in future.
"""

import io
import os
import tempfile
from typing import Any

import joblib
import pm4py
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.ocel2 import (
    E2ORelation,
    O2ORelation,
    OCEL2Event,
    OCEL2EventType,
    OCEL2Object,
    OCEL2ObjectType,
)


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
        if source_format == "xmlocel":
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

        Uses joblib for safer serialization than pickle.

        Future improvement: Store OCEL data and re-discover OC-PN on-demand
        instead of storing the model itself (faster and safer).

        Args:
            oc_pn: Object-Centric Petri Net

        Returns:
            Serialized bytes (joblib format)
        """
        buffer = io.BytesIO()
        joblib.dump(oc_pn, buffer)
        return buffer.getvalue()

    def deserialize_oc_petri_net(self, data: bytes):
        """Deserialize an Object-Centric Petri Net from storage.

        Args:
            data: Serialized bytes (joblib format)

        Returns:
            Object-Centric Petri Net
        """
        buffer = io.BytesIO(data)
        return joblib.load(buffer)

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
                    nodes.append(
                        {
                            "id": f"{ot}_{act}",
                            "name": act,
                            "object_type": ot,
                            "frequency": activity_freq.get(act, 0),
                        }
                    )

                # Build edges
                edges = []
                for (src, tgt, edge_ot), freq in edges_dict.items():
                    if edge_ot == ot:
                        edges.append(
                            {
                                "source": src,
                                "target": tgt,
                                "object_type": ot,
                                "frequency": freq,
                            }
                        )

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

    # =========================================================================
    # Object Graphs (Phase 3 PM4py Integration)
    # =========================================================================

    def discover_object_graph(self, ocel, graph_type: str = "object_interaction") -> dict[str, Any]:
        """
        Discover object relationships graph of specified type.

        Args:
            ocel: PM4Py OCEL object
            graph_type: One of:
                - 'object_interaction': Objects that participate in same events
                - 'object_descendants': Parent-child object relationships
                - 'object_inheritance': Type hierarchy relationships
                - 'object_cobirth': Objects created in same event
                - 'object_codeath': Objects terminated in same event

        Returns:
            Object graph as dictionary with nodes and edges
        """
        try:
            graph = pm4py.discover_objects_graph(ocel, graph_type=graph_type)

            # Convert to frontend-friendly format
            nodes = set()
            edges = []

            for (src, tgt), data in graph.items():
                nodes.add(src)
                nodes.add(tgt)
                edges.append(
                    {
                        "source": src,
                        "target": tgt,
                        "weight": data if isinstance(data, (int, float)) else 1,
                    }
                )

            return {
                "graph_type": graph_type,
                "nodes": [{"id": n} for n in nodes],
                "edges": edges,
                "total_nodes": len(nodes),
                "total_edges": len(edges),
            }
        except Exception as e:
            return {"error": str(e), "graph_type": graph_type}

    def get_all_object_graphs(self, ocel) -> dict[str, Any]:
        """
        Get all available object graph types.

        Returns:
            Dictionary with all graph types and their data
        """
        graph_types = [
            "object_interaction",
            "object_descendants",
            "object_inheritance",
            "object_cobirth",
            "object_codeath",
        ]

        result = {}
        for gt in graph_types:
            result[gt] = self.discover_object_graph(ocel, gt)

        return result

    # =========================================================================
    # OCEL Enrichment (Phase 3 PM4py Integration)
    # =========================================================================

    def enrich_ocel_o2o(self, ocel):
        """
        Enrich OCEL with object-to-object relationships.

        Adds o2o relationships based on event participation patterns.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Enriched OCEL object
        """
        return pm4py.ocel_o2o_enrichment(ocel)

    def enrich_ocel_e2o_lifecycle(self, ocel):
        """
        Enrich OCEL with event-to-object lifecycle information.

        Adds lifecycle qualifiers (create, use, terminate) to e2o relationships.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Enriched OCEL object
        """
        return pm4py.ocel_e2o_lifecycle_enrichment(ocel)

    # =========================================================================
    # OCEL Sampling & Clustering (Phase 3 PM4py Integration)
    # =========================================================================

    def sample_ocel_objects(self, ocel, num_objects: int = 100, object_type: str | None = None):
        """
        Sample OCEL by selecting a subset of objects.

        Useful for processing large OCELs incrementally.

        Args:
            ocel: PM4Py OCEL object
            num_objects: Number of objects to sample
            object_type: Optional object type to filter by

        Returns:
            Sampled OCEL object
        """
        if object_type:
            return pm4py.sample_ocel_objects(
                ocel, num_entities=num_objects, object_type=object_type
            )
        return pm4py.sample_ocel_objects(ocel, num_entities=num_objects)

    def sample_ocel_connected_components(self, ocel, max_components: int = 10):
        """
        Sample OCEL by selecting connected components.

        Preserves complete object interactions within components.

        Args:
            ocel: PM4Py OCEL object
            max_components: Maximum number of connected components

        Returns:
            Sampled OCEL object
        """
        return pm4py.sample_ocel_connected_components(ocel, max_entities=max_components)

    def cluster_equivalent_ocel(self, ocel) -> dict[str, Any]:
        """
        Cluster OCEL events by equivalent object sets.

        Groups events that involve the same set of objects.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Clustering result with cluster assignments
        """
        try:
            clusters = pm4py.cluster_equivalent_ocel(ocel)
            return {
                "total_clusters": len(set(clusters.values())) if clusters else 0,
                "event_to_cluster": clusters,
            }
        except Exception as e:
            return {"error": str(e)}

    # =========================================================================
    # OCEL Utilities (Phase 3 PM4py Integration)
    # =========================================================================

    def drop_duplicates(self, ocel):
        """
        Remove duplicate events from OCEL.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            OCEL with duplicates removed
        """
        return pm4py.ocel_drop_duplicates(ocel)

    def merge_duplicates(self, ocel):
        """
        Merge duplicate events in OCEL.

        Combines duplicate events while preserving object relationships.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            OCEL with duplicates merged
        """
        return pm4py.ocel_merge_duplicates(ocel)

    def get_temporal_summary(self, ocel) -> dict[str, Any]:
        """
        Get temporal summary of OCEL.

        Returns time-based statistics about events and objects.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Temporal summary dictionary
        """
        try:
            summary = pm4py.ocel_temporal_summary(ocel)
            return dict(summary) if summary else {}
        except Exception as e:
            return {"error": str(e)}

    def get_objects_summary(self, ocel) -> dict[str, Any]:
        """
        Get detailed summary of objects in OCEL.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Objects summary with counts and attributes
        """
        try:
            summary = pm4py.ocel_objects_summary(ocel)
            # Convert to serializable format
            if hasattr(summary, "to_dict"):
                return summary.to_dict("records")
            return dict(summary) if summary else {}
        except Exception as e:
            return {"error": str(e)}

    def get_interactions_summary(self, ocel) -> dict[str, Any]:
        """
        Get summary of object interactions in OCEL.

        Shows how different object types interact with each other.

        Args:
            ocel: PM4Py OCEL object

        Returns:
            Interactions summary
        """
        try:
            summary = pm4py.ocel_objects_interactions_summary(ocel)
            # Convert to serializable format
            if hasattr(summary, "to_dict"):
                return summary.to_dict("records")
            return dict(summary) if summary else {}
        except Exception as e:
            return {"error": str(e)}

    async def persist_ocel_2_0(self, session: AsyncSession, ocel, source_log_id: str | None = None):
        """Persist OCEL 2.0 data into the relational OCEL2 tables.

        This enables deep object-centric queries without re-parsing the blob.
        """
        # 1. Create Event Types
        event_types = {}
        activities = self.get_activities(ocel)
        for act in activities:
            et = OCEL2EventType(name=act)
            session.add(et)
            event_types[act] = et

        # 2. Create Object Types
        object_types = {}
        ot_names = self.get_object_types(ocel)
        for ot in ot_names:
            obj_type = OCEL2ObjectType(name=ot)
            session.add(obj_type)
            object_types[ot] = obj_type

        await session.flush()  # Get IDs

        # 3. Create Objects
        objects = {}
        for ot in ot_names:
            obj_ids = self.get_objects_by_type(ocel, ot)
            for oid in obj_ids:
                obj = OCEL2Object(
                    object_type_id=object_types[ot].id,
                    object_id=oid,
                    attributes={},  # Could be populated from ocel.objects
                )
                session.add(obj)
                objects[oid] = obj

        await session.flush()

        # 4. Create Events and E2O Relations
        events_df = ocel.events
        for _, row in events_df.iterrows():
            activity = row["ocel:activity"]
            timestamp = row["ocel:timestamp"]
            row["ocel:eid"]

            event = OCEL2Event(
                event_type_id=event_types[activity].id,
                activity=activity,
                timestamp=timestamp,
                source_log_id=source_log_id,
                attributes={},  # Could be populated from other cols
            )
            session.add(event)

            # Relationships
            # In OCEL 2.0/PM4Py, related objects are in columns prefixed with ocel:type:
            for col in events_df.columns:
                if col.startswith("ocel:type:"):
                    col.replace("ocel:type:", "")
                    related_val = row[col]
                    if related_val and isinstance(related_val, (list, set)):
                        for r_oid in related_val:
                            if r_oid in objects:
                                rel = E2ORelation(
                                    event=event, object=objects[r_oid], qualifier="involved"
                                )
                                session.add(rel)
                    elif related_val and isinstance(related_val, str):
                        if related_val in objects:
                            rel = E2ORelation(
                                event=event, object=objects[related_val], qualifier="involved"
                            )
                            session.add(rel)

        # 5. O2O Relations
        try:
            o2o = pm4py.ocel_o2o_graph(ocel)
            for (src_oid, tgt_oid), _freq in o2o.items():
                if src_oid in objects and tgt_oid in objects:
                    rel = O2ORelation(
                        source_object_id=objects[src_oid].id,
                        target_object_id=objects[tgt_oid].id,
                        qualifier="related",
                    )
                    session.add(rel)
        except Exception:
            pass  # O2O might not be available

        await session.commit()


# Singleton instance
ocpm_service = OCPMService()
