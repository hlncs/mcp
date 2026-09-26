"""
Distributed tracing utilities with OpenTelemetry
"""
from contextlib import contextmanager
from typing import Optional, Dict, Any
from functools import wraps
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from opentelemetry.trace.span import Span
import structlog
import time
import asyncio

logger = structlog.get_logger(__name__)

# Get the global tracer
tracer = trace.get_tracer(__name__)

class TraceContext:
    """Context manager for tracing operations"""
    
    def __init__(
        self,
        operation_name: str,
        attributes: Optional[Dict[str, Any]] = None,
        record_exception: bool = True
    ):
        self.operation_name = operation_name
        self.attributes = attributes or {}
        self.record_exception = record_exception
        self.span = None
    
    def __enter__(self) -> Span:
        """Start the span"""
        self.span = tracer.start_span(self.operation_name)
        
        # Add attributes
        for key, value in self.attributes.items():
            if value is not None:
                try:
                    self.span.set_attribute(key, value)
                except Exception as e:
                    logger.debug("failed_to_set_span_attribute", key=key, error=str(e))
        
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """End the span"""
        if exc_type is not None and self.record_exception:
            self.span.record_exception(exc_val)
            self.span.set_status(Status(StatusCode.ERROR))
        else:
            self.span.set_status(Status(StatusCode.OK))
        
        self.span.end()

def trace_span(
    operation_name: str,
    attributes: Optional[Dict[str, Any]] = None,
    record_exception: bool = True
):
    """Create a trace span context manager"""
    return TraceContext(operation_name, attributes, record_exception)

def trace_function(
    operation_name: Optional[str] = None,
    record_exception: bool = True,
    record_inputs: bool = True,
    record_outputs: bool = True
):
    """Decorator to automatically trace a function"""
    def decorator(func):
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            attributes = {}
            
            if record_inputs:
                if args:
                    attributes["args_count"] = len(args)
                if kwargs:
                    attributes["kwargs"] = str(list(kwargs.keys()))
            
            with trace_span(op_name, attributes, record_exception) as span:
                try:
                    result = await func(*args, **kwargs)
                    
                    if record_outputs:
                        span.set_attribute("has_result", result is not None)
                    
                    return result
                except Exception as e:
                    logger.error(f"error_in_{op_name}", error_type=type(e).__name__, error=str(e), exc_info=True)
                    raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            attributes = {}
            
            if record_inputs:
                if args:
                    attributes["args_count"] = len(args)
                if kwargs:
                    attributes["kwargs"] = str(list(kwargs.keys()))
            
            with trace_span(op_name, attributes, record_exception) as span:
                try:
                    result = func(*args, **kwargs)
                    
                    if record_outputs:
                        span.set_attribute("has_result", result is not None)
                    
                    return result
                except Exception as e:
                    logger.error(f"error_in_{op_name}", error_type=type(e).__name__, error=str(e), exc_info=True)
                    raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

class PerformanceTracker:
    """Track performance metrics for operations"""
    
    def __init__(self, operation_name: str):
        self.operation_name = operation_name
        self.start_time = None
        self.end_time = None
        self.duration_ms = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration_ms = (self.end_time - self.start_time) * 1000
        
        status = "success" if exc_type is None else "error"
        logger.info(
            f"{self.operation_name}_completed",
            duration_ms=round(self.duration_ms, 2),
            status=status
        )

def set_span_attribute(key: str, value: Any):
    """Set attribute on current span"""
    try:
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            current_span.set_attribute(key, value)
    except Exception as e:
        logger.debug("failed_to_set_span_attribute", key=key, error=str(e))

def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """Add event to current span"""
    try:
        current_span = trace.get_current_span()
        if current_span and current_span.is_recording():
            current_span.add_event(name, attributes or {})
    except Exception as e:
        logger.debug("failed_to_add_span_event", name=name, error=str(e))