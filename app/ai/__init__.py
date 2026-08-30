"""
ELARA - AI Module
This module provides AI capabilities for natural language understanding and response generation.
"""

from app.ai.intent_parser import (
    IntentParser,
    Intent,
    IntentCategory,
    IntentAction,
    Parameter
)

from app.ai.llm_provider import (
    LLMProvider,
    LLMModel,
    LLMProviderBase,
    OpenAIProvider,
    AnthropicProvider,
    MockProvider,
    LLMProviderManager
)

from app.ai.action_generator import (
    ActionGenerator,
    GeneratedAction
)

from app.ai.response_generator import (
    ResponseGenerator,
    ResponseContext
)

from app.ai.ai_manager import (
    AIManager,
    AIRequest,
    AIResponse
)

__all__ = [
    # Intent Parser
    'IntentParser',
    'Intent',
    'IntentCategory',
    'IntentAction',
    'Parameter',
    
    # LLM Provider
    'LLMProvider',
    'LLMModel',
    'LLMProviderBase',
    'OpenAIProvider',
    'AnthropicProvider',
    'MockProvider',
    'LLMProviderManager',
    
    # Action Generator
    'ActionGenerator',
    'GeneratedAction',
    
    # Response Generator
    'ResponseGenerator',
    'ResponseContext',
    
    # AI Manager
    'AIManager',
    'AIRequest',
    'AIResponse',
]
