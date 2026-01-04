"""Circuit breaker pattern for external services.

Prevents cascading failures by failing fast when an external service is unhealthy.
Based on Martin Fowler's Circuit Breaker pattern.

States:
- CLOSED: Normal operation, requests flow through
- OPEN: Service is considered down, requests fail immediately
- HALF_OPEN: Testing if service has recovered

Usage:
    circuit_breaker = CircuitBreaker(name="pm4py", failure_threshold=5)

    @circuit_breaker
    def call_pm4py(log):
        return pm4py.discover_petri_net_inductive(log)
"""

import asyncio
import functools
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, TypeVar

from src.core.exceptions import ServiceUnavailableError
from src.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 2  # Successes in half-open to close
    reset_timeout: float = 60.0  # Seconds before attempting reset
    half_open_max_calls: int = 3  # Max concurrent calls in half-open state


@dataclass
class CircuitBreakerState:
    """Mutable state for a circuit breaker."""

    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: float | None = None
    last_state_change: datetime = field(default_factory=datetime.utcnow)
    half_open_calls: int = 0


class CircuitBreaker:
    """Circuit breaker implementation for service protection.

    Monitors failures and prevents calling an unhealthy service.
    Automatically tests for recovery after a timeout.

    Attributes:
        name: Identifier for this circuit breaker (for logging/metrics)
        config: Circuit breaker configuration
        state: Current circuit state
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        reset_timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        self.name = name
        self.config = CircuitBreakerConfig(
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            reset_timeout=reset_timeout,
            half_open_max_calls=half_open_max_calls,
        )
        self._state = CircuitBreakerState()
        self._lock = asyncio.Lock()

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for timeout-based transitions."""
        if self._state.state == CircuitState.OPEN and self._should_attempt_reset():
            self._transition_to(CircuitState.HALF_OPEN)
        return self._state.state

    @property
    def is_closed(self) -> bool:
        return self.state == CircuitState.CLOSED

    @property
    def is_open(self) -> bool:
        return self.state == CircuitState.OPEN

    @property
    def is_half_open(self) -> bool:
        return self.state == CircuitState.HALF_OPEN

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._state.last_failure_time is None:
            return True
        elapsed = time.monotonic() - self._state.last_failure_time
        return elapsed >= self.config.reset_timeout

    def _transition_to(self, new_state: CircuitState) -> None:
        """Transition to a new state with logging."""
        old_state = self._state.state
        self._state.state = new_state
        self._state.last_state_change = datetime.utcnow()

        if new_state == CircuitState.HALF_OPEN:
            self._state.success_count = 0
            self._state.half_open_calls = 0
        elif new_state == CircuitState.CLOSED:
            self._state.failure_count = 0
            self._state.success_count = 0

        logger.info(
            "circuit_breaker_state_changed",
            circuit=self.name,
            from_state=old_state.value,
            to_state=new_state.value,
        )

    def _record_success(self) -> None:
        """Record a successful call."""
        if self._state.state == CircuitState.HALF_OPEN:
            self._state.success_count += 1
            if self._state.success_count >= self.config.success_threshold:
                self._transition_to(CircuitState.CLOSED)

    def _record_failure(self) -> None:
        """Record a failed call."""
        self._state.failure_count += 1
        self._state.last_failure_time = time.monotonic()

        if self._state.state == CircuitState.HALF_OPEN:
            # Any failure in half-open opens the circuit again
            self._transition_to(CircuitState.OPEN)
        elif self._state.failure_count >= self.config.failure_threshold:
            self._transition_to(CircuitState.OPEN)

    def _can_execute(self) -> bool:
        """Check if a call can be executed."""
        state = self.state  # This may trigger state transition

        if state == CircuitState.CLOSED:
            return True
        if state == CircuitState.OPEN:
            return False
        # HALF_OPEN
        # Limit concurrent calls in half-open state
        if self._state.half_open_calls < self.config.half_open_max_calls:
            self._state.half_open_calls += 1
            return True
        return False

    def __call__(self, fn: Callable[..., T]) -> Callable[..., T]:
        """Decorator that wraps a function with circuit breaker protection."""

        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            if not self._can_execute():
                raise ServiceUnavailableError(
                    service=self.name,
                    retry_after=int(self.config.reset_timeout),
                )

            try:
                result = fn(*args, **kwargs)
                self._record_success()
                return result
            except Exception:
                self._record_failure()
                raise

        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            if not self._can_execute():
                raise ServiceUnavailableError(
                    service=self.name,
                    retry_after=int(self.config.reset_timeout),
                )

            try:
                result = await fn(*args, **kwargs)
                self._record_success()
                return result
            except Exception:
                self._record_failure()
                raise

        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper

    def get_status(self) -> dict[str, Any]:
        """Get current circuit breaker status for monitoring."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._state.failure_count,
            "success_count": self._state.success_count,
            "last_state_change": self._state.last_state_change.isoformat(),
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "success_threshold": self.config.success_threshold,
                "reset_timeout": self.config.reset_timeout,
            },
        }

    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        self._state = CircuitBreakerState()
        logger.info("circuit_breaker_manually_reset", circuit=self.name)


# =============================================================================
# Pre-configured Circuit Breakers
# =============================================================================

# PM4Py operations circuit breaker
pm4py_circuit = CircuitBreaker(
    name="pm4py",
    failure_threshold=5,
    reset_timeout=60.0,
)

# Database circuit breaker
database_circuit = CircuitBreaker(
    name="database",
    failure_threshold=3,
    reset_timeout=30.0,
)

# Cache circuit breaker (more lenient, not critical)
cache_circuit = CircuitBreaker(
    name="cache",
    failure_threshold=10,
    reset_timeout=30.0,
)


def get_all_circuit_statuses() -> list[dict[str, Any]]:
    """Get status of all registered circuit breakers."""
    return [
        pm4py_circuit.get_status(),
        database_circuit.get_status(),
        cache_circuit.get_status(),
    ]
