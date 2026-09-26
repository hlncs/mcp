import json
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult
from mock_data import MockDataServer

# Initialize MCP Server
server = Server("event-planning-server")

# Define available tools for MCP
TOOLS: list[Tool] = [
    {
        "name": "get_hotels",
        "description": "Get available hotels in a location with check-in and check-out dates",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Hotel location"},
                "check_in": {"type": "string", "description": "Check-in date (YYYY-MM-DD)"},
                "check_out": {"type": "string", "description": "Check-out date (YYYY-MM-DD)"}
            },
            "required": ["location", "check_in", "check_out"]
        }
    },
    {
        "name": "get_flights",
        "description": "Get available flights between two cities",
        "inputSchema": {
            "type": "object",
            "properties": {
                "departure": {"type": "string", "description": "Departure city"},
                "arrival": {"type": "string", "description": "Arrival city"},
                "date": {"type": "string", "description": "Flight date (YYYY-MM-DD)"}
            },
            "required": ["departure", "arrival", "date"]
        }
    },
    {
        "name": "get_venues",
        "description": "Get available event venues in a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Venue location"},
                "capacity": {"type": "integer", "description": "Required capacity"}
            },
            "required": ["location", "capacity"]
        }
    },
    {
        "name": "get_catering_options",
        "description": "Get catering service options in a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Catering location"},
                "guest_count": {"type": "integer", "description": "Number of guests"}
            },
            "required": ["location", "guest_count"]
        }
    },
    {
        "name": "get_entertainment_options",
        "description": "Get entertainment service options in a location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Entertainment location"}
            },
            "required": ["location"]
        }
    },
    {
        "name": "get_transportation_options",
        "description": "Get transportation options between two locations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "departure": {"type": "string", "description": "Departure location"},
                "arrival": {"type": "string", "description": "Arrival location"},
                "date": {"type": "string", "description": "Travel date (YYYY-MM-DD)"},
                "passengers": {"type": "integer", "description": "Number of passengers"}
            },
            "required": ["departure", "arrival", "date", "passengers"]
        }
    },
    {
        "name": "search_services",
        "description": "Search and filter services by type and location",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_type": {
                    "type": "string",
                    "enum": ["hotels", "flights", "venues", "catering", "entertainment", "transportation"],
                    "description": "Type of service to search"
                },
                "location": {"type": "string", "description": "Service location"},
                "min_rating": {"type": "number", "description": "Minimum rating filter"},
                "sort_by": {"type": "string", "enum": ["price", "rating"], "description": "Sort results by"}
            },
            "required": ["service_type", "location"]
        }
    },
    {
        "name": "make_reservation",
        "description": "Make a reservation for a service",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_type": {"type": "string", "description": "Type of service"},
                "service_id": {"type": "string", "description": "Service ID"},
                "details": {"type": "object", "description": "Reservation details"}
            },
            "required": ["service_type", "service_id", "details"]
        }
    },
    {
        "name": "calculate_total_cost",
        "description": "Calculate total event cost with breakdown and tax",
        "inputSchema": {
            "type": "object",
            "properties": {
                "venue_cost": {"type": "number"},
                "catering_cost": {"type": "number"},
                "entertainment_cost": {"type": "number"},
                "transportation_cost": {"type": "number"},
                "accommodation_cost": {"type": "number"},
                "miscellaneous_cost": {"type": "number"}
            },
            "required": ["venue_cost", "catering_cost", "entertainment_cost"]
        }
    },
    {
        "name": "validate_budget",
        "description": "Validate if costs fit within allocated budget",
        "inputSchema": {
            "type": "object",
            "properties": {
                "allocated_budget": {"type": "number"},
                "calculated_cost": {"type": "number"}
            },
            "required": ["allocated_budget", "calculated_cost"]
        }
    },
    {
        "name": "create_event_plan",
        "description": "Create a comprehensive event plan",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_type": {"type": "string", "description": "Type of event"},
                "location": {"type": "string", "description": "Event location"},
                "date": {"type": "string", "description": "Event date (YYYY-MM-DD)"},
                "guest_count": {"type": "integer", "description": "Number of guests"},
                "budget": {"type": "number", "description": "Budget in USD"},
                "weather_data": {"type": "object", "description": "Weather forecast data"}
            },
            "required": ["event_type", "location", "date", "guest_count", "budget"]
        }
    },
    {
        "name": "get_event_summary",
        "description": "Generate a summary of the event plan",
        "inputSchema": {
            "type": "object",
            "properties": {
                "event_plan": {"type": "object", "description": "Event plan object"}
            },
            "required": ["event_plan"]
        }
    }
]

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return TOOLS

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ToolResult]:
    """Handle tool calls from LangChain agents"""
    
    try:
        if name == "get_hotels":
            result = MockDataServer.get_hotels(
                arguments["location"],
                arguments["check_in"],
                arguments["check_out"]
            )
        elif name == "get_flights":
            result = MockDataServer.get_flights(
                arguments["departure"],
                arguments["arrival"],
                arguments["date"]
            )
        elif name == "get_venues":
            result = MockDataServer.get_venues(
                arguments["location"],
                arguments["capacity"]
            )
        elif name == "get_catering_options":
            result = MockDataServer.get_catering_options(
                arguments["location"],
                arguments["guest_count"]
            )
        elif name == "get_entertainment_options":
            result = MockDataServer.get_entertainment_options(
                arguments["location"]
            )
        elif name == "get_transportation_options":
            result = MockDataServer.get_transportation_options(
                arguments["departure"],
                arguments["arrival"],
                arguments["date"],
                arguments["passengers"]
            )
        elif name == "search_services":
            result = MockDataServer.search_services(
                arguments["service_type"],
                arguments["location"],
                **{k: v for k, v in arguments.items() if k not in ["service_type", "location"]}
            )
        elif name == "make_reservation":
            result = MockDataServer.make_reservation(
                arguments["service_type"],
                arguments["service_id"],
                arguments["details"]
            )
        elif name == "calculate_total_cost":
            result = MockDataServer.calculate_total_cost(
                arguments.get("venue_cost", 0),
                arguments.get("catering_cost", 0),
                arguments.get("entertainment_cost", 0),
                arguments.get("transportation_cost", 0),
                arguments.get("accommodation_cost", 0),
                arguments.get("miscellaneous_cost", 0)
            )
        elif name == "validate_budget":
            result = MockDataServer.validate_budget(
                arguments["allocated_budget"],
                arguments["calculated_cost"]
            )
        elif name == "create_event_plan":
            result = MockDataServer.create_event_plan(
                arguments["event_type"],
                arguments["location"],
                arguments["date"],
                arguments["guest_count"],
                arguments["budget"],
                arguments.get("weather_data")
            )
        elif name == "get_event_summary":
            result = MockDataServer.get_event_summary(
                arguments["event_plan"]
            )
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    except Exception as e:
        error_msg = {"error": str(e), "tool": name}
        return [TextContent(type="text", text=json.dumps(error_msg))]

async def main():
    """Run the MCP server"""
    async with server:
        print("Event Planning MCP Server running...")
        await server.wait_for_shutdown()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())