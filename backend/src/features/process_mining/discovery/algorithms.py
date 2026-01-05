"""Process Mining Algorithms - PM4Py Algorithm Wrappers.

Contains individual mining algorithm implementations.
Each algorithm is a thin wrapper around PM4Py with standardized interface.
"""

import warnings
from typing import Any

import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.process_tree.obj import ProcessTree

from src.platform.core.enums import MinerType, ModelFormat
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class AlphaMiner:
    """Alpha Miner - Classic process discovery algorithm."""

    @staticmethod
    def discover(log: PM4PyLog) -> tuple[PetriNet, Marking, Marking]:
        """Discover Petri net using Alpha algorithm."""
        return pm4py.discover_petri_net_alpha(log)


class AlphaPlusMiner:
    """Alpha+ Miner - Handles short loops (DEPRECATED)."""

    @staticmethod
    def discover(log: PM4PyLog) -> tuple[PetriNet, Marking, Marking]:
        """Discover Petri net using Alpha+ algorithm.

        DEPRECATED: May be removed in future PM4Py versions.
        """
        warnings.warn(
            "Alpha+ miner is deprecated. Use Inductive Miner instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        try:
            return pm4py.discover_petri_net_alpha_plus(log)
        except AttributeError:
            logger.warning("alpha_plus_not_available_falling_back_to_alpha")
            return pm4py.discover_petri_net_alpha(log)


class InductiveMiner:
    """Inductive Miner - Recommended algorithm, produces sound process trees."""

    @staticmethod
    def discover(log: PM4PyLog, noise_threshold: float = 0.0) -> ProcessTree:
        """Discover process tree using Inductive Miner.

        Args:
            log: PM4Py event log
            noise_threshold: Filter infrequent behavior (0.0-1.0)
        """
        return pm4py.discover_process_tree_inductive(log, noise_threshold=noise_threshold)


class HeuristicsMiner:
    """Heuristics Miner - Frequency-based, handles noise well."""

    @staticmethod
    def discover(log: PM4PyLog) -> tuple[PetriNet, Marking, Marking]:
        """Discover Petri net using Heuristics Miner."""
        return pm4py.discover_petri_net_heuristics(log)


class DFGMiner:
    """DFG Miner - Directly-Follows Graph discovery."""

    @staticmethod
    def discover(log: PM4PyLog) -> tuple[dict, dict, dict]:
        """Discover DFG (frequency-based)."""
        return pm4py.discover_dfg(log)

    @staticmethod
    def discover_performance(log: PM4PyLog) -> tuple[dict, dict, dict]:
        """Discover DFG with performance metrics."""
        return pm4py.discover_performance_dfg(log)


class ILPMiner:
    """ILP Miner - Integer Linear Programming based discovery."""

    @staticmethod
    def discover(log: PM4PyLog, alpha: float = 1.0) -> tuple[PetriNet, Marking, Marking]:
        """Discover Petri net using ILP Miner.

        Args:
            log: PM4Py event log
            alpha: Noise filtering (0.0-1.0, default 1.0 = no filtering)
        """
        return pm4py.discover_petri_net_ilp(log, alpha=alpha)


class DeclarativeMiner:
    """Declarative miners - DECLARE, Log Skeleton, Temporal Profile."""

    @staticmethod
    def discover_declare(log: PM4PyLog) -> dict:
        """Discover DECLARE constraints."""
        return pm4py.discover_declare(log)

    @staticmethod
    def discover_log_skeleton(log: PM4PyLog, noise_threshold: float = 0.0) -> dict:
        """Discover Log Skeleton constraints."""
        return pm4py.discover_log_skeleton(log, noise_threshold=noise_threshold)

    @staticmethod
    def discover_temporal_profile(log: PM4PyLog) -> dict:
        """Discover Temporal Profile (activity timing statistics)."""
        return pm4py.discover_temporal_profile(log)


class AdvancedMiner:
    """Advanced mining algorithms - POWL, BPMN, Prefix Tree, etc."""

    @staticmethod
    def discover_powl(log: PM4PyLog) -> Any:
        """Discover POWL (Partially Ordered Workflow Language) model."""
        return pm4py.discover_powl(log)

    @staticmethod
    def discover_bpmn(log: PM4PyLog) -> Any:
        """Discover BPMN model directly."""
        return pm4py.discover_bpmn_inductive(log)

    @staticmethod
    def discover_prefix_tree(log: PM4PyLog) -> Any:
        """Discover Prefix Tree (Trie) for prediction."""
        return pm4py.discover_prefix_tree(log)

    @staticmethod
    def discover_transition_system(
        log: PM4PyLog, direction: str = "forward", window: int = 2
    ) -> Any:
        """Discover Transition System from activity windows."""
        return pm4py.discover_transition_system(log, direction=direction, window=window)

    @staticmethod
    def discover_batches(log: PM4PyLog) -> Any:
        """Detect batch activities."""
        return pm4py.discover_batches(log)

    @staticmethod
    def discover_correlation(
        log: PM4PyLog,
        activity_key: str = "concept:name",
        timestamp_key: str = "time:timestamp",
        start_timestamp_key: str | None = None,
    ) -> Any:
        """Correlation Miner - DFG without case IDs."""
        return pm4py.correlation_miner(
            log,
            activity_key=activity_key,
            timestamp_key=timestamp_key,
            start_timestamp_key=start_timestamp_key,
        )


def get_miner(miner_type: MinerType):
    """Get the appropriate miner class for a given type."""
    miner_map = {
        MinerType.ALPHA: AlphaMiner,
        MinerType.ALPHA_PLUS: AlphaPlusMiner,
        MinerType.INDUCTIVE: InductiveMiner,
        MinerType.INDUCTIVE_INFREQUENT: InductiveMiner,
        MinerType.HEURISTICS: HeuristicsMiner,
        MinerType.DFG: DFGMiner,
        MinerType.PERFORMANCE_DFG: DFGMiner,
        MinerType.ILP: ILPMiner,
    }
    return miner_map.get(miner_type)


def get_available_miners() -> list[dict[str, str]]:
    """Get list of available mining algorithms with metadata."""
    return [
        # Classic algorithms
        {
            "id": MinerType.INDUCTIVE.value,
            "name": "Inductive Miner",
            "description": "Recommended - produces sound, fitting process trees",
            "output_format": ModelFormat.PROCESS_TREE.value,
            "category": "classic",
        },
        {
            "id": MinerType.ALPHA.value,
            "name": "Alpha Miner",
            "description": "Classic algorithm, produces Petri nets",
            "output_format": ModelFormat.PETRI_NET.value,
            "category": "classic",
        },
        {
            "id": MinerType.ALPHA_PLUS.value,
            "name": "Alpha+ Miner (Deprecated)",
            "description": "⚠️ DEPRECATED: Use Inductive Miner instead.",
            "output_format": ModelFormat.PETRI_NET.value,
            "category": "classic",
            "deprecated": True,
        },
        {
            "id": MinerType.INDUCTIVE_INFREQUENT.value,
            "name": "Inductive Miner (Infrequent)",
            "description": "Handles noise, filters infrequent behavior",
            "output_format": ModelFormat.PROCESS_TREE.value,
            "category": "classic",
        },
        {
            "id": MinerType.HEURISTICS.value,
            "name": "Heuristics Miner",
            "description": "Frequency-based, handles noise well",
            "output_format": ModelFormat.PETRI_NET.value,
            "category": "classic",
        },
        {
            "id": MinerType.DFG.value,
            "name": "Directly-Follows Graph",
            "description": "Simple activity flow visualization",
            "output_format": ModelFormat.DFG.value,
            "category": "classic",
        },
        {
            "id": MinerType.PERFORMANCE_DFG.value,
            "name": "Performance DFG",
            "description": "DFG with timing metrics between activities",
            "output_format": ModelFormat.PERFORMANCE_DFG.value,
            "category": "classic",
        },
        # Advanced algorithms
        {
            "id": MinerType.ILP.value,
            "name": "ILP Miner",
            "description": "Integer Linear Programming - guaranteed sound Petri nets",
            "output_format": ModelFormat.PETRI_NET.value,
            "category": "advanced",
        },
        {
            "id": MinerType.POWL.value,
            "name": "POWL",
            "description": "Partially Ordered Workflow Language - handles concurrency",
            "output_format": ModelFormat.POWL.value,
            "category": "advanced",
        },
        {
            "id": MinerType.BPMN_INDUCTIVE.value,
            "name": "BPMN Inductive",
            "description": "Direct BPMN 2.0 discovery without conversion",
            "output_format": ModelFormat.BPMN.value,
            "category": "advanced",
        },
        {
            "id": MinerType.DECLARE.value,
            "name": "DECLARE",
            "description": "Declarative constraints (response, precedence, existence)",
            "output_format": ModelFormat.DECLARE.value,
            "category": "declarative",
        },
        {
            "id": MinerType.LOG_SKELETON.value,
            "name": "Log Skeleton",
            "description": "Activity occurrence and ordering constraints",
            "output_format": ModelFormat.LOG_SKELETON.value,
            "category": "declarative",
        },
        {
            "id": MinerType.TEMPORAL_PROFILE.value,
            "name": "Temporal Profile",
            "description": "Time statistics between activities for anomaly detection",
            "output_format": ModelFormat.TEMPORAL_PROFILE.value,
            "category": "declarative",
        },
        {
            "id": MinerType.PREFIX_TREE.value,
            "name": "Prefix Tree",
            "description": "Automaton of unique trace prefixes for prediction",
            "output_format": ModelFormat.PREFIX_TREE.value,
            "category": "advanced",
        },
        {
            "id": MinerType.TRANSITION_SYSTEM.value,
            "name": "Transition System",
            "description": "State-based model from activity windows",
            "output_format": ModelFormat.TRANSITION_SYSTEM.value,
            "category": "advanced",
        },
        {
            "id": MinerType.BATCHES.value,
            "name": "Batch Detection",
            "description": "Identifies activities executed in batches",
            "output_format": ModelFormat.BATCHES.value,
            "category": "analysis",
        },
        {
            "id": MinerType.CORRELATION.value,
            "name": "Correlation Miner",
            "description": "DFG discovery without case IDs using timestamps",
            "output_format": ModelFormat.DFG.value,
            "category": "advanced",
        },
    ]
