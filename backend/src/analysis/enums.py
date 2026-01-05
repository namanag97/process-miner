"""Analysis layer enums.

Enums related to process mining algorithms and analysis methods.
"""

from enum import Enum


class MinerType(str, Enum):
    """Process mining algorithm types."""

    # Classic algorithms
    ALPHA = "alpha"
    ALPHA_PLUS = "alpha_plus"
    INDUCTIVE = "inductive"
    INDUCTIVE_INFREQUENT = "inductive_infrequent"
    HEURISTICS = "heuristics"
    DFG = "dfg"
    PERFORMANCE_DFG = "performance_dfg"

    # Advanced algorithms (Phase 1 PM4py integration)
    ILP = "ilp"  # Integer Linear Programming miner
    POWL = "powl"  # Partially Ordered Workflow Language
    BPMN_INDUCTIVE = "bpmn_inductive"  # Direct BPMN discovery
    DECLARE = "declare"  # Declarative constraints
    LOG_SKELETON = "log_skeleton"  # Log skeleton model
    TEMPORAL_PROFILE = "temporal_profile"  # Temporal constraints
    PREFIX_TREE = "prefix_tree"  # Prefix tree automaton
    TRANSITION_SYSTEM = "transition_system"  # State-based model
    BATCHES = "batches"  # Batch activity detection
    CORRELATION = "correlation"  # Correlation miner (no case ID)


class ModelFormat(str, Enum):
    """Process model formats."""

    PETRI_NET = "petri_net"
    PROCESS_TREE = "process_tree"
    DFG = "dfg"
    PERFORMANCE_DFG = "performance_dfg"
    BPMN = "bpmn"

    # Advanced formats (Phase 1 PM4py integration)
    POWL = "powl"
    DECLARE = "declare"
    LOG_SKELETON = "log_skeleton"
    TEMPORAL_PROFILE = "temporal_profile"
    PREFIX_TREE = "prefix_tree"
    TRANSITION_SYSTEM = "transition_system"
    BATCHES = "batches"


class ConformanceMethod(str, Enum):
    """Conformance checking methods."""

    TOKEN_REPLAY = "token_replay"
    ALIGNMENT = "alignment"

    # Declarative conformance (Phase 2 PM4py integration)
    DECLARE = "declare"  # DECLARE constraint conformance
    LOG_SKELETON = "log_skeleton"  # Log skeleton conformance
    TEMPORAL_PROFILE = "temporal_profile"  # Temporal constraint conformance
    FOOTPRINTS = "footprints"  # Footprints-based conformance
