"""
FastAPI application with OpenTelemetry observability
"""
import os
import sys
import logging
from datetime import datetime, timezone
from uuid import uuid4

# Configure logging BEFORE importing anything else
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Initialize OpenTelemetry BEFORE creating FastAPI app
try:
    from config.opentelemetry_config import init_otel
    otel = init_otel(service_name="event-planning-api")
except Exception as e:
    logger.error(f"Failed to import OpenTelemetry config: {e}")
    otel = None

# Now import FastAPI
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import asyncio

# Initialize FastAPI
app = FastAPI(
    title="Event Planning MCP API",
    description="Model Context Protocol with Observability",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

# Initialize OpenTelemetry with FastAPI
if otel:
    otel.initialize(app)
    logger.info("✅ OpenTelemetry initialized successfully")
else:
    logger.warning("⚠️  OpenTelemetry not available")

# Get allowed origins from environment
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Models
class HealthResponse(BaseModel):
    status: str
    message: str
    python_version: str
    opentelemetry_enabled: bool

class PlanRequest(BaseModel):
    query: str
    context: Optional[dict] = None
    event_date: Optional[str] = None
    event_location: Optional[str] = None
    num_people: Optional[int] = 0
    budget: Optional[float] = 0.0

class PlanResponse(BaseModel):
    plan_id: str
    status: str
    query: str
    created_at: str
    event_date: Optional[str] = None
    event_location: Optional[str] = None
    num_people: Optional[int] = 0
    budget: Optional[float] = 0.0
    progress: Optional[int] = 0
    result: Optional[dict] = None
    updated_at: Optional[str] = None

# In-memory storage
plans_db = {}

# Routes
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Event Planning MCP API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "API is running",
        "python_version": f"{sys.version.split()[0]}",
        "opentelemetry_enabled": otel is not None
    }

@app.post("/plan/create", response_model=PlanResponse, tags=["Plans"])
async def create_plan(request: PlanRequest):
    """Create a new planning request"""
    plan_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    
    logger.info(
        f"Creating plan: {plan_id}",
        extra={
            "plan_id": plan_id,
            "query": request.query,
            "location": request.event_location
        }
    )
    
    plans_db[plan_id] = {
        "plan_id": plan_id,
        "status": "processing",
        "query": request.query,
        "event_date": request.event_date,
        "event_location": request.event_location,
        "num_people": request.num_people,
        "budget": request.budget,
        "context": request.context or {},
        "progress": 0,
        "result": None,
        "created_at": now,
        "updated_at": now
    }
    
    # Start background processing
    asyncio.create_task(process_plan(plan_id))
    
    return PlanResponse(**plans_db[plan_id])

@app.get("/plan/{plan_id}", response_model=PlanResponse, tags=["Plans"])
async def get_plan(plan_id: str):
    """Get a specific plan"""
    logger.info(f"Retrieving plan: {plan_id}")
    
    if plan_id not in plans_db:
        logger.warning(f"Plan not found: {plan_id}")
        raise HTTPException(status_code=404, detail=f"Plan {plan_id} not found")
    
    return PlanResponse(**plans_db[plan_id])

@app.get("/plans", tags=["Plans"])
async def list_plans():
    """List all plans"""
    logger.info(f"Listing all plans (total: {len(plans_db)})")
    
    return {
        "total": len(plans_db),
        "plans": list(plans_db.values())
    }

@app.get("/metrics", tags=["Metrics"])
async def get_metrics():
    """Get system metrics"""
    return {
        "total_plans": len(plans_db),
        "plans_by_status": {
            "processing": sum(1 for p in plans_db.values() if p["status"] == "processing"),
            "completed": sum(1 for p in plans_db.values() if p["status"] == "completed"),
            "failed": sum(1 for p in plans_db.values() if p["status"] == "failed")
        }
    }

# Background task
async def process_plan(plan_id: str):
    """Simulate plan processing"""
    try:
        plan = plans_db.get(plan_id)
        if not plan:
            return
        
        steps = [
            "Step 1: Initial planning",
            "Step 2: Resource allocation",
            "Step 3: Timeline creation",
            "Step 4: Budget breakdown"
        ]
        
        for i, step in enumerate(steps):
            await asyncio.sleep(1)  # Simulate work
            plan["progress"] = int((i + 1) / len(steps) * 100)
            plan["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        plan["status"] = "completed"
        plan["result"] = {
            "steps": steps,
            "estimated_cost": plan['budget'],
            "duration_days": 30
        }
        
        logger.info(f"Plan completed: {plan_id}")
    
    except Exception as e:
        logger.error(f"Plan processing failed: {plan_id} - {str(e)}", exc_info=True)
        plan = plans_db.get(plan_id)
        if plan:
            plan["status"] = "failed"
            plan["result"] = {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"🚀 Starting server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)