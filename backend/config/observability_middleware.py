"""
Observability middleware for tracing, metrics, and logging
"""
import time
import uuid
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from opentelemetry import trace
import structlog

from backend.config.tracing import TraceContext, set_span_attribute, add_span_event
from backend.config.prometheus_config import (
    http_requests_total,
    http_request_duration_seconds,
    http_errors_total
)

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer(__name__)

class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Comprehensive observability middleware"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate or extract trace ID
        trace_id = request.headers.get("X-Trace-ID", str(uuid.uuid4()))
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Store in request state
        request.state.trace_id = trace_id
        request.state.request_id = request_id
        
        # Create span for the request
        span_name = f"{request.method} {request.url.path}"
        attributes = {
            "http.method": request.method,
            "http.url": str(request.url),
            "http.target": request.url.path,
            "http.host": request.url.hostname or "unknown",
            "http.scheme": request.url.scheme,
            "trace_id": trace_id,
            "request_id": request_id,
            "http.client_ip": request.client.host if request.client else "unknown",
        }
        
        start_time = time.time()
        
        with TraceContext(span_name, attributes) as span:
            try:
                # Process request
                response = await call_next(request)
                
                # Record response metrics
                duration_ms = (time.time() - start_time) * 1000
                status_code = response.status_code
                
                # Set span attributes
                set_span_attribute("http.status_code", status_code)
                set_span_attribute("http.duration_ms", duration_ms)
                
                # Record Prometheus metrics
                http_requests_total.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=status_code
                ).inc()
                
                http_request_duration_seconds.labels(
                    method=request.method,
                    endpoint=request.url.path
                ).observe(duration_ms / 1000)
                
                # Log request completion with structlog
                logger.info(
                    "request_completed",
                    method=request.method,
                    path=request.url.path,
                    status_code=status_code,
                    duration_ms=round(duration_ms, 2),
                    trace_id=trace_id,
                    request_id=request_id,
                    client_ip=request.client.host if request.client else "unknown"
                )
                
                # Add trace headers to response
                response.headers["X-Trace-ID"] = trace_id
                response.headers["X-Request-ID"] = request_id
                response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))
                
                # Record error if status >= 400
                if status_code >= 400:
                    error_type = "client_error" if status_code < 500 else "server_error"
                    http_errors_total.labels(
                        method=request.method,
                        endpoint=request.url.path,
                        status=status_code,
                        error_type=error_type
                    ).inc()
                    
                    add_span_event("http_error", {
                        "status_code": status_code,
                        "error_type": error_type
                    })
                    
                    logger.warning(
                        "http_error_response",
                        method=request.method,
                        path=request.url.path,
                        status_code=status_code,
                        error_type=error_type,
                        trace_id=trace_id,
                        request_id=request_id
                    )
                
                return response
            
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Record error
                set_span_attribute("error", True)
                set_span_attribute("error.type", type(e).__name__)
                set_span_attribute("error.message", str(e))
                
                # Record Prometheus metrics
                http_requests_total.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=500
                ).inc()
                
                http_errors_total.labels(
                    method=request.method,
                    endpoint=request.url.path,
                    status=500,
                    error_type="server_error"
                ).inc()
                
                # Log error with structlog
                logger.error(
                    "request_error",
                    method=request.method,
                    path=request.url.path,
                    error_type=type(e).__name__,
                    error_message=str(e),
                    duration_ms=round(duration_ms, 2),
                    trace_id=trace_id,
                    request_id=request_id,
                    exc_info=True
                )
                
                raise