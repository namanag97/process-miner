"""Data Ingestion Service - CSV/XES parsing.

Ported from: src/application/support/ingestion_service.py
Simplified: Removed aggregates, event bus, ports - direct data processing.
"""

import csv
import io
import json
import os
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from pm4py.objects.log.importer.xes import importer as xes_importer
from sqlalchemy.ext.asyncio import AsyncSession

from src.features.process_mining.models import (
    Dataset,
    DatasetStatus,
    ProcessCase,
    ProcessEvent,
    UploadedFile,
)
from src.platform.core.exceptions import ValidationError
from src.platform.core.logging_config import get_logger

logger = get_logger(__name__)


class IngestionService:
    """
    Data Ingestion Service.
    Handles CSV, XES file parsing and event log creation.
    """

    async def ingest_csv(
        self,
        session: AsyncSession,
        file_content: bytes,
        filename: str,
        name: str | None = None,
        case_id_col: str = "case_id",
        activity_col: str = "activity",
        timestamp_col: str = "timestamp",
        resource_col: str | None = None,
        delimiter: str = ",",
        precomputed_stats: dict[str, Any] | None = None,
    ) -> Dataset:
        """
        Ingest a CSV file as an event log.

        Returns:
            EventLog ORM model (persisted to database)
        """
        # Parse CSV into events
        events_data = self._parse_csv(
            file_content,
            case_id_col,
            activity_col,
            timestamp_col,
            resource_col,
            delimiter,
        )

        # Create dataset
        dataset_name = name or Path(filename).stem
        dataset = await self._create_dataset(
            session,
            name=dataset_name,
            source_file=filename,
            source_format="csv",
            events_data=events_data,
            precomputed_stats=precomputed_stats,
        )

        # Store the file and create UploadedFile record
        await self._store_file(session, file_content, filename, dataset.id)

        return dataset

    async def ingest_xes(
        self,
        session: AsyncSession,
        file_content: bytes,
        filename: str,
        name: str | None = None,
    ) -> Dataset:
        """
        Ingest an XES file as an event log.
        """
        # Parse XES using PM4Py
        events_data = self._parse_xes(file_content)

        # Create dataset
        dataset_name = name or Path(filename).stem
        dataset = await self._create_dataset(
            session,
            name=dataset_name,
            source_file=filename,
            source_format="xes",
            events_data=events_data,
        )

        # Store the file and create UploadedFile record
        await self._store_file(session, file_content, filename, dataset.id)

        return dataset

    async def ingest_file(
        self,
        session: AsyncSession,
        file_content: bytes,
        filename: str,
        name: str | None = None,
        case_id_col: str | None = None,
        activity_col: str | None = None,
        timestamp_col: str | None = None,
        resource_col: str | None = None,
        precomputed_stats: dict[str, Any] | None = None,
    ) -> Dataset:
        """
        Ingest a file, auto-detecting format.
        """
        extension = Path(filename).suffix.lower()
        logger.info("ingest_file_started", filename=filename, extension=extension, name=name)
        start_time = time.perf_counter()

        if extension == ".xes":
            result = await self.ingest_xes(session, file_content, filename, name)
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "ingest_file_completed",
                dataset_id=result.id,
                format="xes",
                total_events=result.total_events,
                total_cases=result.total_cases,
                duration_ms=round(duration_ms, 2),
            )
            return result
        if extension in [".csv", ".txt"]:
            # Auto-detect columns if not provided
            if not all([case_id_col, activity_col, timestamp_col]):
                detection = self.detect_columns(file_content)
                suggestions = detection.get("suggestions", {})

                case_id_col = case_id_col or suggestions.get("case_id")
                activity_col = activity_col or suggestions.get("activity")
                timestamp_col = timestamp_col or suggestions.get("timestamp")
                resource_col = resource_col or suggestions.get("resource")

                if not case_id_col:
                    raise ValidationError(
                        f"Could not detect case_id column. Available: {detection['columns']}",
                        field="case_id_column",
                    )
                if not activity_col:
                    raise ValidationError(
                        f"Could not detect activity column. Available: {detection['columns']}",
                        field="activity_column",
                    )
                if not timestamp_col:
                    raise ValidationError(
                        f"Could not detect timestamp column. Available: {detection['columns']}",
                        field="timestamp_column",
                    )

            logger.debug(
                "csv_columns_detected",
                case_id_col=case_id_col,
                activity_col=activity_col,
                timestamp_col=timestamp_col,
            )

            result = await self.ingest_csv(
                session,
                file_content,
                filename,
                name,
                case_id_col,
                activity_col,
                timestamp_col,
                resource_col,
                precomputed_stats=precomputed_stats,
            )
            duration_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                "ingest_file_completed",
                dataset_id=result.id,
                format="csv",
                total_events=result.total_events,
                total_cases=result.total_cases,
                duration_ms=round(duration_ms, 2),
            )
            return result
        logger.warning("unsupported_file_format", extension=extension)
        raise ValidationError(f"Unsupported file format: {extension}")

    async def store_only(
        self,
        session: AsyncSession,
        file_content: bytes,
        filename: str,
        name: str | None = None,
        project_id: str | None = None,
    ) -> Dataset:
        """
        Store file without parsing (Phase 1 of deferred ingestion).

        Creates Dataset with status=UNSTRUCTURED and stores raw file.
        User must call /ingest endpoint with mapping to trigger parsing.

        Returns:
            Dataset with status=UNSTRUCTURED
        """
        import hashlib

        from src.platform.storage.storage import storage_service

        logger.info("store_only_started", filename=filename, name=name)
        start_time = time.perf_counter()

        extension = Path(filename).suffix.lower()
        log_name = name or Path(filename).stem

        # Create dataset record (UNSTRUCTURED - no stats yet)
        dataset = Dataset(
            name=log_name,
            source_file=filename,
            source_format=extension.lstrip("."),
            status=DatasetStatus.UNSTRUCTURED.value,
            project_id=project_id,
            total_cases=0,
            total_events=0,
            total_activities=0,
        )
        session.add(dataset)
        await session.flush()

        # Store raw file
        storage_path = await storage_service.store_dataset_file(file_content, dataset.id, filename)

        # Create UploadedFile record
        uploaded_file = UploadedFile(
            dataset_id=dataset.id,
            filename=filename,
            storage_path=storage_path,
            size_bytes=len(file_content),
            checksum=hashlib.sha256(file_content).hexdigest(),
        )
        session.add(uploaded_file)
        await session.flush()
        await session.refresh(dataset)

        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(
            "store_only_completed",
            dataset_id=dataset.id,
            storage_path=storage_path,
            duration_ms=round(duration_ms, 2),
        )

        return dataset

    def detect_columns(
        self,
        file_content: bytes,
        delimiter: str = ",",
    ) -> dict[str, Any]:
        """
        Detect column types from a CSV file.
        Returns suggested column mappings.

        Performance: Only reads first 100KB or 100 lines (whichever comes first)
        to avoid processing large files unnecessarily.
        """
        # Only read first 100KB for column detection (header + sample rows)
        MAX_BYTES = 100 * 1024  # 100KB
        chunk = file_content[:MAX_BYTES]

        # Decode only the chunk we need
        try:
            text = chunk.decode("utf-8")
        except UnicodeDecodeError:
            # If chunk cuts mid-character, try slightly smaller
            text = chunk[:-100].decode("utf-8", errors="ignore")

        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

        columns = reader.fieldnames or []
        sample_rows = []
        for i, row in enumerate(reader):
            if i >= 5:
                break
            sample_rows.append(row)

        suggestions = {
            "case_id": None,
            "activity": None,
            "timestamp": None,
            "resource": None,
        }

        # Common column name patterns
        case_patterns = [
            "case_id",
            "case:concept:name",
            "caseid",
            "case",
            "trace_id",
            "traceid",
            "trace",
            "process_id",
        ]
        activity_patterns = [
            "activity_name",
            "concept:name",
            "activity",
            "event_name",
            "event",
            "action",
            "task",
        ]
        timestamp_patterns = [
            "time:timestamp",
            "timestamp",
            "start_time",
            "event_time",
            "time",
            "datetime",
            "date",
        ]
        resource_patterns = [
            "org:resource",
            "resource",
            "user",
            "actor",
            "agent",
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

    async def _create_dataset(
        self,
        session: AsyncSession,
        name: str,
        source_file: str,
        source_format: str,
        events_data: list[dict[str, Any]],
        precomputed_stats: dict[str, Any] | None = None,
    ) -> Dataset:
        """Create Dataset with cases and events from parsed data."""

        # Group events by case
        cases_dict: dict[str, list[dict]] = {}
        for event in events_data:
            case_id = event["case_id"]
            if case_id not in cases_dict:
                cases_dict[case_id] = []
            cases_dict[case_id].append(event)

        # Collect unique activities
        activities = sorted({e["activity"] for e in events_data})

        # Create dataset with READY status (data fully parsed)
        dataset = Dataset(
            name=name,
            source_file=source_file,
            source_format=source_format,
            total_cases=len(cases_dict),
            total_events=len(events_data),
            total_activities=len(activities),
            activities_json=json.dumps(activities),
            statistics_json=json.dumps(precomputed_stats) if precomputed_stats else None,
            status=DatasetStatus.READY.value,  # FIX: Explicitly set status after successful parsing
        )
        session.add(dataset)
        # Flush to ensure dataset.id is populated before creating related objects
        await session.flush()

        # Create cases and events
        for case_id, case_events in cases_dict.items():
            # Sort by timestamp
            case_events.sort(key=lambda e: e["timestamp"])

            # Create variant key (activity sequence)
            variant_key = " -> ".join(e["activity"] for e in case_events)

            # Parse timestamps for start/end
            timestamps = [self._parse_timestamp(e["timestamp"]) for e in case_events]

            case = ProcessCase(
                dataset_id=dataset.id,
                case_id=case_id,
                variant_key=variant_key,
                start_time=min(timestamps) if timestamps else None,
                end_time=max(timestamps) if timestamps else None,
            )
            session.add(case)
            # Flush to ensure case.id is populated before creating events
            await session.flush()

            for event_data in case_events:
                # Extract attributes (non-standard fields)
                attributes = {
                    k: v
                    for k, v in event_data.items()
                    if k not in ["case_id", "activity", "timestamp", "resource"]
                }

                event = ProcessEvent(
                    case_ref_id=case.id,
                    activity=event_data["activity"],
                    timestamp=self._parse_timestamp(event_data["timestamp"]),
                    resource=event_data.get("resource"),
                    attributes_json=json.dumps(attributes) if attributes else None,
                )
                session.add(event)

        await session.flush()
        await session.refresh(dataset)

        return dataset

    def _parse_csv(
        self,
        content: bytes,
        case_id_col: str,
        activity_col: str,
        timestamp_col: str,
        resource_col: str | None,
        delimiter: str,
    ) -> list[dict[str, Any]]:
        """Parse CSV content into event data."""
        text = content.decode("utf-8")
        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)

        columns = reader.fieldnames or []

        # Validate columns exist
        missing = []
        if case_id_col not in columns:
            missing.append(f"case_id_column '{case_id_col}'")
        if activity_col not in columns:
            missing.append(f"activity_column '{activity_col}'")
        if timestamp_col not in columns:
            missing.append(f"timestamp_column '{timestamp_col}'")

        if missing:
            raise ValidationError(f"Columns not found: {', '.join(missing)}. Available: {columns}")

        events = []
        for row in reader:
            case_id = row.get(case_id_col, "").strip()
            activity = row.get(activity_col, "").strip()
            timestamp = row.get(timestamp_col, "").strip()

            if not case_id or not activity or not timestamp:
                continue

            event = {
                "case_id": case_id,
                "activity": activity,
                "timestamp": timestamp,
            }

            if resource_col and resource_col in row:
                resource = row[resource_col]
                if resource and resource.strip():
                    event["resource"] = resource.strip()

            # Add other columns as attributes
            for key, value in row.items():
                if key not in [case_id_col, activity_col, timestamp_col, resource_col]:
                    event[key] = value

            events.append(event)

        if not events:
            raise ValidationError("No valid events found in CSV. Check column mappings.")

        return events

    def _parse_xes(self, content: bytes) -> list[dict[str, Any]]:
        """Parse XES content into event data using PM4Py."""
        with tempfile.NamedTemporaryFile(suffix=".xes", delete=False) as f:
            f.write(content)
            temp_path = f.name

        try:
            pm4py_log = xes_importer.apply(temp_path)

            events = []
            for trace in pm4py_log:
                case_id = trace.attributes.get("concept:name", "")
                for event in trace:
                    events.append(
                        {
                            "case_id": case_id,
                            "activity": event.get("concept:name", ""),
                            "timestamp": event.get("time:timestamp", ""),
                            "resource": event.get("org:resource"),
                        }
                    )

            return events
        finally:
            os.unlink(temp_path)

    def _parse_timestamp(self, value: Any) -> datetime:
        """Parse timestamp from various formats."""
        if isinstance(value, datetime):
            return value

        if isinstance(value, str):
            # Try common formats
            formats = [
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d",
                "%d/%m/%Y %H:%M:%S",
                "%m/%d/%Y %H:%M:%S",
            ]
            for fmt in formats:
                try:
                    return datetime.strptime(value.replace("Z", "+0000"), fmt)
                except ValueError:
                    continue

            # Fallback: try parsing with dateutil if available
            try:
                from dateutil import parser

                return parser.parse(value)
            except Exception:
                pass

        raise ValidationError(f"Cannot parse timestamp: {value}")

    async def _store_file(
        self,
        session,
        content: bytes,
        filename: str,
        dataset_id: str,
        mime_type: str | None = None,
    ) -> str:
        """Store uploaded file and create UploadedFile record."""
        import hashlib

        from src.features.process_mining.models import UploadedFile
        from src.platform.storage.storage import storage_service

        # Store to filesystem/S3
        storage_path = await storage_service.store_dataset_file(content, dataset_id, filename)

        # Create DB record
        uploaded_file = UploadedFile(
            dataset_id=dataset_id,
            filename=filename,
            storage_path=storage_path,
            size_bytes=len(content),
            mime_type=mime_type,
            checksum=hashlib.sha256(content).hexdigest(),
        )
        session.add(uploaded_file)

        return storage_path


# Singleton instance
ingestion_service = IngestionService()
