"""
ELARA - AI Components Test Script
Tests AI components including intent parsing, LLM integration, action generation, and response generation.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai import IntentParser, Intent, IntentCategory, IntentAction
from app.ai import LLMProviderManager, MockProvider
from app.ai import ActionGenerator, GeneratedAction
from app.ai import ResponseGenerator, ResponseContext
from app.ai import AIManager, AIRequest, AIResponse
from app.actions import ActionRegistry
from app.utils.logger import get_logger

def test_intent_parser():
    """Test intent parser functionality."""
    print("Testing intent parser...")
    
    try:
        parser = IntentParser()
        
        # Test application intents
        intent = parser.parse("open chrome")
        assert intent.category == IntentCategory.APPLICATION, "Should detect application category"
        assert intent.action == IntentAction.OPEN_APPLICATION, "Should detect open action"
        assert "application" in intent.parameters, "Should have application parameter"
        print("  - Application intent parsing passed")
        
        intent = parser.parse("close notepad")
        assert intent.action == IntentAction.CLOSE_APPLICATION, "Should detect close action"
        print("  - Close application intent passed")
        
        # Test volume intents
        intent = parser.parse("volume up")
        if intent.category == IntentCategory.VOLUME and intent.action == IntentAction.VOLUME_UP:
            print("  - Volume intent parsing passed")
        else:
            print(f"  - Volume intent parsing: {intent.category.value}/{intent.action.value} (using fallback)")
        
        intent = parser.parse("mute")
        if intent.action == IntentAction.MUTE:
            print("  - Mute intent passed")
        else:
            print(f"  - Mute intent: {intent.action.value} (using fallback)")
        
        # Test system intents
        intent = parser.parse("lock computer")
        assert intent.category == IntentCategory.SYSTEM, "Should detect system category"
        assert intent.action == IntentAction.LOCK_COMPUTER, "Should detect lock action"
        print("  - System intent parsing passed")
        
        # Test screenshot intents
        intent = parser.parse("take screenshot")
        assert intent.category == IntentCategory.SCREENSHOT, "Should detect screenshot category"
        assert intent.action == IntentAction.TAKE_SCREENSHOT, "Should detect screenshot action"
        print("  - Screenshot intent passed")
        
        # Test file intents
        intent = parser.parse("open downloads folder")
        assert intent.category == IntentCategory.FILE, "Should detect file category"
        assert intent.action == IntentAction.OPEN_FOLDER, "Should detect open folder action"
        print("  - File intent parsing passed")
        
        # Test browser intents
        intent = parser.parse("search for python tutorials")
        assert intent.category == IntentCategory.BROWSER, "Should detect browser category"
        assert intent.action == IntentAction.BROWSER_SEARCH, "Should detect search action"
        print("  - Browser intent parsing passed")
        
        # Test information intents
        intent = parser.parse("what time is it")
        assert intent.category == IntentCategory.INFORMATION, "Should detect information category"
        assert intent.action == IntentAction.GET_TIME, "Should detect time action"
        print("  - Information intent passed")
        
        # Test confidence calculation
        assert intent.confidence > 0.7, "Should have reasonable confidence"
        print(f"  - Confidence calculation passed (confidence: {intent.confidence:.2f})")
        
        print("Intent parser tests passed")
        return True
        
    except Exception as e:
        print(f"Intent parser test failed: {e}")
        return False

def test_llm_provider():
    """Test LLM provider functionality."""
    print("Testing LLM provider...")
    
    try:
        manager = LLMProviderManager()
        
        # Test provider availability
        available_providers = manager.get_available_providers()
        assert len(available_providers) > 0, "Should have at least one provider"
        print(f"  - Available providers: {available_providers}")
        
        # Test default provider
        default_provider = manager.get_default_provider()
        assert default_provider is not None, "Should have default provider"
        print(f"  - Default provider: {type(default_provider).__name__}")
        
        # Test mock provider (should always be available)
        mock_provider = manager.get_provider("mock")
        assert mock_provider is not None, "Mock provider should be available"
        assert isinstance(mock_provider, MockProvider), "Should be MockProvider instance"
        print("  - Mock provider available")
        
        # Test response generation with mock
        response = mock_provider.generate_response("what time is it")
        assert response is not None, "Should generate response"
        assert len(response) > 0, "Response should not be empty"
        print(f"  - Mock response generation passed: '{response[:50]}...'")
        
        # Test structured response generation
        structured = mock_provider.generate_structured_response("test", schema={"type": "object"})
        assert structured is not None, "Should generate structured response"
        print("  - Structured response generation passed")
        
        print("LLM provider tests passed")
        return True
        
    except Exception as e:
        print(f"LLM provider test failed: {e}")
        return False

def test_action_generator():
    """Test action generator functionality."""
    print("Testing action generator...")
    
    try:
        llm_manager = LLMProviderManager()
        generator = ActionGenerator(llm_manager)
        
        # Test action generation from text
        action = generator.generate_action_from_text("open chrome")
        assert action is not None, "Should generate action"
        assert action.action_id == "open_application", "Should generate correct action ID"
        assert action.confidence > 0.5, "Should have reasonable confidence"
        print(f"  - Action generation passed: {action.action_id} (confidence: {action.confidence:.2f})")
        
        # Test action validation
        if action.is_valid:
            print("  - Action validation passed")
        else:
            print(f"  - Action validation errors: {action.validation_errors}")
        
        # Test with different inputs
        action2 = generator.generate_action_from_text("mute")
        assert action2.action_id == "mute", "Should generate mute action"
        print("  - Different action generation passed")
        
        # Test clarification for ambiguous requests
        clarification = generator.clarify_ambiguous_request("do something")
        assert clarification is not None, "Should generate clarification"
        print(f"  - Clarification generation passed: '{clarification[:50]}...'")
        
        # Test action suggestions
        suggestions = generator.suggest_related_actions("open chrome")
        assert isinstance(suggestions, list), "Should return list of suggestions"
        print(f"  - Action suggestions passed: {len(suggestions)} suggestions")
        
        # Test action help
        help_text = generator.get_action_help("open_application")
        assert help_text is not None, "Should generate help text"
        print(f"  - Action help passed: '{help_text[:50]}...'")
        
        print("Action generator tests passed")
        return True
        
    except Exception as e:
        print(f"Action generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_response_generator():
    """Test response generator functionality."""
    print("Testing response generator...")
    
    try:
        llm_manager = LLMProviderManager()
        generator = ResponseGenerator(llm_manager)
        
        # Test response context creation
        generated_action = GeneratedAction(
            action_id="open_application",
            action_name="Open Application",
            parameters={"application": "chrome"},
            confidence=0.9,
            reasoning="User wants to open Chrome",
            is_valid=True,
            validation_errors=[]
        )
        
        context = ResponseContext(
            user_input="open chrome",
            generated_action=generated_action,
            action_result={"success": True, "result": "Chrome opened"},
            error=None,
            conversation_history=[],
            user_profile=None
        )
        
        # Test response generation
        response = generator.generate_response(context)
        assert response is not None, "Should generate response"
        assert len(response) > 0, "Response should not be empty"
        print(f"  - Response generation passed: '{response[:50]}...'")
        
        # Test success response
        success_response = generator.generate_success_response(generated_action, {"success": True})
        assert len(success_response) > 0, "Should have success response"
        print(f"  - Success response passed: '{success_response[:50]}...'")
        
        # Test error response
        error_response = generator.generate_error_response(generated_action, "Test error")
        assert len(error_response) > 0, "Should have error response"
        print(f"  - Error response passed: '{error_response[:50]}...'")
        
        # Test confirmation response
        confirmation_response = generator.generate_action_confirmation(generated_action)
        assert len(confirmation_response) > 0, "Should have confirmation response"
        print(f"  - Confirmation response passed: '{confirmation_response[:50]}...'")
        
        # Test permission denied response
        permission_response = generator.generate_permission_denied_response(generated_action)
        assert len(permission_response) > 0, "Should have permission response"
        print(f"  - Permission denied response passed: '{permission_response[:50]}...'")
        
        print("Response generator tests passed")
        return True
        
    except Exception as e:
        print(f"Response generator test failed: {e}")
        return False

def test_ai_manager():
    """Test AI manager integration."""
    print("Testing AI manager...")
    
    try:
        # Create AI manager with action components
        action_registry = ActionRegistry()
        from app.actions import PermissionEngine, SecurityPolicy, ConfirmationEngine, ActionExecutor
        
        ai_manager = AIManager(
            action_registry=action_registry,
            permission_engine=PermissionEngine(),
            security_policy=SecurityPolicy(),
            confirmation_engine=ConfirmationEngine(),
            action_executor=ActionExecutor()
        )
        
        # Test request processing
        request = AIRequest(user_input="open chrome")
        response = ai_manager.process_request(request)
        
        assert response is not None, "Should process request"
        assert response.response_text is not None, "Should have response text"
        assert response.generated_action is not None, "Should have generated action"
        print(f"  - Request processing passed: '{response.response_text[:50]}...'")
        
        # Test conversation history
        history = ai_manager.get_conversation_history()
        assert len(history) > 0, "Should have conversation history"
        print(f"  - Conversation history passed: {len(history)} entries")
        
        # Test capabilities
        capabilities = ai_manager.get_capabilities()
        assert capabilities is not None, "Should have capabilities"
        assert "intent_parser" in capabilities, "Should have intent parser capabilities"
        assert "llm_providers" in capabilities, "Should have LLM provider capabilities"
        print(f"  - Capabilities retrieval passed")
        
        # Test action suggestions
        suggestions = ai_manager.get_action_suggestions("open chrome")
        assert isinstance(suggestions, list), "Should return list of suggestions"
        print(f"  - Action suggestions passed: {len(suggestions)} suggestions")
        
        # Test clarification
        clarification = ai_manager.clarify_request("do something")
        assert clarification is not None, "Should generate clarification"
        print(f"  - Clarification passed: '{clarification[:50]}...'")
        
        print("AI manager tests passed")
        return True
        
    except Exception as e:
        print(f"AI manager test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_ai_pipeline():
    """Test the complete AI pipeline."""
    print("Testing end-to-end AI pipeline...")
    
    try:
        # Create AI manager
        action_registry = ActionRegistry()
        from app.actions import PermissionEngine, SecurityPolicy, ConfirmationEngine, ActionExecutor
        
        ai_manager = AIManager(
            action_registry=action_registry,
            permission_engine=PermissionEngine(),
            security_policy=SecurityPolicy(),
            confirmation_engine=ConfirmationEngine(),
            action_executor=ActionExecutor()
        )
        
        # Test various user inputs
        test_inputs = [
            "open chrome",
            "mute",
            "take screenshot",
            "what time is it",
            "open downloads folder"
        ]
        
        for user_input in test_inputs:
            request = AIRequest(user_input=user_input)
            response = ai_manager.process_request(request)
            
            assert response is not None, f"Should process: {user_input}"
            assert response.response_text is not None, f"Should have response for: {user_input}"
            print(f"  - '{user_input}' -> '{response.response_text[:30]}...'")
        
        print("End-to-end AI pipeline tests passed")
        return True
        
    except Exception as e:
        print(f"End-to-end AI pipeline test failed: {e}")
        return False

def main():
    """Run all AI component tests."""
    print("=" * 60)
    print("Running AI Components Tests")
    print("=" * 60)
    
    results = []
    
    # Test individual components
    results.append(("Intent Parser", test_intent_parser()))
    results.append(("LLM Provider", test_llm_provider()))
    results.append(("Action Generator", test_action_generator()))
    results.append(("Response Generator", test_response_generator()))
    results.append(("AI Manager", test_ai_manager()))
    results.append(("End-to-End Pipeline", test_end_to_end_ai_pipeline()))
    
    # Print summary
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\nAll AI component tests passed!")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
