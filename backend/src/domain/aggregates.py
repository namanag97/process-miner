"""Domain Aggregates - Consistency boundaries for domain entities."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Any
from uuid import UUID, uuid4

from src.domain.entities import (
    EventLog,
    ProcessCase,
    ProcessEvent,
    ProcessModel,
    ConformanceResult,
    PerformanceMetrics,
    Variant,
)
from src.domain.events import (
    DomainEvent,
    LogIngested,
    ModelDiscovered,
    ConformanceChecked,
    PerformanceAnalyzed,
)
from src.domain.value_objects import MinerType, ModelFormat


@dataclass
class EventLogAggregate:
    """
    Aggregate root for Event Log bounded context.
    Manages the consistency of an event log and its cases.
    """
    log: EventLog
    _pending_events: list[DomainEvent] = field(default_factory=list)
    
    @classmethod
    def create(cls, name: str, source_file: Optional[str] = None) -> "EventLogAggregate":
        """Factory method to create a new event log aggregate."""
        log = EventLog.create(name=name, source_file=source_file)
        return cls(log=log)
    
    @classmethod
    def reconstitute(cls, log: EventLog) -> "EventLogAggregate":
        """Reconstitute an aggregate from stored data."""
        return cls(log=log)
    
    def ingest_events(self, events_data: list[dict[str, Any]]) -> None:
        """
        Ingest raw event data into the log.
        Events are grouped by case_id and sorted by timestamp.
        """
        # Group events by case
        case_events: dict[str, list[dict]] = {}
        for event_data in events_data:
            case_id = event_data.get("case_id", event_data.get("case:concept:name", "unknown"))
            if case_id not in case_events:
                case_events[case_id] = []
            case_events[case_id].append(event_data)
        
        # Create cases with events
        for case_id, events in case_events.items():
            case = ProcessCase.create(case_id=str(case_id))
            
            for event_data in events:
                activity = event_data.get("activity", event_data.get("concept:name", "unknown"))
                timestamp = event_data.get("timestamp", event_data.get("time:timestamp"))
                resource = event_data.get("resource", event_data.get("org:resource"))
                
                if isinstance(timestamp, str):
                    from dateutil import parser
                    timestamp = parser.parse(timestamp)
                
                event = ProcessEvent.create(
                    case_id=str(case_id),
                    activity=activity,
                    timestamp=timestamp,
                    resource=resource,
                )
                case.add_event(event)
            
            self.log.add_case(case)
        
        # Emit domain event
        self._pending_events.append(LogIngested(
            log_id=self.log.id,
            log_name=self.log.name,
            total_cases=self.log.total_cases,
            total_events=self.log.total_events,
            source_file=self.log.source_file,
        ))
    
    def get_variants(self) -> list[Variant]:
        """Get all variants in the log."""
        return self.log.variants
    
    def get_statistics(self) -> dict[str, Any]:
        """Get log statistics."""
        start, end = self.log.date_range
        return {
            "total_cases": self.log.total_cases,
            "total_events": self.log.total_events,
            "unique_activities": len(self.log.activities),
            "unique_resources": len(self.log.resources),
            "variant_count": len(self.log.variants),
            "start_date": start.isoformat() if start else None,
            "end_date": end.isoformat() if end else None,
        }
    
    def pop_events(self) -> list[DomainEvent]:
        """Pop pending domain events for publishing."""
        events = self._pending_events.copy()
        self._pending_events.clear()
        return events


@dataclass
class ProcessModelAggregate:
    """
    Aggregate root for Process Model bounded context.
    Manages process models and their lifecycle.
    """
    model: ProcessModel
    _pending_events: list[DomainEvent] = field(default_factory=list)
    
    @classmethod
    def create_from_discovery(
        cls,
        name: str,
        source_log_id: UUID,
        miner_type: MinerType,
        model_format: ModelFormat,
        model_data: Any = None,
    ) -> "ProcessModelAggregate":
        """Create a model aggregate from process discovery."""
        model = ProcessModel.create(
            name=name,
            format=model_format,
            source_log_id=source_log_id,
            miner_type=miner_type,
        )
        model.model_data = model_data
        
        aggregate = cls(model=model)
        aggregate._pending_events.append(ModelDiscovered(
            model_id=model.id,
            model_name=model.name,
            source_log_id=source_log_id,
            miner_type=miner_type.value,
            model_format=model_format.value,
        ))
        
        return aggregate
    
    @classmethod
    def reconstitute(cls, model: ProcessModel) -> "ProcessModelAggregate":
        """Reconstitute an aggregate from stored data."""
        return cls(model=model)
    
    def pop_events(self) -> list[DomainEvent]:
        """Pop pending domain events for publishing."""
        events = self._pending_events.copy()
        self._pending_events.clear()
        return events


@dataclass
class AnalysisAggregate:
    """
    Aggregate root for Process Analysis bounded context.
    Manages conformance and performance analysis results.
    """
    log_id: UUID
    model_id: Optional[UUID] = None
    conformance: Optional[ConformanceResult] = None
    performance: Optional[PerformanceMetrics] = None
    _pending_events: list[DomainEvent] = field(default_factory=list)
    
    @classmethod
    def create(cls, log_id: UUID, model_id: Optional[UUID] = None) -> "AnalysisAggregate":
        """Create a new analysis aggregate."""
        return cls(log_id=log_id, model_id=model_id)
    
    def set_conformance_result(self, result: ConformanceResult) -> None:
        """Set conformance checking result."""
        self.conformance = result
        self._pending_events.append(ConformanceChecked(
            result_id=result.id,
            log_id=result.log_id,
            model_id=result.model_id,
            fitness=result.fitness,
            is_conformant=result.is_conformant,
        ))
    
    def set_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """Set performance analysis metrics."""
        self.performance = metrics
        self._pending_events.append(PerformanceAnalyzed(
            log_id=metrics.log_id,
            avg_duration_seconds=metrics.avg_case_duration.total_seconds,
            bottleneck_count=len(metrics.bottleneck_activities),
        ))
    
    def pop_events(self) -> list[DomainEvent]:
        """Pop pending domain events for publishing."""
        events = self._pending_events.copy()
        self._pending_events.clear()
        return events
