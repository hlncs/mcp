"""
Prometheus metrics configuration
"""
from prometheus_client import (
    Counter, Histogram, Gauge,
    CollectorRegistry, generate_latest
)
from prometheus_client.core import REGISTRY
import logging

logger = logging.getLogger(__name__)

# HTTP Request Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

http_request_size_bytes = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

http_response_size_bytes = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint', 'status']
)

http_errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status', 'error_type']
)

# Plan Metrics
plans_created_total = Counter(
    'plans_created_total',
    'Total event plans created',
    ['status']
)

plans_processing_time_seconds = Histogram(
    'plans_processing_time_seconds',
    'Event plan processing time in seconds',
    buckets=(1, 5, 10, 30, 60, 120, 300, 600)
)

active_plans_gauge = Gauge(
    'active_plans',
    'Number of active event plans',
    ['status']
)

plan_progress_gauge = Gauge(
    'plan_progress',
    'Current progress of event plans'
)

budget_utilization_gauge = Gauge(
    'budget_utilization_percent',
    'Budget utilization percentage for event plans'
)

# MCP Tool Metrics
mcp_tool_calls_total = Counter(
    'mcp_tool_calls_total',
    'Total MCP tool calls',
    ['tool_name', 'status']
)

mcp_tool_duration_seconds = Histogram(
    'mcp_tool_duration_seconds',
    'MCP tool execution duration in seconds',
    ['tool_name'],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0)
)

mcp_tool_errors_total = Counter(
    'mcp_tool_errors_total',
    'Total MCP tool errors',
    ['tool_name', 'error_type']
)

# SSE Metrics
sse_connections_active = Gauge(
    'sse_connections_active',
    'Number of active SSE connections'
)

sse_events_published_total = Counter(
    'sse_events_published_total',
    'Total SSE events published',
    ['event_type', 'status']
)

sse_message_size_bytes = Histogram(
    'sse_message_size_bytes',
    'SSE message size in bytes'
)

# System Metrics
otel_spans_created_total = Counter(
    'otel_spans_created_total',
    'Total OpenTelemetry spans created'
)

otel_spans_active = Gauge(
    'otel_spans_active',
    'Number of active OpenTelemetry spans'
)

# Database Metrics (placeholder for future use)
db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type', 'table']
)

db_query_errors_total = Counter(
    'db_query_errors_total',
    'Total database query errors',
    ['query_type', 'table', 'error_type']
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

cache_size_bytes = Gauge(
    'cache_size_bytes',
    'Cache size in bytes',
    ['cache_name']
)

def init_prometheus_metrics():
    """Initialize Prometheus metrics"""
    logger.info("✅ Prometheus metrics initialized")
    return REGISTRY

def get_metrics():
    """Get all metrics in Prometheus format"""
    return generate_latest(REGISTRY).decode('utf-8')

def increment_plan_creation(status: str = "success"):
    """Increment plan creation counter"""
    plans_created_total.labels(status=status).inc()

def observe_plan_processing_time(duration: float):
    """Record plan processing time"""
    plans_processing_time_seconds.observe(duration)

def set_active_plans_gauge(status: str, count: int):
    """Set active plans gauge"""
    active_plans_gauge.labels(status=status).set(count)

def set_sse_subscriptions_gauge(count: int):
    """Set SSE subscriptions gauge"""
    sse_connections_active.set(count)

def record_sse_event(event_type: str, status: str = "published"):
    """Record SSE event"""
    sse_events_published_total.labels(event_type=event_type, status=status).inc()

def record_budget_utilization(percent: float):
    """Record budget utilization"""
    budget_utilization_gauge.set(percent)