# Event Planning MCP Server

Advanced event planning system with Model Context Protocol (MCP) integration, real-time SSE updates, and comprehensive observability.

## Features

✅ **MCP Integration**
- 4 built-in MCP tools for event planning
- Tool discovery and execution
- Extensible tool framework

✅ **Real-time Updates**
- Server-Sent Events (SSE) for plan progress
- Event streaming for status updates
- Live progress tracking

✅ **Full Observability Stack**
- **Distributed Tracing**: Jaeger for request flow visualization
- **Metrics**: Prometheus for time-series metrics collection
- **Dashboards**: Grafana for visualization
- **Logging**: Structured JSON logging with structlog

✅ **Production Ready**
- OpenTelemetry instrumentation
- Error tracking and reporting
- Performance monitoring
- Request tracing with correlation IDs

## Quick Start

### Prerequisites

- Python 3.14.6
- Docker & Docker Compose
- curl/jq for testing

### 1. Start Observability Stack

```bash
docker-compose up -d
```

This starts:
- **Jaeger** (http://localhost:16686) - Distributed tracing
- **Prometheus** (http://localhost:9090) - Metrics storage
- **Grafana** (http://localhost:3000) - Dashboards

### 2. Start API Server

```bash
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Create Event Plan

```bash
curl -X POST http://localhost:8000/plan/create \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Wedding",
    "event_date": "2026-12-15",
    "event_location": "Paris",
    "num_people": 150,
    "budget": 50000
  }' | jq
```

### 4. View Traces

Visit http://localhost:16686 to see distributed traces.

---

## Architecture

```
┌─────────────────────────┐
│   Event Planning API    │
│  (FastAPI + OpenTel)    │
└────────┬────────────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │          │          │          │
    ▼          ▼          ▼          ▼
┌────────┐ ┌──────────┐ ┌──────┐ ┌────────┐
│ Jaeger │ │Prometheus│ │Grafana│ │Stdout  │
│Tracing │ │ Metrics  │ │ UI   │ │ Logs   │
└────────┘ └──────────┘ └──────┘ └────────┘
```

---

## API Endpoints

### Health Check
```
GET /health
```

### Plan Management
```
POST /plan/create              # Create new plan
GET  /plan/{plan_id}           # Get plan details
GET  /plans                    # List all plans
GET  /plan/{plan_id}/events    # Stream plan events (SSE)
```

### MCP Tools
```
GET  /mcp/tools                # List available tools
POST /mcp/tools/{tool_name}    # Execute tool
```

### Metrics
```
GET  /metrics                  # Application metrics (JSON)
GET  /metrics/prometheus       # Prometheus format metrics
```

---

## Project Structure

```
mcp/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── mcp_server.py          # MCP tools implementation
│   ├── sse_manager.py         # Server-Sent Events manager
│   └── config/
│       ├── opentelemetry_config.py    # Tracing setup
│       ├── prometheus_config.py       # Metrics definitions
│       ├── tracing.py                 # Tracing utilities
│       ├── observability_middleware.py # HTTP middleware
│       └── __init__.py
├── docs/
│   ├── OBSERVABILITY.md       # Detailed observability guide
│   └── QUICK_START.md         # Getting started guide
├── docker-compose.yml         # Observability stack
├── prometheus.yml             # Prometheus configuration
└── requirements.txt           # Python dependencies
```

---

## Documentation

- **[Quick Start](./docs/QUICK_START.md)** - Get running in 5 minutes
- **[Observability Guide](./docs/OBSERVABILITY.md)** - Complete monitoring guide
  - Jaeger distributed tracing
  - Prometheus metrics queries
  - Grafana dashboards
  - Structured logging
  - Troubleshooting

---

## Observability

### Distributed Tracing (Jaeger)

View request execution flow with detailed timing:

```
http://localhost:16686
```

**Features:**
- Request flow visualization
- Span timing and duration
- Error tracking
- Correlation IDs

### Metrics (Prometheus)

Query time-series metrics:

```
http://localhost:9090
```

**Key Metrics:**
- `http_requests_total` - Total requests by endpoint
- `http_request_duration_seconds` - Request latency (p50, p95, p99)
- `mcp_tool_calls_total` - MCP tool executions
- `plans_created_total` - Plans created
- `active_plans` - Active plans by status

### Dashboards (Grafana)

Pre-built dashboards for visualization:

```
http://localhost:3000
Username: admin
Password: admin
```

**Default Dashboard:**
- HTTP request rate and latency
- Error rate and breakdown
- MCP tool performance
- Plan status distribution

### Structured Logging

All logs are output as JSON for easy parsing:

```json
{
  "event": "plan_created",
  "plan_id": "uuid",
  "query": "Wedding",
  "timestamp": "2026-09-27T16:15:52.123Z",
  "trace_id": "correlation-id"
}
```

---

## Examples

### Create Plan and Stream Progress

```bash
# Terminal 1: Create plan
PLAN_ID=$(curl -s -X POST http://localhost:8000/plan/create \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Wedding",
    "event_date": "2026-12-15",
    "event_location": "Paris",
    "num_people": 150,
    "budget": 50000
  }' | jq -r '.plan_id')

# Terminal 2: Stream events
curl http://localhost:8000/plan/$PLAN_ID/events
```

### Execute MCP Tool

```bash
curl -X POST http://localhost:8000/mcp/tools/create_plan \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Birthday Party",
    "event_date": "2026-11-15",
    "event_location": "San Francisco",
    "num_people": 50,
    "budget": 2000
  }' | jq
```

### Query Metrics

```bash
# Request rate (requests/second)
curl 'http://localhost:9090/api/query?query=rate(http_requests_total[5m])'

# p95 latency
curl 'http://localhost:9090/api/query?query=histogram_quantile(0.95,http_request_duration_seconds)'

# Error rate
curl 'http://localhost:9090/api/query?query=rate(http_errors_total[5m])'
```

---

## Development

### Environment Variables

```bash
# Logging output format
ENV=dev    # Colored console output
ENV=prod   # JSON output (default)
```

### Running Tests

```bash
pytest tests/ -v
```

### Code Quality

```bash
# Format code
black backend/

# Lint
pylint backend/

# Type checking
mypy backend/
```

---

## Troubleshooting

### Jaeger not showing traces?

```bash
docker-compose restart jaeger
curl http://localhost:16686/api/services
```

### High error rate?

1. Check logs: `docker-compose logs backend`
2. View errors in Jaeger: http://localhost:16686 (filter `error=true`)
3. Query Prometheus: `http_errors_total`

### API not starting?

```bash
# Check for port conflicts
lsof -i :8000

# Check dependencies
pip install -r requirements.txt

# Restart with more logging
PYTHONUNBUFFERED=1 python -m uvicorn backend.main:app --log-level debug
```

---

## Performance

### SLOs (Service Level Objectives)

| Metric | Target |
|--------|--------|
| Availability | 99.9% |
| p95 Latency | < 200ms |
| p99 Latency | < 500ms |
| Error Rate | < 0.1% |
| Plan Success | > 99% |

### Optimization Tips

1. Monitor Jaeger for slow traces
2. Use Grafana to identify bottlenecks
3. Profile MCP tool execution
4. Optimize database queries
5. Configure caching strategies

---

## Production Deployment

### Docker Build

```bash
docker build -t event-planning-mcp:latest .
```

### Kubernetes

See `k8s/` directory for Kubernetes manifests:
```bash
kubectl apply -f k8s/
```

### Environment Setup

```bash
# Set secure configuration
export JAEGER_HOST=jaeger.production.svc.cluster.local
export PROMETHEUS_URL=http://prometheus:9090
export GRAFANA_URL=http://grafana:3000
```

---

## Contributing

1. Create feature branch: `git checkout -b feature/my-feature`
2. Make changes and test locally
3. Run tests: `pytest`
4. Submit pull request

---

## License

MIT License - See LICENSE file

---

## Support

For issues and questions:
- Check [OBSERVABILITY.md](./docs/OBSERVABILITY.md)
- Review error traces in Jaeger
- Query metrics in Prometheus
- Check logs in stdout

---

## Links

- **GitHub**: https://github.com/user/mcp
- **Documentation**: ./docs/
- **Issues**: https://github.com/user/mcp/issues
- **OpenTelemetry**: https://opentelemetry.io/
- **MCP Spec**: https://modelcontextprotocol.io/
