"""Prediction Service - Mock ML predictions."""

from statistics import mean
from typing import Any, Dict, List

from src.domain.entities import EventLog, ProcessCase


class PredictionService:
    """
    Prediction Service - Mock ML-based predictions.
    Provides remaining time, next activity, and anomaly detection.
    In production, this would integrate with actual ML models.
    """

    def predict_remaining_time(
        self,
        event_log: EventLog,
        case: ProcessCase,
    ) -> Dict[str, Any]:
        """
        Predict remaining time for an ongoing case.
        Uses historical case durations as a simple baseline.
        """
        # Get current progress through the case
        current_activities = case.activities
        if not current_activities:
            return {"predicted_seconds": 0, "confidence": 0.0}

        # Find similar completed cases
        similar_cases = []
        for completed_case in event_log.cases:
            if (
                completed_case.duration
                and completed_case.case_id != case.case_id
                and self._is_prefix_match(current_activities, completed_case.activities)
            ):
                similar_cases.append(completed_case)

        if not similar_cases:
            # No similar cases, use average
            all_durations = [c.duration.total_seconds for c in event_log.cases if c.duration]
            avg_duration = mean(all_durations) if all_durations else 0
            current_duration = case.duration.total_seconds if case.duration else 0
            remaining = max(0, avg_duration - current_duration)

            return {
                "predicted_seconds": remaining,
                "confidence": 0.3,
                "method": "global_average",
            }

        # Calculate remaining time based on similar cases
        remaining_times = []
        for similar in similar_cases:
            similar_duration = similar.duration.total_seconds
            # Estimate remaining based on progress ratio
            progress = len(current_activities) / len(similar.activities)
            remaining = similar_duration * (1 - progress)
            remaining_times.append(max(0, remaining))

        predicted = mean(remaining_times)
        confidence = min(0.9, 0.5 + len(similar_cases) * 0.05)

        return {
            "predicted_seconds": predicted,
            "confidence": confidence,
            "method": "similar_cases",
            "similar_cases_count": len(similar_cases),
        }

    def predict_next_activity(
        self,
        event_log: EventLog,
        case: ProcessCase,
    ) -> Dict[str, Any]:
        """
        Predict the next most likely activity.
        Uses simple frequency-based prediction.
        """
        current_activities = case.activities
        if not current_activities:
            # Predict start activity
            start_activities = {}
            for c in event_log.cases:
                if c.activities:
                    first = c.activities[0]
                    start_activities[first] = start_activities.get(first, 0) + 1

            if start_activities:
                predicted = max(start_activities, key=start_activities.get)
                total = sum(start_activities.values())
                confidence = start_activities[predicted] / total
                return {
                    "predicted_activity": predicted,
                    "confidence": confidence,
                    "alternatives": [
                        {"activity": a, "probability": c / total}
                        for a, c in sorted(start_activities.items(), key=lambda x: -x[1])[:3]
                    ],
                }
            return {"predicted_activity": None, "confidence": 0.0}

        # Find what typically follows the current activity sequence
        last_activity = current_activities[-1]
        next_activities = {}

        for c in event_log.cases:
            acts = c.activities
            for i, act in enumerate(acts[:-1]):
                if act == last_activity:
                    next_act = acts[i + 1]
                    next_activities[next_act] = next_activities.get(next_act, 0) + 1

        if not next_activities:
            return {"predicted_activity": None, "confidence": 0.0}

        total = sum(next_activities.values())
        predicted = max(next_activities, key=next_activities.get)
        confidence = next_activities[predicted] / total

        return {
            "predicted_activity": predicted,
            "confidence": confidence,
            "alternatives": [
                {"activity": a, "probability": c / total}
                for a, c in sorted(next_activities.items(), key=lambda x: -x[1])[:5]
            ],
        }

    def detect_anomalies(
        self,
        event_log: EventLog,
        threshold: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalous cases based on duration and variant.
        Uses simple statistical methods (mock ML).
        """
        anomalies = []

        # Calculate duration statistics
        durations = [c.duration.total_seconds for c in event_log.cases if c.duration]

        if not durations:
            return []

        avg_duration = mean(durations)
        std_duration = (sum((d - avg_duration) ** 2 for d in durations) / len(durations)) ** 0.5

        # Find rare variants
        variant_counts = {}
        for c in event_log.cases:
            key = c.variant_key
            variant_counts[key] = variant_counts.get(key, 0) + 1

        total_cases = len(event_log.cases)
        rare_threshold = 0.01  # 1% of cases

        for case in event_log.cases:
            is_anomaly = False
            reasons = []

            # Check duration anomaly
            if case.duration:
                duration = case.duration.total_seconds
                z_score = abs(duration - avg_duration) / std_duration if std_duration > 0 else 0

                if z_score > threshold:
                    is_anomaly = True
                    reasons.append(
                        {
                            "type": "duration",
                            "score": z_score,
                            "value": duration,
                            "expected": avg_duration,
                        }
                    )

            # Check variant rarity
            variant_count = variant_counts.get(case.variant_key, 0)
            if variant_count / total_cases < rare_threshold:
                is_anomaly = True
                reasons.append(
                    {
                        "type": "rare_variant",
                        "frequency": variant_count / total_cases,
                        "variant": case.variant_key[:100],  # Truncate long variants
                    }
                )

            if is_anomaly:
                anomalies.append(
                    {
                        "case_id": case.case_id,
                        "reasons": reasons,
                        "severity": "high" if len(reasons) > 1 else "medium",
                    }
                )

        return anomalies[:100]  # Limit results

    def get_process_insights(
        self,
        event_log: EventLog,
    ) -> Dict[str, Any]:
        """
        Generate high-level process insights.
        """
        variants = event_log.variants
        activities = event_log.activities

        # Calculate variant concentration
        top_variants = variants[:5] if len(variants) >= 5 else variants
        top_variant_coverage = (
            sum(v.case_count for v in top_variants) / event_log.total_cases
            if event_log.total_cases > 0
            else 0
        )

        # Analyze activity distribution
        activity_counts = {}
        for case in event_log.cases:
            for event in case.events:
                act = str(event.activity)
                activity_counts[act] = activity_counts.get(act, 0) + 1

        total_events = event_log.total_events
        activity_distribution = {
            act: count / total_events for act, count in activity_counts.items()
        }

        # Identify potential start/end activities
        start_activities = {}
        end_activities = {}
        for case in event_log.cases:
            if case.activities:
                start = case.activities[0]
                end = case.activities[-1]
                start_activities[start] = start_activities.get(start, 0) + 1
                end_activities[end] = end_activities.get(end, 0) + 1

        return {
            "process_complexity": {
                "unique_activities": len(activities),
                "unique_variants": len(variants),
                "avg_case_length": total_events / event_log.total_cases
                if event_log.total_cases > 0
                else 0,
            },
            "process_standardization": {
                "top_5_variant_coverage": top_variant_coverage,
                "is_highly_standardized": top_variant_coverage > 0.8,
            },
            "activity_distribution": dict(
                sorted(activity_distribution.items(), key=lambda x: -x[1])[:10]
            ),
            "likely_start_activities": dict(
                sorted(start_activities.items(), key=lambda x: -x[1])[:3]
            ),
            "likely_end_activities": dict(sorted(end_activities.items(), key=lambda x: -x[1])[:3]),
        }

    def _is_prefix_match(
        self,
        prefix: List[str],
        full_sequence: List[str],
    ) -> bool:
        """Check if prefix matches the start of full_sequence."""
        if len(prefix) >= len(full_sequence):
            return False
        return full_sequence[: len(prefix)] == prefix


# Singleton instance
prediction_service = PredictionService()
