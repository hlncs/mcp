"""Event Planning MCP Backend"""

__version__ = "1.0.0"
__author__ = "Event Planning Team"

from backend.main import app
from backend.mcp_server import mcp_server
from backend.sse_manager import sse_manager

__all__ = [
    'app',
    'mcp_server',
    'sse_manager',
]