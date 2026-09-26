import uuid
import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from backend.monitoring import metrics_collector
from config.logging_config import set_trace_context

logger = logging.getLogger('api')

class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to record request metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Calculate duration in milliseconds
            duration_ms = (time.time() - start_time) * 1000
            
            # Record metrics
            metrics_collector.record_request(
                path=request.url.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms
            )
            
            logger.info(
                f'{request.method} {request.url.path} - {response.status_code}',
                extra={
                    'http_method': request.method,
                    'http_path': request.url.path,
                    'http_status': response.status_code,
                    'duration_ms': duration_ms,
                }
            )
            
            return response
        
        except Exception as e:
            # Record error metrics
            duration_ms = (time.time() - start_time) * 1000
            metrics_collector.record_request(
                path=request.url.path,
                method=request.method,
                status_code=500,
                duration_ms=duration_ms
            )
            
            logger.error(
                f'{request.method} {request.url.path} - Error: {str(e)}',
                extra={
                    'http_method': request.method,
                    'http_path': request.url.path,
                    'http_status': 500,
                    'duration_ms': duration_ms,
                },
                exc_info=True
            )
            
            raise

class TracingMiddleware(BaseHTTPMiddleware):
    """Middleware for distributed tracing"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Extract or create trace ID
        trace_id = request.headers.get('X-Trace-ID', str(uuid.uuid4()))
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Set trace context for logging
        set_trace_context(trace_id, request_id)
        
        # Add trace headers to request state
        request.state.trace_id = trace_id
        request.state.span_id = request_id
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add trace headers to response
            response.headers['X-Trace-ID'] = trace_id
            response.headers['X-Request-ID'] = request_id
            response.headers['X-Response-Time-Ms'] = str(round((time.time() - start_time) * 1000, 2))
            
            return response
        
        except Exception as e:
            logger.error(
                f'{request.method} {request.url.path} - Error: {str(e)}',
                extra={
                    'trace_id': trace_id,
                    'request_id': request_id,
                    'http_method': request.method,
                    'http_path': request.url.path,
                    'duration_ms': round((time.time() - start_time) * 1000, 2),
                },
                exc_info=True
            )
            
            raise

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request/response logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Log request
        logger.debug(
            f'Request started: {request.method} {request.url.path}',
            extra={
                'trace_id': getattr(request.state, 'trace_id', 'N/A'),
                'request_id': getattr(request.state, 'request_id', 'N/A'),
            }
        )
        
        response = await call_next(request)
        
        # Log response
        logger.debug(
            f'Response sent: {response.status_code}',
            extra={
                'trace_id': getattr(request.state, 'trace_id', 'N/A'),
                'request_id': getattr(request.state, 'request_id', 'N/A'),
            }
        )
        
        return response