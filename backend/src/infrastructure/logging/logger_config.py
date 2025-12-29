"""Logging configuration with JSON formatting and file rotation."""

import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Dict


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "client_ip"):
            log_data["client_ip"] = record.client_ip
        if hasattr(record, "query_params"):
            log_data["query_params"] = record.query_params
        if hasattr(record, "request_body"):
            log_data["request_body"] = record.request_body
        if hasattr(record, "response_body"):
            log_data["response_body"] = record.response_body
        if hasattr(record, "error"):
            log_data["error"] = record.error

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, default=str, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """Colored console formatter for better readability."""

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for console."""
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]

        # Build a readable message
        base_msg = f"{color}[{record.levelname}]{reset}"

        if hasattr(record, "method") and hasattr(record, "path"):
            status = getattr(record, "status_code", "")
            duration = getattr(record, "duration_ms", "")
            status_color = "\033[32m" if str(status).startswith("2") else "\033[31m"
            base_msg += f" {status_color}{status}{reset} {record.method} {record.path}"
            if duration:
                base_msg += f" ({duration:.2f}ms)"
        else:
            base_msg += f" {record.getMessage()}"

        return base_msg


def setup_logging(
    logs_dir: Path,
    log_level: str = "INFO",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
) -> None:
    """
    Set up logging configuration.

    Args:
        logs_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        max_bytes: Maximum size per log file before rotation
        backup_count: Number of backup files to keep
    """
    # Ensure logs directory exists
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Get root logger for API requests
    api_logger = logging.getLogger("api.requests")
    api_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    api_logger.handlers.clear()

    # JSON file handler with rotation
    log_file = logs_dir / "api_requests.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(JSONFormatter())
    file_handler.setLevel(logging.DEBUG)
    api_logger.addHandler(file_handler)

    # Console handler with colored output
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(ConsoleFormatter())
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    api_logger.addHandler(console_handler)

    # Prevent propagation to root logger
    api_logger.propagate = False

    api_logger.info(f"API logging initialized. Logs: {log_file}")


def get_api_logger() -> logging.Logger:
    """Get the API request logger."""
    return logging.getLogger("api.requests")
