"""Unified Ingestion Service - Single entry point for all ingestion operations.

Provides a consistent interface that dispatches to the appropriate service
(PM4Py for XES, DuckDB for CSV) based on file type.

This solves the bifurcation problem where different code paths used different
services, leading to inconsistent column detection and parsing.
"""

import os
from typing import Any, Optional

from src.core.logging_config import get_logger
from src.services.duckdb_ingestion import duckdb_ingestion_service
from src.services.ingestion import ingestion_service

logger = get_logger(__name__)


class UnifiedIngestionService:
    """Unified ingestion service that routes to PM4Py or DuckDB based on file type.

    This ensures consistent behavior regardless of which API endpoint is used.
    """

    def __init__(self):
        self.pm4py_service = ingestion_service
        self.duckdb_service = duckdb_ingestion_service

    def detect_columns(self, file_content: bytes, filename: str) -> dict[str, Any]:
        """Detect column mappings from a file.

        Routes to the appropriate service based on file extension.
        Returns a standardized response with snake_case keys.

        Args:
            file_content: Raw file content
            filename: Original filename (used to determine file type)

        Returns:
            dict with keys: columns, suggestions, sample_rows, row_count
            All keys use snake_case for consistency.
        """
        ext = os.path.splitext(filename)[1].lower()

        logger.info("unified_detect_columns", filename=filename, extension=ext)

        if ext == ".csv":
            # Use DuckDB for CSV (10x faster)
            result = self.duckdb_service.detect_columns_fast(file_content)

            # Standardize response format
            return {
                "columns": [c["name"] for c in result["columns"]],
                "suggestions": self._standardize_suggestions(result["suggestions"]),
                "sample_rows": [],  # DuckDB doesn't return sample rows yet
                "row_count": result["row_count"],
            }
        else:
            # Use PM4Py for XES and other formats
            result = self.pm4py_service.detect_columns(file_content)

            # Ensure suggestions use snake_case
            return {
                "columns": result.get("columns", []),
                "suggestions": self._standardize_suggestions(result.get("suggestions", {})),
                "sample_rows": result.get("sample_rows", []),
                "row_count": result.get("row_count", 0),
            }

    def parse(
        self,
        file_content: bytes,
        filename: str,
        case_id_col: str,
        activity_col: str,
        timestamp_col: str,
        resource_col: Optional[str] = None,
    ) -> dict[str, Any]:
        """Parse a file and return structured event log data.

        Routes to the appropriate service based on file extension.
        Returns a standardized response.

        Args:
            file_content: Raw file content
            filename: Original filename
            case_id_col: Column name for case ID
            activity_col: Column name for activity
            timestamp_col: Column name for timestamp
            resource_col: Optional column name for resource

        Returns:
            dict with standardized keys (statistics, cases_arrow, events_arrow, etc.)
        """
        ext = os.path.splitext(filename)[1].lower()

        logger.info(
            "unified_parse",
            filename=filename,
            extension=ext,
            case_id_col=case_id_col,
            activity_col=activity_col,
        )

        if ext == ".csv":
            # Use DuckDB for CSV (vectorized, fast)
            return self.duckdb_service.parse_csv_fast(
                file_content=file_content,
                case_id_col=case_id_col,
                activity_col=activity_col,
                timestamp_col=timestamp_col,
                resource_col=resource_col,
            )
        else:
            # Use PM4Py for XES (standard library)
            # Parse using PM4Py service and return standardized format
            events_data = self.pm4py_service._parse_xes(file_content)
            
            # Compute statistics manually from events
            cases = {}
            activities = set()
            for event in events_data:
                case_id = event.get("case_id")
                if case_id not in cases:
                    cases[case_id] = {"events": [], "start_time": None, "end_time": None}
                cases[case_id]["events"].append(event)
                activities.add(event.get("activity"))
            
            # Build statistics
            statistics = {
                "total_cases": len(cases),
                "total_events": len(events_data),
                "total_activities": len(activities),
                "activities": list(activities),
            }
            
            return {
                "statistics": statistics,
                "events_data": events_data,  # Raw events for DB insert
                "cases_arrow": None,  # XES doesn't use Arrow path
                "events_arrow": None,
            }

    def _standardize_suggestions(self, suggestions: dict[str, Any]) -> dict[str, Any]:
        """Standardize suggestion keys to use snake_case.

        Converts camelCase keys to snake_case for consistency across services.

        Args:
            suggestions: Raw suggestions dict (may have camelCase or snake_case)

        Returns:
            dict with snake_case keys
        """
        standardized = {}

        # Map common camelCase to snake_case
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


# Singleton instance
unified_ingestion_service = UnifiedIngestionService()
