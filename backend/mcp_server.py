import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class MCPTool:
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]

class MCPEventPlanningServer:
    """MCP Server for event planning operations"""
    
    def __init__(self):
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[MCPTool]:
        """Define available MCP tools"""
        return [
            MCPTool(
                name="create_plan",
                description="Create a new event planning request",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Event planning query"
                        },
                        "event_date": {
                            "type": "string",
                            "description": "Event date (YYYY-MM-DD)"
                        },
                        "event_location": {
                            "type": "string",
                            "description": "Event location"
                        },
                        "num_people": {
                            "type": "integer",
                            "description": "Number of people"
                        },
                        "budget": {
                            "type": "number",
                            "description": "Budget in dollars"
                        }
                    },
                    "required": ["query", "event_date", "event_location", "num_people", "budget"]
                }
            ),
            MCPTool(
                name="get_plan",
                description="Get details of a specific plan",
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                            "description": "Plan ID (UUID)"
                        }
                    },
                    "required": ["plan_id"]
                }
            ),
            MCPTool(
                name="list_plans",
                description="List all event plans",
                input_schema={
                    "type": "object",
                    "properties": {
                        "status": {
                            "type": "string",
                            "enum": ["processing", "completed", "failed"],
                            "description": "Filter by status (optional)"
                        }
                    }
                }
            ),
            MCPTool(
                name="update_plan",
                description="Update an existing plan",
                input_schema={
                    "type": "object",
                    "properties": {
                        "plan_id": {
                            "type": "string",
                            "description": "Plan ID"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["processing", "completed", "failed"],
                            "description": "Plan status"
                        },
                        "progress": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 100,
                            "description": "Progress percentage"
                        },
                        "result": {
                            "type": "string",
                            "description": "Planning result"
                        }
                    },
                    "required": ["plan_id"]
                }
            )
        ]
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """Get list of tools"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema
            }
            for tool in self.tools
        ]
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool"""
        logger.info(f"Calling MCP tool: {name} with args: {arguments}")
        
        if name == "create_plan":
            return {
                "status": "success",
                "message": "Plan creation initiated via MCP",
                "arguments": arguments
            }
        
        elif name == "get_plan":
            return {
                "status": "success",
                "plan_id": arguments.get("plan_id"),
                "message": "Plan retrieved via MCP"
            }
        
        elif name == "list_plans":
            return {
                "status": "success",
                "message": "Plans listed via MCP",
                "filter": arguments.get("status")
            }
        
        elif name == "update_plan":
            return {
                "status": "success",
                "plan_id": arguments.get("plan_id"),
                "message": "Plan updated via MCP"
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown tool: {name}"
            }
    
    async def run(self):
        """Initialize MCP server"""
        logger.info("MCP Server initialized with %d tools", len(self.tools))

# Global instance
mcp_server = MCPEventPlanningServer()