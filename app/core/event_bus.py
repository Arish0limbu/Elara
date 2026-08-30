"""
ELARA - Event Bus
This module provides a centralized event system for component communication.
"""

from typing import Callable, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import logging

from app.utils.logger import get_logger


class EventType(Enum):
    """Event types for the event bus."""
    # Assistant events
    STATE_CHANGED = "state_changed"
    COMMAND_RECEIVED = "command_received"
    RESPONSE_GENERATED = "response_generated"
    
    # Voice events
    WAKE_WORD_DETECTED = "wake_word_detected"
    SPEECH_RECOGNIZED = "speech_recognized"
    VOICE_VERIFICATION_RESULT = "voice_verification_result"
    
    # Action events
    ACTION_STARTED = "action_started"
    ACTION_COMPLETED = "action_completed"
    ACTION_FAILED = "action_failed"
    
    # System events
    SYSTEM_READY = "system_ready"
    SYSTEM_SHUTDOWN = "system_shutdown"
    ERROR_OCCURRED = "error_occurred"
    
    # UI events
    SHOW_NOTIFICATION = "show_notification"
    UPDATE_STATUS = "update_status"


@dataclass
class Event:
    """Event data structure."""
    type: EventType
    data: Dict[str, Any]
    timestamp: float
    
    def __init__(self, event_type: EventType, data: Dict[str, Any]):
        import time
        self.type = event_type
        self.data = data
        self.timestamp = time.time()


class EventBus:
    """Centralized event bus for component communication."""
    
    def __init__(self):
        self.logger = get_logger("elara.event_bus")
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history_size = 1000
    
    def subscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Subscribe to an event type.
        
        Args:
            event_type: The event type to subscribe to
            callback: The callback function to call when event occurs
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        self._subscribers[event_type].append(callback)
        self.logger.debug(f"Subscribed to event: {event_type.value}")
    
    def unsubscribe(self, event_type: EventType, callback: Callable) -> None:
        """
        Unsubscribe from an event type.
        
        Args:
            event_type: The event type to unsubscribe from
            callback: The callback function to remove
        """
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                self.logger.debug(f"Unsubscribed from event: {event_type.value}")
    
    def publish(self, event_type: EventType, data: Dict[str, Any] = None) -> None:
        """
        Publish an event to all subscribers.
        
        Args:
            event_type: The event type to publish
            data: Optional event data
        """
        if data is None:
            data = {}
        
        event = Event(event_type, data)
        
        # Add to history
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
        
        # Notify subscribers
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(event)
                except Exception as e:
                    self.logger.error(f"Error in event callback: {e}")
        
        self.logger.debug(f"Published event: {event_type.value}")
    
    def get_event_history(self, event_type: EventType = None) -> List[Event]:
        """
        Get event history.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            List of events
        """
        if event_type:
            return [e for e in self._event_history if e.type == event_type]
        return self._event_history.copy()
    
    def clear_history(self) -> None:
        """Clear event history."""
        self._event_history.clear()
        self.logger.debug("Event history cleared")
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """
        Get the number of subscribers for an event type.
        
        Args:
            event_type: The event type
            
        Returns:
            Number of subscribers
        """
        return len(self._subscribers.get(event_type, []))
