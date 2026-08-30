"""
ELARA - AI Response Generator
This module generates natural language responses for user interactions.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import json

from app.ai.llm_provider import LLMProviderManager
from app.ai.action_generator import GeneratedAction
from app.utils.logger import get_logger


@dataclass
class ResponseContext:
    """Context for generating responses."""
    user_input: str
    generated_action: Optional[GeneratedAction]
    action_result: Optional[Dict[str, Any]]
    error: Optional[str]
    conversation_history: List[Dict[str, str]]
    user_profile: Optional[Dict[str, Any]]


class ResponseGenerator:
    """Generates natural language responses for user interactions."""
    
    def __init__(self, llm_manager: Optional[LLMProviderManager] = None):
        self.logger = get_logger("elara.response_generator")
        
        self.llm_manager = llm_manager or LLMProviderManager()
        
        # System prompt for response generation
        self.system_prompt = """You are ELARA, a helpful Windows AI assistant. Your responses should be:
- Concise and direct
- Natural and conversational
- Action-oriented when appropriate
- Professional but friendly
- Clear about what you're doing or have done

When describing actions, be specific about results. When errors occur, explain clearly and suggest alternatives."""

        # Response templates for common scenarios
        self.response_templates = {
            "action_success": [
                "I've {action_description}.",
                "Done! {action_description}.",
                "{action_description} for you.",
                "Successfully {action_description}."
            ],
            "action_failed": [
                "I couldn't {action_description}. {error}",
                "Sorry, {action_description} failed. {error}",
                "There was an issue: {error}",
                "Failed to {action_description}. {error}"
            ],
            "confirmation_required": [
                "I need confirmation before {action_description}. Are you sure?",
                "Before I {action_description}, please confirm.",
                "Are you sure you want me to {action_description}?",
                "This action requires confirmation: {action_description}. Proceed?"
            ],
            "permission_denied": [
                "I can't {action_description} due to security restrictions.",
                "Sorry, {action_description} is not permitted.",
                "That action is blocked for security reasons.",
                "I don't have permission to {action_description}."
            ],
            "clarification_needed": [
                "Could you clarify what you'd like me to do?",
                "I'm not sure I understand. Could you be more specific?",
                "What exactly would you like me to help with?",
                "Can you provide more details about what you need?"
            ],
            "information_response": [
                "{information}",
                "Here's what I found: {information}",
                "{information}",
                "Here's the information: {information}"
            ]
        }
    
    def generate_response(
        self,
        context: ResponseContext,
        use_llm: bool = True
    ) -> str:
        """
        Generate a natural language response based on context.
        
        Args:
            context: Response context
            use_llm: Whether to use LLM for generation
            
        Returns:
            Generated response text
        """
        self.logger.info(f"Generating response for: '{context.user_input}'")
        
        # Determine response type based on context
        if context.error:
            response_type = "action_failed"
        elif context.generated_action and context.action_result:
            if context.action_result.get("success", False):
                response_type = "action_success"
            else:
                response_type = "action_failed"
        elif context.generated_action and not context.generated_action.is_valid:
            response_type = "clarification_needed"
        else:
            response_type = "information_response"
        
        # Generate response
        if use_llm and self.llm_manager.get_default_provider():
            return self._generate_llm_response(context, response_type)
        else:
            return self._generate_template_response(context, response_type)
    
    def _generate_llm_response(self, context: ResponseContext, response_type: str) -> str:
        """
        Generate response using LLM.
        
        Args:
            context: Response context
            response_type: Type of response to generate
            
        Returns:
            Generated response text
        """
        try:
            # Build context information for LLM
            context_info = self._build_context_info(context, response_type)
            
            prompt = f"""User said: "{context.user_input}"

Context:
{context_info}

