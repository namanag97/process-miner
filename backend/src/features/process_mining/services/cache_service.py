"""Cache Service for DFG and Variant Caching.

Pre-computes and caches DFG and variant data for performance.
"""

import json
import time
from collections import Counter
from typing import Any
from uuid import uuid4

import pm4py
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.process_mining.models import DFGCache, VariantCache
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class CacheService:
    """Service for DFG and Variant caching operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_compute_dfg(
        self,
        dataset_id: str,
        force_recompute: bool = False,
    ) -> dict[str, Any]:
        """Get cached DFG or compute and cache it.

        Args:
            dataset_id: Dataset identifier
            force_recompute: Bypass cache and recompute

        Returns:
            DFG data with edges, start/end activities
        """
        if not force_recompute:
            # Try to get from cache
            cache_query = select(DFGCache).where(DFGCache.dataset_id == dataset_id)
            result = await self.db.execute(cache_query)
            cached = result.scalar_one_or_none()

            if cached:
                logger.debug("dfg_cache_hit", dataset_id=dataset_id)
                return {
                    "edges": json.loads(cached.dfg_data),
                    "start_activities": json.loads(cached.start_activities),
                    "end_activities": json.loads(cached.end_activities),
                    "activity_counts": json.loads(cached.activity_counts)
                    if cached.activity_counts
                    else None,
                    "has_performance_data": cached.has_performance_data,
                    "from_cache": True,
                }

        # Compute DFG
        logger.info("dfg_cache_computing", dataset_id=dataset_id)
        start_time = time.perf_counter()

        try:
            dfg_data = await self._compute_dfg(dataset_id)
            computation_time_ms = int((time.perf_counter() - start_time) * 1000)

            # Store in cache
            await self._store_dfg_cache(dataset_id, dfg_data, computation_time_ms)

            dfg_data["from_cache"] = False
            return dfg_data

        except Exception as e:
            logger.error("dfg_computation_failed", dataset_id=dataset_id, error=str(e))
            raise

    async def get_or_compute_variants(
        self,
        dataset_id: str,
        force_recompute: bool = False,
    ) -> dict[str, Any]:
        """Get cached variants or compute and cache them.

        Args:
            dataset_id: Dataset identifier
            force_recompute: Bypass cache and recompute

        Returns:
            Variant data with sequences and counts
        """
        if not force_recompute:
            # Try to get from cache
            cache_query = select(VariantCache).where(VariantCache.dataset_id == dataset_id)
            result = await self.db.execute(cache_query)
            cached = result.scalar_one_or_none()

            if cached:
                logger.debug("variant_cache_hit", dataset_id=dataset_id)
                return {
                    "variants": json.loads(cached.variants_data),
                    "variant_count": cached.variant_count,
                    "top_variant_coverage": cached.top_variant_coverage,
                    "from_cache": True,
                }

        # Compute variants
        logger.info("variant_cache_computing", dataset_id=dataset_id)
        start_time = time.perf_counter()

        try:
            variant_data = await self._compute_variants(dataset_id)
            computation_time_ms = int((time.perf_counter() - start_time) * 1000)

            # Store in cache
            await self._store_variant_cache(dataset_id, variant_data, computation_time_ms)

            variant_data["from_cache"] = False
            return variant_data

        except Exception as e:
            logger.error("variant_computation_failed", dataset_id=dataset_id, error=str(e))
            raise

    async def invalidate_cache(self, dataset_id: str) -> None:
        """Invalidate all caches for a dataset.

        Called when dataset is updated or re-ingested.
        """
        await self.db.execute(delete(DFGCache).where(DFGCache.dataset_id == dataset_id))
        await self.db.execute(delete(VariantCache).where(VariantCache.dataset_id == dataset_id))
        await self.db.commit()
        logger.info("cache_invalidated", dataset_id=dataset_id)

    async def precompute_caches(self, dataset_id: str) -> dict[str, Any]:
        """Pre-compute all caches for a dataset.

        Called during ingestion workflow for optimal performance.
        """
        logger.info("precompute_caches_started", dataset_id=dataset_id)

        results = {}

        try:
            dfg_result = await self.get_or_compute_dfg(dataset_id, force_recompute=True)
            results["dfg"] = {
                "edge_count": len(dfg_result.get("edges", [])),
                "cached": True,
            }
        except Exception as e:
            results["dfg"] = {"error": str(e)}

        try:
            variant_result = await self.get_or_compute_variants(dataset_id, force_recompute=True)
            results["variants"] = {
                "variant_count": variant_result.get("variant_count", 0),
                "cached": True,
            }
        except Exception as e:
            results["variants"] = {"error": str(e)}

        logger.info("precompute_caches_completed", dataset_id=dataset_id, results=results)
        return results

    async def _compute_dfg(self, dataset_id: str) -> dict[str, Any]:
        """Compute DFG from dataset events."""
        from src.features.process_mining.services.event_log_loader import EventLogLoader

        loader = EventLogLoader(self.db)
        log = await loader.load_pm4py_log(dataset_id)

        # Compute frequency DFG
        dfg, start_activities, end_activities = pm4py.discover_dfg(log)

        # Convert to serializable format
        edges = [[source, target, frequency] for (source, target), frequency in dfg.items()]

        # Get activity frequencies
        activity_counts = Counter()
        for trace in log:
            for event in trace:
                activity_counts[event["concept:name"]] += 1

        return {
            "edges": edges,
            "start_activities": dict(start_activities),
            "end_activities": dict(end_activities),
            "activity_counts": dict(activity_counts),
            "has_performance_data": False,
        }

    async def _compute_variants(self, dataset_id: str) -> dict[str, Any]:
        """Compute variant representation from dataset events."""
        from src.features.process_mining.services.event_log_loader import EventLogLoader

        loader = EventLogLoader(self.db)
        log = await loader.load_pm4py_log(dataset_id)

        # Get variants
        variants = pm4py.get_variants(log)

        # Convert to list format
        total_cases = sum(count for count in variants.values())
        variant_list = []
        for variant_tuple, count in sorted(variants.items(), key=lambda x: x[1], reverse=True):
            variant_list.append(
                {
                    "sequence": list(variant_tuple),
                    "count": count,
                    "percentage": round(count / total_cases * 100, 2) if total_cases > 0 else 0,
                }
            )

        # Compute statistics
        top_variant_coverage = variant_list[0]["percentage"] if variant_list else 0
        top_5_coverage = sum(v["percentage"] for v in variant_list[:5]) if variant_list else 0
        avg_length = (
            sum(len(v["sequence"]) * v["count"] for v in variant_list) / total_cases
            if total_cases > 0
            else 0
        )

        return {
            "variants": variant_list,
            "variant_count": len(variant_list),
            "top_variant_coverage": top_variant_coverage,
            "top_5_coverage": top_5_coverage,
            "avg_variant_length": round(avg_length, 2),
        }

    async def _store_dfg_cache(
        self,
        dataset_id: str,
        dfg_data: dict[str, Any],
        computation_time_ms: int,
    ) -> None:
        """Store DFG in cache table."""
        # Delete existing cache
        await self.db.execute(delete(DFGCache).where(DFGCache.dataset_id == dataset_id))

        cache_entry = DFGCache(
            id=str(uuid4()),
            dataset_id=dataset_id,
            dfg_data=json.dumps(dfg_data["edges"]),
            start_activities=json.dumps(dfg_data["start_activities"]),
            end_activities=json.dumps(dfg_data["end_activities"]),
            activity_counts=json.dumps(dfg_data.get("activity_counts"))
            if dfg_data.get("activity_counts")
            else None,
            has_performance_data=dfg_data.get("has_performance_data", False),
            edge_count=len(dfg_data["edges"]),
            activity_count=len(dfg_data.get("activity_counts", {})),
            computation_time_ms=computation_time_ms,
        )

        self.db.add(cache_entry)
        await self.db.commit()

    async def _store_variant_cache(
        self,
        dataset_id: str,
        variant_data: dict[str, Any],
        computation_time_ms: int,
    ) -> None:
        """Store variants in cache table."""
        # Delete existing cache
        await self.db.execute(delete(VariantCache).where(VariantCache.dataset_id == dataset_id))

        cache_entry = VariantCache(
            id=str(uuid4()),
            dataset_id=dataset_id,
            variants_data=json.dumps(variant_data["variants"]),
            variant_count=variant_data["variant_count"],
            top_variant_coverage=variant_data.get("top_variant_coverage"),
            top_5_coverage=variant_data.get("top_5_coverage"),
            avg_variant_length=variant_data.get("avg_variant_length"),
            computation_time_ms=computation_time_ms,
        )

        self.db.add(cache_entry)
        await self.db.commit()
