import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger('monitoring')

class MetricsCollector:
    """Collect and aggregate metrics"""
    
    def __init__(self):
        self.request_counts = defaultdict(int)
        self.error_counts = defaultdict(int)
        self.duration_totals = defaultdict(float)
        self.duration_counts = defaultdict(int)
    
    def record_request(
        self,
        path: str,
        method: str,
        status_code: int,
        duration_ms: float
    ):
        """Record request metric"""
        key = f'{method} {path}'
        self.request_counts[key] += 1
        self.duration_totals[key] += duration_ms
        self.duration_counts[key] += 1
        
        if status_code >= 400:
            self.error_counts[key] += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics"""
        endpoints = []
        
        for endpoint, count in self.request_counts.items():
            avg_duration = self.duration_totals[endpoint] / self.duration_counts[endpoint]
            error_count = self.error_counts[endpoint]
            
            endpoints.append({
                'endpoint': endpoint,
                'request_count': count,
                'error_count': error_count,
                'error_rate': (error_count / count * 100) if count > 0 else 0,
                'avg_duration_ms': round(avg_duration, 2),
            })
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_endpoints': len(endpoints),
            'total_requests': sum(self.request_counts.values()),
            'total_errors': sum(self.error_counts.values()),
            'endpoints': sorted(endpoints, key=lambda x: x['request_count'], reverse=True)
        }

# Global metrics collector
metrics_collector = MetricsCollector()

# Add to main.py
@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    logger.debug('Retrieving metrics')
    return metrics_collector.get_metrics()

## 🔍 Logging & Distributed Tracing

# The system includes comprehensive logging and distributed tracing capabilities:

### Logging Features

# - **Structured JSON Logging** - All logs in JSON format for easy parsing
# - **Multiple Log Levels** - DEBUG, INFO, WARNING, ERROR, CRITICAL
# - **Rotating File Logs** - Automatic log rotation (10MB per file, 10 backups)
# - **Console & File Output** - Logs to both stdout and files
# - **Context Tracking** - Trace IDs, Request IDs, User IDs in all logs

# **Log Files Location:**
# ```
# logs/
# ├── app.log           # Application logs
# ├── app.log.1         # Rotated backups
# └── app.log.2
# ```

### Distributed Tracing

- **Trace IDs** - Unique identifier for entire request flow
- **Span IDs** - Individual operation within a trace
- **Span Metrics** - Duration, status, errors for each span
- **Request Correlation** - Track requests through multiple services
- **Performance Analysis** - Identify bottlenecks

**Request Headers:**
```
X-Trace-ID: 550e8400-e29b-41d4-a716-446655440000
X-Request-ID: 22ac78f9-7ae1-4e8c-9e1f-f4f4c4f4c4f4
X-Response-Time-Ms: 1234
```

### View Traces

```bash
# Get trace data
curl http://localhost:8000/traces/{trace_id}

# Response:
{
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "span_count": 5,
  "total_duration_ms": 1234.56,
  "spans": [
    {
      "trace_id": "550e8400-e29b-41d4-a716-446655440000",
      "span_id": "22ac78f9-7ae1-4e8c-9e1f-f4f4c4f4c4f4",
      "operation_name": "POST /plan/create-stream",
      "duration_ms": 1200.50,
      "status": "SUCCESS",
      "tags": {
        "http.method": "POST",
        "http.status_code": 200
      }
    }
  ]
}
```

### View Metrics

```bash
# Get system metrics
curl http://localhost:8000/metrics

# Response:
{
  "timestamp": "2026-09-26T10:30:00",
  "total_endpoints": 12,
  "total_requests": 150,
  "total_errors": 2,
  "endpoints": [
    {
      "endpoint": "POST /plan/create-stream",
      "request_count": 25,
      "error_count": 1,
      "error_rate": 4.0,
      "avg_duration_ms": 1250.75
    }
  ]
}
```

### Log Examples

**Success Log:**
```json
{
  "timestamp": "2026-09-26T10:30:00.123456",
  "level": "INFO",
  "logger": "api",
  "message": "POST /plan/create-stream - 200",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "span_id": "22ac78f9-7ae1-4e8c-9e1f-f4f4c4f4c4f4",
  "request_id": "req-12345",
  "http_method": "POST",
  "http_status": 200,
  "duration_ms": 1234.56
}
```

**Error Log:**
```json
{
  "timestamp": "2026-09-26T10:30:01.123456",
  "level": "ERROR",
  "logger": "backend",
  "message": "Error creating event plan",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "plan_id": "plan-12345",
  "exception": "ValueError: Invalid budget",
  "module": "main",
  "function": "create_event_plan_with_stream",
  "line": 256
}
```

### Configuration

Set log level via environment variable:

```env
# Backend
LOG_LEVEL=INFO    # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Using Traces in Code

**Trace a function:**
```python
from config.tracing import trace_function

@trace_function("my_operation")
def my_function(arg1, arg2):
    # Function automatically traced
    return result
```

**Manual span creation:**
```python
from config.tracing import trace_span

with trace_span("complex_operation", tags={"user_id": "123"}) as span:
    # Do work
    span.set_tag("items_processed", 100)
    if error:
        span.set_error(exception)
```

**Access trace in request:**
```python
from fastapi import Request

@app.post("/my-endpoint")
async def my_endpoint(request: Request):
    trace_id = request.state.trace_id
    request_id = request.state.request_id
    # Use for logging
```

### Performance Monitoring

Monitor API performance via metrics endpoint:

```bash
# Real-time metrics
curl http://localhost:8000/metrics | jq '.endpoints | sort_by(.avg_duration_ms) | reverse'
```

**Identify slow endpoints:**
```bash
curl http://localhost:8000/metrics | jq '.endpoints[] | select(.avg_duration_ms > 1000)'
```

**Monitor error rates:**
```bash
curl http://localhost:8000/metrics | jq '.endpoints[] | select(.error_rate > 0)'
```