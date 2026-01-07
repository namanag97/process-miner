"""Quality Metrics Service.

Service for computing and managing process model quality metrics.
"""

import time
from typing import Any
from uuid import uuid4

import pm4py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.process_mining.models import (
    ProcessModel,
    ProcessModelMetrics,
)
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class QualityService:
    """Service for computing process model quality metrics."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate_model(
        self,
        model_id: str,
        dataset_id: str,
        metrics: list[str] | None = None,
    ) -> dict[str, Any]:
        """Evaluate a process model with specified metrics.

        Args:
            model_id: Process model to evaluate
            dataset_id: Dataset to evaluate against
            metrics: List of metrics to compute. Default: all available
                     Options: 'fitness', 'precision', 'generalization', 'simplicity'

        Returns:
            Dictionary with computed metrics
        """
        if metrics is None:
            metrics = ["fitness", "precision", "generalization", "simplicity"]

        logger.info(
            "quality_evaluation_started",
            model_id=model_id,
            dataset_id=dataset_id,
            metrics=metrics,
        )

        start_time = time.perf_counter()

        # Load model and log
        model_data, model_format = await self._load_model(model_id)
        log = await self._load_event_log(dataset_id)

        if not model_data:
            raise ValueError(f"Model not found: {model_id}")

        results: dict[str, Any] = {}

        # Convert to Petri net if needed
        net, im, fm = await self._get_petri_net(model_data, model_format)

        # Compute requested metrics
        if "fitness" in metrics and net:
            try:
                fitness_result = self._compute_fitness(log, net, im, fm)
                results["fitness"] = fitness_result
            except Exception as e:
                logger.warning("fitness_computation_failed", error=str(e))
                results["fitness"] = {"error": str(e)}

        if "precision" in metrics and net:
            try:
                precision_result = self._compute_precision(log, net, im, fm)
                results["precision"] = precision_result
            except Exception as e:
                logger.warning("precision_computation_failed", error=str(e))
                results["precision"] = {"error": str(e)}

        if "generalization" in metrics and net:
            try:
                gen_result = self._compute_generalization(log, net, im, fm)
                results["generalization"] = gen_result
            except Exception as e:
                logger.warning("generalization_computation_failed", error=str(e))
                results["generalization"] = {"error": str(e)}

        if "simplicity" in metrics and net:
            try:
                simp_result = self._compute_simplicity(net)
                results["simplicity"] = simp_result
            except Exception as e:
                logger.warning("simplicity_computation_failed", error=str(e))
                results["simplicity"] = {"error": str(e)}

        computation_time_ms = int((time.perf_counter() - start_time) * 1000)

        # Store results
        await self._store_metrics(model_id, dataset_id, results, computation_time_ms)

        # Update quick metrics on model
        await self._update_model_quick_metrics(model_id, results)

        logger.info(
            "quality_evaluation_completed",
            model_id=model_id,
            computation_time_ms=computation_time_ms,
            results={k: v.get("value") if isinstance(v, dict) else v for k, v in results.items()},
        )

        return {
            "model_id": model_id,
            "dataset_id": dataset_id,
            "metrics": results,
            "computation_time_ms": computation_time_ms,
        }

    async def get_metrics(self, model_id: str) -> dict[str, Any] | None:
        """Get stored metrics for a model.

        Args:
            model_id: Process model identifier

        Returns:
            Stored metrics or None if not computed
        """
        query = select(ProcessModelMetrics).where(ProcessModelMetrics.model_id == model_id)
        result = await self.db.execute(query)
        metrics = result.scalar_one_or_none()

        if not metrics:
            return None

        return {
            "model_id": model_id,
            "dataset_id": metrics.dataset_id,
            "fitness": metrics.fitness,
            "precision": metrics.precision,
            "generalization": metrics.generalization,
            "simplicity": metrics.simplicity,
            "f_score": metrics.f_score,
            "computed_at": metrics.computed_at.isoformat() if metrics.computed_at else None,
            "computation_time_ms": metrics.computation_time_ms,
        }

    def _compute_fitness(
        self,
        log: Any,
        net: Any,
        im: Any,
        fm: Any,
    ) -> dict[str, Any]:
        """Compute fitness using token-based replay."""
        fitness_result = pm4py.fitness_token_based_replay(log, net, im, fm)

        return {
            "value": round(fitness_result.get("log_fitness", 0), 4),
            "average_trace_fitness": round(fitness_result.get("average_trace_fitness", 0), 4),
            "percentage_of_fitting_traces": round(
                fitness_result.get("percentage_of_fitting_traces", 0), 2
            ),
            "method": "token_replay",
        }

    def _compute_precision(
        self,
        log: Any,
        net: Any,
        im: Any,
        fm: Any,
    ) -> dict[str, Any]:
        """Compute precision using ETC precision."""
        try:
            precision = pm4py.precision_token_based_replay(log, net, im, fm)
            return {
                "value": round(precision, 4),
                "method": "token_replay",
            }
        except Exception:
            # Fallback to alignments-based if token replay fails
            try:
                precision = pm4py.precision_alignments(log, net, im, fm)
                return {
                    "value": round(precision, 4),
                    "method": "alignments",
                }
            except Exception as e:
                raise ValueError(f"Precision computation failed: {e}")

    def _compute_generalization(
        self,
        log: Any,
        net: Any,
        im: Any,
        fm: Any,
    ) -> dict[str, Any]:
        """Compute generalization using k-fold cross-validation approach."""
        try:
            # PM4Py's generalization metric
            gen = pm4py.generalization_tbr(log, net, im, fm)
            return {
                "value": round(gen, 4),
                "method": "token_replay",
            }
        except Exception as e:
            logger.warning("generalization_tbr_failed", error=str(e))
            # Generalization is often hard to compute, return placeholder
            return {
                "value": None,
                "method": "unavailable",
                "note": "Generalization metric not available for this model",
            }

    def _compute_simplicity(self, net: Any) -> dict[str, Any]:
        """Compute simplicity based on model structure."""
        try:
            simplicity = pm4py.simplicity_arc_degree(net)
            return {
                "value": round(simplicity, 4),
                "method": "arc_degree",
            }
        except Exception:
            # Manual computation
            places = len(net.places) if hasattr(net, "places") else 0
            transitions = len(net.transitions) if hasattr(net, "transitions") else 0
            arcs = len(net.arcs) if hasattr(net, "arcs") else 0

            # Simple inverse arc-to-node ratio
            nodes = places + transitions
            simplicity = 1 / (1 + arcs / max(nodes, 1)) if nodes > 0 else 0

            return {
                "value": round(simplicity, 4),
                "places": places,
                "transitions": transitions,
                "arcs": arcs,
                "method": "arc_ratio",
            }

    async def _load_model(self, model_id: str) -> tuple[Any, str]:
        """Load process model from database."""
        query = select(ProcessModel).where(ProcessModel.id == model_id)
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            return None, ""

        # Deserialize model
        if model.serialized_model:
            import pickle

            model_data = pickle.loads(model.serialized_model)
            return model_data, model.model_format or model.miner_type or "unknown"

        return None, ""

    async def _load_event_log(self, dataset_id: str) -> Any:
        """Load event log from database."""
        from src.features.process_mining.services.event_log_loader import EventLogLoader

        loader = EventLogLoader(self.db)
        return await loader.load_pm4py_log(dataset_id)

    async def _get_petri_net(
        self,
        model_data: Any,
        model_format: str,
    ) -> tuple[Any, Any, Any]:
        """Convert model to Petri net if needed."""
        if model_format == "petri_net":
            # Already a tuple of (net, im, fm)
            if isinstance(model_data, tuple) and len(model_data) == 3:
                return model_data

        if model_format == "process_tree":
            # Convert process tree to Petri net
            net, im, fm = pm4py.convert_to_petri_net(model_data)
            return net, im, fm

        # For other formats, try conversion
        try:
            net, im, fm = pm4py.convert_to_petri_net(model_data)
            return net, im, fm
        except Exception:
            return None, None, None

    async def _store_metrics(
        self,
        model_id: str,
        dataset_id: str,
        results: dict[str, Any],
        computation_time_ms: int,
    ) -> None:
        """Store computed metrics in database."""
        from datetime import datetime

        # Check if metrics already exist
        query = select(ProcessModelMetrics).where(ProcessModelMetrics.model_id == model_id)
        result = await self.db.execute(query)
        existing = result.scalar_one_or_none()

        def get_value(metric_result: dict | float | None) -> float | None:
            if isinstance(metric_result, dict):
                return metric_result.get("value")
            return metric_result

        fitness = get_value(results.get("fitness"))
        precision = get_value(results.get("precision"))
        generalization = get_value(results.get("generalization"))
        simplicity = get_value(results.get("simplicity"))

        # Compute F-score if we have both fitness and precision
        f_score = None
        if fitness is not None and precision is not None:
            if fitness + precision > 0:
                f_score = 2 * fitness * precision / (fitness + precision)

        if existing:
            existing.fitness = fitness
            existing.precision = precision
            existing.generalization = generalization
            existing.simplicity = simplicity
            existing.f_score = f_score
            existing.computation_time_ms = computation_time_ms
            existing.computed_at = datetime.utcnow()
        else:
            metrics = ProcessModelMetrics(
                id=str(uuid4()),
                model_id=model_id,
                dataset_id=dataset_id,
                fitness=fitness,
                precision=precision,
                generalization=generalization,
                simplicity=simplicity,
                f_score=f_score,
                computation_time_ms=computation_time_ms,
            )
            self.db.add(metrics)

        await self.db.commit()

    async def _update_model_quick_metrics(
        self,
        model_id: str,
        results: dict[str, Any],
    ) -> None:
        """Update quick-access metrics on the model itself."""
        query = select(ProcessModel).where(ProcessModel.id == model_id)
        result = await self.db.execute(query)
        model = result.scalar_one_or_none()

        if model:
            fitness_result = results.get("fitness")
            precision_result = results.get("precision")

            if isinstance(fitness_result, dict):
                model.fitness = fitness_result.get("value")
            if isinstance(precision_result, dict):
                model.precision = precision_result.get("value")

            await self.db.commit()
