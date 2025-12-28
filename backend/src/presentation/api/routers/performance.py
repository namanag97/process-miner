"""Performance Analysis API Router.

Phase 5.1: Performance & Bottleneck API
Covers business activities: PER-001 to PER-005, BOT-001, BOT-002
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.infrastructure.persistence.models import (
    PerformanceAnalysisRunModel,
    ActivityPerformanceMetricModel,
    TransitionPerformanceMetricModel,
    ResourcePerformanceMetricModel,
    BottleneckFindingModel,
)
from src.presentation.api.routers.auth import require_auth, User


router = APIRouter(prefix="/performance")


# =============================================================================
# RESPONSE MODELS
# =============================================================================

class ActivityPerformanceResponse(BaseModel):
    """Performance metrics for a single activity."""
    activity_name: str
    execution_count: int
    distinct_cases: int
    min_duration_seconds: Optional[float]
    max_duration_seconds: Optional[float]
    avg_duration_seconds: Optional[float]
    median_duration_seconds: Optional[float]
    p95_duration_seconds: Optional[float]
    total_processing_time_seconds: Optional[float]
    total_waiting_time_seconds: Optional[float]


class TransitionPerformanceResponse(BaseModel):
    """Performance metrics for a transition between activities."""
    from_activity: str
    to_activity: str
    transition_count: int
    min_time_seconds: Optional[float]
    max_time_seconds: Optional[float]
    avg_time_seconds: Optional[float]
    median_time_seconds: Optional[float]
    probability: float


class ResourcePerformanceResponse(BaseModel):
    """Performance metrics for a resource."""
    resource_identifier: str
    events_handled: int
    cases_touched: int
    distinct_activities: int
    total_active_time_seconds: Optional[float]
    avg_handling_time_seconds: Optional[float]
    utilization_rate: float
    handoff_count_out: int
    handoff_count_in: int


class BottleneckResponse(BaseModel):
    """Detected bottleneck finding."""
    id: str
    location: str  # activity, transition, resource
    bottleneck_type: str  # processing_time, waiting_time, resource_contention
    activity_name: Optional[str]
    from_activity: Optional[str]
    to_activity: Optional[str]
    severity_score: float
    avg_delay_seconds: Optional[float]
    total_time_impact_seconds: Optional[float]
    cases_affected: int
    description: Optional[str]
    recommended_action: Optional[str]


class DurationHistogramBin(BaseModel):
    """A single bin in the duration histogram."""
    bin_start: float
    bin_end: float
    count: int
    percentage: float


class DurationHistogramResponse(BaseModel):
    """Duration distribution histogram data."""
    log_id: str
    total_cases: int
    bins: List[DurationHistogramBin]
    min_duration_seconds: float
    max_duration_seconds: float
    avg_duration_seconds: float
    median_duration_seconds: float


class PerformanceSummaryResponse(BaseModel):
    """Aggregated performance summary for an event log."""
    log_id: str
    analysis_run_id: Optional[str]
    analyzed_at: Optional[str]
    
    # Duration statistics
    total_cases: int
    total_events: int
    avg_case_duration_seconds: Optional[float]
    median_case_duration_seconds: Optional[float]
    min_case_duration_seconds: Optional[float]
    max_case_duration_seconds: Optional[float]
    
    # Activity metrics
    total_activities: int
    slowest_activities: List[Dict[str, Any]]
    fastest_activities: List[Dict[str, Any]]
    
    # Bottleneck summary
    bottleneck_count: int
    top_bottlenecks: List[BottleneckResponse]


class PerformanceAnalyzeRequest(BaseModel):
    """Request to run performance analysis."""
    name: Optional[str] = None
    analysis_type: str = "duration"  # duration, frequency, bottleneck, throughput


class PerformanceAnalyzeResponse(BaseModel):
    """Response from running performance analysis."""
    analysis_run_id: str
    log_id: str
    name: str
    analysis_type: str
    status: str
    activity_metrics_count: int
    transition_metrics_count: int
    bottleneck_count: int


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def generate_uuid() -> str:
    """Generate a UUID string."""
    from uuid import uuid4
    return str(uuid4())


async def calculate_activity_metrics(log, session: AsyncSession) -> List[Dict[str, Any]]:
    """Calculate performance metrics for each activity using PM4Py-style analysis."""
    activity_stats = {}
    
    for case in log.cases:
        sorted_events = sorted(case.events, key=lambda e: e.timestamp.value)
        
        for i, event in enumerate(sorted_events):
            activity = str(event.activity)
            
            if activity not in activity_stats:
                activity_stats[activity] = {
                    "execution_count": 0,
                    "cases": set(),
                    "durations": [],
                    "waiting_times": [],
                }
            
            activity_stats[activity]["execution_count"] += 1
            activity_stats[activity]["cases"].add(str(case.case_id))
            
            # Calculate service time (if next event exists)
            if i < len(sorted_events) - 1:
                next_event = sorted_events[i + 1]
                try:
                    duration = (next_event.timestamp.value - event.timestamp.value).total_seconds()
                    if duration >= 0:
                        activity_stats[activity]["durations"].append(duration)
                except:
                    pass
    
    # Build metrics list
    metrics = []
    for activity, stats in activity_stats.items():
        durations = sorted(stats["durations"]) if stats["durations"] else []
        
        metrics.append({
            "activity_name": activity,
            "execution_count": stats["execution_count"],
            "distinct_cases": len(stats["cases"]),
            "min_duration_seconds": durations[0] if durations else None,
            "max_duration_seconds": durations[-1] if durations else None,
            "avg_duration_seconds": sum(durations) / len(durations) if durations else None,
            "median_duration_seconds": durations[len(durations) // 2] if durations else None,
            "p95_duration_seconds": durations[int(len(durations) * 0.95)] if len(durations) > 20 else None,
            "total_processing_time_seconds": sum(durations) if durations else None,
        })
    
    return sorted(metrics, key=lambda x: x["execution_count"], reverse=True)


async def calculate_transition_metrics(log, session: AsyncSession) -> List[Dict[str, Any]]:
    """Calculate performance metrics for transitions between activities."""
    transition_stats = {}
    activity_totals = {}
    
    for case in log.cases:
        sorted_events = sorted(case.events, key=lambda e: e.timestamp.value)
        
        for i in range(len(sorted_events) - 1):
            from_activity = str(sorted_events[i].activity)
            to_activity = str(sorted_events[i + 1].activity)
            key = (from_activity, to_activity)
            
            if from_activity not in activity_totals:
                activity_totals[from_activity] = 0
            activity_totals[from_activity] += 1
            
            if key not in transition_stats:
                transition_stats[key] = {
                    "count": 0,
                    "times": [],
                }
            
            transition_stats[key]["count"] += 1
            
            try:
                transition_time = (sorted_events[i + 1].timestamp.value - sorted_events[i].timestamp.value).total_seconds()
                if transition_time >= 0:
                    transition_stats[key]["times"].append(transition_time)
            except:
                pass
    
    # Build metrics list
    metrics = []
    for (from_act, to_act), stats in transition_stats.items():
        times = sorted(stats["times"]) if stats["times"] else []
        total_from = activity_totals.get(from_act, 1)
        
        metrics.append({
            "from_activity": from_act,
            "to_activity": to_act,
            "transition_count": stats["count"],
            "min_time_seconds": times[0] if times else None,
            "max_time_seconds": times[-1] if times else None,
            "avg_time_seconds": sum(times) / len(times) if times else None,
            "median_time_seconds": times[len(times) // 2] if times else None,
            "probability": round(stats["count"] / total_from, 4) if total_from > 0 else 0.0,
        })
    
    return sorted(metrics, key=lambda x: x["transition_count"], reverse=True)


async def detect_bottlenecks(
    activity_metrics: List[Dict[str, Any]],
    transition_metrics: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Detect bottlenecks based on activity and transition metrics."""
    bottlenecks = []
    
    # Calculate thresholds for bottleneck detection
    avg_durations = [m["avg_duration_seconds"] for m in activity_metrics if m["avg_duration_seconds"]]
    if avg_durations:
        duration_mean = sum(avg_durations) / len(avg_durations)
        duration_threshold = duration_mean * 1.5  # 50% above average
        
        # Find activity bottlenecks
        for metric in activity_metrics:
            if metric["avg_duration_seconds"] and metric["avg_duration_seconds"] > duration_threshold:
                severity = min(1.0, (metric["avg_duration_seconds"] - duration_mean) / duration_mean)
                bottlenecks.append({
                    "id": generate_uuid(),
                    "location": "activity",
                    "bottleneck_type": "processing_time",
                    "activity_name": metric["activity_name"],
                    "from_activity": None,
                    "to_activity": None,
                    "severity_score": round(severity, 3),
                    "avg_delay_seconds": metric["avg_duration_seconds"],
                    "total_time_impact_seconds": metric.get("total_processing_time_seconds"),
                    "cases_affected": metric["distinct_cases"],
                    "description": f"Activity '{metric['activity_name']}' has high processing time ({metric['avg_duration_seconds']:.1f}s avg)",
                    "recommended_action": "Review activity for automation or process improvement opportunities",
                })
    
    # Find transition bottlenecks (waiting time)
    transition_times = [m["avg_time_seconds"] for m in transition_metrics if m["avg_time_seconds"]]
    if transition_times:
        transition_mean = sum(transition_times) / len(transition_times)
        transition_threshold = transition_mean * 2.0  # 100% above average
        
        for metric in transition_metrics:
            if metric["avg_time_seconds"] and metric["avg_time_seconds"] > transition_threshold:
                severity = min(1.0, (metric["avg_time_seconds"] - transition_mean) / transition_mean)
                bottlenecks.append({
                    "id": generate_uuid(),
                    "location": "transition",
                    "bottleneck_type": "waiting_time",
                    "activity_name": None,
                    "from_activity": metric["from_activity"],
                    "to_activity": metric["to_activity"],
                    "severity_score": round(severity, 3),
                    "avg_delay_seconds": metric["avg_time_seconds"],
                    "total_time_impact_seconds": metric["avg_time_seconds"] * metric["transition_count"],
                    "cases_affected": metric["transition_count"],
                    "description": f"Transition from '{metric['from_activity']}' to '{metric['to_activity']}' has high waiting time ({metric['avg_time_seconds']:.1f}s avg)",
                    "recommended_action": "Investigate handoff between activities for delays",
                })
    
    # Sort by severity
    return sorted(bottlenecks, key=lambda x: x["severity_score"], reverse=True)


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post("/analyze/{log_id}", response_model=PerformanceAnalyzeResponse)
async def run_performance_analysis(
    log_id: UUID,
    request: PerformanceAnalyzeRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Run performance analysis on an event log.
    
    Calculates activity durations, transition times, and detects bottlenecks.
    Results are stored for subsequent retrieval.
    
    **Analysis Types:**
    - duration: Focus on case and activity durations
    - frequency: Focus on event and activity frequencies
    - bottleneck: Detect and rank bottlenecks
    - throughput: Calculate throughput rates
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Generate analysis name
        analysis_name = request.name or f"Performance Analysis - {log.name}"
        
        # Calculate metrics
        activity_metrics = await calculate_activity_metrics(log, session)
        transition_metrics = await calculate_transition_metrics(log, session)
        bottlenecks = await detect_bottlenecks(activity_metrics, transition_metrics)
        
        # Create analysis run record
        run_id = generate_uuid()
        analysis_run = PerformanceAnalysisRunModel(
            id=run_id,
            log_id=str(log_id),
            name=analysis_name,
            analysis_type=request.analysis_type,
            status="completed",
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            summary_statistics_json=json.dumps({
                "total_cases": len(log.cases),
                "total_activities": len(activity_metrics),
                "bottleneck_count": len(bottlenecks),
            }),
        )
        session.add(analysis_run)
        
        # Store activity metrics
        for metric in activity_metrics:
            activity_metric = ActivityPerformanceMetricModel(
                id=generate_uuid(),
                analysis_run_id=run_id,
                activity_name=metric["activity_name"],
                execution_count=metric["execution_count"],
                distinct_cases=metric["distinct_cases"],
                min_duration_seconds=metric["min_duration_seconds"],
                max_duration_seconds=metric["max_duration_seconds"],
                avg_duration_seconds=metric["avg_duration_seconds"],
                median_duration_seconds=metric["median_duration_seconds"],
                p95_duration_seconds=metric["p95_duration_seconds"],
                total_processing_time_seconds=metric["total_processing_time_seconds"],
            )
            session.add(activity_metric)
        
        # Store transition metrics
        for metric in transition_metrics:
            transition_metric = TransitionPerformanceMetricModel(
                id=generate_uuid(),
                analysis_run_id=run_id,
                from_activity_name=metric["from_activity"],
                to_activity_name=metric["to_activity"],
                transition_count=metric["transition_count"],
                min_time_seconds=metric["min_time_seconds"],
                max_time_seconds=metric["max_time_seconds"],
                avg_time_seconds=metric["avg_time_seconds"],
                median_time_seconds=metric["median_time_seconds"],
                transition_probability=metric["probability"],
            )
            session.add(transition_metric)
        
        # Store bottleneck findings
        for bottleneck in bottlenecks[:20]:  # Store top 20 bottlenecks
            finding = BottleneckFindingModel(
                id=bottleneck["id"],
                analysis_run_id=run_id,
                location=bottleneck["location"],
                bottleneck_type=bottleneck["bottleneck_type"],
                severity_score=bottleneck["severity_score"],
                avg_delay_seconds=bottleneck["avg_delay_seconds"],
                total_time_impact_seconds=bottleneck["total_time_impact_seconds"],
                cases_affected=bottleneck["cases_affected"],
                description=bottleneck["description"],
                recommended_action=bottleneck["recommended_action"],
            )
            session.add(finding)
        
        await session.commit()
        
        return PerformanceAnalyzeResponse(
            analysis_run_id=run_id,
            log_id=str(log_id),
            name=analysis_name,
            analysis_type=request.analysis_type,
            status="completed",
            activity_metrics_count=len(activity_metrics),
            transition_metrics_count=len(transition_metrics),
            bottleneck_count=len(bottlenecks),
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance analysis failed: {str(e)}")


@router.get("/summary/{log_id}", response_model=PerformanceSummaryResponse)
async def get_performance_summary(
    log_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get aggregated performance summary for an event log.
    
    Includes case duration statistics, activity performance, and top bottlenecks.
    This is a quick summary endpoint; for detailed analysis, use POST /analyze first.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    try:
        # Get latest analysis run if exists
        stmt = select(PerformanceAnalysisRunModel).where(
            PerformanceAnalysisRunModel.log_id == str(log_id)
        ).order_by(PerformanceAnalysisRunModel.created_at.desc()).limit(1)
        result = await session.execute(stmt)
        latest_run = result.scalar_one_or_none()
        
        # Calculate case durations
        durations = []
        for case in log.cases:
            if case.duration:
                durations.append(case.duration.total_seconds)
        
        durations.sort()
        
        # Calculate activity metrics (on-the-fly)
        activity_metrics = await calculate_activity_metrics(log, session)
        
        # Get bottlenecks
        bottlenecks = []
        if latest_run:
            stmt = select(BottleneckFindingModel).where(
                BottleneckFindingModel.analysis_run_id == latest_run.id
            ).order_by(BottleneckFindingModel.severity_score.desc()).limit(5)
            result = await session.execute(stmt)
            for b in result.scalars():
                bottlenecks.append(BottleneckResponse(
                    id=b.id,
                    location=b.location,
                    bottleneck_type=b.bottleneck_type,
                    activity_name=None,
                    from_activity=None,
                    to_activity=None,
                    severity_score=b.severity_score,
                    avg_delay_seconds=b.avg_delay_seconds,
                    total_time_impact_seconds=b.total_time_impact_seconds,
                    cases_affected=b.cases_affected,
                    description=b.description,
                    recommended_action=b.recommended_action,
                ))
        
        # Build slowest/fastest activity lists
        slowest = [
            {"activity": m["activity_name"], "avg_duration_seconds": m["avg_duration_seconds"]}
            for m in activity_metrics[:5] if m["avg_duration_seconds"]
        ]
        fastest = [
            {"activity": m["activity_name"], "avg_duration_seconds": m["avg_duration_seconds"]}
            for m in sorted(
                [m for m in activity_metrics if m["avg_duration_seconds"]],
                key=lambda x: x["avg_duration_seconds"]
            )[:5]
        ]
        
        return PerformanceSummaryResponse(
            log_id=str(log_id),
            analysis_run_id=latest_run.id if latest_run else None,
            analyzed_at=latest_run.completed_at.isoformat() if latest_run and latest_run.completed_at else None,
            total_cases=len(log.cases),
            total_events=sum(len(c.events) for c in log.cases),
            avg_case_duration_seconds=sum(durations) / len(durations) if durations else None,
            median_case_duration_seconds=durations[len(durations) // 2] if durations else None,
            min_case_duration_seconds=durations[0] if durations else None,
            max_case_duration_seconds=durations[-1] if durations else None,
            total_activities=len(activity_metrics),
            slowest_activities=slowest,
            fastest_activities=fastest,
            bottleneck_count=len(bottlenecks),
            top_bottlenecks=bottlenecks,
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Performance summary failed: {str(e)}")


@router.get("/bottlenecks/{log_id}", response_model=List[BottleneckResponse])
async def get_bottlenecks(
    log_id: UUID,
    limit: int = Query(default=20, le=100),
    min_severity: float = Query(default=0.0, ge=0.0, le=1.0),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detected bottlenecks for an event log.
    
    Returns bottlenecks from the most recent performance analysis run.
    Use POST /analyze first to generate bottleneck data.
    
    **Filters:**
    - min_severity: Minimum severity score (0.0-1.0)
    - limit: Maximum number of bottlenecks to return
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    # Get latest analysis run
    stmt = select(PerformanceAnalysisRunModel).where(
        PerformanceAnalysisRunModel.log_id == str(log_id)
    ).order_by(PerformanceAnalysisRunModel.created_at.desc()).limit(1)
    result = await session.execute(stmt)
    latest_run = result.scalar_one_or_none()
    
    if not latest_run:
        raise HTTPException(
            status_code=404,
            detail="No performance analysis found. Run POST /performance/analyze/{log_id} first."
        )
    
    # Get bottlenecks
    stmt = select(BottleneckFindingModel).where(
        BottleneckFindingModel.analysis_run_id == latest_run.id,
        BottleneckFindingModel.severity_score >= min_severity
    ).order_by(BottleneckFindingModel.severity_score.desc()).limit(limit)
    
    result = await session.execute(stmt)
    
    bottlenecks = []
    for b in result.scalars():
        bottlenecks.append(BottleneckResponse(
            id=b.id,
            location=b.location,
            bottleneck_type=b.bottleneck_type,
            activity_name=None,
            from_activity=None,
            to_activity=None,
            severity_score=b.severity_score,
            avg_delay_seconds=b.avg_delay_seconds,
            total_time_impact_seconds=b.total_time_impact_seconds,
            cases_affected=b.cases_affected,
            description=b.description,
            recommended_action=b.recommended_action,
        ))
    
    return bottlenecks


@router.get("/duration-histogram/{log_id}", response_model=DurationHistogramResponse)
async def get_duration_histogram(
    log_id: UUID,
    bins: int = Query(default=10, ge=5, le=50),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get case duration distribution as histogram data.
    
    Returns binned duration data suitable for frontend chart rendering.
    
    **Parameters:**
    - bins: Number of histogram bins (5-50)
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    # Calculate durations
    durations = []
    for case in log.cases:
        if case.duration:
            durations.append(case.duration.total_seconds)
    
    if not durations:
        raise HTTPException(status_code=400, detail="No case durations available")
    
    durations.sort()
    min_dur = durations[0]
    max_dur = durations[-1]
    avg_dur = sum(durations) / len(durations)
    median_dur = durations[len(durations) // 2]
    
    # Create histogram bins
    bin_width = (max_dur - min_dur) / bins if max_dur > min_dur else 1
    histogram_bins = []
    
    for i in range(bins):
        bin_start = min_dur + i * bin_width
        bin_end = min_dur + (i + 1) * bin_width
        count = sum(1 for d in durations if bin_start <= d < bin_end)
        if i == bins - 1:  # Last bin includes max value
            count = sum(1 for d in durations if bin_start <= d <= bin_end)
        
        histogram_bins.append(DurationHistogramBin(
            bin_start=round(bin_start, 2),
            bin_end=round(bin_end, 2),
            count=count,
            percentage=round(count / len(durations) * 100, 2),
        ))
    
    return DurationHistogramResponse(
        log_id=str(log_id),
        total_cases=len(durations),
        bins=histogram_bins,
        min_duration_seconds=round(min_dur, 2),
        max_duration_seconds=round(max_dur, 2),
        avg_duration_seconds=round(avg_dur, 2),
        median_duration_seconds=round(median_dur, 2),
    )


@router.get("/activities/{log_id}", response_model=List[ActivityPerformanceResponse])
async def get_activity_performance(
    log_id: UUID,
    limit: int = Query(default=50, le=200),
    sort_by: str = Query(default="execution_count", pattern="^(execution_count|avg_duration)$"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get performance metrics for all activities in an event log.
    
    **Sort Options:**
    - execution_count: Most executed activities first
    - avg_duration: Slowest activities first
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    # Check for existing analysis
    stmt = select(PerformanceAnalysisRunModel).where(
        PerformanceAnalysisRunModel.log_id == str(log_id)
    ).order_by(PerformanceAnalysisRunModel.created_at.desc()).limit(1)
    result = await session.execute(stmt)
    latest_run = result.scalar_one_or_none()
    
    if latest_run:
        # Return from stored metrics
        stmt = select(ActivityPerformanceMetricModel).where(
            ActivityPerformanceMetricModel.analysis_run_id == latest_run.id
        )
        if sort_by == "avg_duration":
            stmt = stmt.order_by(ActivityPerformanceMetricModel.avg_duration_seconds.desc())
        else:
            stmt = stmt.order_by(ActivityPerformanceMetricModel.execution_count.desc())
        
        stmt = stmt.limit(limit)
        result = await session.execute(stmt)
        
        return [
            ActivityPerformanceResponse(
                activity_name=m.activity_name,
                execution_count=m.execution_count,
                distinct_cases=m.distinct_cases,
                min_duration_seconds=m.min_duration_seconds,
                max_duration_seconds=m.max_duration_seconds,
                avg_duration_seconds=m.avg_duration_seconds,
                median_duration_seconds=m.median_duration_seconds,
                p95_duration_seconds=m.p95_duration_seconds,
                total_processing_time_seconds=m.total_processing_time_seconds,
                total_waiting_time_seconds=m.total_waiting_time_seconds,
            )
            for m in result.scalars()
        ]
    else:
        # Calculate on-the-fly
        metrics = await calculate_activity_metrics(log, session)
        
        if sort_by == "avg_duration":
            metrics = sorted(
                [m for m in metrics if m["avg_duration_seconds"]],
                key=lambda x: x["avg_duration_seconds"],
                reverse=True
            )
        
        return [
            ActivityPerformanceResponse(**m)
            for m in metrics[:limit]
        ]


@router.get("/transitions/{log_id}", response_model=List[TransitionPerformanceResponse])
async def get_transition_performance(
    log_id: UUID,
    limit: int = Query(default=50, le=200),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get performance metrics for transitions (DFG edges) in an event log.
    
    Returns transition times and probabilities between activities.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(log_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Event log not found")
    
    # Check for existing analysis
    stmt = select(PerformanceAnalysisRunModel).where(
        PerformanceAnalysisRunModel.log_id == str(log_id)
    ).order_by(PerformanceAnalysisRunModel.created_at.desc()).limit(1)
    result = await session.execute(stmt)
    latest_run = result.scalar_one_or_none()
    
    if latest_run:
        # Return from stored metrics
        stmt = select(TransitionPerformanceMetricModel).where(
            TransitionPerformanceMetricModel.analysis_run_id == latest_run.id
        ).order_by(TransitionPerformanceMetricModel.transition_count.desc()).limit(limit)
        
        result = await session.execute(stmt)
        
        return [
            TransitionPerformanceResponse(
                from_activity=m.from_activity_name,
                to_activity=m.to_activity_name,
                transition_count=m.transition_count,
                min_time_seconds=m.min_time_seconds,
                max_time_seconds=m.max_time_seconds,
                avg_time_seconds=m.avg_time_seconds,
                median_time_seconds=m.median_time_seconds,
                probability=m.transition_probability,
            )
            for m in result.scalars()
        ]
    else:
        # Calculate on-the-fly
        metrics = await calculate_transition_metrics(log, session)
        
        return [
            TransitionPerformanceResponse(
                from_activity=m["from_activity"],
                to_activity=m["to_activity"],
                transition_count=m["transition_count"],
                min_time_seconds=m["min_time_seconds"],
                max_time_seconds=m["max_time_seconds"],
                avg_time_seconds=m["avg_time_seconds"],
                median_time_seconds=m["median_time_seconds"],
                probability=m["probability"],
            )
            for m in metrics[:limit]
        ]
