"""
Insight Service - Extract and persist insights from analysis.

Takes raw analysis results (deviations, bottlenecks) and creates
queryable Insight records with severity scoring.
"""

import json
from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models import (
    Insight,
    InsightCreate,
    InsightSummary,
    Dataset,
    Deviation,
)
from ..core import get_logger

log = get_logger(__name__)


class InsightService:
    """Service for extracting and managing insights."""
    
    # Severity thresholds
    SEVERITY_THRESHOLDS = {
        "critical": 0.8,
        "high": 0.6,
        "medium": 0.3,
        "low": 0.0,
    }
    
    @staticmethod
    def calculate_severity(
        affected_case_count: int,
        total_cases: int,
        metric_value: Optional[float] = None,
        metric_threshold: Optional[float] = None,
    ) -> tuple[str, float]:
        """
        Calculate severity level and score.
        
        Args:
            affected_case_count: Number of cases affected
            total_cases: Total number of cases
            metric_value: Optional metric value
            metric_threshold: Optional threshold that was breached
            
        Returns:
            Tuple of (severity level, severity score 0.0-1.0)
        """
        # Base score from affected percentage
        if total_cases > 0:
            base_score = affected_case_count / total_cases
        else:
            base_score = 0.0
        
        # Boost score if metric exceeds threshold significantly
        if metric_value is not None and metric_threshold is not None:
            if metric_threshold > 0:
                ratio = metric_value / metric_threshold
                if ratio > 2:
                    base_score = min(1.0, base_score + 0.3)
                elif ratio > 1.5:
                    base_score = min(1.0, base_score + 0.2)
        
        # Clamp to 0-1
        score = max(0.0, min(1.0, base_score))
        
        # Determine level
        if score >= InsightService.SEVERITY_THRESHOLDS["critical"]:
            level = "critical"
        elif score >= InsightService.SEVERITY_THRESHOLDS["high"]:
            level = "high"
        elif score >= InsightService.SEVERITY_THRESHOLDS["medium"]:
            level = "medium"
        else:
            level = "low"
        
        return level, score
    
    @staticmethod
    async def extract_insights_from_analysis(
        db: AsyncSession,
        dataset_id: str,
        deviations: list[dict],
        stats: dict,
    ) -> list[Insight]:
        """
        Extract insights from analysis results.
        
        Args:
            db: Database session
            dataset_id: ID of the dataset
            deviations: List of deviation dictionaries
            stats: Process statistics dictionary
            
        Returns:
            List of created Insight records
        """
        insights = []
        total_cases = stats.get("total_cases", 1)
        
        for deviation in deviations:
            deviation_type = deviation.get("type", "deviation")
            affected_cases = deviation.get("affected_cases", [])
            affected_count = len(affected_cases)
            
            # Calculate severity
            severity, score = InsightService.calculate_severity(
                affected_case_count=affected_count,
                total_cases=total_cases,
            )
            
            # Map deviation type to insight type
            insight_type_map = {
                "rework": "rework",
                "skip": "deviation",
                "unusual_path": "deviation",
            }
            insight_type = insight_type_map.get(deviation_type, "deviation")
            
            # Create insight
            insight = Insight(
                dataset_id=dataset_id,
                insight_type=insight_type,
                severity=severity,
                severity_score=score,
                title=f"{deviation_type.replace('_', ' ').title()} Detected",
                description=deviation.get("description", ""),
                affected_case_count=affected_count,
                affected_case_ids_json=json.dumps(affected_cases[:100]),  # Limit stored IDs
                data_json=json.dumps(deviation),
                created_at=datetime.utcnow(),
            )
            
            db.add(insight)
            insights.append(insight)
        
        await db.commit()
        
        # Refresh all insights
        for insight in insights:
            await db.refresh(insight)
        
        log.info(
            "insights_extracted",
            dataset_id=dataset_id,
            count=len(insights),
        )
        
        return insights
    
    @staticmethod
    async def create_bottleneck_insight(
        db: AsyncSession,
        dataset_id: str,
        activity_name: str,
        avg_duration_ms: float,
        threshold_ms: float,
        affected_case_count: int,
        total_cases: int,
    ) -> Insight:
        """
        Create a bottleneck insight for a slow activity.
        
        Args:
            db: Database session
            dataset_id: Dataset ID
            activity_name: Name of bottleneck activity
            avg_duration_ms: Average duration in milliseconds
            threshold_ms: Threshold that was exceeded
            affected_case_count: Cases going through this activity
            total_cases: Total cases
            
        Returns:
            Created Insight
        """
        severity, score = InsightService.calculate_severity(
            affected_case_count=affected_case_count,
            total_cases=total_cases,
            metric_value=avg_duration_ms,
            metric_threshold=threshold_ms,
        )
        
        insight = Insight(
            dataset_id=dataset_id,
            insight_type="bottleneck",
            severity=severity,
            severity_score=score,
            title=f"Bottleneck at '{activity_name}'",
            description=f"Activity '{activity_name}' has high average duration of {avg_duration_ms/1000:.1f}s, exceeding threshold of {threshold_ms/1000:.1f}s.",
            affected_activity=activity_name,
            affected_case_count=affected_case_count,
            metric_name="avg_duration_ms",
            metric_value=avg_duration_ms,
            metric_threshold=threshold_ms,
            created_at=datetime.utcnow(),
        )
        
        db.add(insight)
        await db.commit()
        await db.refresh(insight)
        
        return insight
    
    @staticmethod
    async def get_insights_for_dataset(
        db: AsyncSession,
        dataset_id: str,
        insight_type: Optional[str] = None,
        severity: Optional[str] = None,
    ) -> list[Insight]:
        """
        Get insights for a dataset with optional filtering.
        """
        query = (
            select(Insight)
            .where(Insight.dataset_id == dataset_id)
            .order_by(Insight.severity_score.desc())
        )
        
        if insight_type:
            query = query.where(Insight.insight_type == insight_type)
        if severity:
            query = query.where(Insight.severity == severity)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def get_insight_summary(
        db: AsyncSession,
        dataset_id: str,
    ) -> InsightSummary:
        """
        Get aggregated insight summary for a dataset.
        """
        # Get all insights for the dataset
        insights = await InsightService.get_insights_for_dataset(db, dataset_id)
        
        # Aggregate
        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        critical_count = 0
        unacknowledged_count = 0
        
        for insight in insights:
            # By type
            by_type[insight.insight_type] = by_type.get(insight.insight_type, 0) + 1
            # By severity
            by_severity[insight.severity] = by_severity.get(insight.severity, 0) + 1
            # Critical count
            if insight.severity == "critical":
                critical_count += 1
            # Unacknowledged
            if not insight.is_acknowledged:
                unacknowledged_count += 1
        
        return InsightSummary(
            total_insights=len(insights),
            by_type=by_type,
            by_severity=by_severity,
            critical_count=critical_count,
            unacknowledged_count=unacknowledged_count,
        )
    
    @staticmethod
    async def acknowledge_insight(
        db: AsyncSession,
        insight_id: str,
        user_id: Optional[str] = None,
    ) -> Optional[Insight]:
        """
        Mark an insight as acknowledged.
        """
        result = await db.execute(
            select(Insight).where(Insight.id == insight_id)
        )
        insight = result.scalar_one_or_none()
        
        if insight:
            insight.is_acknowledged = True
            insight.acknowledged_at = datetime.utcnow()
            insight.acknowledged_by = user_id
            await db.commit()
            await db.refresh(insight)
        
        return insight


# Singleton instance
insight_service = InsightService()
