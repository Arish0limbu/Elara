"""
ELARA - LLM Provider Integration
This module handles integration with various LLM providers (OpenAI, Anthropic, etc.).
"""

from typing import Dict, List, Optional, Any, Union
from enum import Enum
import json
from abc import ABC, abstractmethod

from app.utils.logger import get_logger


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"
    MOCK = "mock"


class LLMModel(Enum):
    """Supported LLM models."""
    # OpenAI models
    GPT_4 = "gpt-4"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Anthropic models
    CLAUDE_3_OPUS = "claude-3-opus"
    CLAUDE_3_SONNET = "claude-3-sonnet"
    CLAUDE_3_HAIKU = "claude-3-haiku"
    
    # Local models
    LLAMA_2 = "llama-2"
    MISTRAL = "mistral"


class LLMProviderBase(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.logger = get_logger(f"elara.llm.{self.__class__.__name__.lower()}")
        self.api_key = api_key
        self.model = model
        self._is_available = False
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass
    
    @abstractmethod
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def generate_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a structured JSON response from the LLM."""
        pass


class OpenAIProvider(LLMProviderBase):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = LLMModel.GPT_3_5_TURBO.value):
        super().__init__(api_key, model)
        self._client = None
        self._check_availability()
    
    def _check_availability(self):
        """Check if OpenAI is available."""
        try:
            import openai
            self._client = openai
            if self.api_key:
                self._client.api_key = self.api_key
            self._is_available = True
            self.logger.info("OpenAI provider available")
        except ImportError:
            self.logger.warning("OpenAI library not installed. Install with: pip install openai")
            self._is_available = False
        except Exception as e:
            self.logger.error(f"OpenAI provider initialization failed: {e}")
            self._is_available = False
    
    def is_available(self) -> bool:
        return self._is_available
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response from OpenAI GPT."""
        if not self._is_available:
            raise RuntimeError("OpenAI provider is not available")
        
        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            
            response = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            self.logger.error(f"OpenAI response generation failed: {e}")
            raise
    
    def generate_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a structured JSON response from OpenAI GPT."""
        if not self._is_available:
            raise RuntimeError("OpenAI provider is not available")
        
        try:
            # Add JSON formatting instructions
            json_instruction = "Respond with valid JSON only."
            if schema:
                json_instruction += f" Use this schema: {json.dumps(schema)}"
            
            full_prompt = f"{prompt}\n\n{json_instruction}"
            
            response_text = self.generate_response(
                prompt=full_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for structured output
                **kwargs
            )
            
            # Parse JSON response
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            raise
        except Exception as e:
            self.logger.error(f"OpenAI structured response generation failed: {e}")
            raise


class AnthropicProvider(LLMProviderBase):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = LLMModel.CLAUDE_3_SONNET.value):
        super().__init__(api_key, model)
        self._client = None
        self._check_availability()
    
    def _check_availability(self):
        """Check if Anthropic is available."""
        try:
            import anthropic
            self._client = anthropic
            if self.api_key:
                self._client.api_key = self.api_key
            self._is_available = True
            self.logger.info("Anthropic provider available")
        except ImportError:
            self.logger.warning("Anthropic library not installed. Install with: pip install anthropic")
            self._is_available = False
        except Exception as e:
            self.logger.error(f"Anthropic provider initialization failed: {e}")
            self._is_available = False
    
    def is_available(self) -> bool:
        return self._is_available
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a response from Anthropic Claude."""
        if not self._is_available:
            raise RuntimeError("Anthropic provider is not available")
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            response = self._client.messages.create(
                model=self.model,
                messages=messages,
                system=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            return response.content[0].text
            
        except Exception as e:
            self.logger.error(f"Anthropic response generation failed: {e}")
            raise
    
    def generate_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a structured JSON response from Anthropic Claude."""
        if not self._is_available:
            raise RuntimeError("Anthropic provider is not available")
        
        try:
            # Add JSON formatting instructions
            json_instruction = "Respond with valid JSON only."
            if schema:
                json_instruction += f" Use this schema: {json.dumps(schema)}"
            
            full_prompt = f"{prompt}\n\n{json_instruction}"
            
            response_text = self.generate_response(
                prompt=full_prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Lower temperature for structured output
                **kwargs
            )
            
            # Parse JSON response
            return json.loads(response_text)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Anthropic structured response generation failed: {e}")
            raise


class MockProvider(LLMProviderBase):
    """Mock provider for testing and fallback."""
    
    def __init__(self, model: str = "mock-model"):
        super().__init__(None, model)
        self._is_available = True
        self.logger.info("Mock provider initialized")
    
    def is_available(self) -> bool:
        return True
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate a mock response."""
        self.logger.info(f"Generating mock response for: '{prompt[:50]}...'")
        
        # Simple keyword-based mock responses
        prompt_lower = prompt.lower()
        
        if "time" in prompt_lower:
            from datetime import datetime
            return f"The current time is {datetime.now().strftime('%H:%M:%S')}."
        elif "weather" in prompt_lower:
            return "I don't have access to weather information, but you can check weather.com or use a weather app."
        elif "system" in prompt_lower or "computer" in prompt_lower:
            return "Your computer is running Windows. You can ask me to perform specific actions like opening applications, managing windows, or controlling volume."
        elif "help" in prompt_lower:
            return "I can help you with: opening applications, managing windows, controlling volume, taking screenshots, system operations, file management, and web searches. Just ask me what you'd like to do!"
        else:
            return "I understand your request. This is a mock response since no AI provider is configured. Please configure an API key for a real AI provider to get intelligent responses."
    
    def generate_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a mock structured response."""
        self.logger.info(f"Generating mock structured response")
        
        # Return a basic mock structure
        return {
            "status": "mock",
            "message": "This is a mock structured response",
            "data": {}
        }


class LLMProviderManager:
    """Manages multiple LLM providers and handles fallback."""
    
    def __init__(self):
        self.logger = get_logger("elara.llm.manager")
        self._providers: Dict[str, LLMProviderBase] = {}
        self._default_provider: Optional[str] = None
        self._fallback_order: List[str] = []
        
        # Initialize providers
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize available providers."""
        # Try to initialize each provider
        providers_to_try = [
            (LLMProvider.OPENAI, OpenAIProvider),
            (LLMProvider.ANTHROPIC, AnthropicProvider),
            (LLMProvider.MOCK, MockProvider),
        ]
        
        for provider_type, provider_class in providers_to_try:
            try:
                provider = provider_class()
                if provider.is_available():
                    self._providers[provider_type.value] = provider
                    self._fallback_order.append(provider_type.value)
                    self.logger.info(f"Initialized {provider_type.value} provider")
            except Exception as e:
                self.logger.warning(f"Failed to initialize {provider_type.value}: {e}")
        
        # Set default provider (prefer real AI over mock)
        for provider_type in self._fallback_order:
            if provider_type != LLMProvider.MOCK.value:
                self._default_provider = provider_type
                break
        
        # Fallback to mock if no real provider available
        if self._default_provider is None and LLMProvider.MOCK.value in self._providers:
            self._default_provider = LLMProvider.MOCK.value
            self.logger.warning("Using mock provider as fallback")
        
        self.logger.info(f"Default provider: {self._default_provider}")
    
    def add_provider(self, provider_type: str, provider: LLMProviderBase, set_as_default: bool = False):
        """
        Add a provider to the manager.
        
        Args:
            provider_type: Provider type identifier
            provider: Provider instance
            set_as_default: Whether to set as default provider
        """
        if provider.is_available():
            self._providers[provider_type] = provider
            if provider_type not in self._fallback_order:
                self._fallback_order.append(provider_type)
            if set_as_default:
                self._default_provider = provider_type
            self.logger.info(f"Added provider: {provider_type}")
        else:
            self.logger.warning(f"Provider {provider_type} is not available")
    
    def set_default_provider(self, provider_type: str):
        """
        Set the default provider.
        
        Args:
            provider_type: Provider type identifier
        """
        if provider_type in self._providers:
            self._default_provider = provider_type
            self.logger.info(f"Default provider set to: {provider_type}")
        else:
            self.logger.error(f"Provider {provider_type} not available")
    
    def get_default_provider(self) -> Optional[LLMProviderBase]:
        """Get the default provider."""
        if self._default_provider and self._default_provider in self._providers:
            return self._providers[self._default_provider]
        return None
    
    def get_provider(self, provider_type: str) -> Optional[LLMProviderBase]:
        """
        Get a specific provider.
        
        Args:
            provider_type: Provider type identifier
            
        Returns:
            Provider instance or None
        """
        return self._providers.get(provider_type)
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider_type: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate a response using the specified or default provider.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            provider_type: Optional specific provider to use
            **kwargs: Additional parameters for the provider
            
        Returns:
            Generated response text
        """
        provider = self._get_provider_for_request(provider_type)
        
        if not provider:
            raise RuntimeError("No available LLM provider")
        
        try:
            return provider.generate_response(prompt, system_prompt, **kwargs)
        except Exception as e:
            self.logger.error(f"Response generation failed with {provider_type or 'default'}: {e}")
            
            # Try fallback providers
            for fallback_type in self._fallback_order:
                if fallback_type != (provider_type or self._default_provider):
                    fallback_provider = self._providers.get(fallback_type)
                    if fallback_provider:
                        try:
                            self.logger.info(f"Trying fallback provider: {fallback_type}")
                            return fallback_provider.generate_response(prompt, system_prompt, **kwargs)
                        except Exception as fallback_error:
                            self.logger.error(f"Fallback provider {fallback_type} also failed: {fallback_error}")
            
            raise RuntimeError("All LLM providers failed")
    
    def generate_structured_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        schema: Optional[Dict] = None,
        provider_type: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a structured response using the specified or default provider.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            schema: Optional JSON schema for structured output
            provider_type: Optional specific provider to use
            **kwargs: Additional parameters for the provider
            
        Returns:
            Generated structured response
        """
        provider = self._get_provider_for_request(provider_type)
        
        if not provider:
            raise RuntimeError("No available LLM provider")
        
        try:
            return provider.generate_structured_response(prompt, system_prompt, schema, **kwargs)
        except Exception as e:
            self.logger.error(f"Structured response generation failed: {e}")
            raise
    
    def _get_provider_for_request(self, provider_type: Optional[str]) -> Optional[LLMProviderBase]:
        """Get the appropriate provider for a request."""
        if provider_type:
            return self._providers.get(provider_type)
        return self.get_default_provider()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider types."""
        return list(self._providers.keys())
    
    def is_provider_available(self, provider_type: str) -> bool:
        """Check if a specific provider is available."""
        return provider_type in self._providers
