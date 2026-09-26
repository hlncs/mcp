# Paste the code from Option 1 above
"""
Server-Sent Events (SSE) support for streaming responses
"""
from typing import AsyncGenerator, Dict, Any
import json
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class PlanningEventTracker:
    """Track planning events for streaming"""
    event_id: str
    status: str = "pending"
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "status": self.status,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


# Global tracking dictionary
planning_trackers: Dict[str, PlanningEventTracker] = {}


async def event_stream(event_id: str) -> AsyncGenerator[str, None]:
    """
    Stream planning events as SSE
    
    Args:
        event_id: Unique identifier for the planning session
        
    Yields:
        SSE formatted event strings
    """
    if event_id not in planning_trackers:
        planning_trackers[event_id] = PlanningEventTracker(event_id=event_id)
    
    tracker = planning_trackers[event_id]
    
    # Initial connection event
    yield f"data: {json.dumps({'type': 'connected', 'event_id': event_id})}\n\n"
    
    # Yield tracker status
    yield f"data: {json.dumps({'type': 'status', **tracker.to_dict()})}\n\n"


def create_event(event_id: str, status: str, metadata: Dict[str, Any] = None) -> None:
    """
    Create or update a planning event
    
    Args:
        event_id: Event identifier
        status: Event status
        metadata: Additional event metadata
    """
    if event_id not in planning_trackers:
        planning_trackers[event_id] = PlanningEventTracker(event_id=event_id)
    
    tracker = planning_trackers[event_id]
    tracker.status = status
    if metadata:
        tracker.metadata.update(metadata)
    tracker.timestamp = datetime.now()