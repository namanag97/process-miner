"""Unified Ingestion Service - Single entry point for all ingestion operations.

Routes to the appropriate parser (PM4Py for XES, DuckDB for CSV) based on file type.
"""

import os
import time
from typing import Any

from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


def _log_validation(
    entity: str, is_valid: bool, errors: list[str] | None = None, field_count: int | None = None
) -> None:
    """Log validation to dev console (lazy import to avoid service->api dependency)."""
    try:
        from src.api.routers.dev_logs_stream import log_validation

        log_validation(entity=entity, is_valid=is_valid, errors=errors, field_count=field_count)
    except ImportError:
        pass


class UnifiedIngestionService:
    """Unified ingestion service that routes to PM4Py or DuckDB based on file type."""

    def __init__(self):
        # Lazy imports to avoid circular dependencies
        self._pm4py_service = None
        self._duckdb_service = None

    @property
    def pm4py_service(self):
        if self._pm4py_service is None:
            from .service import ingestion_service

            self._pm4py_service = ingestion_service
        return self._pm4py_service

    @property
    def duckdb_service(self):
        if self._duckdb_service is None:
            from .duckdb_parser import duckdb_parser

            self._duckdb_service = duckdb_parser
        return self._duckdb_service

    def detect_columns(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """Detect column mappings from a file.

        Routes to the appropriate service based on file extension.
        """
        start_time = time.perf_counter()
        ext = os.path.splitext(filename)[1].lower()

        logger.info(
            "unified_detect_columns_start",
            filename=filename,
            extension=ext,
            size_kb=len(file_content) / 1024,
        )

        try:
            if ext == ".csv":
                # Use DuckDB for CSV (10x faster)
                result = self.duckdb_service.detect_columns(file_content)
                response = {
                    "columns": result["columns"],
                    "suggestions": self._standardize_suggestions(result["suggestions"]),
                    "sample_rows": [],
                    "row_count": result["row_count"],
                }
            else:
                # Use PM4Py for XES and other formats
                result = self.pm4py_service.detect_columns(file_content)
                response = {
                    "columns": result.get("columns", []),
                    "suggestions": self._standardize_suggestions(result.get("suggestions", {})),
                    "sample_rows": result.get("sample_rows", []),
                    "row_count": result.get("row_count", 0),
                }

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            has_suggestions = bool(response.get("suggestions"))
            _log_validation(
                entity=f"file_{ext.lstrip('.')}",
                is_valid=has_suggestions,
                errors=[] if has_suggestions else ["No column suggestions found"],
                field_count=len(response.get("columns", [])),
            )

            logger.info(
                "unified_detect_columns_complete",
                filename=filename,
                extension=ext,
                columns_found=len(response.get("columns", [])),
                row_count=response.get("row_count", 0),
                duration_ms=duration_ms,
            )

            return response

        except Exception as e:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error(
                "unified_detect_columns_failed",
                filename=filename,
                error=str(e),
                duration_ms=duration_ms,
            )
            raise

    def parse(
        self,
        file_content: bytes,
        filename: str,
        case_id_col: str,
        activity_col: str,
        timestamp_col: str,
        resource_col: str | None = None,
    ) -> dict[str, Any]:
        """Parse a file and return structured event log data."""
        start_time = time.perf_counter()
        ext = os.path.splitext(filename)[1].lower()

        logger.info(
            "unified_parse_start",
            filename=filename,
            extension=ext,
            size_kb=len(file_content) / 1024,
            case_id_col=case_id_col,
            activity_col=activity_col,
        )

        required_cols = [case_id_col, activity_col, timestamp_col]
        missing_cols = [c for c in required_cols if not c]
        if missing_cols:
            _log_validation(
                entity="column_mapping",
                is_valid=False,
                errors=[
                    f"Missing required columns: {', '.join(['case_id', 'activity', 'timestamp'][i] for i, c in enumerate(required_cols) if not c)}"
                ],
            )
            raise ValueError("Missing required column mappings")

        _log_validation(entity="column_mapping", is_valid=True, field_count=len(required_cols))

        try:
            if ext == ".csv":
                # Use DuckDB for CSV (vectorized, fast)
                result = self.duckdb_service.parse_csv(
                    file_content=file_content,
                    case_id_col=case_id_col,
                    activity_col=activity_col,
                    timestamp_col=timestamp_col,
                    resource_col=resource_col,
                )
            else:
                # Use PM4Py for XES
                events_data = self.pm4py_service._parse_xes(file_content)

                cases = {}
                activities = set()
                for event in events_data:
                    case_id = event.get("case_id")
                    if case_id not in cases:
                        cases[case_id] = {"events": [], "start_time": None, "end_time": None}
                    cases[case_id]["events"].append(event)
                    activities.add(event.get("activity"))

                statistics = {
                    "total_cases": len(cases),
                    "total_events": len(events_data),
                    "total_activities": len(activities),
                    "activities": list(activities),
                }

                result = {
                    "statistics": statistics,
                    "events_data": events_data,
                    "cases_arrow": None,
                    "events_arrow": None,
                }

            duration_ms = int((time.perf_counter() - start_time) * 1000)

            logger.info(
                "unified_parse_complete",
                filename=filename,
                extension=ext,
                total_cases=result.get("statistics", {}).get("total_cases", 0),
                total_events=result.get("statistics", {}).get("total_events", 0),
                total_activities=result.get("statistics", {}).get("total_activities", 0),
                duration_ms=duration_ms,
            )

            return result

        except Exception as e:
            duration_ms = int((time.perf_counter() - start_time) * 1000)
            logger.error(
                "unified_parse_failed", filename=filename, error=str(e), duration_ms=duration_ms
            )
            raise

    def _standardize_suggestions(self, suggestions: dict[str, Any]) -> dict[str, Any]:
        """Standardize suggestion keys to snake_case."""
        standardized = {}
        key_mapping = {
            "caseId": "case_id_column",
            "caseID": "case_id_column",
            "caseIdColumn": "case_id_column",
            "case_id": "case_id_column",
            "case_id_column": "case_id_column",
            "activity": "activity_column",
            "activityColumn": "activity_column",
            "activity_column": "activity_column",
            "timestamp": "timestamp_column",
            "timestampColumn": "timestamp_column",
            "timestamp_column": "timestamp_column",
            "resource": "resource_column",
            "resourceColumn": "resource_column",
            "resource_column": "resource_column",
        }

        for key, value in suggestions.items():
            standardized_key = key_mapping.get(key, key)
            standardized[standardized_key] = value

        return standardized


# DEPRECATED: Singleton pattern - only use for stateless methods like detect_columns.
# For methods requiring session, create service with session via Container.
unified_ingestion_service = UnifiedIngestionService()
