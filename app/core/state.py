"""
ELARA - State Manager
This module manages the application state machine for ELARA.
"""

from enum import Enum
from typing import Optional, Callable
from threading import Lock

from app.config.constants import AssistantState
from app.utils.logger import get_logger
from app.core.event_bus import EventBus, EventType


class StateManager:
    """Manages the application state machine."""
    
    def __init__(self, event_bus: EventBus):
        self.logger = get_logger("elara.state")
        self.event_bus = event_bus
        self._current_state = AssistantState.IDLE
        self._previous_state = AssistantState.IDLE
        self._state_lock = Lock()
        self._state_callbacks: dict = {}
        
        # Subscribe to relevant events
        self.event_bus.subscribe(EventType.WAKE_WORD_DETECTED, self._on_wake_word)
        self.event_bus.subscribe(EventType.SPEECH_RECOGNIZED, self._on_speech_recognized)
        self.event_bus.subscribe(EventType.ACTION_STARTED, self._on_action_started)
        self.event_bus.subscribe(EventType.ACTION_COMPLETED, self._on_action_completed)
        self.event_bus.subscribe(EventType.ACTION_FAILED, self._on_action_failed)
        self.event_bus.subscribe(EventType.VOICE_VERIFICATION_RESULT, self._on_voice_verification_result)
    
    def get_state(self) -> AssistantState:
        """Get the current state."""
        with self._state_lock:
            return self._current_state
    
    def set_state(self, new_state: AssistantState) -> None:
        """
        Set a new state.
        
        Args:
            new_state: The new state to set
        """
        with self._state_lock:
            if self._current_state == new_state:
                return
            
            old_state = self._current_state
            self._previous_state = old_state
            self._current_state = new_state
            
            self.logger.info(f"State changed: {old_state.value} -> {new_state.value}")
            
            # Publish state change event
            self.event_bus.publish(EventType.STATE_CHANGED, {
                "old_state": old_state.value,
                "new_state": new_state.value
            })
            
            # Call state callbacks
            self._call_state_callbacks(new_state)
    
    def register_state_callback(self, state: AssistantState, callback: Callable) -> None:
        """
        Register a callback for a specific state.
        
        Args:
            state: The state to register callback for
            callback: The callback function
        """
        if state not in self._state_callbacks:
            self._state_callbacks[state] = []
        
        self._state_callbacks[state].append(callback)
        self.logger.debug(f"Registered callback for state: {state.value}")
    
    def _call_state_callbacks(self, state: AssistantState) -> None:
        """Call all callbacks registered for a state."""
        if state in self._state_callbacks:
            for callback in self._state_callbacks[state]:
                try:
                    callback(state)
                except Exception as e:
                    self.logger.error(f"Error in state callback: {e}")
    
    def _on_wake_word(self, event) -> None:
        """Handle wake word detection event."""
        self.set_state(AssistantState.WAKEWORD_DETECTED)
    
    def _on_speech_recognized(self, event) -> None:
        """Handle speech recognition event."""
        self.set_state(AssistantState.PROCESSING)
    
    def _on_action_started(self, event) -> None:
        """Handle action started event."""
        self.set_state(AssistantState.EXECUTING)
    
    def _on_action_completed(self, event) -> None:
        """Handle action completed event."""
        self.set_state(AssistantState.SPEAKING)
    
    def _on_action_failed(self, event) -> None:
        """Handle action failed event."""
        self.set_state(AssistantState.ERROR)
    
    def _on_voice_verification_result(self, event) -> None:
        """Handle voice verification result event."""
        result = event.data.get('result', False)
        if result:
            self.set_state(AssistantState.LISTENING_FOR_COMMAND)
        else:
            self.set_state(AssistantState.IDLE)
    
    def can_transition_to(self, new_state: AssistantState) -> bool:
        """
        Check if a state transition is valid.
        
        Args:
            new_state: The desired new state
            
        Returns:
            True if transition is valid, False otherwise
        """
        # Define valid state transitions
        valid_transitions = {
            AssistantState.IDLE: [
                AssistantState.LISTENING_FOR_WAKEWORD,
                AssistantState.PROCESSING
            ],
            AssistantState.LISTENING_FOR_WAKEWORD: [
                AssistantState.WAKEWORD_DETECTED,
                AssistantState.IDLE
            ],
            AssistantState.WAKEWORD_DETECTED: [
                AssistantState.VERIFYING_USER,
                AssistantState.LISTENING_FOR_COMMAND,
                AssistantState.IDLE
            ],
            AssistantState.VERIFYING_USER: [
                AssistantState.LISTENING_FOR_COMMAND,
                AssistantState.IDLE
            ],
            AssistantState.LISTENING_FOR_COMMAND: [
                AssistantState.PROCESSING,
                AssistantState.IDLE
            ],
            AssistantState.PROCESSING: [
                AssistantState.WAITING_FOR_CONFIRMATION,
                AssistantState.EXECUTING,
                AssistantState.SPEAKING,
                AssistantState.ERROR,
                AssistantState.IDLE
            ],
            AssistantState.WAITING_FOR_CONFIRMATION: [
                AssistantState.EXECUTING,
                AssistantState.IDLE
            ],
            AssistantState.EXECUTING: [
                AssistantState.SPEAKING,
                AssistantState.ERROR,
                AssistantState.IDLE
            ],
            AssistantState.SPEAKING: [
                AssistantState.IDLE,
                AssistantState.LISTENING_FOR_WAKEWORD
            ],
            AssistantState.ERROR: [
                AssistantState.IDLE,
                AssistantState.LISTENING_FOR_WAKEWORD
            ]
        }
        
        return new_state in valid_transitions.get(self._current_state, [])
    
    def reset_to_idle(self) -> None:
        """Reset the state to IDLE."""
        self.set_state(AssistantState.IDLE)
    
    def get_previous_state(self) -> AssistantState:
        """Get the previous state."""
        with self._state_lock:
            return self._previous_state
