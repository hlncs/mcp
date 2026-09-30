import asyncio
import json
import logging
from datetime import datetime
from typing import AsyncGenerator, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)

class EventType(str, Enum):
    """SSE Event Types"""
    PLAN_CREATED = "plan.created"
    PLAN_UPDATED = "plan.updated"
    PLAN_COMPLETED = "plan.completed"
    PLAN_FAILED = "plan.failed"
    STATUS_UPDATE = "status.update"
    PROGRESS_UPDATE = "progress.update"
    ERROR = "error"

@dataclass
class SSEEvent:
    """Server-Sent Event"""
    event_type: EventType
    data: Dict
    plan_id: Optional[str] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    def to_sse_format(self) -> str:
        """Convert to SSE format"""
        def _default(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, Enum):
                return obj.value
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        lines = [f"event: {self.event_type.value}"]
        lines.append(f"data: {json.dumps(asdict(self), default=_default)}")
        lines.append("")
        return "\n".join(lines)

class SSEManager:
    """Manages Server-Sent Events for real-time updates"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[asyncio.Queue]] = {}
        self.event_history: List[SSEEvent] = []
        self.max_history = 100
    
    async def subscribe(self, plan_id: str) -> AsyncGenerator[str, None]:
        """Subscribe to events for a specific plan"""
        queue: asyncio.Queue = asyncio.Queue()
        
        if plan_id not in self.subscribers:
            self.subscribers[plan_id] = []
        
        self.subscribers[plan_id].append(queue)
        logger.info(f"Subscriber joined for plan {plan_id}")
        
        try:
            # Send recent history
            for event in self._get_plan_history(plan_id):
                yield event.to_sse_format()
            
            # Stream new events
            while True:
                event_data = await queue.get()
                if event_data is None:  # Unsubscribe signal
                    break
                
                event = SSEEvent(**event_data)
                yield event.to_sse_format()
        
        finally:
            if plan_id in self.subscribers:
                self.subscribers[plan_id].remove(queue)
                if not self.subscribers[plan_id]:
                    del self.subscribers[plan_id]
            logger.info(f"Subscriber left for plan {plan_id}")
    
    async def publish(self, plan_id: str, event_type: EventType, data: Dict):
        """Publish an event to all subscribers"""
        event = SSEEvent(
            event_type=event_type,
            data=data,
            plan_id=plan_id
        )
        
        # Store in history
        self._add_to_history(event)
        
        # Publish to subscribers
        if plan_id in self.subscribers:
            for queue in self.subscribers[plan_id]:
                try:
                    await queue.put(asdict(event))
                except asyncio.QueueFull:
                    logger.warning(f"Queue full for subscriber on plan {plan_id}")
    
    def _add_to_history(self, event: SSEEvent):
        """Add event to history"""
        self.event_history.append(event)
        if len(self.event_history) > self.max_history:
            self.event_history.pop(0)
    
    def _get_plan_history(self, plan_id: str) -> List[SSEEvent]:
        """Get event history for a plan"""
        return [e for e in self.event_history if e.plan_id == plan_id]
    
    async def broadcast(self, event_type: EventType, data: Dict):
        """Broadcast event to all subscribers"""
        for plan_id in self.subscribers:
            await self.publish(plan_id, event_type, data)
    
    def get_active_subscriptions(self) -> Dict[str, int]:
        """Get count of active subscriptions per plan"""
        return {
            plan_id: len(queues) 
            for plan_id, queues in self.subscribers.items()
        }

# Global instance
sse_manager = SSEManager()