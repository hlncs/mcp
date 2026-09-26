from typing import Any, Dict, List
from pydantic import BaseModel

class WeatherForecast(BaseModel):
    location: str
    date: str
    temperature: float
    condition: str
    confidence: float
    humidity: int
    wind_speed: float

class Tool(BaseModel):
    name: str
    description: str
    input_schema: Dict[str, Any]

# Weather Forecaster Tools
WEATHER_TOOLS = [
    {
        "name": "get_forecast",
        "description": "Get weather forecast for a specific location and date",
        "input_schema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Location name (e.g., 'Sydney, Australia')"},
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"}
            },
            "required": ["location", "date"]
        }
    }
]

# Venue Booker Tools
VENUE_TOOLS = [
    {
        "name": "book_venue",
        "description": "Book a venue for the event",
        "input_schema": {
            "type": "object",
            "properties": {
                "venue_name": {"type": "string"},
                "location": {"type": "string"},
                "date": {"type": "string"},
                "capacity": {"type": "integer"},
                "duration_hours": {"type": "number"},
                "event_type": {"type": "string"}
            },
            "required": ["venue_name", "location", "date", "capacity"]
        }
    }
]

# Hotel Reservation Tools
HOTEL_TOOLS = [
    {
        "name": "make_hotel_reservation",
        "description": "Make a hotel reservation",
        "input_schema": {
            "type": "object",
            "properties": {
                "hotel_name": {"type": "string"},
                "location": {"type": "string"},
                "check_in": {"type": "string", "description": "YYYY-MM-DD"},
                "check_out": {"type": "string", "description": "YYYY-MM-DD"},
                "rooms": {"type": "integer"},
                "guests": {"type": "integer"}
            },
            "required": ["hotel_name", "location", "check_in", "check_out", "rooms"]
        }
    }
]

# Flight Booking Tools
FLIGHT_TOOLS = [
    {
        "name": "book_flight",
        "description": "Book a flight for event attendees",
        "input_schema": {
            "type": "object",
            "properties": {
                "departure_city": {"type": "string"},
                "arrival_city": {"type": "string"},
                "departure_date": {"type": "string"},
                "return_date": {"type": "string"},
                "passengers": {"type": "integer"},
                "cabin_class": {"type": "string", "enum": ["economy", "business", "first"]}
            },
            "required": ["departure_city", "arrival_city", "departure_date", "passengers"]
        }
    }
]

# Budget Manager Tools
BUDGET_TOOLS = [
    {
        "name": "manage_budget",
        "description": "Track and manage event budget",
        "input_schema": {
            "type": "object",
            "properties": {
                "total_budget": {"type": "number"},
                "category": {"type": "string", "enum": ["venue", "catering", "entertainment", "travel", "accommodation", "misc"]},
                "amount": {"type": "number"},
                "description": {"type": "string"}
            },
            "required": ["total_budget", "category", "amount"]
        }
    }
]

# Plan Summarizer Tools
SUMMARY_TOOLS = [
    {
        "name": "summarize_plan",
        "description": "Generate a comprehensive event plan summary",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_type": {"type": "string"},
                "date": {"type": "string"},
                "location": {"type": "string"},
                "weather_data": {"type": "object"},
                "bookings": {"type": "object"},
                "budget_summary": {"type": "object"}
            },
            "required": ["event_type", "date", "location"]
        }
    }
]

# Tool registry
TOOLS_REGISTRY = {
    "weather_forecaster": WEATHER_TOOLS,
    "venue_booker": VENUE_TOOLS,
    "hotel_reservation_agent": HOTEL_TOOLS,
    "flight_booking_agent": FLIGHT_TOOLS,
    "budget_manager": BUDGET_TOOLS,
    "plan_summarizer": SUMMARY_TOOLS
}