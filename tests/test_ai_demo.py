"""
ELARA - AI System Demo
Demonstrates the AI system working with predefined commands.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai import AIManager, AIRequest
from app.actions import ActionRegistry, PermissionEngine, SecurityPolicy, ConfirmationEngine, ActionExecutor
from app.utils.logger import get_logger

def main():
    """Run AI system demo."""
    print("=" * 60)
    print("ELARA AI System - Demo")
    print("=" * 60)
    print()
    
    # Initialize AI system
    action_registry = ActionRegistry()
    ai_manager = AIManager(
        action_registry=action_registry,
        permission_engine=PermissionEngine(),
        security_policy=SecurityPolicy(),
        confirmation_engine=ConfirmationEngine(),
        action_executor=ActionExecutor()
    )
    
    print("AI System initialized successfully!")
    print(f"Available actions: {len(action_registry.get_all_actions())}")
    print()
    
    # Test commands
    test_commands = [
        "open chrome",
        "mute",
        "take screenshot",
        "what time is it",
        "open downloads",
        "search for python tutorials",
        "volume up",
        "get system info"
    ]
    
    print("Processing test commands:")
    print("-" * 60)
    
    for user_input in test_commands:
        print(f"\nYou: {user_input}")
        
        try:
            # Process the request
            request = AIRequest(user_input=user_input)
            response = ai_manager.process_request(request)
            
            print(f"ELARA: {response.response_text}")
            
            if response.generated_action:
                print(f"  - Action: {response.generated_action.action_id}")
                print(f"  - Confidence: {response.generated_action.confidence:.2f}")
            
            if response.action_result:
                print(f"  - Result: {response.action_result}")
            
        except Exception as e:
            print(f"  - Error: {e}")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)
    
    # Show system capabilities
    print("\nSystem Capabilities:")
    capabilities = ai_manager.get_capabilities()
    print(f"  - Intent categories: {len(capabilities['intent_parser']['supported_categories'])}")
    print(f"  - Supported actions: {capabilities['intent_parser']['supported_actions']}")
    print(f"  - LLM providers: {capabilities['llm_providers']['available']}")
    print(f"  - Default provider: {capabilities['llm_providers']['default']}")
    print(f"  - Registered actions: {capabilities['action_registry']['total_actions']}")

if __name__ == "__main__":
    main()
