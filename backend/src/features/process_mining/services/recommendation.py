"""Recommendation Service - The Prescriptive Engine.

This service implements the "Cognitive Engine" (Pillar 1) of the Master Plan.
It takes "Signals" (Predictions, Violations) and converts them into
"Prescriptions" (Actions) using a rule-based engine.
"""

import json
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.features.process_mining.models import Recommendation
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)


class ActionType(str, Enum):
    """Types of actions that can be recommended."""

    REASSIGN_RESOURCE = "reassign_resource"
    PRIORITIZE_CASE = "prioritize_case"
    SEND_NOTIFICATION = "send_notification"
    TRIGGER_WEBHOOK = "trigger_webhook"


class SignalType(str, Enum):
    """Types of signals that trigger recommendations."""

    PREDICTED_DELAY = "predicted_delay"
    CONFORMANCE_VIOLATION = "conformance_violation"
    RESOURCE_OVERLOAD = "resource_overload"


@dataclass
class ActionRecommendation:
    """A generated recommendation (in-memory)."""

    action_type: ActionType
    params: dict[str, Any]
    priority: str = "medium"
    reason: str = ""


@dataclass
class Rule:
    """A prescriptive rule."""

    name: str
    signal_type: SignalType
    condition: Callable[[dict], bool]
    action_generator: Callable[[dict], ActionRecommendation]


class RecommendationService:
    """
    Service for generating and managing prescriptive recommendations.
    """

    def __init__(self):
        # In a real system, these might be loaded from a DB or config file
        self._rules: list[Rule] = self._load_default_rules()

    def _load_default_rules(self) -> list[Rule]:
        """Load the default set of prescriptive rules."""
        rules = []

        # Rule 1: extensive delay -> Prioritize
        rules.append(
            Rule(
                name="High Delay Risk",
                signal_type=SignalType.PREDICTED_DELAY,
                condition=lambda data: data.get("remaining_time_seconds", 0)
                > 86400 * 2,  # > 2 days
                action_generator=lambda data: ActionRecommendation(
                    action_type=ActionType.PRIORITIZE_CASE,
                    params={"priority_level": "high"},
                    priority="high",
                    reason=f"Predicted delay of {round(data.get('remaining_time_seconds', 0) / 3600, 1)} hours exceeds threshold.",
                ),
            )
        )

        # Rule 2: Resource overload -> Reassign
        rules.append(
            Rule(
                name="Resource Overload",
                signal_type=SignalType.RESOURCE_OVERLOAD,
                condition=lambda data: data.get("utilization", 0) > 0.9,
                action_generator=lambda data: ActionRecommendation(
                    action_type=ActionType.REASSIGN_RESOURCE,
                    params={"current_resource": data.get("resource"), "strategy": "least_busy"},
                    priority="medium",
                    reason=f"Resource {data.get('resource')} is at {int(data.get('utilization', 0) * 100)}% utilization.",
                ),
            )
        )

        return rules

    async def generate_recommendations(
        self,
        session: AsyncSession,
        dataset_id: str,
        case_id: str,
        signal_type: SignalType,
        signal_data: dict[str, Any],
        persist: bool = True,
    ) -> list[Recommendation]:
        """
        Generate recommendations based on a signal.

        Args:
            session: DB session
            dataset_id: Dataset ID
            case_id: Case ID
            signal_type: The type of signal (e.g. PREDICTED_DELAY)
            signal_data: Context data for the signal (e.g. prediction result)
            persist: Whether to save to DB

        Returns:
            List of Recommendation objects
        """
        logger.info("generating_recommendations", case_id=case_id, signal=signal_type.value)

        matches = []
        for rule in self._rules:
            if rule.signal_type == signal_type:
                try:
                    if rule.condition(signal_data):
                        matches.append(rule.action_generator(signal_data))
                except Exception as e:
                    logger.error("rule_evaluation_failed", rule=rule.name, error=str(e))

        recommendations = []
        for match in matches:
            rec = Recommendation(
                dataset_id=dataset_id,
                case_id=case_id,
                signal_type=signal_type.value,
                signal_data_json=json.dumps(signal_data),
                action_type=match.action_type.value,
                action_params_json=json.dumps(match.params),
                priority=match.priority,
                state="pending",
            )
            recommendations.append(rec)

        if persist and recommendations:
            session.add_all(recommendations)
            await session.flush()
            logger.info("recommendations_persisted", count=len(recommendations))

        return recommendations

    async def get_recommendations_for_case(
        self, session: AsyncSession, case_id: str
    ) -> list[Recommendation]:
        """Get all recommendations for a specific case."""
        stmt = (
            select(Recommendation)
            .where(Recommendation.case_id == case_id)
            .order_by(Recommendation.created_at.desc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())


recommendation_service = RecommendationService()