Generate a natural, helpful response. Keep it concise and conversational."""

            response = self.llm_manager.generate_response(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.7
            )
            
            return response.strip()
            
        except Exception as e:
            self.logger.error(f"LLM response generation failed: {e}")
            return self._generate_template_response(context, response_type)
    
    def _build_context_info(self, context: ResponseContext, response_type: str) -> str:
        """Build context information string for LLM."""
        info_parts = []
        
        if context.generated_action:
            info_parts.append(f"Action: {context.generated_action.action_name}")
            if context.generated_action.parameters:
                info_parts.append(f"Parameters: {json.dumps(context.generated_action.parameters)}")
            if context.generated_action.reasoning:
                info_parts.append(f"Reasoning: {context.generated_action.reasoning}")
        
        if context.action_result:
            info_parts.append(f"Result: {json.dumps(context.action_result)}")
        
        if context.error:
            info_parts.append(f"Error: {context.error}")
        
        if context.conversation_history:
            recent_history = context.conversation_history[-3:]  # Last 3 exchanges
            info_parts.append("Recent conversation:")
            for exchange in recent_history:
                info_parts.append(f"  User: {exchange.get('user', '')}")
                info_parts.append(f"  Assistant: {exchange.get('assistant', '')}")
        
        return "\n".join(info_parts)
    
    def _generate_template_response(self, context: ResponseContext, response_type: str) -> str:
        """
        Generate response using templates.
        
        Args:
            context: Response context
            response_type: Type of response to generate
            
        Returns:
            Generated response text
        """
        templates = self.response_templates.get(response_type, self.response_templates["information_response"])
        template = templates[0]  # Use first template as default
        
        # Fill in template variables
        if context.generated_action:
            action_description = self._get_action_description(context.generated_action)
            template = template.replace("{action_description}", action_description)
        
        if context.error:
            template = template.replace("{error}", context.error)
        
        if context.action_result and context.action_result.get("result"):
            information = str(context.action_result["result"])
            template = template.replace("{information}", information)
        
        return template
    
    def _get_action_description(self, action: GeneratedAction) -> str:
        """Get a natural language description of an action."""
        if action.parameters:
            param_str = ", ".join(f"{k}={v}" for k, v in action.parameters.items())
            return f"{action.action_name} with {param_str}"
        return action.action_name.lower()
    
    def generate_action_confirmation(self, action: GeneratedAction) -> str:
        """
        Generate a confirmation request for an action.
        
        Args:
            action: Action to confirm
            
        Returns:
            Confirmation message
        """
        template = self.response_templates["confirmation_required"][0]
        action_description = self._get_action_description(action)
        return template.replace("{action_description}", action_description)
    
    def generate_success_response(self, action: GeneratedAction, result: Dict[str, Any]) -> str:
        """
        Generate a success response for completed action.
        
        Args:
            action: Action that was executed
            result: Execution result
            
        Returns:
            Success message
        """
        template = self.response_templates["action_success"][0]
        action_description = self._get_action_description(action)
        
        # Add result details if available
        if result.get("result"):
            action_description += f" - {result['result']}"
        
        return template.replace("{action_description}", action_description)
    
    def generate_error_response(self, action: GeneratedAction, error: str) -> str:
        """
        Generate an error response for failed action.
        
        Args:
            action: Action that failed
            error: Error message
            
        Returns:
            Error message
        """
        template = self.response_templates["action_failed"][0]
        action_description = self._get_action_description(action)
        return template.replace("{action_description}", action_description).replace("{error}", error)
    
    def generate_permission_denied_response(self, action: GeneratedAction) -> str:
        """
        Generate a permission denied response.
        
        Args:
            action: Action that was denied
            
        Returns:
            Permission denied message
        """
        template = self.response_templates["permission_denied"][0]
        action_description = self._get_action_description(action)
        return template.replace("{action_description}", action_description)
    
    def generate_information_response(self, information: str) -> str:
        """
        Generate an information response.
        
        Args:
            information: Information to convey
            
        Returns:
            Information message
        """
        template = self.response_templates["information_response"][0]
        return template.replace("{information}", information)
    
    def generate_suggestion_response(self, suggestions: List[str]) -> str:
        """
        Generate a response with action suggestions.
        
        Args:
            suggestions: List of suggested actions
            
        Returns:
            Suggestion message
        """
        if not suggestions:
            return "I'm not sure what you'd like me to do. Could you be more specific?"
        
        suggestions_text = "Here are some things I can help you with:\n"
        for i, suggestion in enumerate(suggestions, 1):
            suggestions_text += f"{i}. {suggestion}\n"
        
        return suggestions_text.strip()
    
    def add_custom_template(self, response_type: str, template: str):
        """
        Add a custom response template.
        
        Args:
            response_type: Type of response
            template: Template string with placeholders
        """
        if response_type not in self.response_templates:
            self.response_templates[response_type] = []
        self.response_templates[response_type].append(template)
        self.logger.info(f"Added custom template for {response_type}")
    
    def set_conversation_style(self, style: str):
        """
        Set the conversation style.
        
        Args:
            style: Style (e.g., "formal", "casual", "technical")
        """
        style_prompts = {
            "formal": "You are ELARA, a professional Windows AI assistant. Be formal and precise.",
            "casual": "You are ELARA, a friendly Windows AI assistant. Be casual and conversational.",
            "technical": "You are ELARA, a technical Windows AI assistant. Be detailed and precise."
        }
        
        self.system_prompt = style_prompts.get(style, self.system_prompt)
        self.logger.info(f"Conversation style set to: {style}")
