"""Data Ingestion Service - ETL Pipeline."""

import csv
import io
from pathlib import Path
from typing import Any, Dict, List, Optional

from pm4py.objects.log.importer.xes import importer as xes_importer

from src.application.ports import EventBusPort, FileStoragePort
from src.domain.aggregates import EventLogAggregate
from src.domain.value_objects import ColumnMapping


class IngestionService:
    """
    Data Ingestion Service.
    Handles CSV, XES file parsing and event log creation.
    """

    def __init__(
        self,
        file_storage: FileStoragePort,
        event_bus: EventBusPort,
    ):
        """Initialize with injected dependencies."""
        self._file_storage = file_storage
        self._event_bus = event_bus

    async def ingest_csv(
        self,
        file_content: bytes,
        filename: str,
        name: Optional[str] = None,
        column_mapping: Optional[ColumnMapping] = None,
        delimiter: str = ",",
    ) -> EventLogAggregate:
        """
        Ingest a CSV file as an event log.

        Args:
            file_content: Raw CSV file bytes
            filename: Original filename
            name: Name for the event log
            column_mapping: Mapping of columns to event fields
            delimiter: CSV delimiter

        Returns:
            EventLogAggregate with the ingested log
        """
        # Create aggregate
        log_name = name or Path(filename).stem
        aggregate = EventLogAggregate.create(
            name=log_name,
            source_file=filename,
        )

        # Store the file
        file_path = await self._file_storage.upload_log_bytes(
            content=file_content,
            filename=filename,
            log_id=aggregate.log.id,
        )
        aggregate.log.source_file = file_path

        # Parse CSV
        mapping = column_mapping or ColumnMapping()
        events_data = self._parse_csv(file_content, mapping, delimiter)

        # Ingest events
        aggregate.ingest_events(events_data)

        # Publish domain events
        await self._event_bus.publish_all(aggregate.pop_events())

        return aggregate

    async def ingest_xes(
        self,
        file_content: bytes,
        filename: str,
        name: Optional[str] = None,
    ) -> EventLogAggregate:
        """
        Ingest an XES file as an event log.
        """
        # Create aggregate
        log_name = name or Path(filename).stem
        aggregate = EventLogAggregate.create(
            name=log_name,
            source_file=filename,
        )

        # Store the file
        file_path = await self._file_storage.upload_log_bytes(
            content=file_content,
            filename=filename,
            log_id=aggregate.log.id,
        )
        aggregate.log.source_file = file_path

        # Parse XES using PM4Py
        events_data = self._parse_xes(file_content)

        # Ingest events
        aggregate.ingest_events(events_data)

        # Publish domain events
        await self._event_bus.publish_all(aggregate.pop_events())

        return aggregate

    async def ingest_file(
        self,
        file_content: bytes,
        filename: str,
        name: Optional[str] = None,
        column_mapping: Optional[Dict[str, str]] = None,
    ) -> EventLogAggregate:
        """
        Ingest a file automatically detecting format.
        If no column_mapping is provided for CSV files, auto-detect columns.
        """
        extension = Path(filename).suffix.lower()

        if extension == ".xes":
            return await self.ingest_xes(file_content, filename, name)
        elif extension in [".csv", ".txt"]:
            # Build or auto-detect column mapping
            mapping = None
            placeholder_values = ["string", "null", "none", ""]

            if column_mapping:
                # Filter out placeholder values from Swagger UI
                filtered_mapping = {}
                for key in ["case_id", "activity", "timestamp", "resource"]:
                    value = column_mapping.get(key)
                    if value and value.lower() not in placeholder_values:
                        filtered_mapping[key] = value

                # Only use explicit mapping if valid values were provided
                if filtered_mapping:
                    # Auto-detect missing required columns
                    if len(filtered_mapping) < 3:  # Need at least case_id, activity, timestamp
                        detection = self.detect_columns(file_content)
                        suggestions = detection.get("suggestions", {})

                        if "case_id" not in filtered_mapping and suggestions.get("case_id"):
                            filtered_mapping["case_id"] = suggestions["case_id"]
                        if "activity" not in filtered_mapping and suggestions.get("activity"):
                            filtered_mapping["activity"] = suggestions["activity"]
                        if "timestamp" not in filtered_mapping and suggestions.get("timestamp"):
                            filtered_mapping["timestamp"] = suggestions["timestamp"]
                        if "resource" not in filtered_mapping and suggestions.get("resource"):
                            filtered_mapping["resource"] = suggestions["resource"]

                    mapping = ColumnMapping(
                        case_id=filtered_mapping.get("case_id", "case:concept:name"),
                        activity=filtered_mapping.get("activity", "concept:name"),
                        timestamp=filtered_mapping.get("timestamp", "time:timestamp"),
                        resource=filtered_mapping.get("resource"),
                    )

            # If no mapping, auto-detect from file
            if mapping is None:
                detection = self.detect_columns(file_content)
                suggestions = detection.get("suggestions", {})
                columns = detection.get("columns", [])

                # Check if we detected required columns
                if not suggestions.get("case_id"):
                    raise ValueError(
                        f"Could not auto-detect case_id column. Please specify case_id_column. "
                        f"Available columns: {columns}"
                    )
                if not suggestions.get("activity"):
                    raise ValueError(
                        f"Could not auto-detect activity column. Please specify activity_column. "
                        f"Available columns: {columns}"
                    )
                if not suggestions.get("timestamp"):
                    raise ValueError(
                        f"Could not auto-detect timestamp column. Please specify timestamp_column. "
                        f"Available columns: {columns}"
                    )

                mapping = ColumnMapping(
                    case_id=suggestions.get("case_id", "case:concept:name"),
                    activity=suggestions.get("activity", "concept:name"),
                    timestamp=suggestions.get("timestamp", "time:timestamp"),
                    resource=suggestions.get("resource"),
                )

            return await self.ingest_csv(file_content, filename, name, mapping)
        else:
            raise ValueError(f"Unsupported file format: {extension}")

    def detect_columns(
        self,
        file_content: bytes,
        delimiter: str = ",",
    ) -> Dict[str, Any]:
        """
        Detect column types from a CSV file.
        Returns suggested column mappings.
        """
        text = file_content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

        columns = reader.fieldnames or []
        sample_rows = []
        for i, row in enumerate(reader):
            if i >= 5:
                break
            sample_rows.append(row)

        # Detect likely mappings
        suggestions = {
            "case_id": None,
            "activity": None,
            "timestamp": None,
            "resource": None,
        }

        # Common column name patterns (order matters - more specific patterns first)
        case_patterns = [
            "case_id",
            "case:concept:name",
            "caseid",
            "case-id",
            "case",
            "trace_id",
            "traceid",
            "trace",
            "process_id",
            "processid",
        ]
        activity_patterns = [
            "activity_name",
            "activityname",
            "concept:name",
            "activity",
            "event_name",
            "eventname",
            "event",
            "action",
            "task",
            "step",
        ]
        timestamp_patterns = [
            "time:timestamp",
            "timestamp",
            "start_time",
            "starttime",
            "event_time",
            "eventtime",
            "time",
            "datetime",
            "date",
        ]
        resource_patterns = [
            "org:resource",
            "resource",
            "user_name",
            "username",
            "user",
            "actor",
            "agent",
            "worker",
            "performer",
            "assigned_to",
        ]

        for col in columns:
            col_lower = col.lower()

            if not suggestions["case_id"] and any(p in col_lower for p in case_patterns):
                suggestions["case_id"] = col
            if not suggestions["activity"] and any(p in col_lower for p in activity_patterns):
                suggestions["activity"] = col
            if not suggestions["timestamp"] and any(p in col_lower for p in timestamp_patterns):
                suggestions["timestamp"] = col
            if not suggestions["resource"] and any(p in col_lower for p in resource_patterns):
                suggestions["resource"] = col

        return {
            "columns": columns,
            "suggestions": suggestions,
            "sample_rows": sample_rows,
            "row_count": len(sample_rows),
        }

    def validate_log(self, aggregate: EventLogAggregate) -> Dict[str, Any]:
        """
        Validate an ingested event log.
        Returns validation results and warnings.
        """
        log = aggregate.log
        issues = []
        warnings = []

        # Check for empty log
        if log.total_cases == 0:
            issues.append("Event log has no cases")

        if log.total_events == 0:
            issues.append("Event log has no events")

        # Check for cases with single events
        single_event_cases = sum(1 for c in log.cases if len(c.events) == 1)
        if single_event_cases > log.total_cases * 0.5:
            warnings.append(f"{single_event_cases} cases have only one event")

        # Check for unusual timestamps
        start, end = log.date_range
        if start and end:
            duration_days = (end - start).days
            if duration_days > 3650:  # 10 years
                warnings.append(f"Date range spans {duration_days} days")

        # Check for duplicate events
        seen = set()
        duplicates = 0
        for case in log.cases:
            for event in case.events:
                key = (event.case_id, str(event.activity), event.timestamp.to_iso())
                if key in seen:
                    duplicates += 1
                seen.add(key)

        if duplicates > 0:
            warnings.append(f"Found {duplicates} potential duplicate events")

        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "statistics": aggregate.get_statistics(),
        }

    def _parse_csv(
        self,
        content: bytes,
        mapping: ColumnMapping,
        delimiter: str,
    ) -> List[Dict[str, Any]]:
        """Parse CSV content into event data."""
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

        columns = reader.fieldnames or []

        # Validate that required columns exist in the CSV
        missing_columns = []
        placeholder_values = ["string", "null", "none", ""]

        # Check for placeholder values that Swagger UI sends
        if mapping.case_id.lower() in placeholder_values:
            raise ValueError(
                f"Invalid case_id_column value: '{mapping.case_id}'. "
                f"Please specify an actual column name from your CSV. Available columns: {columns}"
            )
        if mapping.activity.lower() in placeholder_values:
            raise ValueError(
                f"Invalid activity_column value: '{mapping.activity}'. "
                f"Please specify an actual column name from your CSV. Available columns: {columns}"
            )
        if mapping.timestamp.lower() in placeholder_values:
            raise ValueError(
                f"Invalid timestamp_column value: '{mapping.timestamp}'. "
                f"Please specify an actual column name from your CSV. Available columns: {columns}"
            )

        # Validate columns exist in CSV
        if mapping.case_id not in columns:
            missing_columns.append(f"case_id_column '{mapping.case_id}'")
        if mapping.activity not in columns:
            missing_columns.append(f"activity_column '{mapping.activity}'")
        if mapping.timestamp not in columns:
            missing_columns.append(f"timestamp_column '{mapping.timestamp}'")
        if (
            mapping.resource
            and mapping.resource.lower() not in placeholder_values
            and mapping.resource not in columns
        ):
            missing_columns.append(f"resource_column '{mapping.resource}'")

        if missing_columns:
            raise ValueError(
                f"Column(s) not found in CSV: {', '.join(missing_columns)}. "
                f"Available columns: {columns}"
            )

        events = []
        row_number = 1  # Start at 1 for header row
        for row in reader:
            row_number += 1
            case_id = row.get(mapping.case_id, "").strip()
            activity = row.get(mapping.activity, "").strip()
            timestamp = row.get(mapping.timestamp, "").strip()

            # Skip rows with empty required fields and collect warnings
            if not case_id:
                continue  # Skip rows without case_id
            if not activity:
                continue  # Skip rows without activity
            if not timestamp:
                continue  # Skip rows without timestamp

            event = {
                "case_id": case_id,
                "activity": activity,
                "timestamp": timestamp,
            }

            if mapping.resource and mapping.resource in row:
                resource_val = row[mapping.resource]
                if resource_val and resource_val.strip():
                    event["resource"] = resource_val.strip()

            # Add other columns as attributes
            for key, value in row.items():
                if key not in [
                    mapping.case_id,
                    mapping.activity,
                    mapping.timestamp,
                    mapping.resource,
                ]:
                    event[key] = value

            events.append(event)

        if not events:
            raise ValueError(
                f"No valid events found in CSV. Please check that your column mappings are correct. "
                f"Mapped columns: case_id='{mapping.case_id}', activity='{mapping.activity}', "
                f"timestamp='{mapping.timestamp}'"
            )

        return events

    def _parse_xes(self, content: bytes) -> List[Dict[str, Any]]:
        """Parse XES content into event data using PM4Py."""
        # Save to temp file for PM4Py
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".xes", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            # Import using PM4Py
            pm4py_log = xes_importer.apply(temp_path)

            # Convert to our format
            events = []
            for trace in pm4py_log:
                case_id = trace.attributes.get("concept:name", "")
                for event in trace:
                    events.append(
                        {
                            "case_id": case_id,
                            "activity": event.get("concept:name", ""),
                            "timestamp": event.get("time:timestamp", ""),
                            "resource": event.get("org:resource", ""),
                        }
                    )

            return events
        finally:
            import os

            os.unlink(temp_path)


# Note: Service instances are created in src.infrastructure.container
