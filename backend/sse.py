import asyncio
import json
from typing import AsyncGenerator, Callable, Dict, Any
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class EventStream:
    """Server-Sent Events stream manager"""
    
    def __init__(self):
        self.subscribers: Dict[str, list] = {}
    
    async def subscribe(self, channel: str) -> AsyncGenerator[str, None]:
        """Subscribe to a channel"""
        queue = asyncio.Queue()
        
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        
        self.subscribers[channel].append(queue)
        
        try:
            while True:
                message = await queue.get()
                yield f"data: {json.dumps(message)}\n\n"
        except asyncio.CancelledError:
            self.subscribers[channel].remove(queue)
            raise
    
    async def publish(self, channel: str, message: Dict[str, Any]):
        """Publish message to channel"""
        if channel in self.subscribers:
            for queue in self.subscribers[channel]:
                try:
                    await queue.put(message)
                except Exception as e:
                    logger.error(f"Error publishing to queue: {str(e)}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast to all channels"""
        for channel in self.subscribers:
            await self.publish(channel, message)

# Global event stream instance
event_stream = EventStream()

class PlanningEventTracker:
    """Track event planning progress"""
    
    def __init__(self, plan_id: str):
        self.plan_id = plan_id
        self.steps = []
        self.status = "started"
    
    async def log_step(self, step_name: str, status: str, details: Dict[str, Any] = None):
        """Log a planning step"""
        event = {
            "plan_id": self.plan_id,
            "step": step_name,
            "status": status,
            "details": details or {},
            "timestamp": asyncio.get_event_loop().time()
        }
        self.steps.append(event)
        await event_stream.publish(f"plan_{self.plan_id}", event)
    
    async def complete(self, result: Dict[str, Any]):
        """Mark planning as complete"""
        await self.log_step("planning", "completed", result)
        self.status = "completed"
    
    async def error(self, error_message: str):
        """Mark planning as errored"""
        await self.log_step("planning", "error", {"error": error_message})
        self.status = "error"

# Planning trackers storage
planning_trackers: Dict[str, PlanningEventTracker] = {}