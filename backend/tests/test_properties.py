"""Property-based tests using Hypothesis.

Tests invariants and edge cases that are hard to find with example-based tests:
- DFG discovery never crashes on valid inputs
- Value Objects reject invalid inputs
- Serialization round-trips preserve data
- Error responses follow RFC 7807

Usage:
    pytest tests/test_properties.py -v --hypothesis-show-statistics
"""

import json
from datetime import datetime
from typing import Any

import pytest
from hypothesis import HealthCheck, assume, given, settings
from hypothesis import strategies as st

# =============================================================================
# Strategies for Process Mining Domain
# =============================================================================

# Valid activity names
activity_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("L", "N", "P", "S")),
    min_size=1,
    max_size=50,
).filter(lambda x: x.strip())

# Case IDs
case_id_strategy = st.text(min_size=1, max_size=100).filter(lambda x: x.strip())

# Valid UUIDs
uuid_strategy = st.uuids().map(str)

# Timestamps
timestamp_strategy = st.datetimes(
    min_value=datetime(2000, 1, 1),
    max_value=datetime(2030, 12, 31),
)

# Event (case_id, activity, timestamp)
event_strategy = st.tuples(case_id_strategy, activity_name_strategy, timestamp_strategy)

# Event list for a case
case_events_strategy = st.lists(
    st.tuples(activity_name_strategy, timestamp_strategy),
    min_size=1,
    max_size=20,
)

# Full event log
event_log_strategy = st.dictionaries(
    keys=case_id_strategy,
    values=case_events_strategy,
    min_size=1,
    max_size=50,
)


# =============================================================================
# Value Object Tests
# =============================================================================


class TestValueObjectProperties:
    """Property tests for Value Objects."""

    @given(uuid_strategy)
    def test_process_id_accepts_valid_uuids(self, uuid_str: str):
        """ProcessId should accept any valid UUID."""
        from src.core.value_objects import ProcessId

        pid = ProcessId(uuid_str)
        assert str(pid) == uuid_str
        assert pid.value == uuid_str

    @given(st.text(min_size=1, max_size=100).filter(lambda x: "-" not in x))
    def test_process_id_rejects_non_uuids(self, invalid_str: str):
        """ProcessId should reject non-UUID strings."""
        from src.core.value_objects import ProcessId

        # Most non-UUID strings should be rejected
        assume(len(invalid_str) != 36 or invalid_str.count("-") != 4)

        with pytest.raises(ValueError):
            ProcessId(invalid_str)

    @given(st.text(min_size=1, max_size=255).filter(lambda x: x.strip()))
    def test_activity_name_preserves_value(self, name: str):
        """ActivityName should preserve the input value."""
        from src.core.value_objects import ActivityName

        activity = ActivityName(name)
        assert str(activity) == name

    @given(st.text(max_size=5).filter(lambda x: not x.strip()))
    def test_activity_name_rejects_blank(self, blank: str):
        """ActivityName should reject blank strings."""
        from src.core.value_objects import ActivityName

        with pytest.raises(ValueError):
            ActivityName(blank)

    @given(st.floats(min_value=0, max_value=1e6, allow_nan=False))
    def test_duration_non_negative(self, seconds: float):
        """Duration should accept any non-negative value."""
        from src.core.value_objects import Duration

        d = Duration(seconds)
        assert d.seconds == seconds
        assert d.minutes == seconds / 60
        assert d.hours == seconds / 3600

    @given(st.floats(max_value=-0.1, allow_nan=False))
    def test_duration_rejects_negative(self, seconds: float):
        """Duration should reject negative values."""
        from src.core.value_objects import Duration

        with pytest.raises(ValueError):
            Duration(seconds)

    @given(st.floats(min_value=0, max_value=100))
    def test_percentage_in_range(self, value: float):
        """Percentage should accept values 0-100."""
        from src.core.value_objects import Percentage

        p = Percentage(value)
        assert p.value == value
        assert 0 <= p.ratio <= 1

    @given(st.floats(min_value=100.1, max_value=1000))
    def test_percentage_rejects_over_100(self, value: float):
        """Percentage should reject values over 100."""
        from src.core.value_objects import Percentage

        with pytest.raises(ValueError):
            Percentage(value)


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorProperties:
    """Property tests for error handling."""

    @given(st.text(min_size=1, max_size=200), uuid_strategy)
    def test_app_exception_to_dict_has_required_fields(self, message: str, corr_id: str):
        """AppException.to_dict() should always include required RFC 7807 fields."""
        from src.core.error_codes import ErrorCode
        from src.core.exceptions import AppException

        exc = AppException(
            message=message,
            error_code=ErrorCode.INTERNAL_ERROR,
            correlation_id=corr_id,
        )

        result = exc.to_dict()

        # Required RFC 7807 fields
        assert "type" in result
        assert "title" in result
        assert "status" in result
        assert "detail" in result
        assert result["detail"] == message
        assert result["correlation_id"] == corr_id

    @given(
        st.sampled_from(
            [
                "VALIDATION_FAILED",
                "RESOURCE_NOT_FOUND",
                "PROCESSING_FAILED",
                "EXTERNAL_SERVICE_ERROR",
                "INTERNAL_ERROR",
            ]
        )
    )
    def test_error_codes_have_metadata(self, code_name: str):
        """All error codes should have metadata."""
        from src.core.error_codes import ErrorCode, get_error_metadata

        code = ErrorCode[code_name]
        metadata = get_error_metadata(code)

        assert "title" in metadata
        assert "http_status" in metadata
        assert isinstance(metadata["http_status"], int)
        assert 400 <= metadata["http_status"] <= 599


