"""
ELARA - Core Module
This module contains the core components of ELARA including the event bus, state management, lifecycle management, and main assistant logic.
"""

from .event_bus import EventBus, EventType, Event
from .state import StateManager
from .lifecycle import LifecycleManager
from .assistant import Assistant

__all__ = [
    "EventBus",
    "EventType", 
    "Event",
    "StateManager",
    "LifecycleManager",
    "Assistant"
]
