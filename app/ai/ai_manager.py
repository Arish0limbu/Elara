"""
ELARA - AI Manager
This module coordinates AI components and integrates with the action/permission system.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json

from app.ai.intent_parser import IntentCategory, IntentAction, IntentParser, Intent
from app.ai.llm_provider import LLMProviderManager
from app.ai.action_generator import ActionGenerator, GeneratedAction
from app.ai.response_generator import ResponseGenerator, ResponseContext
from app.actions.registry import ActionRegistry
from app.actions.permissions import PermissionEngine, SecurityPolicy
from app.actions.confirmation import ConfirmationEngine
from app.actions.executor import ActionExecutor
from app.utils.logger import get_logger


@dataclass
class AIRequest:
    """Represents a user request to the AI system."""
    user_input: str
    user_id: Optional[str] = None
    request_id: Optional[str] = None
    timestamp: datetime = None
    context: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.request_id is None:
            import uuid
            self.request_id = str(uuid.uuid4())


@dataclass
class AIResponse:
    """Represents the AI system's response."""
    response_text: str
    generated_action: Optional[GeneratedAction]
    action_result: Optional[Dict[str, Any]]
    was_executed: bool
    error: Optional[str]
    request_id: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


class AIManager:
    """Manages AI components and coordinates with action/permission system."""
    
    def __init__(
        self,
        action_registry: Optional[ActionRegistry] = None,
        permission_engine: Optional[PermissionEngine] = None,
        security_policy: Optional[SecurityPolicy] = None,
        confirmation_engine: Optional[ConfirmationEngine] = None,
        action_executor: Optional[ActionExecutor] = None
    ):
        self.logger = get_logger("elara.ai_manager")
        
        # AI components
        self.intent_parser = IntentParser()
        self.llm_manager = LLMProviderManager()
        self.action_generator = ActionGenerator(self.llm_manager)
        self.response_generator = ResponseGenerator(self.llm_manager)
        
        # Security and action components
        self.action_registry = action_registry or ActionRegistry()
        self.permission_engine = permission_engine or PermissionEngine()
        self.security_policy = security_policy or SecurityPolicy()
        self.confirmation_engine = confirmation_engine or ConfirmationEngine()
        self.action_executor = action_executor or ActionExecutor()
        
        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []
        self.max_history_length = 20
        
        # User profiles (simplified - in production would use database)
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        
        self.logger.info("AI manager initialized")
    
    def process_request(self, request: AIRequest) -> AIResponse:
        """
        Process a user request through the full AI pipeline.
        
        Args:
            request: User request
            
        Returns:
            AI response
        """
        self.logger.info(f"Processing request: '{request.user_input}'")
        
        try:
            # Step 1: Parse intent
            intent = self.intent_parser.parse(request.user_input)
            self.logger.info(f"Parsed intent: {intent.category.value}/{intent.action.value}")
            
            # Step 2: Generate action
            generated_action = self.action_generator.generate_action_from_text(request.user_input)
            self.logger.info(f"Generated action: {generated_action.action_id} (confidence: {generated_action.confidence:.2f})")
            
            # Step 3: Validate action
            if not generated_action.is_valid:
                error = f"Invalid action: {', '.join(generated_action.validation_errors)}"
                self.logger.warning(error)
                return self._create_error_response(request, generated_action, error)
            
            # Step 4: Check permissions
            from app.config.constants import PermissionLevel
            action = self.action_registry.get_action(generated_action.action_id)
            if action:
                permitted, reason = self.permission_engine.check_permission(
                    generated_action.action_id,
                    action.permission_level,
                    request.user_id
                )
                
                if not permitted:
                    self.logger.warning(f"Permission denied: {reason}")
                    response_text = self.response_generator.generate_permission_denied_response(generated_action)
                    return AIResponse(
                        response_text=response_text,
                        generated_action=generated_action,
                        action_result=None,
                        was_executed=False,
                        error=reason,
                        request_id=request.request_id
                    )
            
            # Step 5: Check if confirmation required
            requires_confirmation = self._requires_confirmation(generated_action)
            if requires_confirmation:
                confirmation_response = self._handle_confirmation_request(request, generated_action)
                if confirmation_response:
                    return confirmation_response
            
            # Step 6: Execute action
            action_result = self._execute_action(generated_action)
            
            # Step 7: Generate response
            response_text = self._generate_response(request, generated_action, action_result)
            
            # Step 8: Update conversation history
            self._update_conversation_history(request, response_text)
            
            return AIResponse(
                response_text=response_text,
                generated_action=generated_action,
                action_result=action_result,
                was_executed=action_result.get("success", False) if action_result else False,
                error=None,
                request_id=request.request_id
            )
            
        except Exception as e:
            self.logger.error(f"Request processing failed: {e}")
            return self._create_error_response(request, None, str(e))
    
    def _requires_confirmation(self, action: GeneratedAction) -> bool:
        """Check if an action requires confirmation."""
        from app.config.constants import PermissionLevel
        
        # Check security policy
        registered_action = self.action_registry.get_action(action.action_id)
        if registered_action:
            return self.security_policy.requires_confirmation(registered_action.permission_level)
        
        # Default to confirmation for critical/unknown actions
        return action.confidence < 0.8
    
    def _handle_confirmation_request(self, request: AIRequest, action: GeneratedAction) -> Optional[AIResponse]:
        """Handle confirmation request for sensitive actions."""
        try:
            from app.config.constants import PermissionLevel
            
            # Create confirmation request
            registered_action = self.action_registry.get_action(action.action_id)
            permission_level = registered_action.permission_level if registered_action else PermissionLevel.SENSITIVE
            
            confirmation_request = self.confirmation_engine.request_confirmation(
                action_id=action.action_id,
                action_name=action.action_name,
                message=self.response_generator.generate_action_confirmation(action),
                permission_level=permission_level
            )
            
            # In a real application, this would wait for user input
            # For now, we'll auto-approve for testing
            self.confirmation_engine.respond_to_confirmation(
                confirmation_request.request_id,
                True,
                "Auto-approved for testing"
            )
            
            # If user denied, return denial response
            status = self.confirmation_engine.get_request_status(confirmation_request.request_id)
            from app.actions.confirmation import ConfirmationStatus
            if status == ConfirmationStatus.DENIED:
                response_text = "Action cancelled by user."
                return AIResponse(
                    response_text=response_text,
                    generated_action=action,
                    action_result=None,
                    was_executed=False,
                    error="User denied confirmation",
                    request_id=request.request_id
                )
            
            return None  # Proceed with execution
            
        except Exception as e:
            self.logger.error(f"Confirmation handling failed: {e}")
            return None  # Proceed with execution on error
    
    def _execute_action(self, generated_action: GeneratedAction) -> Optional[Dict[str, Any]]:
        """Execute a generated action."""
        try:
            action = self.action_registry.get_action(generated_action.action_id)
            if not action:
                return {"success": False, "error": f"Action {generated_action.action_id} not found"}
            
            # Execute using action executor
            result = self.action_executor.execute_action(
                action,
                generated_action.parameters,
                skip_confirmation=True  # Already handled confirmation
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_response(
        self,
        request: AIRequest,
        generated_action: GeneratedAction,
        action_result: Optional[Dict[str, Any]]
    ) -> str:
        """Generate natural language response."""
        context = ResponseContext(
            user_input=request.user_input,
            generated_action=generated_action,
            action_result=action_result,
            error=None,
            conversation_history=self.conversation_history,
            user_profile=self.user_profiles.get(request.user_id) if request.user_id else None
        )
        
        return self.response_generator.generate_response(context)
    
    def _create_error_response(self, request: AIRequest, generated_action: Optional[GeneratedAction], error: str) -> AIResponse:
        """Create an error response."""
        if generated_action:
            response_text = self.response_generator.generate_error_response(generated_action, error)
        else:
            response_text = f"Sorry, I encountered an error: {error}"
        
        return AIResponse(
            response_text=response_text,
            generated_action=generated_action,
            action_result=None,
            was_executed=False,
            error=error,
            request_id=request.request_id
        )
    
    def _update_conversation_history(self, request: AIRequest, response: str):
        """Update conversation history."""
        self.conversation_history.append({
            "user": request.user_input,
            "assistant": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
    
    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation history."""
        return self.conversation_history[-limit:]
    
    def clear_conversation_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        self.logger.info("Conversation history cleared")
    
    def set_user_profile(self, user_id: str, profile: Dict[str, Any]):
        """Set user profile."""
        self.user_profiles[user_id] = profile
        self.logger.info(f"User profile set for: {user_id}")
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user profile."""
        return self.user_profiles.get(user_id)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get AI system capabilities."""
        return {
            "intent_parser": {
                "supported_categories": [cat.value for cat in IntentCategory],
                "supported_actions": len([action for action in IntentAction if action != IntentAction.UNKNOWN_ACTION])
            },
            "llm_providers": {
                "available": self.llm_manager.get_available_providers(),
                "default": self.llm_manager._default_provider if self.llm_manager else None
            },
            "action_registry": {
                "total_actions": len(self.action_registry.get_all_actions()),
                "action_ids": [action.id for action in self.action_registry.get_all_actions()]
            },
            "security": {
                "confirmation_required_critical": self.security_policy.get_policy_summary().get('require_confirmation_critical'),
                "confirmation_required_sensitive": self.security_policy.get_policy_summary().get('require_confirmation_sensitive')
            }
        }
    
    def process_batch_requests(self, requests: List[AIRequest]) -> List[AIResponse]:
        """Process multiple requests in batch."""
        return [self.process_request(request) for request in requests]
    
    def get_action_suggestions(self, user_input: str) -> List[str]:
        """Get action suggestions based on user input."""
        return self.action_generator.suggest_related_actions(user_input)
    
    def clarify_request(self, user_input: str) -> str:
        """Generate a clarification question for ambiguous requests."""
        return self.action_generator.clarify_ambiguous_request(user_input)
