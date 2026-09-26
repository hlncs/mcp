from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import logging
from datetime import datetime
import sys
import os
from fastapi.responses import StreamingResponse
import uuid
from sse import event_stream, PlanningEventTracker, planning_trackers

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.agents import AGENTS, AGENT_ROUTING_CONFIG, WEATHER_CONFIG
from mcp_servers.mock_data import MockDataServer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Event Planning API",
    description="AI-powered event planning with multi-agent orchestration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== Request/Response Models ====================

class LocationQuery(BaseModel):
    location: str
    date: Optional[str] = None

class WeatherRequest(BaseModel):
    location: str
    date: str

class EventPlanRequest(BaseModel):
    event_type: str
    location: str
    date: str
    guest_count: int
    budget: float
    weather_data: Optional[Dict[str, Any]] = None

class ReservationRequest(BaseModel):
    service_type: str
    service_id: str
    details: Dict[str, Any]

class BudgetValidationRequest(BaseModel):
    allocated_budget: float
    calculated_cost: float

# ==================== Mock Weather Function ====================

def get_weather_forecast(location: str, date: str) -> Dict[str, Any]:
    """Fetch weather forecast"""
    import random
    conditions = ["sunny", "clear", "partly cloudy"]
    temp = random.randint(18, 28)
    confidence = random.uniform(0.75, 0.99)
    
    return {
        "location": location,
        "date": date,
        "temperature": temp,
        "condition": random.choice(conditions),
        "confidence": round(confidence, 2),
        "humidity": random.randint(30, 70),
        "wind_speed": random.randint(5, 15),
        "is_favorable": (
            temp >= WEATHER_CONFIG["ideal_temp_range"][0] and
            temp <= WEATHER_CONFIG["ideal_temp_range"][1] and
            confidence >= WEATHER_CONFIG["min_confidence"]
        )
    }

# ==================== API Endpoints ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Event Planning API"
    }

@app.get("/agents")
async def list_agents():
    """List all available agents"""
    return {
        "agents": [
            {
                "name": agent["name"],
                "description": agent["description"],
                "skills": agent["skills"]
            }
            for agent in AGENTS
        ]
    }

@app.get("/agents/routing")
async def get_routing_config():
    """Get agent routing configuration"""
    return {"routing_config": AGENT_ROUTING_CONFIG}

@app.post("/weather")
async def get_weather(request: WeatherRequest):
    """Get weather forecast for a location"""
    try:
        weather_data = get_weather_forecast(request.location, request.date)
        return weather_data
    except Exception as e:
        logger.error(f"Weather endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/hotels")
async def search_hotels_endpoint(location: str):
    """Search hotels in a location"""
    try:
        hotels = MockDataServer.get_hotels(location, "", "")
        return {"hotels": hotels}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/venues")
async def search_venues_endpoint(location: str, capacity: int = 100):
    """Search venues in a location"""
    try:
        venues = MockDataServer.get_venues(location, capacity)
        return {"venues": venues}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search/services")
async def search_services(service_type: str, location: str):
    """Search any service type"""
    try:
        services = MockDataServer.search_services(service_type, location)
        return {
            "service_type": service_type,
            "location": location,
            "results": services,
            "count": len(services)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plan/create")
async def create_event_plan(request: EventPlanRequest):
    """Create a comprehensive event plan"""
    try:
        # Get weather forecast first
        weather_data = get_weather_forecast(request.location, request.date)
        
        # Create event plan
        plan = MockDataServer.create_event_plan(
            request.event_type,
            request.location,
            request.date,
            request.guest_count,
            request.budget,
            weather_data
        )
        
        # Generate summary
        summary = MockDataServer.get_event_summary(plan)
        
        return {
            "plan": plan,
            "summary": summary,
            "created_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Plan creation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/budget/validate")
async def validate_budget(request: BudgetValidationRequest):
    """Validate budget for an event"""
    try:
        validation = MockDataServer.validate_budget(
            request.allocated_budget,
            request.calculated_cost
        )
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reservation/make")
async def make_reservation(request: ReservationRequest):
    """Make a reservation for a service"""
    try:
        reservation = MockDataServer.make_reservation(
            request.service_type,
            request.service_id,
            request.details
        )
        return reservation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/services/all")
async def get_all_services(location: str):
    """Get all available services in a location"""
    try:
        services = MockDataServer.list_all_services(location)
        return {
            "location": location,
            "services": services
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== SSE Endpoints ====================

@app.get("/stream/plan/{plan_id}")
async def stream_plan_events(plan_id: str):
    """Stream real-time events for a specific event plan"""
    try:
        return StreamingResponse(
            event_stream.subscribe(f"plan_{plan_id}"),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream/global")
async def stream_global_events():
    """Stream global events to all clients"""
    try:
        return StreamingResponse(
            event_stream.subscribe("global"),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no",
                "Connection": "keep-alive"
            }
        )
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/plan/create-stream")
async def create_event_plan_with_stream(request: EventPlanRequest):
    """Create event plan with real-time progress streaming"""
    plan_id = str(uuid.uuid4())
    tracker = PlanningEventTracker(plan_id)
    planning_trackers[plan_id] = tracker
    
    try:
        # Start planning steps
        await tracker.log_step("validation", "started", {
            "event_type": request.event_type,
            "location": request.location
        })
        
        # Simulate planning process
        await tracker.log_step("validation", "completed")
        
        await tracker.log_step("weather_check", "started", {"location": request.location})
        weather_data = get_weather_forecast(request.location, request.date)
        await tracker.log_step("weather_check", "completed", weather_data)
        
        await tracker.log_step("venue_search", "started", {"capacity": request.guest_count})
        venues = MockDataServer.get_venues(request.location, request.guest_count)
        await tracker.log_step("venue_search", "completed", {"count": len(venues)})
        
        await tracker.log_step("catering_search", "started", {"guests": request.guest_count})
        catering = MockDataServer.get_catering_options(request.location, request.guest_count)
        await tracker.log_step("catering_search", "completed", {"count": len(catering)})
        
        await tracker.log_step("entertainment_search", "started", {"location": request.location})
        entertainment = MockDataServer.get_entertainment_options(request.location)
        await tracker.log_step("entertainment_search", "completed", {"count": len(entertainment)})
        
        await tracker.log_step("plan_creation", "started")
        plan = MockDataServer.create_event_plan(
            request.event_type,
            request.location,
            request.date,
            request.guest_count,
            request.budget,
            weather_data
        )
        await tracker.log_step("plan_creation", "completed")
        
        await tracker.log_step("summary_generation", "started")
        summary = MockDataServer.get_event_summary(plan)
        await tracker.log_step("summary_generation", "completed")
        
        await tracker.complete({
            "plan": plan,
            "summary": summary
        })
        
        return {
            "plan_id": plan_id,
            "stream_url": f"/stream/plan/{plan_id}",
            "plan": plan,
            "summary": summary
        }
    
    except Exception as e:
        logger.error(f"Plan creation error: {str(e)}")
        await tracker.error(str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Startup/Shutdown ====================

@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    logger.info("Event Planning API started")
    logger.info(f"Loaded {len(AGENTS)} agents")
    logger.info(f"Weather confidence threshold: {WEATHER_CONFIG['min_confidence']}")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Event Planning API shutdown")

# ==================== Run Server ====================

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )