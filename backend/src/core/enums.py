"""Domain enums."""

from enum import Enum


class MinerType(str, Enum):
    """Process mining algorithm types."""

    ALPHA = "alpha"
    ALPHA_PLUS = "alpha_plus"
    INDUCTIVE = "inductive"
    INDUCTIVE_INFREQUENT = "inductive_infrequent"
    HEURISTICS = "heuristics"
    DFG = "dfg"


class ModelFormat(str, Enum):
    """Process model formats."""

    PETRI_NET = "petri_net"
    PROCESS_TREE = "process_tree"
    DFG = "dfg"
    BPMN = "bpmn"


class SourceFormat(str, Enum):
    """Event log source formats."""

    CSV = "csv"
    XES = "xes"
    OCEL_JSON = "ocel_json"
    OCEL_SQLITE = "ocel_sqlite"


class ConformanceMethod(str, Enum):
    """Conformance checking methods."""

    TOKEN_REPLAY = "token_replay"
    ALIGNMENT = "alignment"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
