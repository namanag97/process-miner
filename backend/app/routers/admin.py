"""
Admin router - Database stats, visibility, and management.

Provides endpoints for:
- Database entity counts
- Recent activity
- System health metrics
- Data table browsing (NEW)
- Audit logs viewing (NEW)
- Insights aggregation (NEW)
"""

import json
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select

from ..database import get_db
from ..models import (
    User, Upload, Mapping, Job, Dataset,
    Organization, Process, AuditLog, Insight,
    AuditLogFilter, AuditLogResponse, InsightResponse, InsightSummary,
)
from ..services import audit_service, insight_service
from ..core import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# =============================================================================
# Existing Stats Endpoints
# =============================================================================

@router.get("/stats")
async def get_database_stats(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Get counts of all database entities.
    Useful for understanding data volume.
    """
    stats = {}
    
    # Count each table
    for model, name in [
        (Organization, "organizations"),
        (User, "users"),
        (Process, "processes"),
        (Upload, "uploads"),
        (Mapping, "mappings"),
        (Job, "jobs"),
        (Dataset, "datasets"),
        (AuditLog, "audit_logs"),
        (Insight, "insights"),
    ]:
        result = await db.execute(select(func.count()).select_from(model))
        stats[name] = result.scalar() or 0
    
    return {
        "database_stats": stats,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/recent-activity")
async def get_recent_activity(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
) -> dict[str, Any]:
    """
    Get recent uploads and jobs from the last N hours.
    """
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    
    # Recent uploads
    uploads_result = await db.execute(
        select(Upload)
        .where(Upload.created_at >= cutoff)
        .order_by(Upload.created_at.desc())
        .limit(10)
    )
    recent_uploads = [
        {
            "id": u.id,
            "filename": u.filename,
            "status": u.status,
            "row_count": u.row_count,
            "created_at": u.created_at.isoformat(),
        }
        for u in uploads_result.scalars()
    ]
    
    # Recent jobs
    jobs_result = await db.execute(
        select(Job)
        .where(Job.created_at >= cutoff)
        .order_by(Job.created_at.desc())
        .limit(10)
    )
    recent_jobs = [
        {
            "id": j.id,
            "status": j.status,
            "progress": j.progress,
            "dataset_id": j.dataset_id,
            "error": j.error,
            "created_at": j.created_at.isoformat(),
        }
        for j in jobs_result.scalars()
    ]
    
    return {
        "period_hours": hours,
        "recent_uploads": recent_uploads,
        "recent_jobs": recent_jobs,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/job-stats")
async def get_job_statistics(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Get job status breakdown.
    """
    statuses = ["queued", "processing", "completed", "failed"]
    job_stats = {}
    
    for status in statuses:
        result = await db.execute(
            select(func.count()).select_from(Job).where(Job.status == status)
        )
        job_stats[status] = result.scalar() or 0
    
    return {
        "job_statistics": job_stats,
        "total": sum(job_stats.values()),
        "success_rate": (
            job_stats["completed"] / max(job_stats["completed"] + job_stats["failed"], 1)
        ) * 100,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/storage")
async def get_storage_stats(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Get storage usage statistics.
    """
    # Total file size
    result = await db.execute(
        select(func.sum(Upload.file_size_bytes))
    )
    total_bytes = result.scalar() or 0
    
    # Total rows processed
    result = await db.execute(
        select(func.sum(Upload.row_count))
    )
    total_rows = result.scalar() or 0
    
    return {
        "storage": {
            "total_bytes": total_bytes,
            "total_mb": round(total_bytes / (1024 * 1024), 2),
            "total_rows_processed": total_rows,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# Data Tables Endpoints (NEW)
# =============================================================================

TABLE_MODELS = {
    "organizations": Organization,
    "users": User,
    "processes": Process,
    "uploads": Upload,
    "mappings": Mapping,
    "jobs": Job,
    "datasets": Dataset,
    "audit_logs": AuditLog,
    "insights": Insight,
}


@router.get("/tables")
async def list_available_tables() -> dict[str, Any]:
    """List all available tables for browsing."""
    return {
        "tables": list(TABLE_MODELS.keys()),
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get("/tables/{table_name}")
async def get_table_data(
    table_name: str,
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get paginated data from a table.
    """
    if table_name not in TABLE_MODELS:
        raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
    
    model = TABLE_MODELS[table_name]
    
    # Get total count
    count_result = await db.execute(select(func.count()).select_from(model))
    total = count_result.scalar() or 0
    
    # Get paginated data
    query = select(model).offset(offset).limit(limit)
    
    # Add ordering by created_at if available
    if hasattr(model, "created_at"):
        query = query.order_by(model.created_at.desc())
    
    result = await db.execute(query)
    rows = result.scalars().all()
    
    # Convert to dicts
    data = []
    for row in rows:
        row_dict = {}
        for column in row.__table__.columns:
            value = getattr(row, column.name)
            # Handle datetime serialization
            if isinstance(value, datetime):
                value = value.isoformat()
            row_dict[column.name] = value
        data.append(row_dict)
    
    return {
        "table": table_name,
        "data": data,
        "pagination": {
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# Audit Logs Endpoints (NEW)
# =============================================================================

@router.get("/logs", response_model=list[AuditLogResponse])
async def get_audit_logs(
    user_id: Optional[str] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    hours: Optional[int] = Query(None, description="Filter to last N hours"),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[AuditLogResponse]:
    """
    Get audit logs with filtering.
    """
    start_date = None
    if hours:
        start_date = datetime.utcnow() - timedelta(hours=hours)
    
    filters = AuditLogFilter(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=entity_id,
        action=action,
        start_date=start_date,
        limit=limit,
        offset=offset,
    )
    
    logs = await audit_service.get_logs(db, filters)
    
    return [
        AuditLogResponse(
            id=log.id,
            user_id=log.user_id,
            entity_type=log.entity_type,
            entity_id=log.entity_id,
            action=log.action,
            details=log.details,
            ip_address=log.ip_address,
            request_path=log.request_path,
            created_at=log.created_at,
        )
        for log in logs
    ]


@router.get("/logs/entity/{entity_type}/{entity_id}")
async def get_entity_audit_history(
    entity_type: str,
    entity_id: str,
    limit: int = Query(50, le=100),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get audit history for a specific entity.
    """
    logs = await audit_service.get_entity_history(db, entity_type, entity_id, limit)
    
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "history": [
            {
                "id": log.id,
                "action": log.action,
                "user_id": log.user_id,
                "details": log.details,
                "created_at": log.created_at.isoformat(),
            }
            for log in logs
        ],
        "timestamp": datetime.utcnow().isoformat(),
    }


# =============================================================================
# Insights Endpoints (NEW)
# =============================================================================

@router.get("/insights", response_model=list[InsightResponse])
async def get_all_insights(
    insight_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    acknowledged: Optional[bool] = Query(None),
    limit: int = Query(100, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[InsightResponse]:
    """
    Get all insights across all datasets.
    """
    query = select(Insight).order_by(Insight.severity_score.desc())
    
    if insight_type:
        query = query.where(Insight.insight_type == insight_type)
    if severity:
        query = query.where(Insight.severity == severity)
    if acknowledged is not None:
        query = query.where(Insight.is_acknowledged == acknowledged)
    
    query = query.offset(offset).limit(limit)
    
    result = await db.execute(query)
    insights = result.scalars().all()
    
    return [
        InsightResponse(
            id=i.id,
            dataset_id=i.dataset_id,
            insight_type=i.insight_type,
            severity=i.severity,
            severity_score=i.severity_score,
            title=i.title,
            description=i.description,
            affected_activity=i.affected_activity,
            affected_case_count=i.affected_case_count,
            metric_name=i.metric_name,
            metric_value=i.metric_value,
            is_acknowledged=i.is_acknowledged,
            created_at=i.created_at,
        )
        for i in insights
    ]


@router.get("/insights/summary")
async def get_global_insights_summary(
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Get aggregated insights summary across all datasets.
    """
    # Count by type
    type_result = await db.execute(
        select(Insight.insight_type, func.count())
        .group_by(Insight.insight_type)
    )
    by_type = {row[0]: row[1] for row in type_result}
    
    # Count by severity
    severity_result = await db.execute(
        select(Insight.severity, func.count())
        .group_by(Insight.severity)
    )
    by_severity = {row[0]: row[1] for row in severity_result}
    
    # Total and critical
    total_result = await db.execute(select(func.count()).select_from(Insight))
    total = total_result.scalar() or 0
    
    critical_result = await db.execute(
        select(func.count()).select_from(Insight).where(Insight.severity == "critical")
    )
    critical = critical_result.scalar() or 0
    
    unack_result = await db.execute(
        select(func.count()).select_from(Insight).where(Insight.is_acknowledged == False)
    )
    unacknowledged = unack_result.scalar() or 0
    
    return {
        "summary": {
            "total_insights": total,
            "by_type": by_type,
            "by_severity": by_severity,
            "critical_count": critical,
            "unacknowledged_count": unacknowledged,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.post("/insights/{insight_id}/acknowledge")
async def acknowledge_insight(
    insight_id: str,
    user_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    Mark an insight as acknowledged.
    """
    insight = await insight_service.acknowledge_insight(db, insight_id, user_id)
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    return {
        "message": "Insight acknowledged",
        "insight_id": insight_id,
        "acknowledged_at": insight.acknowledged_at.isoformat() if insight.acknowledged_at else None,
    }
