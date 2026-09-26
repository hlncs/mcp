# Quick Start Guide

Get the Event Planning MCP Server running with full observability in 5 minutes.

## Prerequisites

```bash
# Check you have Docker and Python 3.14.6
docker --version
python --version
```

## Step 1: Start Observability Stack

```bash
cd /path/to/Projects/AI/mcp

# Start Jaeger, Prometheus, and Grafana
docker-compose up -d

# Verify services started
docker-compose ps
```

**Expected output:**
```
NAME                COMMAND             STATUS
jaeger              java -jar...        Up
prometheus          /bin/prometheus     Up
grafana             /run.sh             Up
```

## Step 2: Start the API Server

```bash
# In a new terminal
cd /path/to/Projects/AI/mcp

# Install/update dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
✅ Prometheus metrics initialized
✅ OpenTelemetry initialized successfully
```

## Step 3: Create Test Plans

```bash
# Create a wedding plan
curl -X POST http://localhost:8000/plan/create \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Wedding",
    "event_date": "2026-12-15",
    "event_location": "Paris",
    "num_people": 150,
    "budget": 50000
  }' | jq

# Create a conference plan
curl -X POST http://localhost:8000/plan/create \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tech Conference",
    "event_date": "2027-01-20",
    "event_location": "Tokyo",
    "num_people": 500,
    "budget": 100000
  }' | jq
```

## Step 4: View Traces in Jaeger

```
http://localhost:16686
```

1. Select Service: `event-planning-api`
2. Select Operation: `POST /plan/create`
3. Click on a trace to see spans and timing

## Step 5: View Metrics in Grafana

```
http://localhost:3000
Username: admin
Password: admin
```

1. Add Data Source → Prometheus → `http://prometheus:9090`
2. Create Dashboard or Import from JSON
3. Add panels with queries:
   - `rate(http_requests_total[5m])`
   - `histogram_quantile(0.95, http_request_duration_seconds)`

## Step 6: Query Metrics in Prometheus

```
http://localhost:9090
```

Try these queries:
- `http_requests_total`
- `http_errors_total`
- `mcp_tool_calls_total`

---

## Common Operations

### View Health

```bash
curl http://localhost:8000/health | jq
```

### List Available MCP Tools

```bash
curl http://localhost:8000/mcp/tools | jq
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

### Get Metrics

```bash
# JSON format
curl http://localhost:8000/metrics | jq

# Prometheus format
curl http://localhost:8000/metrics/prometheus
```

---

## Troubleshooting

**Jaeger not showing traces?**
```bash
# Restart Jaeger
docker-compose restart jaeger

# Verify API can reach it
curl http://localhost:16686/api/services
```

**Prometheus not scraping metrics?**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/targets

# Restart Prometheus
docker-compose restart prometheus
```

**Port conflicts?**
```bash
# Check what's using ports
lsof -i :8000  # API
lsof -i :16686 # Jaeger
lsof -i :9090  # Prometheus
lsof -i :3000  # Grafana

# Kill process if needed
kill -9 <PID>
```

---

## What's Next?

1. **Read [OBSERVABILITY.md](./OBSERVABILITY.md)** - Deep dive into all features
2. **Setup alerts** - Configure Prometheus alerts
3. **Create dashboards** - Build custom Grafana dashboards
4. **Add custom metrics** - Extend with business metrics
5. **Deploy to production** - Use Kubernetes manifests

---

## Dashboard URLs

| Service | URL | Default Creds |
|---------|-----|----------------|
| API Health | http://localhost:8000/health | - |
| Jaeger Traces | http://localhost:16686 | - |
| Prometheus | http://localhost:9090 | - |
| Grafana | http://localhost:3000 | admin/admin |
