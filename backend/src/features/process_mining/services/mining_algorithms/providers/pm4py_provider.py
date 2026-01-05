"""PM4Py Mining Provider Implementation.

Wraps PM4Py's 17 discovery algorithms in a standardized provider interface.
This is the default provider for the Process Discovery Platform.
"""

import time
from typing import Any

import pm4py
from pm4py.objects.log.obj import EventLog as PM4PyLog

from src.features.process_mining.enums import MinerType, ModelFormat
from src.features.process_mining.services.mining_algorithms.providers.base import (
    ComplexityEstimate,
    MiningProvider,
)
from src.platform.core.logging_config import get_logger, log_business_metric

logger = get_logger(__name__)


class Pm4pyProvider(MiningProvider):
    """PM4Py-based mining provider.

    Supports all PM4Py discovery algorithms with standardized interface.
    Handles algorithm dispatch, metrics logging, and error translation.
    """

    # Algorithm complexity profiles for resource estimation
    ALGORITHM_COMPLEXITY: dict[MinerType, str] = {
        MinerType.ALPHA: "O(n*a^2)",  # n=events, a=activities
        MinerType.ALPHA_PLUS: "O(n*a^2)",
        MinerType.INDUCTIVE: "O(n*a)",
        MinerType.INDUCTIVE_INFREQUENT: "O(n*a)",
        MinerType.HEURISTICS: "O(n*a^2)",
        MinerType.DFG: "O(n)",
        MinerType.PERFORMANCE_DFG: "O(n)",
        MinerType.ILP: "O(n*2^a)",  # Exponential in activities
        MinerType.POWL: "O(n*a)",
        MinerType.BPMN_INDUCTIVE: "O(n*a)",
        MinerType.DECLARE: "O(n*a^2)",
        MinerType.LOG_SKELETON: "O(n*a)",
        MinerType.TEMPORAL_PROFILE: "O(n*a^2)",
        MinerType.PREFIX_TREE: "O(n)",
        MinerType.TRANSITION_SYSTEM: "O(n*a)",
        MinerType.BATCHES: "O(n)",
        MinerType.CORRELATION: "O(n^2)",
    }

    # Output format mapping
    MINER_FORMATS: dict[MinerType, ModelFormat] = {
        MinerType.ALPHA: ModelFormat.PETRI_NET,
        MinerType.ALPHA_PLUS: ModelFormat.PETRI_NET,
        MinerType.INDUCTIVE: ModelFormat.PROCESS_TREE,
        MinerType.INDUCTIVE_INFREQUENT: ModelFormat.PROCESS_TREE,
        MinerType.HEURISTICS: ModelFormat.PETRI_NET,
        MinerType.DFG: ModelFormat.DFG,
        MinerType.PERFORMANCE_DFG: ModelFormat.PERFORMANCE_DFG,
        MinerType.ILP: ModelFormat.PETRI_NET,
        MinerType.POWL: ModelFormat.POWL,
        MinerType.BPMN_INDUCTIVE: ModelFormat.BPMN,
        MinerType.DECLARE: ModelFormat.DECLARE,
        MinerType.LOG_SKELETON: ModelFormat.LOG_SKELETON,
        MinerType.TEMPORAL_PROFILE: ModelFormat.TEMPORAL_PROFILE,
        MinerType.PREFIX_TREE: ModelFormat.PREFIX_TREE,
        MinerType.TRANSITION_SYSTEM: ModelFormat.TRANSITION_SYSTEM,
        MinerType.BATCHES: ModelFormat.BATCHES,
        MinerType.CORRELATION: ModelFormat.DFG,
    }

    @property
    def name(self) -> str:
        """Provider identifier."""
        return "pm4py"

    @property
    def version(self) -> str:
        """PM4Py version."""
        return pm4py.__version__

    def supported_miners(self) -> list[MinerType]:
        """Return all supported mining algorithms."""
        return list(self.MINER_FORMATS.keys())

    def supports_format(self) -> list[ModelFormat]:
        """Return all supported output formats."""
        return list(set(self.MINER_FORMATS.values()))

    def mine(
        self,
        pm4py_log: PM4PyLog,
        miner_type: MinerType,
        **params: Any,
    ) -> tuple[Any, ModelFormat]:
        """Execute mining algorithm.

        Args:
            pm4py_log: PM4Py EventLog object
            miner_type: Algorithm to use
            **params: Algorithm-specific parameters (e.g., noise_threshold)

        Returns:
            Tuple of (model_data, format)

        Raises:
            ValueError: If miner_type not supported
            RuntimeError: If PM4Py fails
        """
        if miner_type not in self.MINER_FORMATS:
            raise ValueError(f"Unsupported miner type: {miner_type}")

        logger.info(
            "pm4py_mining_started",
            miner_type=miner_type.value,
            traces=len(pm4py_log),
            params=params,
        )

        start_time = time.perf_counter()

        try:
            model_data = self._dispatch_mining(pm4py_log, miner_type, **params)
            model_format = self.MINER_FORMATS[miner_type]

            duration_ms = (time.perf_counter() - start_time) * 1000

            logger.info(
                "pm4py_mining_completed",
                miner_type=miner_type.value,
                model_format=model_format.value,
                duration_ms=round(duration_ms, 2),
            )

            log_business_metric(
                "provider_mining_time",
                round(duration_ms, 2),
                "ms",
                tags={"provider": self.name, "miner": miner_type.value},
            )

            return model_data, model_format

        except Exception as e:
            logger.error(
                "pm4py_mining_failed",
                miner_type=miner_type.value,
                error=str(e),
            )
            raise RuntimeError(f"PM4Py mining failed: {e}") from e

    def _dispatch_mining(
        self,
        log: PM4PyLog,
        miner_type: MinerType,
        **params: Any,
    ) -> Any:
        """Dispatch to appropriate PM4Py algorithm."""
        # Core algorithms
        if miner_type == MinerType.ALPHA:
            return pm4py.discover_petri_net_alpha(log)

        if miner_type == MinerType.ALPHA_PLUS:
            return pm4py.discover_petri_net_alpha_plus(log)

        if miner_type == MinerType.INDUCTIVE:
            return pm4py.discover_process_tree_inductive(log)

        if miner_type == MinerType.INDUCTIVE_INFREQUENT:
            noise = params.get("noise_threshold", 0.2)
            return pm4py.discover_process_tree_inductive(log, noise_threshold=noise)

        if miner_type == MinerType.HEURISTICS:
            return pm4py.discover_petri_net_heuristics(log)

        if miner_type == MinerType.DFG:
            return pm4py.discover_dfg(log)

        if miner_type == MinerType.PERFORMANCE_DFG:
            return pm4py.discover_performance_dfg(log)

        # Advanced algorithms
        if miner_type == MinerType.ILP:
            alpha = params.get("alpha", 1.0)
            return pm4py.discover_petri_net_ilp(log, alpha=alpha)

        if miner_type == MinerType.POWL:
            return pm4py.discover_powl(log)

        if miner_type == MinerType.BPMN_INDUCTIVE:
            return pm4py.discover_bpmn_inductive(log)

        if miner_type == MinerType.DECLARE:
            return pm4py.discover_declare(log)

        if miner_type == MinerType.LOG_SKELETON:
            noise = params.get("noise_threshold", 0.0)
            return pm4py.discover_log_skeleton(log, noise_threshold=noise)

        if miner_type == MinerType.TEMPORAL_PROFILE:
            return pm4py.discover_temporal_profile(log)

        if miner_type == MinerType.PREFIX_TREE:
            return pm4py.discover_prefix_tree(log)

        if miner_type == MinerType.TRANSITION_SYSTEM:
            direction = params.get("direction", "forward")
            window = params.get("window", 2)
            return pm4py.discover_transition_system(log, direction=direction, window=window)

        if miner_type == MinerType.BATCHES:
            return pm4py.discover_batches(log)

        if miner_type == MinerType.CORRELATION:
            return pm4py.correlation_miner(log)

        raise ValueError(f"Unhandled miner type: {miner_type}")

    def validate_input(self, pm4py_log: PM4PyLog, miner_type: MinerType) -> list[str]:
        """Validate input before mining.

        Returns list of error codes (empty if valid).
        Error codes use the DiscoveryErrorCode format.
        """
        errors: list[str] = []

        # Check empty log
        if not pm4py_log or len(pm4py_log) == 0:
            errors.append("ERR_DIS_001")  # EMPTY_EVENT_LOG
            return errors  # Can't validate further

        # Check first trace has required attributes
        first_trace = pm4py_log[0]
        if not first_trace:
            errors.append("ERR_DIS_001")
            return errors

        first_event = first_trace[0] if first_trace else None
        if first_event:
            # Check case ID (trace-level attribute 'concept:name' or iterate events)
            if "concept:name" not in first_event:
                errors.append("ERR_DIS_003")  # MISSING_ACTIVITY

            # Check timestamp
            if "time:timestamp" not in first_event:
                # Only some algorithms require timestamps
                if miner_type in [
                    MinerType.PERFORMANCE_DFG,
                    MinerType.TEMPORAL_PROFILE,
                    MinerType.BATCHES,
                ]:
                    errors.append("ERR_DIS_005")  # MISSING_TIMESTAMPS

        # Check activity count (warn but don't block)
        try:
            activities = set()
            for trace in pm4py_log:
                for event in trace:
                    activities.add(event.get("concept:name", ""))
            if len(activities) > 500:
                # This is a warning, not an error - we still return it
                # but caller decides if it's blocking
                errors.append("ERR_DIS_004")  # TOO_MANY_ACTIVITIES
        except Exception:
            pass  # Don't fail validation on count check

        return errors

    def estimate_complexity(self, pm4py_log: PM4PyLog, miner_type: MinerType) -> ComplexityEstimate:
        """Estimate resource requirements.

        Uses heuristics based on log size and algorithm complexity.
        """
        num_events = sum(len(trace) for trace in pm4py_log) if pm4py_log else 0

        # Estimate unique activities
        activities: set[str] = set()
        for trace in pm4py_log or []:
            for event in trace:
                activities.add(event.get("concept:name", ""))
        num_activities = len(activities)

        # Memory estimation (rough heuristics)
        base_memory_mb = 50  # Base PM4Py overhead
        event_memory_mb = (num_events * 200) / (1024 * 1024)  # ~200 bytes per event

        # Algorithm-specific multipliers
        multiplier = 1.0
        if miner_type in [MinerType.ILP]:
            multiplier = 2 ** min(num_activities, 10) / 100  # ILP is exponential
        elif miner_type in [MinerType.CORRELATION]:
            multiplier = num_events / 10000  # Quadratic in events
        elif miner_type in [MinerType.ALPHA, MinerType.HEURISTICS, MinerType.DECLARE]:
            multiplier = (num_activities**2) / 1000  # Quadratic in activities

        estimated_memory_mb = int(base_memory_mb + event_memory_mb * max(1, multiplier))

        # Time estimation (very rough)
        events_per_second = 5000  # Baseline for simple algorithms
        if miner_type in [MinerType.ILP]:
            events_per_second = 100
        elif miner_type in [MinerType.CORRELATION]:
            events_per_second = 500
        elif miner_type in [MinerType.DFG, MinerType.PREFIX_TREE]:
            events_per_second = 50000

        estimated_time_seconds = num_events / events_per_second

        # Should use worker for long operations or large memory
        should_use_worker = estimated_memory_mb > 500 or estimated_time_seconds > 10

        return ComplexityEstimate(
            estimated_memory_mb=estimated_memory_mb,
            estimated_time_seconds=round(estimated_time_seconds, 2),
            algorithm_complexity=self.ALGORITHM_COMPLEXITY.get(miner_type, "O(?)"),
            should_use_worker=should_use_worker,
        )
