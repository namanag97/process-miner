"""Processes Performance Sub-Router.

Provides performance analysis endpoints nested under /processes/{process_id}/performance.
This sub-router is included by the main processes router.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
import uuid as uuid_lib

from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.persistence.database import get_session
from src.infrastructure.persistence.repositories import EventLogRepository
from src.presentation.api.routers.auth import require_auth, User


# =============================================================================
# SUB-ROUTER DEFINITION
# =============================================================================
router = APIRouter()


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


class TransitionPerformanceResponse(BaseModel):
    """Performance metrics for a transition."""
    from_activity: str
    to_activity: str
    transition_count: int
    min_time_seconds: Optional[float]
    max_time_seconds: Optional[float]
    avg_time_seconds: Optional[float]
    median_time_seconds: Optional[float]
    probability: float


class BottleneckResponse(BaseModel):
    """Detected bottleneck finding."""
    id: str
    location: str
    bottleneck_type: str  # activity, transition
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
    process_id: str
    total_cases: int
    bins: List[DurationHistogramBin]
    min_duration_seconds: float
    max_duration_seconds: float
    avg_duration_seconds: float
    median_duration_seconds: float


class PerformanceSummaryResponse(BaseModel):
    """Aggregated performance summary."""
    process_id: str
    total_cases: int
    total_events: int
    avg_case_duration_seconds: Optional[float]
    median_case_duration_seconds: Optional[float]
    min_case_duration_seconds: Optional[float]
    max_case_duration_seconds: Optional[float]
    total_activities: int
    slowest_activities: List[Dict[str, Any]]
    fastest_activities: List[Dict[str, Any]]
    bottleneck_count: int
    top_bottlenecks: List[BottleneckResponse]


class AnalyzeRequest(BaseModel):
    """Request to run performance analysis."""
    name: Optional[str] = None
    analysis_type: str = "duration"  # duration, throughput, waiting


class AnalyzeResponse(BaseModel):
    """Response from running performance analysis."""
    analysis_run_id: str
    process_id: str
    name: str
    analysis_type: str
    status: str
    activity_metrics_count: int
    transition_metrics_count: int
    bottleneck_count: int


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def calculate_case_durations(log) -> List[float]:
    """Calculate case durations from log."""
    durations = []
    for case in log.cases:
        if case.events:
            sorted_events = sorted(case.events, key=lambda e: e.timestamp)
            if len(sorted_events) >= 2:
                duration = (sorted_events[-1].timestamp - sorted_events[0].timestamp).total_seconds()
                durations.append(duration)
    return durations


def calculate_activity_metrics(log) -> List[Dict[str, Any]]:
    """Calculate activity performance metrics."""
    from collections import defaultdict
    
    activity_data = defaultdict(lambda: {"times": [], "cases": set()})
    
    for case in log.cases:
        if case.events:
            sorted_events = sorted(case.events, key=lambda e: e.timestamp)
            for i, event in enumerate(sorted_events):
                activity = event.activity_name
                activity_data[activity]["cases"].add(case.case_id)
                
                # Calculate duration to next event (service time proxy)
                if i < len(sorted_events) - 1:
                    duration = (sorted_events[i + 1].timestamp - event.timestamp).total_seconds()
                    activity_data[activity]["times"].append(duration)
    
    metrics = []
    for activity, data in activity_data.items():
        times = data["times"]
        if times:
            import statistics
            metrics.append({
                "activity_name": activity,
                "execution_count": len(times),
                "distinct_cases": len(data["cases"]),
                "min_duration_seconds": min(times),
                "max_duration_seconds": max(times),
                "avg_duration_seconds": statistics.mean(times),
                "median_duration_seconds": statistics.median(times),
                "p95_duration_seconds": sorted(times)[int(len(times) * 0.95)] if len(times) >= 20 else max(times),
                "total_processing_time_seconds": sum(times),
            })
    
    return sorted(metrics, key=lambda x: x["avg_duration_seconds"], reverse=True)


def calculate_transition_metrics(log) -> List[Dict[str, Any]]:
    """Calculate transition performance metrics."""
    from collections import defaultdict
    
    transition_data = defaultdict(list)
    transition_count = defaultdict(int)
    activity_count = defaultdict(int)
    
    for case in log.cases:
        if case.events:
            sorted_events = sorted(case.events, key=lambda e: e.timestamp)
            for i in range(len(sorted_events) - 1):
                from_act = sorted_events[i].activity_name
                to_act = sorted_events[i + 1].activity_name
                duration = (sorted_events[i + 1].timestamp - sorted_events[i].timestamp).total_seconds()
                
                transition_data[(from_act, to_act)].append(duration)
                transition_count[(from_act, to_act)] += 1
                activity_count[from_act] += 1
    
    metrics = []
    for (from_act, to_act), times in transition_data.items():
        if times:
            import statistics
            prob = transition_count[(from_act, to_act)] / activity_count[from_act] if activity_count[from_act] > 0 else 0
            metrics.append({
                "from_activity": from_act,
                "to_activity": to_act,
                "transition_count": len(times),
                "min_time_seconds": min(times),
                "max_time_seconds": max(times),
                "avg_time_seconds": statistics.mean(times),
                "median_time_seconds": statistics.median(times),
                "probability": prob,
            })
    
    return sorted(metrics, key=lambda x: x["avg_time_seconds"], reverse=True)


def detect_bottlenecks(activity_metrics: List[Dict], transition_metrics: List[Dict]) -> List[Dict]:
    """Detect bottlenecks from metrics."""
    bottlenecks = []
    
    # Activity bottlenecks (top slow activities)
    if activity_metrics:
        avg_duration = sum(m["avg_duration_seconds"] for m in activity_metrics if m["avg_duration_seconds"]) / len(activity_metrics)
        for metric in activity_metrics[:5]:
            if metric["avg_duration_seconds"] and metric["avg_duration_seconds"] > avg_duration * 1.5:
                bottlenecks.append({
                    "id": str(uuid_lib.uuid4()),
                    "location": metric["activity_name"],
                    "bottleneck_type": "activity",
                    "activity_name": metric["activity_name"],
                    "from_activity": None,
                    "to_activity": None,
                    "severity_score": min(1.0, metric["avg_duration_seconds"] / (avg_duration * 3)),
                    "avg_delay_seconds": metric["avg_duration_seconds"],
                    "total_time_impact_seconds": metric["total_processing_time_seconds"],
                    "cases_affected": metric["distinct_cases"],
                    "description": f"Activity '{metric['activity_name']}' has above-average duration",
                    "recommended_action": "Consider process optimization or resource allocation",
                })
    
    # Transition bottlenecks (top slow transitions)
    if transition_metrics:
        avg_time = sum(m["avg_time_seconds"] for m in transition_metrics if m["avg_time_seconds"]) / len(transition_metrics)
        for metric in transition_metrics[:5]:
            if metric["avg_time_seconds"] and metric["avg_time_seconds"] > avg_time * 1.5:
                bottlenecks.append({
                    "id": str(uuid_lib.uuid4()),
                    "location": f"{metric['from_activity']} → {metric['to_activity']}",
                    "bottleneck_type": "transition",
                    "activity_name": None,
                    "from_activity": metric["from_activity"],
                    "to_activity": metric["to_activity"],
                    "severity_score": min(1.0, metric["avg_time_seconds"] / (avg_time * 3)),
                    "avg_delay_seconds": metric["avg_time_seconds"],
                    "total_time_impact_seconds": metric["avg_time_seconds"] * metric["transition_count"],
                    "cases_affected": metric["transition_count"],
                    "description": f"Transition from '{metric['from_activity']}' to '{metric['to_activity']}' has above-average waiting time",
                    "recommended_action": "Investigate handoff delays or resource availability",
                })
    
    return sorted(bottlenecks, key=lambda x: x["severity_score"], reverse=True)


# =============================================================================
# ENDPOINTS
# =============================================================================

@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Run Performance Analysis",
    description="""
    Run performance analysis on the process.
    
    Calculates activity durations, transition times, and detects bottlenecks.
    """,
)
async def run_performance_analysis(
    process_id: UUID,
    request: AnalyzeRequest,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Run performance analysis.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    try:
        activity_metrics = calculate_activity_metrics(log)
        transition_metrics = calculate_transition_metrics(log)
        bottlenecks = detect_bottlenecks(activity_metrics, transition_metrics)
        
        return AnalyzeResponse(
            analysis_run_id=str(uuid_lib.uuid4()),
            process_id=str(process_id),
            name=request.name or f"Analysis - {log.name}",
            analysis_type=request.analysis_type,
            status="completed",
            activity_metrics_count=len(activity_metrics),
            transition_metrics_count=len(transition_metrics),
            bottleneck_count=len(bottlenecks),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get(
    "/summary",
    response_model=PerformanceSummaryResponse,
    summary="Get Performance Summary",
    description="Get aggregated performance summary.",
)
async def get_performance_summary(
    process_id: UUID,
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get performance summary.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    try:
        import statistics
        
        durations = calculate_case_durations(log)
        activity_metrics = calculate_activity_metrics(log)
        transition_metrics = calculate_transition_metrics(log)
        bottlenecks = detect_bottlenecks(activity_metrics, transition_metrics)
        
        return PerformanceSummaryResponse(
            process_id=str(process_id),
            total_cases=len(log.cases) if log.cases else 0,
            total_events=sum(len(c.events) for c in log.cases) if log.cases else 0,
            avg_case_duration_seconds=statistics.mean(durations) if durations else None,
            median_case_duration_seconds=statistics.median(durations) if durations else None,
            min_case_duration_seconds=min(durations) if durations else None,
            max_case_duration_seconds=max(durations) if durations else None,
            total_activities=len(activity_metrics),
            slowest_activities=activity_metrics[:5],
            fastest_activities=activity_metrics[-5:] if len(activity_metrics) >= 5 else activity_metrics,
            bottleneck_count=len(bottlenecks),
            top_bottlenecks=[BottleneckResponse(**b) for b in bottlenecks[:5]],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")


@router.get(
    "/bottlenecks",
    response_model=List[BottleneckResponse],
    summary="Get Bottlenecks",
    description="Get detected bottlenecks.",
)
async def get_bottlenecks(
    process_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get detected bottlenecks.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    try:
        activity_metrics = calculate_activity_metrics(log)
        transition_metrics = calculate_transition_metrics(log)
        bottlenecks = detect_bottlenecks(activity_metrics, transition_metrics)
        
        return [BottleneckResponse(**b) for b in bottlenecks[:limit]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bottleneck detection failed: {str(e)}")


@router.get(
    "/duration-histogram",
    response_model=DurationHistogramResponse,
    summary="Get Duration Histogram",
    description="Get case duration distribution histogram.",
)
async def get_duration_histogram(
    process_id: UUID,
    bins: int = Query(10, ge=5, le=50),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get duration histogram.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    try:
        import statistics
        
        durations = calculate_case_durations(log)
        
        if not durations:
            raise HTTPException(status_code=400, detail="No duration data available")
        
        min_dur = min(durations)
        max_dur = max(durations)
        bin_width = (max_dur - min_dur) / bins if max_dur > min_dur else 1
        
        histogram_bins = []
        for i in range(bins):
            bin_start = min_dur + i * bin_width
            bin_end = min_dur + (i + 1) * bin_width
            count = sum(1 for d in durations if bin_start <= d < bin_end)
            histogram_bins.append(DurationHistogramBin(
                bin_start=bin_start,
                bin_end=bin_end,
                count=count,
                percentage=count / len(durations) * 100,
            ))
        
        return DurationHistogramResponse(
            process_id=str(process_id),
            total_cases=len(durations),
            bins=histogram_bins,
            min_duration_seconds=min_dur,
            max_duration_seconds=max_dur,
            avg_duration_seconds=statistics.mean(durations),
            median_duration_seconds=statistics.median(durations),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Histogram generation failed: {str(e)}")


@router.get(
    "/activities",
    response_model=List[ActivityPerformanceResponse],
    summary="Get Activity Performance",
    description="Get performance metrics for each activity.",
)
async def get_activity_performance(
    process_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    sort_by: str = Query("avg_duration_seconds", pattern="^(avg_duration_seconds|execution_count|activity_name)$"),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get activity performance metrics.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    try:
        metrics = calculate_activity_metrics(log)
        
        if sort_by == "execution_count":
            metrics = sorted(metrics, key=lambda x: x["execution_count"], reverse=True)
        elif sort_by == "activity_name":
            metrics = sorted(metrics, key=lambda x: x["activity_name"])
        
        return [ActivityPerformanceResponse(**m) for m in metrics[:limit]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Activity metrics failed: {str(e)}")


@router.get(
    "/transitions",
    response_model=List[TransitionPerformanceResponse],
    summary="Get Transition Performance",
    description="Get performance metrics for transitions.",
)
async def get_transition_performance(
    process_id: UUID,
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
    user: User = Depends(require_auth),
):
    """
    Get transition performance metrics.
    """
    repo = EventLogRepository(session)
    log = await repo.get_by_id(process_id)
    
    if not log:
        raise HTTPException(status_code=404, detail="Process not found")
    
    try:
        metrics = calculate_transition_metrics(log)
        return [TransitionPerformanceResponse(**m) for m in metrics[:limit]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transition metrics failed: {str(e)}")
