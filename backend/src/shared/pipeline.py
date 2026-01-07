"""Computation Pipeline - DAG-based Analysis Execution.

Model process mining analyses as a directed acyclic graph (DAG).
Enables caching, parallel execution, and resumability.

Usage:
    pipeline = (
        Pipeline("my-analysis")
        .add_node("load", LoadDatasetNode(dataset_id="ds_123"))
        .add_node("filter", FilterNode(conditions=[...]))
        .add_node("discover", DiscoverNode(algorithm="inductive"))
        .connect("load", "filter")
        .connect("filter", "discover")
    )

    result = await pipeline.execute()
"""

import asyncio
import hashlib
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Generic, TypeVar

from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


# =============================================================================
# Pipeline Nodes
# =============================================================================


@dataclass
class NodeResult:
    """Result of a pipeline node execution."""

    node_id: str
    success: bool
    data: Any = None
    error: str | None = None
    duration_ms: int = 0
    cached: bool = False


class PipelineNode(ABC, Generic[T]):
    """Base class for pipeline nodes."""

    @abstractmethod
    async def execute(self, inputs: dict[str, Any]) -> T:
        """Execute the node with inputs from upstream nodes."""
        ...

    def cache_key(self, inputs: dict[str, Any]) -> str:
        """Generate cache key for this node's execution."""
        node_data = {
            "class": self.__class__.__name__,
            "params": self.__dict__,
            "inputs_hash": hashlib.md5(
                json.dumps(inputs, sort_keys=True, default=str).encode()
            ).hexdigest(),
        }
        return hashlib.sha256(json.dumps(node_data, sort_keys=True).encode()).hexdigest()[:16]


@dataclass
class LoadDatasetNode(PipelineNode):
    """Load a dataset for processing."""

    dataset_id: str

    async def execute(self, inputs: dict[str, Any]) -> dict:
        from src.features.process_mining.services.loader import load_event_log

        log = await load_event_log(self.dataset_id)
        return {"event_log": log, "dataset_id": self.dataset_id}


@dataclass
class FilterNode(PipelineNode):
    """Apply filters to an event log."""

    conditions: list[dict[str, Any]] = field(default_factory=list)

    async def execute(self, inputs: dict[str, Any]) -> dict:
        event_log = inputs.get("event_log")
        if not event_log:
            raise ValueError("FilterNode requires event_log input")

        # Apply PM4Py filtering

        filtered = event_log
        for _condition in self.conditions:
            # Apply each filter condition
            pass  # Implement actual filtering

        return {"event_log": filtered, "filter_applied": True}


@dataclass
class DiscoverNode(PipelineNode):
    """Discover process model from event log."""

    algorithm: str = "inductive"
    params: dict[str, Any] = field(default_factory=dict)

    async def execute(self, inputs: dict[str, Any]) -> dict:
        event_log = inputs.get("event_log")
        if not event_log:
            raise ValueError("DiscoverNode requires event_log input")

        # Run discovery
        from pm4py import discover_petri_net_inductive

        if self.algorithm == "inductive":
            net, im, fm = discover_petri_net_inductive(event_log)
            return {"net": net, "initial_marking": im, "final_marking": fm}

        raise ValueError(f"Unknown algorithm: {self.algorithm}")


@dataclass
class ConformanceNode(PipelineNode):
    """Check conformance between log and model."""

    async def execute(self, inputs: dict[str, Any]) -> dict:
        event_log = inputs.get("event_log")
        net = inputs.get("net")

        if not event_log or not net:
            raise ValueError("ConformanceNode requires event_log and net inputs")

        from pm4py.conformance import conformance_diagnostics_token_based_replay

        diagnostics = conformance_diagnostics_token_based_replay(
            event_log, net, inputs["initial_marking"], inputs["final_marking"]
        )

        return {"conformance": diagnostics}


@dataclass
class AnalyticsNode(PipelineNode):
    """Compute analytics on event log."""

    metrics: list[str] = field(default_factory=lambda: ["variants", "throughput"])

    async def execute(self, inputs: dict[str, Any]) -> dict:
        event_log = inputs.get("event_log")
        if not event_log:
            raise ValueError("AnalyticsNode requires event_log input")

        results = {}

        if "variants" in self.metrics:
            from pm4py.statistics.variants import get

            results["variants"] = get.get_variants(event_log)

        return {"analytics": results}


# =============================================================================
# Pipeline Execution
# =============================================================================


