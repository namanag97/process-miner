"""Function Call Tracing - Decorators and utilities for dev observability.

Usage:
    from src.platform.devtools.tracing import trace

    @trace
    async def my_service_function(arg1, arg2):
        ...

This will log function entry/exit/errors to DevConsole SSE stream.
"""

import functools
import time
from typing import Any, Callable, TypeVar

from src.platform.core.config import get_settings
from src.platform.infrastructure.devconsole_types import DevLogEntry, LogLevel

settings = get_settings()

F = TypeVar("F", bound=Callable[..., Any])


def _emit_trace(source: str, phase: str, data: dict | None = None):
    """Emit a trace log to DevConsole stream."""
    if not settings.debug:
        return
    
    from src.platform.infrastructure.log_broker import log_broker
    
    entry = DevLogEntry(
        level=LogLevel.INFO if phase != "ERROR" else LogLevel.ERROR,
        source=source,
        message=f"[{phase}]",
        data=data,
        tags=["trace", phase.lower()],
    )
    log_broker.emit_log(entry)


def trace(func: F) -> F:
    """Decorator to trace function entry/exit for DevConsole.
    
    Works with both sync and async functions.
    """
    func_name = f"{func.__module__}.{func.__qualname__}"
    
    if functools.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not settings.debug:
                return await func(*args, **kwargs)
            
            # Truncate args for logging
            args_str = str(args)[:200] if args else ""
            kwargs_str = str(kwargs)[:200] if kwargs else ""
            
            _emit_trace(func_name, "ENTER", {"args": args_str, "kwargs": kwargs_str})
            start = time.perf_counter()
            
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                result_str = str(result)[:200] if result else ""
                _emit_trace(func_name, "EXIT", {"result": result_str, "duration_ms": round(duration_ms, 2)})
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                _emit_trace(func_name, "ERROR", {"error": str(e), "duration_ms": round(duration_ms, 2)})
                raise
        return async_wrapper  # type: ignore
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not settings.debug:
                return func(*args, **kwargs)
            
            args_str = str(args)[:200] if args else ""
            kwargs_str = str(kwargs)[:200] if kwargs else ""
            
            _emit_trace(func_name, "ENTER", {"args": args_str, "kwargs": kwargs_str})
            start = time.perf_counter()
            
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.perf_counter() - start) * 1000
                result_str = str(result)[:200] if result else ""
                _emit_trace(func_name, "EXIT", {"result": result_str, "duration_ms": round(duration_ms, 2)})
                return result
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                _emit_trace(func_name, "ERROR", {"error": str(e), "duration_ms": round(duration_ms, 2)})
                raise
        return sync_wrapper  # type: ignore


def trace_class(cls):
    """Class decorator to trace all public methods.
    
    Usage:
        @trace_class
        class MyService:
            async def process(self, data):
                ...
    """
    for attr_name in dir(cls):
        if attr_name.startswith("_"):
            continue
        attr = getattr(cls, attr_name)
        if callable(attr):
            setattr(cls, attr_name, trace(attr))
    return cls
