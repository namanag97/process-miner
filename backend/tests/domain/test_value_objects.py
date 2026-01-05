"""Tests for domain value objects."""

from datetime import datetime

import pytest

from src.features.process_mining.services.domain.value_objects import (
    ActivitySequence,
    CaseId,
    ProcessStatistics,
    QualityMetrics,
    TimeRange,
    VariantStats,
)


class TestCaseId:
    """Tests for CaseId value object."""

    def test_valid_case_id(self):
        case_id = CaseId("order-123")
        assert case_id.value == "order-123"
        assert str(case_id) == "order-123"

    def test_case_id_strips_whitespace(self):
        case_id = CaseId("  order-123  ")
        assert case_id.value == "order-123"

    def test_empty_case_id_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            CaseId("")

    def test_whitespace_only_case_id_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            CaseId("   ")

    def test_case_id_equality(self):
        assert CaseId("a") == CaseId("a")
        assert CaseId("a") != CaseId("b")

    def test_case_id_hashable(self):
        case_set = {CaseId("a"), CaseId("a"), CaseId("b")}
        assert len(case_set) == 2


class TestActivitySequence:
    """Tests for ActivitySequence value object."""

    def test_from_list(self):
        seq = ActivitySequence.from_list(["A", "B", "C"])
        assert seq.activities == ("A", "B", "C")
        assert len(seq) == 3

    def test_to_trace_string(self):
        seq = ActivitySequence.from_list(["Submit", "Approve", "Complete"])
        assert seq.to_trace_string() == "Submit → Approve → Complete"

    def test_from_trace_string(self):
        seq = ActivitySequence.from_trace_string("A → B → C")
        assert seq.activities == ("A", "B", "C")

    def test_no_rework(self):
        seq = ActivitySequence.from_list(["A", "B", "C"])
        assert seq.has_rework is False
        assert seq.rework_count == 0
        assert seq.rework_ratio == 0.0

    def test_has_rework(self):
        seq = ActivitySequence.from_list(["A", "B", "A", "C"])
        assert seq.has_rework is True
        assert seq.rework_count == 1
        assert seq.rework_ratio == 0.25

    def test_first_last_activity(self):
        seq = ActivitySequence.from_list(["Start", "Process", "End"])
        assert seq.first_activity == "Start"
        assert seq.last_activity == "End"

    def test_unique_activities(self):
        seq = ActivitySequence.from_list(["A", "B", "A", "C", "B"])
        assert seq.unique_activities == frozenset({"A", "B", "C"})
        assert seq.unique_count == 3

    def test_contains(self):
        seq = ActivitySequence.from_list(["A", "B", "C"])
        assert seq.contains("B") is True
        assert seq.contains("X") is False

    def test_count(self):
        seq = ActivitySequence.from_list(["A", "B", "A", "C", "A"])
        assert seq.count("A") == 3
        assert seq.count("B") == 1
        assert seq.count("X") == 0

    def test_get_prefix(self):
        seq = ActivitySequence.from_list(["A", "B", "C", "D"])
        prefix = seq.get_prefix(2)
        assert prefix.activities == ("A", "B")

    def test_get_suffix(self):
        seq = ActivitySequence.from_list(["A", "B", "C", "D"])
        suffix = seq.get_suffix(2)
        assert suffix.activities == ("C", "D")

    def test_variant_hash_stable(self):
        seq1 = ActivitySequence.from_list(["A", "B", "C"])
        seq2 = ActivitySequence.from_list(["A", "B", "C"])
        assert seq1.variant_hash == seq2.variant_hash

    def test_variant_hash_differs(self):
        seq1 = ActivitySequence.from_list(["A", "B", "C"])
        seq2 = ActivitySequence.from_list(["A", "C", "B"])
        assert seq1.variant_hash != seq2.variant_hash

    def test_empty_sequence_raises(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            ActivitySequence(())

    def test_iteration(self):
        seq = ActivitySequence.from_list(["A", "B", "C"])
        assert list(seq) == ["A", "B", "C"]

    def test_indexing(self):
        seq = ActivitySequence.from_list(["A", "B", "C"])
        assert seq[0] == "A"
        assert seq[1] == "B"
        assert seq[2] == "C"


class TestTimeRange:
    """Tests for TimeRange value object."""

    def test_valid_time_range(self):
        start = datetime(2024, 1, 1, 9, 0)
        end = datetime(2024, 1, 1, 17, 0)
        tr = TimeRange(start=start, end=end)
        assert tr.start == start
        assert tr.end == end

    def test_duration_calculations(self):
        start = datetime(2024, 1, 1, 9, 0)
        end = datetime(2024, 1, 1, 17, 0)  # 8 hours later
        tr = TimeRange(start=start, end=end)
        assert tr.duration_seconds == 8 * 3600
        assert tr.duration_hours == 8.0

    def test_end_before_start_raises(self):
        with pytest.raises(ValueError, match="cannot be before start"):
            TimeRange(
                start=datetime(2024, 1, 2),
                end=datetime(2024, 1, 1),
            )

    def test_same_start_end_valid(self):
        dt = datetime(2024, 1, 1, 12, 0)
        tr = TimeRange(start=dt, end=dt)
        assert tr.duration_seconds == 0

    def test_contains(self):
        tr = TimeRange(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 17, 0),
        )
        assert tr.contains(datetime(2024, 1, 1, 12, 0)) is True
        assert tr.contains(datetime(2024, 1, 1, 8, 0)) is False
        assert tr.contains(datetime(2024, 1, 1, 18, 0)) is False

    def test_overlaps(self):
        tr1 = TimeRange(
            start=datetime(2024, 1, 1, 9, 0),
            end=datetime(2024, 1, 1, 12, 0),
        )
        tr2 = TimeRange(
            start=datetime(2024, 1, 1, 11, 0),
            end=datetime(2024, 1, 1, 14, 0),
        )
        tr3 = TimeRange(
            start=datetime(2024, 1, 1, 13, 0),
            end=datetime(2024, 1, 1, 15, 0),
        )
        assert tr1.overlaps(tr2) is True
        assert tr1.overlaps(tr3) is False


