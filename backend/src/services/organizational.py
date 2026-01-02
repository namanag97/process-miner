"""Organizational Mining Service - Social Network Analysis using PM4Py.

Provides handover network, working together network, resource similarity,
role discovery, and resource profiling.
"""

import time
from collections import defaultdict
from typing import Any

import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class OrganizationalService:
    """Organizational mining service using PM4Py."""

    def discover_handover_network(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Discover handover of work network."""
        logger.info("discovering_handover_network", traces=len(pm4py_log))
        start = time.perf_counter()

        try:
            hw_values = pm4py.discover_handover_of_work_network(pm4py_log)
        except Exception as e:
            logger.warning(
                "organizational_mining_fallback",
                algorithm="discover_handover_of_work_network",
                fallback_to="manual_handover_computation",
                reason=str(e)[:200],
            )
            hw_values = self._compute_handover_manually(pm4py_log)

        nodes, edges = self._network_to_graph(hw_values)
        metrics = self._compute_network_metrics(nodes, edges)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "handover_network_discovered",
            nodes=len(nodes),
            edges=len(edges),
            duration_ms=round(duration, 2),
        )

        return {"network_type": "handover", "nodes": nodes, "edges": edges, "metrics": metrics}

    def discover_working_together_network(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Discover working together network."""
        logger.info("discovering_working_together_network", traces=len(pm4py_log))
        start = time.perf_counter()

        try:
            wt_values = pm4py.discover_working_together_network(pm4py_log)
        except Exception as e:
            logger.warning(
                "organizational_mining_fallback",
                algorithm="discover_working_together_network",
                fallback_to="manual_working_together_computation",
                reason=str(e)[:200],
            )
            wt_values = self._compute_working_together_manually(pm4py_log)

        nodes, edges = self._network_to_graph(wt_values)
        metrics = self._compute_network_metrics(nodes, edges)

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "working_together_network_discovered",
            nodes=len(nodes),
            edges=len(edges),
            duration_ms=round(duration, 2),
        )

        return {
            "network_type": "working_together",
            "nodes": nodes,
            "edges": edges,
            "metrics": metrics,
        }

    def discover_resource_similarity(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Discover activity-based resource similarity."""
        logger.info("discovering_resource_similarity", traces=len(pm4py_log))
        start = time.perf_counter()

        resource_activities = defaultdict(set)
        for trace in pm4py_log:
            for event in trace:
                resource = event.get("org:resource")
                activity = event.get("concept:name", "")
                if resource:
                    resource_activities[resource].add(activity)

        resources = list(resource_activities.keys())
        edges = []
        for i, r1 in enumerate(resources):
            for r2 in resources[i + 1 :]:
                a1, a2 = resource_activities[r1], resource_activities[r2]
                if a1 and a2:
                    similarity = len(a1 & a2) / len(a1 | a2)
                    if similarity > 0.1:
                        edges.append(
                            {
                                "source": r1,
                                "target": r2,
                                "weight": round(similarity, 4),
                                "label": "similar",
                            }
                        )

        nodes = [
            {"id": r, "label": r, "type": "resource", "weight": len(resource_activities[r])}
            for r in resources
        ]
        metrics = {"total_resources": len(resources), "similarity_edges": len(edges)}

        duration = (time.perf_counter() - start) * 1000
        logger.info(
            "resource_similarity_discovered",
            nodes=len(nodes),
            edges=len(edges),
            duration_ms=round(duration, 2),
        )

        return {
            "network_type": "resource_similarity",
            "nodes": nodes,
            "edges": edges,
            "metrics": metrics,
        }

    def discover_roles(self, pm4py_log: PM4PyLog) -> list[dict[str, Any]]:
        """Discover organizational roles based on activity patterns."""
        logger.info("discovering_roles", traces=len(pm4py_log))
        start = time.perf_counter()

        resource_activities = defaultdict(lambda: defaultdict(int))
        for trace in pm4py_log:
            for event in trace:
                resource = event.get("org:resource")
                activity = event.get("concept:name", "")
                if resource:
                    resource_activities[resource][activity] += 1

        activity_signatures = {}
        for resource, activities in resource_activities.items():
            top_activities = frozenset(
                sorted(activities.keys(), key=activities.get, reverse=True)[:5]
            )
            activity_signatures[resource] = top_activities

        role_groups = defaultdict(list)
        for resource, signature in activity_signatures.items():
            role_groups[signature].append(resource)

        roles = []
        for i, (signature, resources) in enumerate(role_groups.items()):
            roles.append(
                {
                    "role_id": f"role_{i + 1}",
                    "resources": resources,
                    "activities": list(signature),
                }
            )

        duration = (time.perf_counter() - start) * 1000
        logger.info("roles_discovered", count=len(roles), duration_ms=round(duration, 2))
        return roles

    def get_resource_profile(self, pm4py_log: PM4PyLog, resource: str) -> dict[str, Any]:
        """Get detailed profile for a specific resource."""
        logger.info("getting_resource_profile", resource=resource)
        start = time.perf_counter()

        activities = defaultdict(int)
        timestamps = []
        processing_times = []

        for trace in pm4py_log:
            for i, event in enumerate(trace):
                if event.get("org:resource") == resource:
                    activities[event.get("concept:name", "")] += 1
                    if "time:timestamp" in event:
                        timestamps.append(event["time:timestamp"])
                    if (
                        i < len(trace) - 1
                        and "time:timestamp" in event
                        and "time:timestamp" in trace[i + 1]
                    ):
                        processing_times.append(
                            (
                                trace[i + 1]["time:timestamp"] - event["time:timestamp"]
                            ).total_seconds()
                        )

        profile = {
            "resource": resource,
            "total_events": sum(activities.values()),
            "activities": dict(activities),
            "avg_processing_time_seconds": round(sum(processing_times) / len(processing_times), 2)
            if processing_times
            else 0,
            "first_activity": min(timestamps).isoformat() if timestamps else None,
            "last_activity": max(timestamps).isoformat() if timestamps else None,
        }

        duration = (time.perf_counter() - start) * 1000
        logger.info("resource_profile_computed", duration_ms=round(duration, 2))
        return profile

    def get_resource_workload(self, pm4py_log: PM4PyLog) -> dict[str, Any]:
        """Get workload distribution across resources."""
        logger.info("getting_resource_workload", traces=len(pm4py_log))
        start = time.perf_counter()

        workload = defaultdict(int)
        for trace in pm4py_log:
            for event in trace:
                resource = event.get("org:resource")
                if resource:
                    workload[resource] += 1

        total = sum(workload.values())
        avg = total / len(workload) if workload else 0

        duration = (time.perf_counter() - start) * 1000
        logger.info("workload_computed", resources=len(workload), duration_ms=round(duration, 2))

        return {"workload": dict(workload), "avg_events_per_resource": round(avg, 2)}

    def _compute_handover_manually(self, pm4py_log: PM4PyLog) -> dict:
        """Compute handover network manually."""
        handover = defaultdict(int)
        for trace in pm4py_log:
            for i in range(len(trace) - 1):
                r1 = trace[i].get("org:resource")
                r2 = trace[i + 1].get("org:resource")
                if r1 and r2 and r1 != r2:
                    handover[(r1, r2)] += 1
        return handover

    def _compute_working_together_manually(self, pm4py_log: PM4PyLog) -> dict:
        """Compute working together network manually."""
        working_together = defaultdict(int)
        for trace in pm4py_log:
            resources = set(e.get("org:resource") for e in trace if e.get("org:resource"))
            for r1 in resources:
                for r2 in resources:
                    if r1 < r2:
                        working_together[(r1, r2)] += 1
        return working_together

    def _network_to_graph(self, network_values: dict) -> tuple[list, list]:
        """Convert network values to nodes and edges."""
        all_resources = set()
        edges = []
        for (r1, r2), weight in network_values.items():
            all_resources.add(r1)
            all_resources.add(r2)
            edges.append({"source": r1, "target": r2, "weight": float(weight), "label": None})

        nodes = [{"id": r, "label": r, "type": "resource", "weight": 1.0} for r in all_resources]
        return nodes, edges

    def _compute_network_metrics(self, nodes: list, edges: list) -> dict:
        """Compute basic network metrics."""
        return {
            "node_count": len(nodes),
            "edge_count": len(edges),
            "density": round(2 * len(edges) / (len(nodes) * (len(nodes) - 1)), 4)
            if len(nodes) > 1
            else 0,
        }


organizational_service = OrganizationalService()
