"""Audit Router - Audit logging endpoints.

Track user actions for compliance and debugging.

## Business Context
Audit logging captures who did what and when:
- User actions (login, create, update, delete)
- API requests for compliance
- **Currently a stub** - returns empty data

## Testing Instructions
- **Get Logs**: `GET /api/v1/audit/logs?page=1&action_type=CREATE`
- **Create Log**: `POST /api/v1/audit/logs` (currently discards)

## Note
This is a placeholder implementation returning empty results.
Full audit logging would store records in a dedicated table.
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Query

from src.api.dependencies import CurrentUser
from src.infra.core.logging_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/audit", tags=["Audit"])


@router.get("/logs")
async def get_audit_logs(
    current_user: CurrentUser,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    action_type: str | None = Query(None),
    entity_type: str | None = Query(None),
) -> dict[str, Any]:
    """Get audit logs (stub - returns empty list)."""
    logger.debug(
        "audit_logs_requested",
        user_id=current_user.id,
        page=page,
        page_size=page_size,
    )

    return {
        "items": [],
        "total": 0,
        "page": page,
        "pageSize": page_size,
    }


@router.post("/logs")
async def create_audit_log(
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Create audit log entry (stub - accepts but discards)."""
    logger.debug("audit_log_created", user_id=current_user.id)

    return {
        "id": "stub-audit-log",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": "logged",
    }
