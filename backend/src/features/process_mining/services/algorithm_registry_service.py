"""Algorithm Registry Service.

Service for querying algorithm metadata and providing recommendations.
"""

import json
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.features.process_mining.models import Algorithm, AlgorithmParameter, Dataset
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class AlgorithmRegistryService:
    """Service for algorithm registry operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_algorithms(
        self,
        category: str | None = None,
        include_disabled: bool = False,
    ) -> list[dict[str, Any]]:
        """List all algorithms with metadata.
        
        Args:
            category: Filter by category (discovery, conformance, declarative, enhancement)
            include_disabled: Include disabled algorithms
            
        Returns:
            List of algorithm metadata dictionaries
        """
        query = (
            select(Algorithm)
            .options(selectinload(Algorithm.parameters))
            .order_by(Algorithm.display_order)
        )
        
        if not include_disabled:
            query = query.where(Algorithm.is_enabled == True)  # noqa: E712
        
        if category:
            query = query.where(Algorithm.category == category)
        
        result = await self.db.execute(query)
        algorithms = result.scalars().all()
        
        return [self._algorithm_to_dict(a) for a in algorithms]

    async def get_algorithm(self, algorithm_id: str) -> dict[str, Any] | None:
        """Get single algorithm with parameters.
        
        Args:
            algorithm_id: Algorithm identifier (e.g., 'inductive')
            
        Returns:
            Algorithm details or None if not found
        """
        query = (
            select(Algorithm)
            .options(selectinload(Algorithm.parameters))
            .where(Algorithm.id == algorithm_id)
        )
        
        result = await self.db.execute(query)
        algorithm = result.scalar_one_or_none()
        
        if not algorithm:
            return None
        
        return self._algorithm_to_dict(algorithm, include_parameters=True)

    async def get_algorithm_parameters(self, algorithm_id: str) -> list[dict[str, Any]]:
        """Get parameters for an algorithm.
        
        Args:
            algorithm_id: Algorithm identifier
            
        Returns:
            List of parameter definitions
        """
        query = (
            select(AlgorithmParameter)
            .where(AlgorithmParameter.algorithm_id == algorithm_id)
            .order_by(AlgorithmParameter.display_order)
        )
        
        result = await self.db.execute(query)
        parameters = result.scalars().all()
        
        return [self._parameter_to_dict(p) for p in parameters]

    async def recommend_algorithm(
        self,
        dataset_id: str,
        use_case: str | None = None,
    ) -> dict[str, Any]:
        """Recommend algorithms based on dataset characteristics.
        
        Args:
            dataset_id: Dataset to analyze
            use_case: Optional use case hint ('quick', 'quality', 'noisy', 'declarative')
            
        Returns:
            Recommendation with primary and alternatives
        """
        # Get dataset stats
        dataset_query = select(Dataset).where(Dataset.id == dataset_id)
        result = await self.db.execute(dataset_query)
        dataset = result.scalar_one_or_none()
        
        if not dataset:
            return {
                "primary": "inductive",
                "alternatives": ["dfg", "heuristics"],
                "reason": "Dataset not found, using default recommendation.",
            }
        
        event_count = dataset.total_events or 0
        activity_count = dataset.total_activities or 0
        
        # Determine log size tier
        if event_count <= 10000:
            size_tier = "small"
        elif event_count <= 100000:
            size_tier = "medium"
        else:
            size_tier = "large"
        
        # Get all enabled algorithms
        algorithms = await self.list_algorithms()
        
        # Scoring logic
        scores: dict[str, float] = {}
        for algo in algorithms:
            score = 0.0
            algo_id = algo["id"]
            
            # Check event count limits
            max_events = algo.get("max_recommended_events") or float("inf")
            if event_count > max_events:
                score -= 50  # Heavy penalty for exceeding limits
            
            # Check activity count limits
            max_activities = algo.get("max_recommended_activities") or float("inf")
            if activity_count > max_activities:
                score -= 30
            
            # Boost recommended algorithms
            if algo.get("is_recommended"):
                score += 20
            
            # Use case specific boosts
            if use_case == "quick":
                score += algo.get("speed_rating", 3) * 5
            elif use_case == "quality":
                if algo.get("guarantees_soundness"):
                    score += 15
            elif use_case == "noisy":
                score += algo.get("noise_tolerance", 3) * 5
            elif use_case == "declarative":
                if algo.get("category") == "declarative":
                    score += 30
            else:
                # Default: balance speed and quality
                score += algo.get("speed_rating", 3) * 3
                score += algo.get("noise_tolerance", 3) * 2
                if algo.get("guarantees_soundness"):
                    score += 10
            
            scores[algo_id] = score
        
        # Sort by score
        sorted_algos = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary = sorted_algos[0][0] if sorted_algos else "inductive"
        alternatives = [a[0] for a in sorted_algos[1:4]]
        
        # Build reason
        reasons = []
        if size_tier == "small":
            reasons.append(f"small dataset ({event_count:,} events)")
        elif size_tier == "large":
            reasons.append(f"large dataset ({event_count:,} events)")
        else:
            reasons.append(f"medium dataset ({event_count:,} events)")
        
        if use_case:
            reasons.append(f"optimizing for {use_case}")
        
        return {
            "primary": primary,
            "alternatives": alternatives,
            "reason": f"Recommended based on: {', '.join(reasons)}",
            "dataset_stats": {
                "event_count": event_count,
                "activity_count": activity_count,
                "size_tier": size_tier,
            },
        }

    def _algorithm_to_dict(
        self,
        algorithm: Algorithm,
        include_parameters: bool = False,
    ) -> dict[str, Any]:
        """Convert Algorithm model to dictionary."""
        result = {
            "id": algorithm.id,
            "name": algorithm.name,
            "description": algorithm.description,
            "category": algorithm.category,
            "output_format": algorithm.output_format,
            "requires_external": algorithm.requires_external,
            "external_dependency": algorithm.external_dependency,
            "guarantees_soundness": algorithm.guarantees_soundness,
            "noise_tolerance": algorithm.noise_tolerance,
            "speed_rating": algorithm.speed_rating,
            "complexity_class": algorithm.complexity_class,
            "max_recommended_events": algorithm.max_recommended_events,
            "max_recommended_activities": algorithm.max_recommended_activities,
            "is_recommended": algorithm.is_recommended,
        }
        
        if include_parameters and algorithm.parameters:
            result["parameters"] = [
                self._parameter_to_dict(p) for p in algorithm.parameters
            ]
        
        return result

    def _parameter_to_dict(self, param: AlgorithmParameter) -> dict[str, Any]:
        """Convert AlgorithmParameter model to dictionary."""
        result = {
            "name": param.param_name,
            "type": param.param_type,
            "default_value": param.default_value,
            "display_name": param.display_name,
            "description": param.description,
            "is_advanced": param.is_advanced,
            "is_required": param.is_required,
        }
        
        if param.min_value is not None:
            result["min_value"] = param.min_value
        if param.max_value is not None:
            result["max_value"] = param.max_value
        if param.enum_values:
            try:
                result["enum_values"] = json.loads(param.enum_values)
            except json.JSONDecodeError:
                result["enum_values"] = []
        
        return result
