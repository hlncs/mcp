# Observability Guide

Complete guide to monitoring and debugging the Event Planning MCP Server.

## Table of Contents

1. [Architecture](#architecture)
2. [Getting Started](#getting-started)
3. [Jaeger - Distributed Tracing](#jaeger---distributed-tracing)
4. [Prometheus - Metrics](#prometheus---metrics)
5. [Grafana - Dashboards](#grafana---dashboards)
6. [Logging](#logging)
7. [Common Queries](#common-queries)
8. [Troubleshooting](#troubleshooting)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Event Planning API                            │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  structlog (JSON Structured Logging)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  OpenTelemetry (Tracing & Spans)                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           ↓                                      │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Prometheus Client (Metrics Collection)                  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         ↓                  ↓                      ↓
    ┌────────┐         ┌──────────┐          ┌─────────┐
    │ Jaeger │         │Prometheus│          │Grafana  │
    │  (UI)  │         │(Storage) │          │(Visual) │
    └────────┘         └──────────┘          └─────────┘
   Port 16686           Port 9090             Port 3000
```

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Python 3.14.6
- OpenTelemetry, Prometheus, structlog installed

### Quick Start

```bash
# Start the observability stack
cd /Users/hien.luong/Projects/AI/mcp
docker-compose up -d

# Start the API server (in another terminal)
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Verify services are running
docker-compose ps
```

### Verify Setup

```bash
# Check API health
curl http://localhost:8000/health | jq

# Check Jaeger is running
curl http://localhost:16686/api/services

# Check Prometheus is running
curl http://localhost:9090/-/healthy
```

---

## Jaeger - Distributed Tracing

Jaeger captures the execution flow of requests through your system.

### Access Jaeger UI

```
http://localhost:16686
```

### View Traces

1. **Select Service**: Dropdown → `event-planning-api`
2. **Select Operation**: 
   - `POST /plan/create` - View plan creation traces
   - `POST /mcp/tools/{tool_name}` - View MCP tool execution
   - `GET /plan/{plan_id}/events` - View SSE streaming

3. **View Trace Details**:
   - Click on a trace to see spans
   - Each span shows timing, attributes, and events
   - View error stack traces for failed operations

### Example Trace for Plan Creation

```
POST /plan/create (100ms)
  ├─ create_plan (95ms)
  │  ├─ plan_creation (90ms)
  │  └─ simulate_plan_processing (started async)
  ├─ sse_manager.publish (4ms)
  └─ database_insert (1ms)
```

### Trace Attributes Captured

| Attribute | Example | Purpose |
|-----------|---------|---------|
| `http.method` | `POST` | HTTP method |
| `http.status_code` | `200` | Response status |
| `http.duration_ms` | `95.23` | Request duration |
| `trace_id` | `abc123def456` | Correlation ID |
| `plan_id` | `uuid-xxxx-yyyy` | Business entity ID |
| `error` | `true` | Error flag |
| `error.type` | `ValueError` | Exception type |

---

## Prometheus - Metrics

Prometheus collects and stores time-series metrics.

### Access Prometheus UI

```
http://localhost:9090
```

### Available Metrics

#### HTTP Metrics

```promql
# Request count by endpoint and status
http_requests_total{endpoint="/plan/create", status="200"}

# Request rate (requests per second)
rate(http_requests_total[5m])

# Request latency (p95)
histogram_quantile(0.95, http_request_duration_seconds)

# Error count by endpoint
http_errors_total{endpoint="/plan/create"}

# Error rate
rate(http_errors_total[5m])
```

#### Plan Metrics

```promql
# Total plans created
plans_created_total{status="success"}

# Plans processing time
histogram_quantile(0.99, plans_processing_time_seconds)

# Active plans by status
active_plans{status="processing"}
active_plans{status="completed"}
active_plans{status="failed"}
```

#### MCP Tool Metrics

```promql
# Tool execution count
mcp_tool_calls_total{tool_name="create_plan", status="success"}

# Tool execution time
histogram_quantile(0.95, mcp_tool_duration_seconds{tool_name="create_plan"})

# Tool errors
mcp_tool_errors_total{tool_name="create_plan", error_type="ValueError"}
```

#### SSE Metrics

```promql
# Active SSE connections
sse_connections_active

# Events published
sse_events_published_total{event_type="PLAN_CREATED"}

# Event message size
histogram_quantile(0.95, sse_message_size_bytes)
```

### Query Examples

**Top 5 slowest endpoints:**
```promql
topk(5, histogram_quantile(0.99, http_request_duration_seconds) by (endpoint))
```

**Success rate:**
```promql
sum(rate(http_requests_total{status="200"}[5m])) /
sum(rate(http_requests_total[5m])) * 100
```

**Plan completion rate:**
```promql
rate(plans_created_total{status="success"}[5m]) /
rate(plans_created_total[5m]) * 100
```

**Error breakdown:**
```promql
sum(rate(http_errors_total[5m])) by (error_type)
```

---

## Grafana - Dashboards

Grafana visualizes metrics from Prometheus.

### Access Grafana

```
http://localhost:3000
Username: admin
Password: admin
```

### Default Dashboard

The dashboard includes:

1. **HTTP Request Rate (5m)** - Requests per second
2. **HTTP Request Duration (p95)** - 95th percentile latency
3. **Error Rate (5m)** - Errors per second
4. **MCP Tool Call Rate (5m)** - Tool execution rate

### Add Custom Dashboard

1. Click **+** → **Dashboard**
2. Click **Add new panel**
3. Select **Prometheus** as data source
4. Enter query (see [Common Queries](#common-queries))
5. Set visualization type (Graph, Stat, Gauge, etc.)
6. Click **Apply**

### Example Dashboard Panels

**Panel 1: Request Volume**
```promql
sum(rate(http_requests_total[1m])) by (endpoint)
```
Visualization: Graph
Legend: Endpoint names

**Panel 2: Error Rate %**
```promql
sum(rate(http_errors_total[5m])) /
sum(rate(http_requests_total[5m])) * 100
```
Visualization: Stat
Threshold: Red at 5%

**Panel 3: Plan Status Distribution**
```promql
active_plans
```
Visualization: Pie Chart
Legend By: Label (status)

---

## Logging

All logs are output as structured JSON for easy parsing and searching.

### Log Format

```json
{
  "event": "request_completed",
  "timestamp": "2026-09-27T16:15:52.123456Z",
  "logger": "backend.config.observability_middleware",
  "level": "info",
  "method": "POST",
  "path": "/plan/create",
  "status_code": 200,
  "duration_ms": 95.23,
  "trace_id": "abc123def456",
  "request_id": "xyz789abc123"
}
```

### Log Levels

| Level | Used For | Example |
|-------|----------|---------|
| DEBUG | Development details | Span attribute failures |
| INFO | Normal operations | Request completion, plan created |
| WARNING | Unexpected conditions | Plan not found, retry attempt |
| ERROR | Error conditions | Request error, tool execution failed |
| CRITICAL | Critical failures | Server startup failed |

### Environment Variable

Toggle between JSON and colored console output:

```bash
# JSON output (production)
ENV=prod python -m uvicorn backend.main:app

# Colored console output (development)
ENV=dev python -m uvicorn backend.main:app
```

### Log Examples

**Plan Created:**
```json
{
  "event": "plan_created",
  "plan_id": "ca8f2b58-5fb4-4fa6-b71a-528c1e73f9c2",
  "query": "Wedding",
  "event_location": "Paris",
  "num_people": 150,
  "budget": 50000.0
}
```

**MCP Tool Executed:**
```json
{
  "event": "mcp_tool_executed",
  "tool_name": "create_plan",
  "duration_seconds": 0.023,
  "status": "success"
}
```

**Error Occurred:**
```json
{
  "event": "request_error",
  "method": "GET",
  "path": "/plan/unknown-id",
  "error_type": "HTTPException",
  "error_message": "Plan not found",
  "trace_id": "abc123def456"
}
```

---

## Common Queries

### Prometheus Queries

**1. Request Latency SLO (p99 < 500ms)**
```promql
histogram_quantile(0.99, http_request_duration_seconds) < 0.5
```

**2. Error Budget (99.9% uptime)**
```promql
(1 - (sum(rate(http_errors_total[30m])) / sum(rate(http_requests_total[30m])))) > 0.999
```

**3. Plan Success Rate**
```promql
sum(rate(plans_created_total{status="success"}[5m])) /
sum(rate(plans_created_total[5m])) * 100
```

**4. MCP Tool Performance**
```promql
histogram_quantile(0.95, mcp_tool_duration_seconds) by (tool_name)
```

**5. Top Errors**
```promql
topk(5, sum(rate(http_errors_total[5m])) by (error_type))
```

### Jaeger Queries

**Find all slow requests (>1s):**
1. Service: `event-planning-api`
2. Operation: `POST /plan/create`
3. Tags: Add filter → `duration > 1000ms`

**Find all errors:**
1. Service: `event-planning-api`
2. Tags: Add filter → `error=true`

**Find by trace ID:**
1. Search bar → Paste trace ID from logs

---

## Troubleshooting

### Issue: No traces in Jaeger

**Check:**
```bash
# 1. Verify Jaeger is running
docker-compose ps | grep jaeger

# 2. Check if API can reach Jaeger
curl http://localhost:16686/api/services

# 3. Verify OTEL initialization in logs
curl http://localhost:8000/health
```

**Fix:**
```bash
# Restart Jaeger
docker-compose restart jaeger

# Restart API
pkill -f uvicorn
python -m uvicorn backend.main:app --reload
```

### Issue: No metrics in Prometheus

**Check:**
```bash
# 1. Verify Prometheus can scrape
curl http://localhost:9090/api/targets

# 2. Check metrics endpoint
curl http://localhost:8000/metrics/prometheus | head -20

# 3. Check prometheus.yml config
cat prometheus.yml
```

**Fix:**
```bash
# Update prometheus.yml if needed
docker-compose restart prometheus
```

### Issue: High error rate

**Investigate:**
```bash
# 1. Check error logs
curl http://localhost:8000/metrics | jq '.error_rate'

# 2. View error traces in Jaeger
# Visit http://localhost:16686
# Filter by error=true

# 3. Check specific endpoint errors
curl http://localhost:9090/api/query?query=http_errors_total
```

### Issue: High latency

**Investigate:**
```bash
# 1. Check p95 latency
curl 'http://localhost:9090/api/query?query=histogram_quantile(0.95,http_request_duration_seconds)'

# 2. Identify slow endpoints
curl 'http://localhost:9090/api/query?query=topk(5,http_request_duration_seconds)'

# 3. View slow traces in Jaeger
# Visit http://localhost:16686
# Add filter: duration > 1000ms
```

---

## Performance Optimization

### Key Metrics to Monitor

| Metric | Target | Alert |
|--------|--------|-------|
| p95 Latency | < 200ms | > 500ms |
| p99 Latency | < 500ms | > 1000ms |
| Error Rate | < 0.1% | > 1% |
| Plan Success | > 99% | < 95% |
| MCP Tool Latency | < 100ms | > 500ms |

### Optimization Tips

1. **Monitor database queries** - Add query tracing
2. **Track SSE connection time** - Identify slow subscriptions
3. **Monitor MCP tool execution** - Profile slow tools
4. **Analyze error patterns** - Fix recurring issues
5. **Set up alerts** - Proactive monitoring

---

## Production Setup

### Enable TLS

Update `docker-compose.yml`:
```yaml
jaeger:
  environment:
    - COLLECTOR_OTLP_ENABLED=true
    - GRPC_STORAGE_TYPE=badger
```

### Data Persistence

```yaml
volumes:
  prometheus_data:
    driver: local
  grafana_data:
    driver: local
  jaeger_data:
    driver: local
```

### Resource Limits

```yaml
services:
  prometheus:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G
  grafana:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

---

## References

- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/grafana/)
- [OpenTelemetry](https://opentelemetry.io/)
- [structlog](https://www.structlog.org/)