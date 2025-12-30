"""Unit tests for domain entities."""

from datetime import datetime

import pytest
from src.domain.entities import (
    EventLog,
    ProcessCase,
    ProcessEvent,
    ProcessModel,
    Variant,
)
from src.domain.value_objects import (
    ActivityName,
    Duration,
    FitnessScore,
    MinerType,
    ModelFormat,
    Timestamp,
    ValidationError,
)


class TestValueObjects:
    """Tests for domain value objects."""

    def test_activity_name_valid(self):
        """Test valid activity name creation."""
        name = ActivityName("Register Request")
        assert str(name) == "Register Request"

    def test_activity_name_strips_whitespace(self):
        """Test activity name strips whitespace."""
        name = ActivityName("  Process  ")
        assert str(name) == "Process"

    def test_activity_name_empty_raises(self):
        """Test empty activity name raises error."""
        with pytest.raises(ValidationError):
            ActivityName("")

    def test_timestamp_creation(self):
        """Test timestamp creation."""
        now = datetime.utcnow()
        ts = Timestamp(now)
        assert ts.value == now

    def test_timestamp_to_iso(self):
        """Test timestamp ISO conversion."""
        dt = datetime(2024, 1, 15, 10, 30, 0)
        ts = Timestamp(dt)
        assert ts.to_iso() == "2024-01-15T10:30:00"

    def test_duration_from_seconds(self):
        """Test duration from seconds."""
        duration = Duration.from_seconds(3661)
        assert duration.total_hours == pytest.approx(1.017, rel=0.01)

    def test_duration_between_timestamps(self):
        """Test duration between two timestamps."""
        start = Timestamp(datetime(2024, 1, 1, 9, 0, 0))
        end = Timestamp(datetime(2024, 1, 1, 10, 30, 0))
        duration = Duration.between(start, end)
        assert duration.total_minutes == 90

    def test_fitness_score_valid(self):
        """Test valid fitness score."""
        score = FitnessScore(0.85)
        assert score.percentage == 85.0
        assert not score.is_perfect

    def test_fitness_score_perfect(self):
        """Test perfect fitness score."""
        score = FitnessScore(1.0)
        assert score.is_perfect

    def test_fitness_score_invalid_raises(self):
        """Test invalid fitness score raises error."""
        with pytest.raises(ValidationError):
            FitnessScore(1.5)


class TestProcessEvent:
    """Tests for ProcessEvent entity."""

    def test_create_event(self):
        """Test event creation."""
        event = ProcessEvent.create(
            case_id="CASE-001",
            activity="Register Request",
            timestamp=datetime(2024, 1, 1, 9, 0, 0),
            resource="John",
        )

        assert event.case_id == "CASE-001"
        assert str(event.activity) == "Register Request"
        assert event.timestamp.value == datetime(2024, 1, 1, 9, 0, 0)
        assert str(event.resource) == "John"


class TestProcessCase:
    """Tests for ProcessCase entity."""

    def test_create_case(self):
        """Test case creation."""
        case = ProcessCase.create(case_id="CASE-001")
        assert case.case_id == "CASE-001"
        assert len(case.events) == 0

    def test_add_events(self):
        """Test adding events to case."""
        case = ProcessCase.create(case_id="CASE-001")

        event1 = ProcessEvent.create(
            case_id="CASE-001",
            activity="Start",
            timestamp=datetime(2024, 1, 1, 9, 0, 0),
        )
        event2 = ProcessEvent.create(
            case_id="CASE-001",
            activity="End",
            timestamp=datetime(2024, 1, 1, 10, 0, 0),
        )

        case.add_event(event2)  # Add in wrong order
        case.add_event(event1)

        # Events should be sorted by timestamp
        assert case.activities == ["Start", "End"]

    def test_variant_key(self):
        """Test variant key generation."""
        case = ProcessCase.create(case_id="CASE-001")
        case.add_event(ProcessEvent.create("CASE-001", "A", datetime(2024, 1, 1, 9, 0, 0)))
        case.add_event(ProcessEvent.create("CASE-001", "B", datetime(2024, 1, 1, 10, 0, 0)))
        case.add_event(ProcessEvent.create("CASE-001", "C", datetime(2024, 1, 1, 11, 0, 0)))

        assert case.variant_key == "A,B,C"

    def test_duration(self):
        """Test case duration calculation."""
        case = ProcessCase.create(case_id="CASE-001")
        case.add_event(ProcessEvent.create("CASE-001", "Start", datetime(2024, 1, 1, 9, 0, 0)))
        case.add_event(ProcessEvent.create("CASE-001", "End", datetime(2024, 1, 1, 11, 30, 0)))

        assert case.duration.total_hours == 2.5


