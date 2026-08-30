"""
ELARA - Assistant Core
This module contains the main assistant logic and coordination.
"""

from typing import Optional, Dict, Any
from datetime import datetime

from app.config.constants import AssistantState
from app.utils.logger import get_logger
from app.core.event_bus import EventBus, EventType
from app.core.state import StateManager


class Assistant:
    """Main ELARA assistant class that coordinates all components."""
    
    def __init__(self, event_bus: EventBus, state_manager: StateManager):
        self.logger = get_logger("elara.assistant")
        self.event_bus = event_bus
        self.state_manager = state_manager
        self._is_active = False
        self._user_id: Optional[str] = None
        self._conversation_context: Dict[str, Any] = {}
        
        # Subscribe to events
        self._setup_event_subscriptions()
    
    def _setup_event_subscriptions(self):
        """Setup event subscriptions for the assistant."""
        self.event_bus.subscribe(EventType.COMMAND_RECEIVED, self._on_command_received)
        self.event_bus.subscribe(EventType.WAKE_WORD_DETECTED, self._on_wake_word_detected)
        self.event_bus.subscribe(EventType.SYSTEM_READY, self._on_system_ready)
    
    def _on_system_ready(self, event) -> None:
        """Handle system ready event."""
        self.logger.info("ELARA assistant ready")
        self._is_active = True
        self.state_manager.set_state(AssistantState.IDLE)
    
    def _on_wake_word_detected(self, event) -> None:
        """Handle wake word detection."""
        self.logger.info("Wake word detected")
        self.state_manager.set_state(AssistantState.WAKEWORD_DETECTED)
        
        # TODO: Start voice verification
        # TODO: Transition to listening for command
    
    def _on_command_received(self, event) -> None:
        """Handle command received event."""
        command = event.data.get("command", "")
        self.logger.info(f"Command received: {command}")
        
        # TODO: Process command
        # TODO: Generate response
        # TODO: Execute actions
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process a user command.
        
        Args:
            command: The user's command
            
        Returns:
            Dictionary with processing results
        """
        self.logger.info(f"Processing command: {command}")
        
        try:
            # Update conversation context
            self._conversation_context["last_command"] = command
            self._conversation_context["last_command_time"] = datetime.now().isoformat()
            
            # TODO: Implement command processing
            # - Intent recognition
            # - Action planning
            # - Permission checking
            # - Execution
            # - Response generation
            
            result = {
                "success": True,
                "response": "Command processed",
                "actions": []
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing command: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I encountered an error processing your command"
            }
    
    def set_user(self, user_id: str) -> None:
        """
        Set the current user.
        
        Args:
            user_id: The user identifier
        """
        self._user_id = user_id
        self.logger.info(f"User set: {user_id}")
    
    def get_user(self) -> Optional[str]:
        """Get the current user ID."""
        return self._user_id
    
    def is_active(self) -> bool:
        """Check if the assistant is active."""
        return self._is_active
    
    def activate(self) -> None:
        """Activate the assistant."""
        self._is_active = True
        self.logger.info("Assistant activated")
    
    def deactivate(self) -> None:
        """Deactivate the assistant."""
        self._is_active = False
        self.logger.info("Assistant deactivated")
    
    def get_conversation_context(self) -> Dict[str, Any]:
        """Get the current conversation context."""
        return self._conversation_context.copy()
    
    def clear_conversation_context(self) -> None:
        """Clear the conversation context."""
        self._conversation_context.clear()
        self.logger.info("Conversation context cleared")
    
    def update_conversation_context(self, key: str, value: Any) -> None:
        """
        Update the conversation context.
        
        Args:
            key: Context key
            value: Context value
        """
        self._conversation_context[key] = value
        self.logger.debug(f"Conversation context updated: {key}")
