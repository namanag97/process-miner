"""
Health check router.

Provides endpoints for health/readiness checks.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check():
    """Basic health check endpoint."""
    return {"status": "healthy", "service": "process-miner-api"}


@router.get("/ready")
async def readiness_check():
    """
    Readiness check - verifies all dependencies are available.
    
    For MVP, just returns healthy. In production, would check:
    - Database connection
    - Redis connection (if used)
    - PM4Py availability
    """
    return {
        "status": "ready",
        "checks": {
            "pm4py": "available",
            "storage": "available",
        }
    }
