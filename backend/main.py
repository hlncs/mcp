"""
FastAPI application with OpenTelemetry observability
"""
import os
import sys
import logging

# Configure logging BEFORE importing anything else
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import structlog early
import structlog

# Configure structlog for JSON output (best for observability)
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.dev.ConsoleRenderer() if os.getenv("ENV") == "dev" else structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Import FastAPI
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
import asyncio
from prometheus_client import CollectorRegistry, generate_latest, REGISTRY

# Import new modules
from backend.location_search import suggest_locations
from backend.booking_manager import (
    create_booking, get_booking, list_bookings, record_decision,
    BookingType,
)

# Import configurations
from backend.config.opentelemetry_config import init_otel
from backend.config.prometheus_config import init_prometheus_metrics, get_metrics
from backend.config.observability_middleware import ObservabilityMiddleware
from backend.config.tracing import trace_function, trace_span, PerformanceTracker

# Import backend modules
from backend.mcp_server import mcp_server
from backend.sse_manager import sse_manager, EventType

# Create FastAPI app
app = FastAPI(
    title="Event Planning MCP Server",
    description="Event planning with MCP and real-time SSE updates",
    version="1.0.0"
)

# Add CORS middleware (before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add observability middleware
app.add_middleware(ObservabilityMiddleware)

# Initialize OpenTelemetry
otel = init_otel(service_name="event-planning-api")
otel.initialize(app)

# Initialize metrics
init_prometheus_metrics()

# Data models
class PlanCreateRequest(BaseModel):
    query: str
    event_date: str
    event_location: str
    num_people: int
    budget: float

class Plan(BaseModel):
    plan_id: str
    status: str
    query: str
    created_at: datetime
    event_date: str
    event_location: str
    num_people: int
    budget: float
    progress: int
    result: Optional[str] = None
    updated_at: datetime

# In-memory storage
plans_db: dict = {}

@app.on_event("startup")
async def startup():
    """Initialize on startup"""
    logger.info("starting_server")
    
    # Initialize MCP server
    await mcp_server.run()
    
    logger.info(
        "server_initialized",
        mcp_tools_count=len(mcp_server.tools),
        features=["opentelemetry", "prometheus", "jaeger", "sse", "mcp"]
    )

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    logger.info("shutting_down_server")

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running",
        "python_version": "3.14.6",
        "opentelemetry_enabled": True,
        "mcp_enabled": True,
        "sse_enabled": True
    }

# Plan endpoints
@app.post("/plan/create")
@trace_function("create_plan")
async def create_plan(request: PlanCreateRequest):
    """Create a new event plan"""
    with PerformanceTracker("plan_creation"):
        plan_id = str(uuid4())
        
        plan = Plan(
            plan_id=plan_id,
            status="processing",
            query=request.query,
            created_at=datetime.utcnow(),
            event_date=request.event_date,
            event_location=request.event_location,
            num_people=request.num_people,
            budget=request.budget,
            progress=0,
            updated_at=datetime.utcnow()
        )
        
        plans_db[plan_id] = plan.dict()
        
        # Publish SSE event
        await sse_manager.publish(
            plan_id,
            EventType.PLAN_CREATED,
            {
                "plan_id": plan_id,
                "query": request.query,
                "event_location": request.event_location
            }
        )
        
        # Log the creation
        logger.info(
            "plan_created",
            plan_id=plan_id,
            query=request.query,
            event_location=request.event_location,
            num_people=request.num_people,
            budget=request.budget
        )
        
        # Simulate async processing
        asyncio.create_task(simulate_plan_processing(plan_id))
        
        return plan

@app.get("/plan/{plan_id}")
@trace_function("get_plan")
async def get_plan(plan_id: str):
    """Get plan details"""
    if plan_id not in plans_db:
        logger.warning("plan_not_found", plan_id=plan_id)
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return plans_db[plan_id]

@app.get("/plans")
async def list_plans(status: Optional[str] = Query(None)):
    """List all plans, optionally filtered by status"""
    plans = list(plans_db.values())
    
    if status:
        plans = [p for p in plans if p["status"] == status]
    
    logger.info("plans_listed", total_count=len(plans_db), filtered_count=len(plans), filter_status=status)
    
    return {
        "total": len(plans),
        "plans": plans
    }

@app.get("/plan/{plan_id}/events")
async def stream_plan_events(plan_id: str):
    """Stream real-time events for a plan"""
    if plan_id not in plans_db:
        logger.warning("plan_not_found_for_sse", plan_id=plan_id)
        raise HTTPException(status_code=404, detail="Plan not found")
    
    logger.info("sse_subscription_started", plan_id=plan_id)
    
    async def event_generator():
        async for event in sse_manager.subscribe(plan_id):
            yield event + "\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )

# MCP Tools endpoint
@app.get("/mcp/tools")
async def list_mcp_tools():
    """List available MCP tools"""
    tools = mcp_server.list_tools()
    logger.info("mcp_tools_listed", tools_count=len(tools))
    return {"tools": tools}