# =============================================================================
# Result Pattern Tests
# =============================================================================


class TestResultProperties:
    """Property tests for Result pattern."""

    @given(st.integers())
    def test_result_success_preserves_value(self, value: int):
        """Result.success should preserve any value."""
        from src.core.result import Result

        r = Result.success(value)
        assert r.is_success
        assert not r.is_failure
        assert r.value == value

    @given(st.text(min_size=1))
    def test_result_failure_preserves_error(self, message: str):
        """Result.failure should preserve the error."""
        from src.core.exceptions import ValidationError
        from src.core.result import Result

        error = ValidationError(message)
        r = Result.failure(error)

        assert r.is_failure
        assert not r.is_success
        assert r.error.message == message

    @given(st.integers())
    def test_result_map_applies_function(self, value: int):
        """Result.map should apply function to success values."""
        from src.core.result import Result

        r = Result.success(value)
        mapped = r.map(lambda x: x * 2)

        assert mapped.is_success
        assert mapped.value == value * 2

    @given(st.integers())
    def test_result_map_preserves_failure(self, value: int):
        """Result.map should not apply function to failures."""
        from src.core.exceptions import ValidationError
        from src.core.result import Result

        r = Result.failure(ValidationError("error"))
        mapped = r.map(lambda x: x * 2)

        assert mapped.is_failure
        assert mapped.error.message == "error"

    @given(st.lists(st.integers(), min_size=1))
    def test_collect_results_all_success(self, values: list[int]):
        """collect_results with all successes should return list of values."""
        from src.core.result import Result, collect_results

        results = [Result.success(v) for v in values]
        collected = collect_results(results)

        assert collected.is_success
        assert collected.value == values


# =============================================================================
# Domain Events Tests
# =============================================================================


class TestDomainEventProperties:
    """Property tests for domain events."""

    @given(uuid_strategy, st.text(min_size=1, max_size=50), st.integers(min_value=0))
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_process_created_serializes_to_dict(self, process_id: str, name: str, events: int):
        """ProcessCreated should serialize to a valid dict."""
        from src.core.domain_events import ProcessCreated

        event = ProcessCreated(
            process_id=process_id,
            name=name,
            total_events=events,
        )

        result = event.to_dict()

        assert result["event_type"] == "process.created"
        assert result["process_id"] == process_id
        assert result["name"] == name
        assert result["total_events"] == events
        assert "event_id" in result
        assert "timestamp" in result


# =============================================================================
# Serialization Round-Trip Tests
# =============================================================================


class TestSerializationProperties:
    """Property tests for JSON serialization."""

    @given(
        st.dictionaries(
            keys=st.text(min_size=1, max_size=20, alphabet="abcdefghijklmnopqrstuvwxyz"),
            values=st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.text(max_size=100),
                st.booleans(),
                st.none(),
            ),
            max_size=10,
        )
    )
    def test_json_round_trip(self, data: dict[str, Any]):
        """JSON serialization should be lossless for valid data."""
        serialized = json.dumps(data)
        deserialized = json.loads(serialized)
        assert deserialized == data


# =============================================================================
# Circuit Breaker Tests
# =============================================================================


class TestCircuitBreakerProperties:
    """Property tests for circuit breaker."""

    @given(
        st.integers(min_value=1, max_value=20),  # failure_threshold
        st.floats(min_value=1.0, max_value=120.0),  # reset_timeout
    )
    def test_circuit_breaker_config_valid(self, threshold: int, timeout: float):
        """Circuit breaker should accept valid configurations."""
        from src.platform.infrastructure.circuit_breaker import CircuitBreaker

        cb = CircuitBreaker(
            name="test",
            failure_threshold=threshold,
            reset_timeout=timeout,
        )

        assert cb.config.failure_threshold == threshold
        assert cb.config.reset_timeout == timeout
        assert cb.is_closed  # Starts closed


# =============================================================================
# Rate Limiter Tests
# =============================================================================


class TestRateLimiterProperties:
    """Property tests for token bucket rate limiter."""

    @given(
        st.integers(min_value=1, max_value=1000),  # capacity
        st.floats(min_value=0.1, max_value=100.0),  # refill_rate
    )
    def test_token_bucket_starts_full(self, capacity: int, refill_rate: float):
        """Token bucket should start at full capacity."""
        from src.platform.infrastructure.rate_limiter import TokenBucket

        bucket = TokenBucket(capacity=capacity, refill_rate=refill_rate)

        # Should be able to consume up to capacity
        for _ in range(capacity):
            assert bucket.consume()

        # Next consume should fail
        assert not bucket.consume()
