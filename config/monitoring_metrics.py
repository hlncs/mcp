"""
Prometheus metrics definitions and collectors
"""
from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

request_size = Histogram(
    'http_request_size_bytes',
    'HTTP request size in bytes',
    ['method', 'endpoint']
)

response_size = Histogram(
    'http_response_size_bytes',
    'HTTP response size in bytes',
    ['method', 'endpoint', 'status']
)

# Error metrics
errors_total = Counter(
    'http_errors_total',
    'Total HTTP errors',
    ['method', 'endpoint', 'status', 'error_type']
)

errors_by_type = Counter(
    'errors_by_type',
    'Errors grouped by type',
    ['error_type', 'component']
)

# Business metrics
plans_created = Counter(
    'plans_created_total',
    'Total plans created',
    ['event_type', 'status']
)

plans_processing_time = Histogram(
    'plan_processing_seconds',
    'Plan processing time in seconds',
    ['event_type'],
    buckets=(1, 5, 10, 30, 60, 120, 300, 600)
)

active_plans = Gauge(
    'active_plans',
    'Number of active plans',
    ['status']
)

budget_allocated = Gauge(
    'budget_allocated_total',
    'Total budget allocated across all plans'
)

# System metrics
db_query_duration = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['query_type', 'table']
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_name']
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_name']
)

# Async task metrics
async_tasks_total = Counter(
    'async_tasks_total',
    'Total async tasks executed',
    ['task_name', 'status']
)

async_task_duration = Histogram(
    'async_task_duration_seconds',
    'Async task duration',
    ['task_name']
)

async_tasks_active = Gauge(
    'async_tasks_active',
    'Number of active async tasks',
    ['task_name']
)

# Real-time streaming metrics
sse_connections_active = Gauge(
    'sse_connections_active',
    'Number of active SSE connections'
)

sse_events_published = Counter(
    'sse_events_published_total',
    'Total SSE events published',
    ['event_type', 'status']
)

sse_disconnections = Counter(
    'sse_disconnections_total',
    'Total SSE disconnections',
    ['reason']
)

# Circuit breaker metrics
circuit_breaker_state = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=half_open, 2=open)',
    ['service_name']
)

circuit_breaker_trips = Counter(
    'circuit_breaker_trips_total',
    'Total circuit breaker trips',
    ['service_name']
)

# Dependencies
dependencies_check_duration = Histogram(
    'dependencies_check_duration_seconds',
    'Duration of dependency health checks',
    ['dependency']
)

dependencies_healthy = Gauge(
    'dependencies_healthy',
    'Health status of dependencies (1=healthy, 0=unhealthy)',
    ['dependency']
)

def record_request_metrics(method: str, endpoint: str, status_code: int, duration_ms: float):
    """Record HTTP request metrics"""
    request_count.labels(method=method, endpoint=endpoint, status=status_code).inc()
    request_duration.labels(method=method, endpoint=endpoint).observe(duration_ms / 1000)

def record_error(method: str, endpoint: str, status_code: int, error_type: str):
    """Record error metrics"""
    errors_total.labels(
        method=method,
        endpoint=endpoint,
        status=status_code,
        error_type=error_type
    ).inc()

def record_plan_created(event_type: str, status: str = "created"):
    """Record plan creation"""
    plans_created.labels(event_type=event_type, status=status).inc()

def record_plan_processing_time(event_type: str, duration_seconds: float):
    """Record plan processing time"""
    plans_processing_time.labels(event_type=event_type).observe(duration_seconds)

def update_active_plans(status: str, value: int):
    """Update active plans gauge"""
    active_plans.labels(status=status).set(value)

def update_budget_allocated(total: float):
    """Update total budget allocated"""
    budget_allocated.set(total)

def record_sse_event(event_type: str, status: str = "published"):
    """Record SSE event"""
    sse_events_published.labels(event_type=event_type, status=status).inc()

def update_sse_connections(count: int):
    """Update active SSE connections"""
    sse_connections_active.set(count)

def record_circuit_breaker_trip(service_name: str):
    """Record circuit breaker trip"""
    circuit_breaker_trips.labels(service_name=service_name).inc()

def update_circuit_breaker_state(service_name: str, state: int):
    """Update circuit breaker state"""
    circuit_breaker_state.labels(service_name=service_name).set(state)