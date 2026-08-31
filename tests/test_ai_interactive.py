"""
ELARA - Interactive AI Test
Demonstrates the AI system working without the full GUI.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai import AIManager, AIRequest
from app.actions import ActionRegistry, PermissionEngine, SecurityPolicy, ConfirmationEngine, ActionExecutor
from app.utils.logger import get_logger

def main():
    """Run interactive AI test."""
    print("=" * 60)
    print("ELARA AI System - Interactive Test")
    print("=" * 60)
    print("Type commands to test the AI system (or 'quit' to exit)")
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
    
    # Example commands
    print("Example commands you can try:")
    print("  - open chrome")
    print("  - mute")
    print("  - take screenshot")
    print("  - what time is it")
    print("  - open downloads")
    print("  - search for python tutorials")
    print()
    
    # Interactive loop
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Process the request
            request = AIRequest(user_input=user_input)
            response = ai_manager.process_request(request)
            
            print(f"ELARA: {response.response_text}")
            
            if response.generated_action:
                print(f"  [Action: {response.generated_action.action_id}, Confidence: {response.generated_action.confidence:.2f}]")
            
            if response.action_result:
                print(f"  [Result: {response.action_result}]")
            
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")
            print()

if __name__ == "__main__":
    main()