class TestEventLog:
    """Tests for EventLog entity."""

    def test_create_log(self):
        """Test log creation."""
        log = EventLog.create(name="Test Log", source_file="test.csv")
        assert log.name == "Test Log"
        assert log.source_file == "test.csv"

    def test_log_statistics(self):
        """Test log statistics."""
        log = EventLog.create(name="Test Log")

        # Add cases
        case1 = ProcessCase.create(case_id="1")
        case1.add_event(ProcessEvent.create("1", "A", datetime(2024, 1, 1, 9, 0, 0)))
        case1.add_event(ProcessEvent.create("1", "B", datetime(2024, 1, 1, 10, 0, 0)))

        case2 = ProcessCase.create(case_id="2")
        case2.add_event(ProcessEvent.create("2", "A", datetime(2024, 1, 1, 9, 0, 0)))
        case2.add_event(ProcessEvent.create("2", "C", datetime(2024, 1, 1, 10, 0, 0)))

        log.add_case(case1)
        log.add_case(case2)

        assert log.total_cases == 2
        assert log.total_events == 4
        assert log.activities == {"A", "B", "C"}

    def test_variants(self):
        """Test variant extraction."""
        log = EventLog.create(name="Test Log")

        # Add cases with same variant
        for i in range(3):
            case = ProcessCase.create(case_id=str(i))
            case.add_event(ProcessEvent.create(str(i), "A", datetime(2024, 1, 1, 9, 0, 0)))
            case.add_event(ProcessEvent.create(str(i), "B", datetime(2024, 1, 1, 10, 0, 0)))
            log.add_case(case)

        # Add case with different variant
        case = ProcessCase.create(case_id="4")
        case.add_event(ProcessEvent.create("4", "A", datetime(2024, 1, 1, 9, 0, 0)))
        case.add_event(ProcessEvent.create("4", "C", datetime(2024, 1, 1, 10, 0, 0)))
        log.add_case(case)

        variants = log.variants
        assert len(variants) == 2
        assert variants[0].case_count == 3  # Most frequent first


class TestVariant:
    """Tests for Variant entity."""

    def test_from_cases(self):
        """Test variant extraction from cases."""
        cases = []

        for i in range(5):
            case = ProcessCase.create(case_id=str(i))
            case.add_event(ProcessEvent.create(str(i), "A", datetime(2024, 1, 1, 9, 0, 0)))
            case.add_event(ProcessEvent.create(str(i), "B", datetime(2024, 1, 1, 10, 0, 0)))
            cases.append(case)

        variants = Variant.from_cases(cases)

        assert len(variants) == 1
        assert variants[0].case_count == 5
        assert variants[0].activities == ("A", "B")


class TestProcessModel:
    """Tests for ProcessModel entity."""

    def test_create_model(self):
        """Test model creation."""
        model = ProcessModel.create(
            name="Test Model",
            format=ModelFormat.PETRI_NET,
            miner_type=MinerType.INDUCTIVE,
        )

        assert model.name == "Test Model"
        assert model.format == ModelFormat.PETRI_NET
        assert model.miner_type == MinerType.INDUCTIVE
