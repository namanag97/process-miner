"""Result/Either pattern for service layer operations.

Provides a functional approach to error handling that makes success/failure explicit
without relying on exceptions for control flow.

Usage:
    def divide(a: int, b: int) -> Result[float]:
        if b == 0:
            return Result.failure(ValidationError("Cannot divide by zero"))
        return Result.success(a / b)
    
    result = divide(10, 2)
    if result.is_success:
        print(f"Result: {result.value}")
    else:
        print(f"Error: {result.error.message}")
        
    # Or use functional composition
    result = (
        divide(10, 2)
        .map(lambda x: x * 2)
        .flat_map(lambda x: divide(x, 0))  # This will fail
    )
"""

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar, Union

from src.core.exceptions import AppException

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class Result(Generic[T]):
    """A container for operation results that can be either success or failure.
    
    This is a simplified Either/Result monad implementation that provides:
    - Explicit success/failure states
    - Functional composition with map/flat_map
    - Type safety for error handling
    
    Attributes:
        _value: The success value (None if failure)
        _error: The error (None if success)
    """
    
    _value: T | None
    _error: AppException | None
    
    @property
    def value(self) -> T:
        """Get the success value.
        
        Raises:
            ValueError: If this is a failure result
        """
        if self._error is not None:
            raise ValueError(f"Cannot get value from failed result: {self._error.message}")
        return self._value  # type: ignore
    
    @property
    def error(self) -> AppException:
        """Get the error.
        
        Raises:
            ValueError: If this is a success result
        """
        if self._error is None:
            raise ValueError("Cannot get error from successful result")
        return self._error
    
    @property
    def is_success(self) -> bool:
        """Check if this is a success result."""
        return self._error is None
    
    @property
    def is_failure(self) -> bool:
        """Check if this is a failure result."""
        return self._error is not None
    
    @classmethod
    def success(cls, value: T) -> "Result[T]":
        """Create a success result."""
        return cls(_value=value, _error=None)
    
    @classmethod
    def failure(cls, error: AppException) -> "Result[T]":
        """Create a failure result."""
        return cls(_value=None, _error=error)
    
    @classmethod
    def from_exception(cls, fn: Callable[[], T]) -> "Result[T]":
        """Create a result from a function that might throw an exception."""
        from src.core.exceptions import ProcessingError
        
        try:
            return cls.success(fn())
        except AppException as e:
            return cls.failure(e)
        except Exception as e:
            return cls.failure(ProcessingError(str(e)))
    
    def map(self, fn: Callable[[T], U]) -> "Result[U]":
        """Transform the success value, passing through failures.
        
        Args:
            fn: Function to apply to the success value
            
        Returns:
            New Result with transformed value or original error
        """
        if self.is_failure:
            return Result.failure(self._error)  # type: ignore
        try:
            return Result.success(fn(self._value))  # type: ignore
        except AppException as e:
            return Result.failure(e)
        except Exception as e:
            from src.core.exceptions import ProcessingError
            return Result.failure(ProcessingError(str(e)))
    
    def flat_map(self, fn: Callable[[T], "Result[U]"]) -> "Result[U]":
        """Chain operations that return Results.
        
        Args:
            fn: Function that takes success value and returns a Result
            
        Returns:
            Result from the chained function or original error
        """
        if self.is_failure:
            return Result.failure(self._error)  # type: ignore
        try:
            return fn(self._value)  # type: ignore
        except AppException as e:
            return Result.failure(e)
        except Exception as e:
            from src.core.exceptions import ProcessingError
            return Result.failure(ProcessingError(str(e)))
    
    def map_error(self, fn: Callable[[AppException], AppException]) -> "Result[T]":
        """Transform the error, passing through successes.
        
        Args:
            fn: Function to transform the error
            
        Returns:
            Original success or new Result with transformed error
        """
        if self.is_success:
            return self
        return Result.failure(fn(self._error))  # type: ignore
    
    def recover(self, fn: Callable[[AppException], T]) -> "Result[T]":
        """Recover from failure by providing a fallback value.
        
        Args:
            fn: Function that takes the error and returns a fallback value
            
        Returns:
            Original success or new success with fallback value
        """
        if self.is_success:
            return self
        try:
            return Result.success(fn(self._error))  # type: ignore
        except Exception as e:
            from src.core.exceptions import ProcessingError
            return Result.failure(ProcessingError(str(e)))
    
    def recover_with(self, fn: Callable[[AppException], "Result[T]"]) -> "Result[T]":
        """Recover from failure by providing an alternative Result.
        
        Args:
            fn: Function that takes the error and returns an alternative Result
            
        Returns:
            Original success or alternative Result
        """
        if self.is_success:
            return self
        return fn(self._error)  # type: ignore
    
    def get_or_else(self, default: T) -> T:
        """Get the value or a default if failure."""
        return self._value if self.is_success else default  # type: ignore
    
    def get_or_raise(self) -> T:
        """Get the value or raise the error.
        
        Raises:
            AppException: The contained error if this is a failure
        """
        if self.is_failure:
            raise self._error  # type: ignore
        return self._value  # type: ignore
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to a dictionary representation."""
        if self.is_success:
            return {"success": True, "value": self._value}
        return {"success": False, "error": self._error.to_dict()}  # type: ignore
    
    def __repr__(self) -> str:
        if self.is_success:
            return f"Result.success({self._value!r})"
        return f"Result.failure({self._error!r})"


# Type alias for async results
AsyncResult = Result


def collect_results(results: list[Result[T]]) -> Result[list[T]]:
    """Collect a list of Results into a Result of list.
    
    Returns success with all values if all results are successful,
    or the first failure encountered.
    
    Args:
        results: List of Result objects
        
    Returns:
        Result containing list of all values or first error
    """
    values = []
    for result in results:
        if result.is_failure:
            return Result.failure(result.error)
        values.append(result.value)
    return Result.success(values)


def sequence_results(results: list[Result[T]]) -> Result[list[T]]:
    """Alias for collect_results (Haskell naming convention)."""
    return collect_results(results)
