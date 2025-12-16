"""
Admin router - Database stats and visibility.

Provides endpoints for:
- Database entity counts
- Recent activity
- System health metrics
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, func, select

from ..database import get_db
from ..models import User, Upload, Mapping, Job, Dataset
from ..core import get_logger

log = get_logger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats")
async def get_database_stats(db: AsyncSession = Depends(get_db)) -> dict[str, Any]:
    """
    Get counts of all database entities.
    Useful for understanding data volume.
    """
    stats = {}
    
    # Count each table
    for model, name in [
        (User, "users"),
        (Upload, "uploads"),
        (Mapping, "mappings"),
        (Job, "jobs"),
        (Dataset, "datasets"),
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
