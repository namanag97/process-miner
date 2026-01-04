"""Dev Logging Router - Development-only endpoint for frontend log aggregation.

Receives log entries from frontend and appends them to dev-logs/app.log.

BUG-037 FIX: Disabled in production to prevent log-bombing DoS attacks.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core.config import get_settings

router = APIRouter(prefix="/dev", tags=["Development"])
settings = get_settings()

# Log file path - PROJECT_ROOT/dev-logs/app.log
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent
LOG_DIR = PROJECT_ROOT / "dev-logs"
LOG_FILE = LOG_DIR / "app.log"

# BUG-037 FIX: Max log entry size to prevent memory attacks
MAX_MESSAGE_SIZE = 10 * 1024  # 10KB max per log message


class LogEntry(BaseModel):
    """Frontend log entry."""

    type: str  # FE-ACTION, API-REQ, API-RES, ERROR
    source: str  # e.g., "Button:Submit", "POST /api/logs"
    message: Any  # Payload/response data
    timestamp: str | None = None  # ISO timestamp, defaults to server time


@router.post("/log")
async def receive_log(entry: LogEntry) -> dict[str, str]:
    """Receive a log entry from frontend and append to dev-logs/app.log."""
    # BUG-037 FIX: Disable in production to prevent log-bombing DoS
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Not found")

    # BUG-037 FIX: Validate message size to prevent memory attacks
    msg_str = str(entry.message)
    if len(msg_str) > MAX_MESSAGE_SIZE:
        raise HTTPException(status_code=413, detail="Log message too large")

    # Ensure log directory exists
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Use provided timestamp or generate server time
    ts = entry.timestamp or datetime.now().isoformat()

    # Format message - truncate if too long
    msg = msg_str
    if len(msg) > 50:
        msg = msg[:47] + "..."

    # Format: [TIMESTAMP] [TYPE] [SOURCE] → MESSAGE
    line = f"[{ts}] [{entry.type}] [{entry.source}] → {msg}\n"

    # Append to log file
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)

    return {"status": "logged"}


@router.get("/logs")
async def get_logs(lines: int = 100) -> dict[str, Any]:
    """Get recent log entries (for debugging)."""
    # BUG-037 FIX: Disable in production
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Not found")

    if not LOG_FILE.exists():
        return {"lines": [], "total": 0}

    with open(LOG_FILE, encoding="utf-8") as f:
        all_lines = f.readlines()

    return {
        "lines": all_lines[-lines:],
        "total": len(all_lines),
    }


@router.delete("/logs")
async def clear_logs() -> dict[str, str]:
    """Clear the dev log file."""
    # BUG-037 FIX: Disable in production
    if not settings.debug:
        raise HTTPException(status_code=404, detail="Not found")

    if LOG_FILE.exists():
        LOG_FILE.unlink()
    return {"status": "cleared"}
