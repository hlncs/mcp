"""
FastAPI application with OpenTelemetry observability
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import asyncio
from uuid import uuid4
import logging
import sys
import os

# Setup structured logging
import structlog
structlog.configure(
    processors=[
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
)
logger = structlog.get_logger()

# Initialize FastAPI
app = FastAPI(
    title="MCP API",
    description="Model Context Protocol with Observability",
    version="0.1.0"
)

# Get allowed origins from environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# Add CORS middleware FIRST (before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add custom middleware (order matters - add metrics FIRST after CORS)
from backend.middleware import MetricsMiddleware, TracingMiddleware, LoggingMiddleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(TracingMiddleware)
app.add_middleware(MetricsMiddleware)

# Import monitoring
from backend.monitoring import metrics_collector

# Models
class HealthResponse(BaseModel):
    status: str
    message: str
    python_version: str

class PlanRequest(BaseModel):
    """Request to create a plan"""
    query: str
    context: Optional[dict] = {}
    event_date: Optional[str] = None
    event_location: Optional[str] = None
    num_people: Optional[int] = 0
    budget: Optional[float] = 0.0

class PlanResponse(BaseModel):
    """Response with plan details"""
    plan_id: str
    status: str
    query: str
    created_at: str
    event_date: Optional[str] = None
    event_location: Optional[str] = None
    num_people: Optional[int] = 0
    budget: Optional[float] = 0.0
    progress: Optional[int] = 0
    result: Optional[dict] = {}
    updated_at: Optional[str] = None

class PlanStatus(BaseModel):
    """Plan status details"""
    plan_id: str
    status: str
    progress: int
    result: dict = {}
    created_at: str
    updated_at: str

# In-memory storage (replace with database later)
plans_db = {}

# Background tasks
async def process_plan(plan_id: str):
    """Simulate plan processing in background"""
    try:
        if plan_id not in plans_db:
            return
        
        plan = plans_db[plan_id]
        
        # Simulate processing steps
        for progress in [25, 50, 75, 100]:
            await asyncio.sleep(2)  # Simulate work
            
            plan["progress"] = progress
            plan["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            logger.info(
                "plan_processing",
                plan_id=plan_id,
                progress=progress
            )
        
        # Mark as completed with results
        plan["status"] = "completed"
        plan["progress"] = 100
        plan["updated_at"] = datetime.now(timezone.utc).isoformat()
        plan["result"] = {
            "summary": f"Plan for: {plan['query']}\nDate: {plan['event_date']}\nLocation: {plan['event_location']}\nGuests: {plan['num_people']}\nBudget: ${plan['budget']}",
            "steps": [
                "Step 1: Initial planning",
                "Step 2: Resource allocation",
                "Step 3: Timeline creation",
                "Step 4: Budget breakdown"
            ],
            "estimated_cost": plan['budget'],
            "duration_days": 30,
            "event_details": {
                "event_date": plan['event_date'],
                "event_location": plan['event_location'],
                "num_people": plan['num_people'],
                "budget": plan['budget']
            }
        }
        
        logger.info(
            "plan_completed",
            plan_id=plan_id
        )
    
    except Exception as e:
        plan = plans_db.get(plan_id)
        if plan:
            plan["status"] = "failed"
            plan["result"] = {"error": str(e)}
        
        logger.error(
            "plan_processing_failed",
            plan_id=plan_id,
            error=str(e),
            exc_info=True
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    logger.info("health_check", endpoint="/health")
    return {
        "status": "healthy",
        "message": "API is running",
        "python_version": f"{sys.version.split()[0]}"
    }

@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("root", endpoint="/")
    return {"message": "Welcome to MCP API"}

@app.post("/plan", response_model=PlanResponse)
@app.post("/plan/create", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    """Create a new planning request"""
    plan_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    logger.info(
        "create_plan",
        plan_id=plan_id,
        query=request.query,
        event_date=request.event_date,
        event_location=request.event_location,
        num_people=request.num_people,
        budget=request.budget
    )
    
    plans_db[plan_id] = {
        "plan_id": plan_id,
        "status": "processing",
        "query": request.query,
        "event_date": request.event_date,
        "event_location": request.event_location,
        "num_people": request.num_people,
        "budget": request.budget,
        "context": request.context,
        "progress": 0,
        "result": {},
        "created_at": now,
        "updated_at": now
    }
    
    # Start background processing task
    asyncio.create_task(process_plan(plan_id))
    
    return {
        "plan_id": plan_id,
        "status": "processing",
        "query": request.query,
        "event_date": request.event_date,
        "event_location": request.event_location,
        "num_people": request.num_people,
        "budget": request.budget,
        "created_at": now
    }

@app.get("/plan/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: str):
    """Get a specific plan"""
    if plan_id not in plans_db:
        logger.warning("get_plan_not_found", plan_id=plan_id)
        raise HTTPException(status_code=404, detail="Plan not found")
    
    plan = plans_db[plan_id]
    logger.info("get_plan", plan_id=plan_id, status=plan["status"])
    
    return {
        "plan_id": plan["plan_id"],
        "status": plan["status"],
        "query": plan["query"],
        "event_date": plan.get("event_date"),
        "event_location": plan.get("event_location"),
        "num_people": plan.get("num_people", 0),
        "budget": plan.get("budget", 0.0),
        "progress": plan.get("progress", 0),
        "result": plan.get("result", {}),
        "created_at": plan["created_at"],
        "updated_at": plan.get("updated_at", plan["created_at"])
    }

@app.get("/plans")
async def list_plans():
    """List all plans"""
    logger.info("list_plans", count=len(plans_db))
    return {
        "total": len(plans_db),
        "plans": list(plans_db.values())
    }

@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    logger.info("metrics_request")
    return metrics_collector.get_metrics()

@app.post("/weather")
async def get_weather(request: PlanRequest):
    """Get weather information for event planning"""
    logger.info("get_weather", query=request.query)
    
    # Mock weather data for now
    return {
        "location": "San Francisco",
        "temperature": 72,
        "condition": "Partly Cloudy",
        "forecast": [
            {"day": "Monday", "high": 75, "low": 62, "condition": "Sunny"},
            {"day": "Tuesday", "high": 68, "low": 59, "condition": "Cloudy"},
            {"day": "Wednesday", "high": 70, "low": 60, "condition": "Rainy"}
        ]
    }

@app.get("/weather/{location}")
async def get_weather_by_location(location: str):
    """Get weather for a specific location"""
    logger.info("get_weather_by_location", location=location)
    
    # Mock weather data - replace with real API call later
    return {
        "location": location,
        "temperature": 72,
        "condition": "Partly Cloudy",
        "forecast": [
            {"day": "Monday", "high": 75, "low": 62, "condition": "Sunny"},
            {"day": "Tuesday", "high": 68, "low": 59, "condition": "Cloudy"},
            {"day": "Wednesday", "high": 70, "low": 60, "condition": "Rainy"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)