class TestQualityMetrics:
    """Tests for QualityMetrics value object."""

    def test_valid_metrics(self):
        metrics = QualityMetrics(fitness=0.95, precision=0.85)
        assert metrics.fitness == 0.95
        assert metrics.precision == 0.85

    def test_f_score(self):
        metrics = QualityMetrics(fitness=0.9, precision=0.8)
        f_score = metrics.f_score
        assert f_score is not None
        assert abs(f_score - 0.8471) < 0.001

    def test_f_score_none_when_missing(self):
        metrics = QualityMetrics(fitness=0.9)
        assert metrics.f_score is None

    def test_is_conformant(self):
        assert QualityMetrics(fitness=0.85).is_conformant is True
        assert QualityMetrics(fitness=0.75).is_conformant is False
        assert QualityMetrics().is_conformant is False

    def test_invalid_value_raises(self):
        with pytest.raises(ValueError, match="must be between"):
            QualityMetrics(fitness=1.5)
        with pytest.raises(ValueError, match="must be between"):
            QualityMetrics(precision=-0.1)


class TestProcessStatistics:
    """Tests for ProcessStatistics value object."""

    def test_avg_events_per_case(self):
        stats = ProcessStatistics(
            total_events=100,
            total_cases=20,
            total_activities=10,
            total_variants=5,
        )
        assert stats.avg_events_per_case == 5.0

    def test_zero_cases_handling(self):
        stats = ProcessStatistics(
            total_events=0,
            total_cases=0,
            total_activities=0,
            total_variants=0,
        )
        assert stats.avg_events_per_case == 0.0


class TestVariantStats:
    """Tests for VariantStats value object."""

    def test_frequency_percent(self):
        seq = ActivitySequence.from_list(["A", "B", "C"])
        stats = VariantStats(
            sequence=seq,
            case_count=30,
            total_cases=100,
        )
        assert stats.frequency_percent == 30.0

    def test_complexity_score(self):
        # Simple variant
        simple_seq = ActivitySequence.from_list(["A", "B", "C"])
        simple_stats = VariantStats(
            sequence=simple_seq,
            case_count=10,
            total_cases=100,
        )

        # Complex variant with rework
        complex_seq = ActivitySequence.from_list(["A", "B", "A", "C", "B", "D"])
        complex_stats = VariantStats(
            sequence=complex_seq,
            case_count=10,
            total_cases=100,
        )

        # Complex should have higher score
        assert complex_stats.complexity_score > simple_stats.complexity_score
