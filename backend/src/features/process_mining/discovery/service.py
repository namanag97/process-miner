"""Process Mining Discovery Service - Orchestrates process discovery.

Main entry point for process mining operations. Uses modular components:
- algorithms.py: Individual mining algorithm implementations
- analysis.py: Statistics and analysis functions
- serialization.py: Model serialization/deserialization
- visualization/service.py: Visualization generation

Serialization: Uses joblib for model storage (safer than pickle, optimized for PM4Py objects).
"""

import time
from typing import Any

import pm4py
from pm4py.objects.petri_net.obj import Marking, PetriNet
from pm4py.objects.process_tree.obj import ProcessTree

from src.features.process_mining.enums import MinerType, ModelFormat
from src.features.process_mining.models import Dataset
from src.platform.core.logging_config import get_logger, log_business_metric

from .algorithms import (
    AdvancedMiner,
    AlphaMiner,
    AlphaPlusMiner,
    DeclarativeMiner,
    DFGMiner,
    HeuristicsMiner,
    ILPMiner,
    InductiveMiner,
    get_available_miners,
)
from .analysis import process_analyzer
from .serialization import model_serializer

logger = get_logger(__name__)


class MiningService:
    """Process Mining Service - Orchestrates PM4Py operations.

    Supports:
    - Discovery: Multiple algorithms (Alpha, Inductive, Heuristics, ILP, etc.)
    - Analysis: Variants, DFG, footprints, statistics
    - Serialization: Model storage and retrieval
    - Visualization: Petri net, DFG rendering (via visualization service)
    """

    # =========================================================================
    # Discovery Orchestration
    # =========================================================================

    def discover(
        self,
        event_log: Dataset,
        miner_type: MinerType = MinerType.INDUCTIVE,
    ) -> tuple[Any, ModelFormat]:
        """Discover a process model from an event log.

        Args:
            event_log: Dataset ORM object
            miner_type: Mining algorithm to use

        Returns:
            Tuple of (model_data, model_format)
        """
        logger.info(
            "discovery_algorithm_started",
            dataset_id=event_log.id,
            miner_type=miner_type.value,
            total_cases=event_log.total_cases,
            total_events=event_log.total_events,
        )
        start_time = time.perf_counter()

        # Load event log using fast DuckDB/Arrow path
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))

        conversion_ms = (time.perf_counter() - start_time) * 1000
        logger.debug("pm4py_log_conversion_fast", duration_ms=round(conversion_ms, 2))

        # Run discovery algorithm
        mining_start = time.perf_counter()
        result = self._run_discovery(pm4py_log, miner_type)

        mining_ms = (time.perf_counter() - mining_start) * 1000
        total_ms = (time.perf_counter() - start_time) * 1000

        logger.info(
            "discovery_algorithm_completed",
            miner_type=miner_type.value,
            model_format=result[1].value,
            mining_duration_ms=round(mining_ms, 2),
            total_duration_ms=round(total_ms, 2),
        )

        # Log business metrics
        log_business_metric(
            "discovery_time",
            round(mining_ms, 2),
            "ms",
            tags={
                "miner": miner_type.value,
                "events": event_log.total_events,
                "cases": event_log.total_cases,
            },
        )
        log_business_metric(
            "discovery_throughput",
            round(event_log.total_events / (mining_ms / 1000), 2) if mining_ms > 0 else 0,
            "events/sec",
            tags={"miner": miner_type.value},
        )

        return result

    def _run_discovery(self, pm4py_log, miner_type: MinerType) -> tuple[Any, ModelFormat]:
        """Run the appropriate discovery algorithm."""
        if miner_type == MinerType.ALPHA:
            return AlphaMiner.discover(pm4py_log), ModelFormat.PETRI_NET

        if miner_type == MinerType.ALPHA_PLUS:
            try:
                return AlphaPlusMiner.discover(pm4py_log), ModelFormat.PETRI_NET
            except Exception as e:
                logger.warning("alpha_plus_fallback_to_alpha", error=str(e))
                return AlphaMiner.discover(pm4py_log), ModelFormat.PETRI_NET

        if miner_type == MinerType.INDUCTIVE:
            return InductiveMiner.discover(pm4py_log), ModelFormat.PROCESS_TREE

        if miner_type == MinerType.INDUCTIVE_INFREQUENT:
            return InductiveMiner.discover(pm4py_log, noise_threshold=0.2), ModelFormat.PROCESS_TREE

        if miner_type == MinerType.HEURISTICS:
            return HeuristicsMiner.discover(pm4py_log), ModelFormat.PETRI_NET

        if miner_type == MinerType.DFG:
            return DFGMiner.discover(pm4py_log), ModelFormat.DFG

        if miner_type == MinerType.PERFORMANCE_DFG:
            return DFGMiner.discover_performance(pm4py_log), ModelFormat.PERFORMANCE_DFG

        if miner_type == MinerType.ILP:
            return ILPMiner.discover(pm4py_log), ModelFormat.PETRI_NET

        if miner_type == MinerType.POWL:
            return AdvancedMiner.discover_powl(pm4py_log), ModelFormat.POWL

        if miner_type == MinerType.BPMN_INDUCTIVE:
            return AdvancedMiner.discover_bpmn(pm4py_log), ModelFormat.BPMN

        if miner_type == MinerType.DECLARE:
            try:
                return DeclarativeMiner.discover_declare(pm4py_log), ModelFormat.DECLARE
            except (IndexError, KeyError, ValueError) as e:
                logger.warning("declare_discovery_failed", error=str(e))
                return {"constraints": [], "activities": [], "error": str(e)}, ModelFormat.DECLARE

        if miner_type == MinerType.LOG_SKELETON:
            return DeclarativeMiner.discover_log_skeleton(pm4py_log), ModelFormat.LOG_SKELETON

        if miner_type == MinerType.TEMPORAL_PROFILE:
            return DeclarativeMiner.discover_temporal_profile(
                pm4py_log
            ), ModelFormat.TEMPORAL_PROFILE

        if miner_type == MinerType.PREFIX_TREE:
            return AdvancedMiner.discover_prefix_tree(pm4py_log), ModelFormat.PREFIX_TREE

        if miner_type == MinerType.TRANSITION_SYSTEM:
            return AdvancedMiner.discover_transition_system(
                pm4py_log
            ), ModelFormat.TRANSITION_SYSTEM

        if miner_type == MinerType.BATCHES:
            return AdvancedMiner.discover_batches(pm4py_log), ModelFormat.BATCHES

        if miner_type == MinerType.CORRELATION:
            try:
                corr_result = AdvancedMiner.discover_correlation(pm4py_log)
                if isinstance(corr_result, tuple) and len(corr_result) >= 1:
                    dfg = corr_result[0]
                    start_act = pm4py.get_start_activities(pm4py_log)
                    end_act = pm4py.get_end_activities(pm4py_log)
                    return (dfg, start_act, end_act), ModelFormat.DFG
                return corr_result, ModelFormat.DFG
            except (IndexError, KeyError, TypeError, ValueError) as e:
                logger.warning("correlation_discovery_failed", error=str(e))
                return DFGMiner.discover(pm4py_log), ModelFormat.DFG

        raise ValueError(f"Unknown miner type: {miner_type}")

    # =========================================================================
    # Specialized Discovery Methods
    # =========================================================================

    def discover_ilp(self, event_log: Dataset, alpha: float = 1.0) -> tuple[Any, ModelFormat]:
        """ILP Miner with custom alpha parameter."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_ilp_started", dataset_id=event_log.id, alpha=alpha)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = ILPMiner.discover(pm4py_log, alpha=alpha), ModelFormat.PETRI_NET

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_ilp_completed", duration_ms=round(duration_ms, 2))
        return result

    def discover_powl(self, event_log: Dataset) -> tuple[Any, ModelFormat]:
        """POWL discovery."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_powl_started", dataset_id=event_log.id)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = AdvancedMiner.discover_powl(pm4py_log), ModelFormat.POWL

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_powl_completed", duration_ms=round(duration_ms, 2))
        return result

    def discover_bpmn(self, event_log: Dataset) -> tuple[Any, ModelFormat]:
        """BPMN discovery."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_bpmn_started", dataset_id=event_log.id)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = AdvancedMiner.discover_bpmn(pm4py_log), ModelFormat.BPMN

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_bpmn_completed", duration_ms=round(duration_ms, 2))
        return result

    def discover_declare(self, event_log: Dataset) -> tuple[Any, ModelFormat]:
        """DECLARE discovery."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_declare_started", dataset_id=event_log.id)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = DeclarativeMiner.discover_declare(pm4py_log), ModelFormat.DECLARE

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_declare_completed", duration_ms=round(duration_ms, 2))
        return result

    def discover_log_skeleton(
        self, event_log: Dataset, noise_threshold: float = 0.0
    ) -> tuple[Any, ModelFormat]:
        """Log Skeleton discovery."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_log_skeleton_started", dataset_id=event_log.id)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = (
            DeclarativeMiner.discover_log_skeleton(pm4py_log, noise_threshold),
            ModelFormat.LOG_SKELETON,
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_log_skeleton_completed", duration_ms=round(duration_ms, 2))
        return result

    def discover_temporal_profile(self, event_log: Dataset) -> tuple[Any, ModelFormat]:
        """Temporal Profile discovery."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_temporal_profile_started", dataset_id=event_log.id)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = DeclarativeMiner.discover_temporal_profile(pm4py_log), ModelFormat.TEMPORAL_PROFILE

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_temporal_profile_completed", duration_ms=round(duration_ms, 2))
        return result

    def discover_prefix_tree(self, event_log: Dataset) -> tuple[Any, ModelFormat]:
        """Prefix Tree discovery."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_prefix_tree_started", dataset_id=event_log.id)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = AdvancedMiner.discover_prefix_tree(pm4py_log), ModelFormat.PREFIX_TREE

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_prefix_tree_completed", duration_ms=round(duration_ms, 2))
        return result

    def discover_transition_system(
        self, event_log: Dataset, direction: str = "forward", window: int = 2
    ) -> tuple[Any, ModelFormat]:
        """Transition System discovery."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_transition_system_started", dataset_id=event_log.id)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = (
            AdvancedMiner.discover_transition_system(pm4py_log, direction, window),
            ModelFormat.TRANSITION_SYSTEM,
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_transition_system_completed", duration_ms=round(duration_ms, 2))
        return result

    def discover_batches(self, event_log: Dataset) -> tuple[Any, ModelFormat]:
        """Batch activity detection."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_batches_started", dataset_id=event_log.id)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = AdvancedMiner.discover_batches(pm4py_log), ModelFormat.BATCHES

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_batches_completed", duration_ms=round(duration_ms, 2))
        return result

    def discover_correlation(
        self,
        event_log: Dataset,
        activity_key: str = "concept:name",
        timestamp_key: str = "time:timestamp",
        start_timestamp_key: str | None = None,
    ) -> tuple[Any, ModelFormat]:
        """Correlation Miner - DFG without case IDs."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_correlation_started", dataset_id=event_log.id)
        start_time = time.perf_counter()

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = (
            AdvancedMiner.discover_correlation(
                pm4py_log, activity_key, timestamp_key, start_timestamp_key
            ),
            ModelFormat.DFG,
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info("discover_correlation_completed", duration_ms=round(duration_ms, 2))
        return result

    # =========================================================================
    # Petri Net Operations
    # =========================================================================

    def get_petri_net(
        self,
        event_log: Dataset,
        miner_type: MinerType = MinerType.INDUCTIVE,
    ) -> tuple[PetriNet, Marking, Marking]:
        """Get Petri net from discovery (converts process tree if needed)."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))

        if miner_type in [MinerType.ALPHA, MinerType.ALPHA_PLUS, MinerType.HEURISTICS]:
            model_data, _ = self.discover(event_log, miner_type)
            return model_data

        tree = InductiveMiner.discover(pm4py_log)
        return pm4py.convert_to_petri_net(tree)

    def tree_to_petri_net(self, tree: ProcessTree) -> tuple[PetriNet, Marking, Marking]:
        """Convert process tree to Petri net."""
        return pm4py.convert_to_petri_net(tree)

    # =========================================================================
    # Visualization (delegates to visualization service)
    # =========================================================================

    def visualize_petri_net(self, net: PetriNet, im: Marking, fm: Marking) -> bytes:
        """Generate SVG visualization of Petri net."""
        from src.features.process_mining.visualization.service import visualization_service

        return visualization_service.visualize_petri_net(net, im, fm)

    def visualize_dfg(self, dfg: dict, start_activities: dict, end_activities: dict) -> bytes:
        """Generate SVG visualization of DFG."""
        from src.features.process_mining.visualization.service import visualization_service

        return visualization_service.visualize_dfg(dfg, start_activities, end_activities)

    def visualize_model(self, model_data: Any, model_format: ModelFormat) -> bytes:
        """Generate visualization for any model type."""
        from src.features.process_mining.visualization.service import visualization_service

        return visualization_service.visualize_model(model_data, model_format)

    # =========================================================================
    # Analysis (delegates to process analyzer)
    # =========================================================================

    def get_start_activities(self, event_log: Dataset) -> dict[str, int]:
        """Get start activities with frequencies."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        return process_analyzer.get_start_activities(pm4py_log)

    def get_end_activities(self, event_log: Dataset) -> dict[str, int]:
        """Get end activities with frequencies."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        return process_analyzer.get_end_activities(pm4py_log)

    def get_variants(self, event_log: Dataset, top_n: int = 20) -> dict[str, Any]:
        """Get process variants with counts."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        return process_analyzer.get_variants(pm4py_log, top_n)

    def get_dfg_data(self, event_log: Dataset) -> dict[str, Any]:
        """Get DFG as structured data for visualization."""
        from src.features.process_mining.services.loader import event_log_loader

        dfg, start_activities, end_activities = event_log_loader.load_dfg(str(event_log.id))
        return process_analyzer.get_dfg_data(dfg, start_activities, end_activities)

    def get_dfg_data_with_performance(self, event_log: Dataset) -> dict[str, Any]:
        """Get DFG with performance metrics."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        return process_analyzer.get_dfg_with_performance(pm4py_log)

    def get_footprints(self, event_log: Dataset) -> dict[str, Any]:
        """Compute behavioral footprints."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        return process_analyzer.get_footprints(pm4py_log)

    def get_activity_statistics(self, event_log: Dataset) -> list[dict[str, Any]]:
        """Get detailed statistics for each activity."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        return process_analyzer.get_activity_statistics(pm4py_log)

    def calculate_variant_complexity(self, activity_trace: str) -> dict[str, Any]:
        """Calculate complexity metrics for a variant."""
        return process_analyzer.calculate_variant_complexity(activity_trace)

    def get_case_statistics(self, event_log: Dataset) -> dict[str, Any]:
        """Get case duration statistics."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        return process_analyzer.get_case_statistics(pm4py_log)

    # =========================================================================
    # Model Quality Evaluation
    # =========================================================================

    def evaluate_fitness(
        self, event_log: Dataset, net: PetriNet, im: Marking, fm: Marking
    ) -> dict[str, float]:
        """Evaluate model fitness using token replay."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        result = pm4py.fitness_token_based_replay(pm4py_log, net, im, fm)
        return {
            "fitness": result.get("average_trace_fitness", 0.0),
            "percentage_fit_traces": result.get("percentage_of_fitting_traces", 0.0),
        }

    def evaluate_precision(
        self, event_log: Dataset, net: PetriNet, im: Marking, fm: Marking
    ) -> float:
        """Evaluate model precision."""
        from src.features.process_mining.services.loader import event_log_loader

        pm4py_log = event_log_loader.load_as_pm4py_log(str(event_log.id))
        return pm4py.precision_token_based_replay(pm4py_log, net, im, fm)

    # =========================================================================
    # Serialization (delegates to model serializer)
    # =========================================================================

    def serialize_model(self, model_data: Any) -> bytes:
        """Serialize model for storage using joblib."""
        return model_serializer.serialize(model_data)

    def serialize_to_graph_json(
        self, model_data: Any, model_format: ModelFormat
    ) -> dict[str, Any] | None:
        """Serialize model to frontend-ready graph JSON."""
        return model_serializer.to_graph_json(model_data, model_format)

    def deserialize_model(self, data: bytes) -> Any:
        """Deserialize model from storage."""
        return model_serializer.deserialize(data)

    # =========================================================================
    # Helpers
    # =========================================================================

    def get_available_miners(self) -> list[dict[str, str]]:
        """Get list of available mining algorithms."""
        return get_available_miners()

    def _to_pm4py_log(self, event_log: Dataset):
        """DEPRECATED: Use event_log_loader.load_as_pm4py_log() instead."""
        import warnings

        warnings.warn(
            "MiningService._to_pm4py_log() is deprecated. "
            "Use event_log_loader.load_as_pm4py_log(dataset_id) instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        raise RuntimeError(
            "MiningService._to_pm4py_log() cannot access Dataset.cases due to lazy='raise'. "
            "Use event_log_loader.load_as_pm4py_log(dataset_id) instead."
        )

    def to_pm4py_dataframe(self, dataset_id: str, connection) -> "pd.DataFrame":
        """Convert EventLog to PM4Py-compatible DataFrame using direct SQL."""
        import pandas as pd

        start_time = time.perf_counter()

        query = """
            SELECT
                pc.case_id as "case:concept:name",
                pe.activity as "concept:name",
                pe.timestamp as "time:timestamp",
                pe.resource as "org:resource"
            FROM process_events pe
            JOIN process_cases pc ON pe.case_ref_id = pc.id
            WHERE pc.dataset_id = :dataset_id
            ORDER BY pc.case_id, pe.timestamp
        """

        df = pd.read_sql(query, connection, params={"dataset_id": dataset_id})

        if "time:timestamp" in df.columns:
            df["time:timestamp"] = pd.to_datetime(df["time:timestamp"])

        df = pm4py.format_dataframe(
            df,
            case_id="case:concept:name",
            activity_key="concept:name",
            timestamp_key="time:timestamp",
        )

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "sql_to_pm4py_dataframe",
            dataset_id=dataset_id,
            rows=len(df),
            duration_ms=round(duration_ms, 2),
        )

        return df

    def discover_from_dataframe(
        self, df: "pd.DataFrame", miner_type: MinerType = MinerType.INDUCTIVE
    ) -> tuple[Any, ModelFormat]:
        """Discover a process model from a PM4Py DataFrame."""
        start_time = time.perf_counter()

        if miner_type == MinerType.ALPHA:
            result = pm4py.discover_petri_net_alpha(df), ModelFormat.PETRI_NET
        elif miner_type == MinerType.ALPHA_PLUS:
            result = pm4py.discover_petri_net_alpha_plus(df), ModelFormat.PETRI_NET
        elif miner_type == MinerType.INDUCTIVE:
            result = pm4py.discover_process_tree_inductive(df), ModelFormat.PROCESS_TREE
        elif miner_type == MinerType.INDUCTIVE_INFREQUENT:
            result = (
                pm4py.discover_process_tree_inductive(df, noise_threshold=0.2),
                ModelFormat.PROCESS_TREE,
            )
        elif miner_type == MinerType.HEURISTICS:
            result = pm4py.discover_petri_net_heuristics(df), ModelFormat.PETRI_NET
        elif miner_type == MinerType.DFG:
            result = pm4py.discover_dfg(df), ModelFormat.DFG
        else:
            raise ValueError(f"Unknown miner type: {miner_type}")

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "discovery_from_dataframe",
            miner_type=miner_type.value,
            rows=len(df),
            duration_ms=round(duration_ms, 2),
        )

        return result

    # =========================================================================
    # High-Performance Methods (using EventLogLoader)
    # =========================================================================

    def discover_fast(
        self, dataset_id: str, miner_type: MinerType = MinerType.INDUCTIVE
    ) -> tuple[Any, ModelFormat]:
        """Discover using high-performance DataFrame loading."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("discover_fast_started", dataset_id=dataset_id, miner_type=miner_type.value)
        start_time = time.perf_counter()

        df = event_log_loader.load_as_dataframe(dataset_id)
        load_ms = (time.perf_counter() - start_time) * 1000
        logger.debug("discover_fast_data_loaded", duration_ms=round(load_ms, 2))

        result = self.discover_from_dataframe(df, miner_type)

        total_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "discover_fast_completed",
            dataset_id=dataset_id,
            miner_type=miner_type.value,
            total_duration_ms=round(total_ms, 2),
        )

        return result

    def get_dfg_fast(self, dataset_id: str) -> dict[str, Any]:
        """Get DFG using SQL-based computation."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("get_dfg_fast_started", dataset_id=dataset_id)
        start_time = time.perf_counter()

        dfg, start_activities, end_activities = event_log_loader.load_dfg(dataset_id)

        all_activities = set()
        for (source, target), _ in dfg.items():
            all_activities.add(source)
            all_activities.add(target)

        all_activities.update(start_activities.keys())
        all_activities.update(end_activities.keys())

        activity_freq = {}
        for (source, target), freq in dfg.items():
            activity_freq[source] = activity_freq.get(source, 0) + freq
            activity_freq[target] = activity_freq.get(target, 0) + freq

        total_freq = sum(dfg.values())

        nodes = [
            {
                "id": act,
                "name": act,
                "frequency": activity_freq.get(act, 0),
                "is_start": act in start_activities,
                "is_end": act in end_activities,
            }
            for act in all_activities
        ]

        edges = [
            {
                "source": source,
                "target": target,
                "frequency": freq,
                "probability": round(freq / total_freq, 4) if total_freq > 0 else 0,
            }
            for (source, target), freq in dfg.items()
        ]

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "get_dfg_fast_completed",
            dataset_id=dataset_id,
            nodes=len(nodes),
            edges=len(edges),
            duration_ms=round(duration_ms, 2),
        )

        return {
            "nodes": nodes,
            "edges": edges,
            "start_activities": start_activities,
            "end_activities": end_activities,
            "total_frequency": total_freq,
        }

    def get_variants_fast(self, dataset_id: str, top_n: int = 20) -> dict[str, Any]:
        """Get process variants using SQL-based computation."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("get_variants_fast_started", dataset_id=dataset_id, top_n=top_n)
        start_time = time.perf_counter()

        variants = event_log_loader.load_variants(dataset_id, top_k=top_n)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "get_variants_fast_completed",
            dataset_id=dataset_id,
            variants_returned=len(variants),
            duration_ms=round(duration_ms, 2),
        )

        return {
            "top_variants": [
                {
                    "variant_key": v["activity_trace"],
                    "case_count": v["case_count"],
                    "frequency_percent": v.get("frequency_percent", 0.0),
                    "avg_duration_seconds": v.get("avg_duration_seconds"),
                }
                for v in variants
            ],
            "total_variants": len(variants),
        }

    def get_statistics_fast(self, dataset_id: str) -> dict[str, Any]:
        """Get event log statistics using SQL-based computation."""
        from src.features.process_mining.services.loader import event_log_loader

        logger.info("get_statistics_fast_started", dataset_id=dataset_id)
        start_time = time.perf_counter()

        stats = event_log_loader.load_statistics(dataset_id)
        start_activities, end_activities = event_log_loader.load_start_end_activities(dataset_id)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "get_statistics_fast_completed",
            dataset_id=dataset_id,
            duration_ms=round(duration_ms, 2),
        )

        return {
            **stats,
            "start_activities": start_activities,
            "end_activities": end_activities,
        }


# Singleton instance
mining_service = MiningService()
