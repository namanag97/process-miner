"""Data Ingestion Service - ETL Pipeline."""

from typing import Optional, Dict, Any, BinaryIO, List
from uuid import UUID
from pathlib import Path
from datetime import datetime
import csv
import io

import pm4py
from pm4py.objects.log.importer.xes import importer as xes_importer

from src.domain.entities import EventLog
from src.domain.value_objects import ColumnMapping, LogFormat
from src.domain.aggregates import EventLogAggregate
from src.infrastructure.storage.file_storage import file_storage
from src.infrastructure.messaging.event_bus import publish_events


class IngestionService:
    """
    Data Ingestion Service.
    Handles CSV, XES file parsing and event log creation.
    """
    
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
        file_path = await file_storage.upload_log_bytes(
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
        await publish_events(aggregate.pop_events())
        
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
        file_path = await file_storage.upload_log_bytes(
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
        await publish_events(aggregate.pop_events())
        
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
        """
        extension = Path(filename).suffix.lower()
        
        if extension == ".xes":
            return await self.ingest_xes(file_content, filename, name)
        elif extension in [".csv", ".txt"]:
            mapping = None
            if column_mapping:
                mapping = ColumnMapping(
                    case_id=column_mapping.get("case_id", "case:concept:name"),
                    activity=column_mapping.get("activity", "concept:name"),
                    timestamp=column_mapping.get("timestamp", "time:timestamp"),
                    resource=column_mapping.get("resource"),
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
        
        # Common column name patterns
        case_patterns = ["case", "case_id", "case:concept:name", "caseid", "trace"]
        activity_patterns = ["activity", "concept:name", "event", "action", "task"]
        timestamp_patterns = ["timestamp", "time:timestamp", "time", "date", "datetime"]
        resource_patterns = ["resource", "org:resource", "user", "actor", "agent"]
        
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
        
        events = []
        for row in reader:
            event = {
                "case_id": row.get(mapping.case_id, ""),
                "activity": row.get(mapping.activity, ""),
                "timestamp": row.get(mapping.timestamp, ""),
            }
            
            if mapping.resource and mapping.resource in row:
                event["resource"] = row[mapping.resource]
            
            # Add other columns as attributes
            for key, value in row.items():
                if key not in [mapping.case_id, mapping.activity, mapping.timestamp, mapping.resource]:
                    event[key] = value
            
            events.append(event)
        
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
                    events.append({
                        "case_id": case_id,
                        "activity": event.get("concept:name", ""),
                        "timestamp": event.get("time:timestamp", ""),
                        "resource": event.get("org:resource", ""),
                    })
            
            return events
        finally:
            import os
            os.unlink(temp_path)


# Singleton instance
ingestion_service = IngestionService()