# MCP Tool execution endpoint
@app.post("/mcp/tools/{tool_name}")
@trace_function("mcp_tool_execution")
async def execute_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    """Execute an MCP tool"""
    from backend.config.prometheus_config import mcp_tool_calls_total, mcp_tool_duration_seconds, mcp_tool_errors_total
    
    start_time = datetime.utcnow()
    try:
        with PerformanceTracker(f"mcp_tool_{tool_name}"):
            result = await mcp_server.call_tool(tool_name, arguments)
            
            # Record metrics
            duration_seconds = (datetime.utcnow() - start_time).total_seconds()
            mcp_tool_calls_total.labels(tool_name=tool_name, status="success").inc()
            mcp_tool_duration_seconds.labels(tool_name=tool_name).observe(duration_seconds)
            
            logger.info(
                "mcp_tool_executed",
                tool_name=tool_name,
                duration_seconds=round(duration_seconds, 3),
                status="success"
            )
            return result
    except Exception as e:
        mcp_tool_calls_total.labels(tool_name=tool_name, status="error").inc()
        mcp_tool_errors_total.labels(tool_name=tool_name, error_type=type(e).__name__).inc()
        
        logger.error(
            "mcp_tool_error",
            tool_name=tool_name,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        raise HTTPException(status_code=500, detail=str(e))

# Metrics endpoint
@app.get("/metrics")
async def get_metrics_json():
    """Get application metrics in JSON format"""
    plans = list(plans_db.values())
    
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "total_plans": len(plans),
        "plans_by_status": {
            "processing": len([p for p in plans if p["status"] == "processing"]),
            "completed": len([p for p in plans if p["status"] == "completed"]),
            "failed": len([p for p in plans if p["status"] == "failed"])
        },
        "active_subscriptions": sse_manager.get_active_subscriptions(),
        "mcp_tools_available": len(mcp_server.tools)
    }
    
    logger.info("metrics_retrieved", metrics=metrics)
    return metrics

@app.get("/metrics/prometheus", response_class=Response)
async def get_prometheus_metrics():
    """Get Prometheus metrics in standard format"""
    from prometheus_client import generate_latest, REGISTRY
    metrics = generate_latest(REGISTRY).decode('utf-8')
    return Response(content=metrics, media_type="text/plain; charset=utf-8")


# ---------------------------------------------------------------------------
# Location search endpoints
# ---------------------------------------------------------------------------

@app.get("/location/search")
async def location_search(q: str = Query(..., min_length=2, description="Location query")):
    """
    Search for locations using OpenStreetMap Nominatim.
    Returns up to 5 suggestions for the given query string.
    Used by the frontend for autocomplete and 'did you mean?' suggestions.
    """
    if not q.strip():
        raise HTTPException(status_code=400, detail="Query must not be empty")

    suggestions = await suggest_locations(q.strip(), limit=5)

    logger.info("location_search_endpoint", extra={"query": q, "results": len(suggestions)})
    return {"query": q, "suggestions": suggestions, "count": len(suggestions)}


# ---------------------------------------------------------------------------
# Booking endpoints (human-in-the-loop)
# ---------------------------------------------------------------------------

class BookingDecisionRequest(BaseModel):
    approved: bool
    note: Optional[str] = None


@app.get("/bookings")
async def list_all_bookings(plan_id: Optional[str] = Query(None)):
    """List all bookings, optionally filtered by plan_id."""
    return {"bookings": list_bookings(plan_id=plan_id)}


@app.get("/bookings/{booking_id}")
async def get_booking_detail(booking_id: str):
    """Get a single booking by ID."""
    booking = get_booking(booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@app.put("/bookings/{booking_id}/decision")
async def decide_booking(booking_id: str, body: BookingDecisionRequest):
    """
    Human approves or rejects a pending booking offer.
    - approved=true  → status transitions to 'confirmed' + confirmation_code issued
    - approved=false → status transitions to 'rejected'
    """
    booking = get_booking(booking_id)
    if booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")

    try:
        updated = record_decision(booking_id, approved=body.approved, note=body.note)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc))

    action = "approved" if body.approved else "rejected"
    logger.info(
        "booking_decision_recorded",
        extra={"booking_id": booking_id, "action": action},
    )

    # Publish SSE event if there's a plan_id associated
    plan_id = updated.get("plan_id")
    if plan_id:
        await sse_manager.publish(
            plan_id,
            EventType.PROGRESS_UPDATE,
            {
                "event": "booking_decision",
                "booking_id": booking_id,
                "booking_type": updated.get("booking_type"),
                "status": updated.get("status"),
                "confirmation_code": updated.get("confirmation_code"),
            },
        )

    return updated

# Helper function for simulating processing
@trace_function("simulate_plan_processing")
async def simulate_plan_processing(plan_id: str):
    """Simulate async plan processing"""
    try:
        logger.info("plan_processing_started", plan_id=plan_id)
        
        # Simulate progress updates
        for progress in range(0, 101, 10):
            await asyncio.sleep(1)
            
            plans_db[plan_id]["progress"] = progress
            
            await sse_manager.publish(
                plan_id,
                EventType.PROGRESS_UPDATE,
                {"progress": progress, "message": f"Processing {progress}%"}
            )
        
        # Mark as completed
        plans_db[plan_id]["status"] = "completed"
        plans_db[plan_id]["result"] = f"Event plan for {plans_db[plan_id]['query']} created successfully"
        plans_db[plan_id]["updated_at"] = datetime.utcnow()
        
        await sse_manager.publish(
            plan_id,
            EventType.PLAN_COMPLETED,
            {
                "plan_id": plan_id,
                "result": plans_db[plan_id]["result"]
            }
        )
        
        logger.info("plan_completed", plan_id=plan_id, query=plans_db[plan_id]["query"])
    
    except Exception as e:
        logger.error(
            "plan_processing_error",
            plan_id=plan_id,
            error_type=type(e).__name__,
            error_message=str(e),
            exc_info=True
        )
        plans_db[plan_id]["status"] = "failed"
        
        await sse_manager.publish(
            plan_id,
            EventType.PLAN_FAILED,
            {"plan_id": plan_id, "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )