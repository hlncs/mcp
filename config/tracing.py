import uuid
import time
from typing import Optional, Dict, Any, Callable
from functools import wraps
from contextlib import contextmanager
import logging
from datetime import datetime

logger = logging.getLogger('tracing')

class Span:
    """Represents a single span in distributed tracing"""
    
    def __init__(
        self,
        trace_id: str,
        span_id: str,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None
    ):
        self.trace_id = trace_id
        self.span_id = span_id
        self.operation_name = operation_name
        self.parent_span_id = parent_span_id
        self.tags = tags or {}
        self.start_time = time.time()
        self.end_time = None
        self.duration_ms = 0
        self.status = 'PENDING'
        self.error = None
    
    def set_tag(self, key: str, value: Any):
        """Set a tag on the span"""
        self.tags[key] = value
    
    def set_error(self, error: Exception):
        """Mark span as error"""
        self.status = 'ERROR'
        self.error = {
            'type': type(error).__name__,
            'message': str(error),
            'traceback': None
        }
    
    def finish(self):
        """Finish the span"""
        self.end_time = time.time()
        self.duration_ms = round((self.end_time - self.start_time) * 1000, 2)
        if self.status == 'PENDING':
            self.status = 'SUCCESS'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert span to dictionary"""
        return {
            'trace_id': self.trace_id,
            'span_id': self.span_id,
            'parent_span_id': self.parent_span_id,
            'operation_name': self.operation_name,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            'duration_ms': self.duration_ms,
            'status': self.status,
            'tags': self.tags,
            'error': self.error,
        }

class Tracer:
    """Distributed tracer"""
    
    def __init__(self):
        self.spans: Dict[str, list] = {}
        self.current_trace_id = None
        self.current_span_id = None
    
    def start_trace(self, trace_id: str = None) -> str:
        """Start a new trace"""
        self.current_trace_id = trace_id or str(uuid.uuid4())
        self.current_span_id = self.current_trace_id
        self.spans[self.current_trace_id] = []
        
        logger.info(
            f'Trace started: {self.current_trace_id}',
            extra={'trace_id': self.current_trace_id}
        )
        
        return self.current_trace_id
    
    def start_span(
        self,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None
    ) -> Span:
        """Start a new span"""
        span_id = str(uuid.uuid4())
        parent_id = parent_span_id or self.current_span_id
        
        span = Span(
            trace_id=self.current_trace_id,
            span_id=span_id,
            operation_name=operation_name,
            parent_span_id=parent_id,
            tags=tags or {}
        )
        
        if self.current_trace_id:
            self.spans[self.current_trace_id].append(span)
        
        self.current_span_id = span_id
        
        logger.debug(
            f'Span started: {operation_name}',
            extra={
                'trace_id': self.current_trace_id,
                'span_id': span_id
            }
        )
        
        return span
    
    def end_span(self, span: Span):
        """End a span"""
        span.finish()
        self.current_span_id = span.parent_span_id
        
        logger.debug(
            f'Span ended: {span.operation_name} ({span.duration_ms}ms)',
            extra={
                'trace_id': span.trace_id,
                'span_id': span.span_id,
                'duration_ms': span.duration_ms
            }
        )
    
    def get_trace(self, trace_id: str) -> list:
        """Get all spans for a trace"""
        return self.spans.get(trace_id, [])
    
    def export_trace(self, trace_id: str) -> Dict[str, Any]:
        """Export trace data"""
        spans = self.get_trace(trace_id)
        return {
            'trace_id': trace_id,
            'span_count': len(spans),
            'spans': [span.to_dict() for span in spans],
            'total_duration_ms': sum(s.duration_ms for s in spans)
        }

# Global tracer instance
tracer = Tracer()

@contextmanager
def trace_span(operation_name: str, tags: Optional[Dict[str, Any]] = None):
    """Context manager for tracing spans"""
    span = tracer.start_span(operation_name, tags=tags)
    try:
        yield span
    except Exception as e:
        span.set_error(e)
        raise
    finally:
        tracer.end_span(span)

def trace_function(operation_name: str = None):
    """Decorator for tracing functions"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            op_name = operation_name or f'{func.__module__}.{func.__name__}'
            with trace_span(op_name, tags={'args': len(args), 'kwargs': len(kwargs)}) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_tag('result_type', type(result).__name__)
                    return result
                except Exception as e:
                    span.set_error(e)
                    raise
        return wrapper
    return decorator

def trace_async_function(operation_name: str = None):
    """Decorator for tracing async functions"""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            op_name = operation_name or f'{func.__module__}.{func.__name__}'
            with trace_span(op_name, tags={'args': len(args), 'kwargs': len(kwargs)}) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_tag('result_type', type(result).__name__)
                    return result
                except Exception as e:
                    span.set_error(e)
                    raise
        return wrapper
    return decorator