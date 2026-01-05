"""Data Viewer - Dev-only endpoint to inspect database records.

Provides endpoints to:
- List all tables in the database
- View records from any table
- Inspect specific record by ID

SECURITY: Only enabled in debug mode.
"""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import inspect, text

from src.platform.core.config import get_settings
from src.platform.infrastructure.database import get_session_context

router = APIRouter(prefix="/dev/data", tags=["DevData"])
settings = get_settings()


def _check_debug():
    """Ensure we're in debug mode."""
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Not found")


@router.get("/tables")
async def list_tables() -> list[str]:
    """List all tables in the database."""
    _check_debug()
    
    async with get_session_context() as session:
        result = await session.execute(text(
            "SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename"
        ))
        return [row[0] for row in result.fetchall()]


@router.get("/records/{table}")
async def get_records(
    table: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Get records from a table with pagination."""
    _check_debug()
    
    # Validate table name to prevent SQL injection
    if not table.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    async with get_session_context() as session:
        # Get total count
        count_result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
        total = count_result.scalar()
        
        # Get records (order by id desc if exists, otherwise no order)
        try:
            result = await session.execute(text(
                f"SELECT * FROM {table} ORDER BY id DESC LIMIT :limit OFFSET :offset"
            ), {"limit": limit, "offset": offset})
        except Exception:
            # Fallback if no 'id' column
            result = await session.execute(text(
                f"SELECT * FROM {table} LIMIT :limit OFFSET :offset"
            ), {"limit": limit, "offset": offset})
        
        columns = list(result.keys())
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
        
        return {
            "table": table,
            "total": total,
            "limit": limit,
            "offset": offset,
            "columns": columns,
            "records": rows,
        }


@router.get("/record/{table}/{record_id}")
async def get_record(table: str, record_id: str) -> dict[str, Any]:
    """Get a single record by ID."""
    _check_debug()
    
    if not table.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid table name")
    
    async with get_session_context() as session:
        result = await session.execute(text(
            f"SELECT * FROM {table} WHERE id = :id"
        ), {"id": record_id})
        
        row = result.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Record not found")
        
        columns = list(result.keys())
        return dict(zip(columns, row))
