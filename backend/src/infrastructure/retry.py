"""Retry policies with exponential backoff.

Provides configurable retry logic for transient failures with:
- Exponential backoff with jitter
- Configurable retry predicates
- Async and sync support
- Logging and metrics integration

Usage:
    @retry(max_attempts=3, backoff=ExponentialBackoff())
    async def call_external_service():
        return await http_client.get("/api/data")
    
    # Or with custom configuration
    @retry(
        max_attempts=5,
        backoff=ExponentialBackoff(base=1.0, max=60.0, jitter=True),
        retry_on=[ConnectionError, TimeoutError],
    )
    def flaky_operation():
        ...
"""

import asyncio
import functools
import random
import time
from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence, Type, TypeVar, Union

from src.core.logging_config import get_logger

logger = get_logger(__name__)

T = TypeVar("T")


@dataclass
class BackoffStrategy:
    """Base class for backoff strategies."""
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number (0-indexed)."""
        raise NotImplementedError


@dataclass
class ExponentialBackoff(BackoffStrategy):
    """Exponential backoff with optional jitter.
    
    Delay = min(max_delay, base * (multiplier ** attempt)) + jitter
    
    Attributes:
        base: Base delay in seconds
        multiplier: Exponential multiplier (default 2)
        max_delay: Maximum delay cap in seconds
        jitter: Whether to add random jitter (recommended for avoiding thundering herd)
        jitter_range: Range of jitter as fraction of delay (0.0 to 1.0)
    """
    
    base: float = 1.0
    multiplier: float = 2.0
    max_delay: float = 60.0
    jitter: bool = True
    jitter_range: float = 0.25
    
    def get_delay(self, attempt: int) -> float:
        """Calculate exponential delay with optional jitter."""
        delay = min(self.max_delay, self.base * (self.multiplier ** attempt))
        
        if self.jitter:
            jitter_amount = delay * self.jitter_range
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay)  # Ensure non-negative
        
        return delay


@dataclass
class LinearBackoff(BackoffStrategy):
    """Linear backoff strategy.
    
    Delay = min(max_delay, base + (increment * attempt))
    """
    
    base: float = 1.0
    increment: float = 1.0
    max_delay: float = 30.0
    
    def get_delay(self, attempt: int) -> float:
        """Calculate linear delay."""
        return min(self.max_delay, self.base + (self.increment * attempt))


@dataclass  
class ConstantBackoff(BackoffStrategy):
    """Constant delay between retries."""
    
    delay: float = 1.0
    
    def get_delay(self, attempt: int) -> float:
        """Return constant delay."""
        return self.delay


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    
    max_attempts: int = 3
    backoff: BackoffStrategy = None  # type: ignore
    retry_on: Sequence[Type[Exception]] = ()
    retry_if: Optional[Callable[[Exception], bool]] = None
    on_retry: Optional[Callable[[Exception, int, float], None]] = None
    
    def __post_init__(self):
        if self.backoff is None:
            self.backoff = ExponentialBackoff()
        if not self.retry_on:
            self.retry_on = (Exception,)  # Retry on all exceptions by default


def retry(
    max_attempts: int = 3,
    backoff: Optional[BackoffStrategy] = None,
    retry_on: Sequence[Type[Exception]] = (),
    retry_if: Optional[Callable[[Exception], bool]] = None,
    on_retry: Optional[Callable[[Exception, int, float], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator that adds retry logic to a function.
    
    Args:
        max_attempts: Maximum number of attempts (including initial)
        backoff: Backoff strategy for delays between retries
        retry_on: Exception types to retry on (default: all exceptions)
        retry_if: Custom predicate to determine if should retry
        on_retry: Callback called before each retry with (exception, attempt, delay)
    
    Returns:
        Decorated function with retry logic
        
    Example:
        @retry(max_attempts=3, backoff=ExponentialBackoff())
        async def fetch_data():
            return await http_client.get("/api")
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        backoff=backoff or ExponentialBackoff(),
        retry_on=retry_on,
        retry_if=retry_if,
        on_retry=on_retry,
    )
    
    def decorator(fn: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(fn)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(config.max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if not _should_retry(e, config):
                        raise
                    
                    if attempt < config.max_attempts - 1:
                        delay = config.backoff.get_delay(attempt)
                        _log_retry(fn.__name__, e, attempt + 1, config.max_attempts, delay)
                        
                        if config.on_retry:
                            config.on_retry(e, attempt + 1, delay)
                        
                        time.sleep(delay)
                    else:
                        raise
            
            # Should never reach here, but for type safety
            raise last_exception  # type: ignore
        
        @functools.wraps(fn)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(config.max_attempts):
                try:
                    return await fn(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if not _should_retry(e, config):
                        raise
                    
                    if attempt < config.max_attempts - 1:
                        delay = config.backoff.get_delay(attempt)
                        _log_retry(fn.__name__, e, attempt + 1, config.max_attempts, delay)
                        
                        if config.on_retry:
                            config.on_retry(e, attempt + 1, delay)
                        
                        await asyncio.sleep(delay)
                    else:
                        raise
            
            # Should never reach here, but for type safety
            raise last_exception  # type: ignore
        
        if asyncio.iscoroutinefunction(fn):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def _should_retry(exception: Exception, config: RetryConfig) -> bool:
    """Determine if an exception should trigger a retry."""
    # Check custom predicate first
    if config.retry_if is not None:
        return config.retry_if(exception)
    
    # Check exception type
    return isinstance(exception, tuple(config.retry_on))


def _log_retry(
    func_name: str,
    exception: Exception,
    attempt: int,
    max_attempts: int,
    delay: float,
) -> None:
    """Log retry attempt."""
    logger.warning(
        "retry_attempt",
        function=func_name,
        attempt=attempt,
        max_attempts=max_attempts,
        delay_seconds=round(delay, 2),
        exception_type=type(exception).__name__,
        exception_message=str(exception),
    )


# =============================================================================
# Pre-configured Retry Policies
# =============================================================================

def retry_pm4py() -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry policy for PM4Py operations.
    
    - 3 attempts
    - Exponential backoff: 1s, 2s, 4s
    - Retries on any exception
    """
    return retry(
        max_attempts=3,
        backoff=ExponentialBackoff(base=1.0, max_delay=10.0),
    )


def retry_database() -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry policy for database operations.
    
    - 3 attempts  
    - Quick retries: 0.5s, 1s, 2s
    """
    return retry(
        max_attempts=3,
        backoff=ExponentialBackoff(base=0.5, max_delay=5.0),
    )


def retry_external_api() -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry policy for external API calls.
    
    - 5 attempts with longer backoff
    - Exponential backoff: 1s, 2s, 4s, 8s, 16s (capped at 30s)
    """
    return retry(
        max_attempts=5,
        backoff=ExponentialBackoff(base=1.0, max_delay=30.0, jitter=True),
    )


def retry_file_operation() -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Retry policy for file operations.
    
    - 3 attempts with short delays
    - Handles transient file system errors
    """
    return retry(
        max_attempts=3,
        backoff=ConstantBackoff(delay=0.5),
        retry_on=(OSError, IOError),
    )