@dataclass
class Pipeline:
    """Computation pipeline with DAG execution."""

    name: str
    nodes: dict[str, PipelineNode] = field(default_factory=dict)
    edges: list[tuple[str, str]] = field(default_factory=list)
    cache: dict[str, Any] | None = None

    def add_node(self, node_id: str, node: PipelineNode) -> "Pipeline":
        """Add a node to the pipeline."""
        self.nodes[node_id] = node
        return self

    def connect(self, from_node: str, to_node: str) -> "Pipeline":
        """Connect two nodes."""
        if from_node not in self.nodes:
            raise ValueError(f"Node {from_node} not found")
        if to_node not in self.nodes:
            raise ValueError(f"Node {to_node} not found")
        self.edges.append((from_node, to_node))
        return self

    def _get_execution_order(self) -> list[str]:
        """Topological sort of nodes."""
        in_degree = dict.fromkeys(self.nodes, 0)
        adjacency = {node_id: [] for node_id in self.nodes}

        for from_node, to_node in self.edges:
            adjacency[from_node].append(to_node)
            in_degree[to_node] += 1

        # Kahn's algorithm
        queue = [n for n, d in in_degree.items() if d == 0]
        order = []

        while queue:
            node = queue.pop(0)
            order.append(node)
            for neighbor in adjacency[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(order) != len(self.nodes):
            raise ValueError("Pipeline contains a cycle")

        return order

    def _get_inputs_for_node(
        self,
        node_id: str,
        results: dict[str, NodeResult],
    ) -> dict[str, Any]:
        """Collect inputs for a node from upstream results."""
        inputs = {}
        for from_node, to_node in self.edges:
            if to_node == node_id and from_node in results:
                inputs.update(results[from_node].data or {})
        return inputs

    async def execute(
        self,
        cache: dict[str, Any] | None = None,
    ) -> dict[str, NodeResult]:
        """Execute the pipeline in topological order."""
        self.cache = cache or {}
        results: dict[str, NodeResult] = {}

        execution_order = self._get_execution_order()
        logger.info("pipeline_start", name=self.name, nodes=execution_order)

        for node_id in execution_order:
            node = self.nodes[node_id]
            inputs = self._get_inputs_for_node(node_id, results)

            # Check cache
            cache_key = node.cache_key(inputs)
            if cache_key in self.cache:
                logger.info("cache_hit", node=node_id)
                results[node_id] = NodeResult(
                    node_id=node_id,
                    success=True,
                    data=self.cache[cache_key],
                    cached=True,
                )
                continue

            # Execute node
            start = datetime.utcnow()
            try:
                data = await node.execute(inputs)
                duration = int((datetime.utcnow() - start).total_seconds() * 1000)

                results[node_id] = NodeResult(
                    node_id=node_id,
                    success=True,
                    data=data,
                    duration_ms=duration,
                )

                # Cache result
                self.cache[cache_key] = data
                logger.info("node_complete", node=node_id, duration_ms=duration)

            except Exception as e:
                duration = int((datetime.utcnow() - start).total_seconds() * 1000)
                results[node_id] = NodeResult(
                    node_id=node_id,
                    success=False,
                    error=str(e),
                    duration_ms=duration,
                )
                logger.error("node_failed", node=node_id, error=str(e))
                break  # Stop on failure

        return results

    async def execute_parallel(
        self,
        cache: dict[str, Any] | None = None,
    ) -> dict[str, NodeResult]:
        """Execute independent nodes in parallel."""
        self.cache = cache or {}
        results: dict[str, NodeResult] = {}

        # Build dependency graph
        in_degree = dict.fromkeys(self.nodes, 0)
        dependents = {node_id: [] for node_id in self.nodes}

        for from_node, to_node in self.edges:
            in_degree[to_node] += 1
            dependents[from_node].append(to_node)

        # Process in waves
        ready = {n for n, d in in_degree.items() if d == 0}

        while ready:
            # Execute all ready nodes in parallel
            tasks = []
            for node_id in ready:
                node = self.nodes[node_id]
                inputs = self._get_inputs_for_node(node_id, results)
                tasks.append(self._execute_node(node_id, node, inputs))

            wave_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results and find new ready nodes
            next_ready = set()
            for result in wave_results:
                if isinstance(result, Exception):
                    continue
                results[result.node_id] = result

                if result.success:
                    for dependent in dependents[result.node_id]:
                        in_degree[dependent] -= 1
                        if in_degree[dependent] == 0:
                            next_ready.add(dependent)

            ready = next_ready

        return results

    async def _execute_node(
        self,
        node_id: str,
        node: PipelineNode,
        inputs: dict[str, Any],
    ) -> NodeResult:
        """Execute a single node."""
        cache_key = node.cache_key(inputs)

        if cache_key in self.cache:
            return NodeResult(
                node_id=node_id,
                success=True,
                data=self.cache[cache_key],
                cached=True,
            )

        start = datetime.utcnow()
        try:
            data = await node.execute(inputs)
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            self.cache[cache_key] = data
            return NodeResult(
                node_id=node_id,
                success=True,
                data=data,
                duration_ms=duration,
            )
        except Exception as e:
            duration = int((datetime.utcnow() - start).total_seconds() * 1000)
            return NodeResult(
                node_id=node_id,
                success=False,
                error=str(e),
                duration_ms=duration,
            )
