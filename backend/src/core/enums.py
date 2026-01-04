"""Domain enums."""

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

    # Declarative conformance (Phase 2 PM4py integration)
    DECLARE = "declare"  # DECLARE constraint conformance
    LOG_SKELETON = "log_skeleton"  # Log skeleton conformance
    TEMPORAL_PROFILE = "temporal_profile"  # Temporal constraint conformance
    FOOTPRINTS = "footprints"  # Footprints-based conformance


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


# =============================================================================
# Job-Centric Architecture Enums
# =============================================================================


class JobType(str, Enum):
    """Types of async jobs for unified tracking."""

    INGESTION = "ingestion"  # Dataset parsing and ingestion
    VALIDATION = "validation"  # File validation and column detection
    DISCOVERY = "discovery"  # Process model discovery
    CONFORMANCE = "conformance"  # Conformance checking
    PREDICTION_TRAINING = "prediction_training"  # ML model training
    OCEL_IMPORT = "ocel_import"  # OCEL file import
    SIMULATION = "simulation"  # Process simulation
    FILTERING = "filtering"  # Dataset filtering
    FLATTEN = "flatten"  # OCEL flattening to traditional log
    ANALYSIS = "analysis"  # General analysis (bottleneck, etc.)


class JobStatus(str, Enum):
    """Job lifecycle states."""

    # Primary status values
    QUEUED = "queued"  # Job created, waiting to start
    RUNNING = "running"  # Job in progress
    COMPLETED = "completed"  # Job finished successfully
    FAILED = "failed"  # Job failed with error
    CANCELLED = "cancelled"  # Job cancelled by user

    # Legacy alias (for backward compatibility with existing code/data)
    PENDING = "pending"  # Legacy: prefer QUEUED for new code


class EntityType(str, Enum):
    """Types of entities created by jobs."""

    DATASET = "dataset"
    MODEL = "model"
    ANALYSIS = "analysis"
    PREDICTOR = "predictor"
    OCEL_LOG = "ocel_log"
    CONFORMANCE_RESULT = "conformance_result"
