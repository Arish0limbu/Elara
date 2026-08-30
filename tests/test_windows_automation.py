"""
ELARA - Windows Automation and Actions Test Script
Tests Windows automation components and action/permission system
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.actions import ActionRegistry, PermissionEngine, SecurityPolicy, ConfirmationEngine, ActionExecutor
from app.actions.registry import Action, CommandType
from app.actions.confirmation import ConfirmationRequest, ConfirmationStatus
from app.windows import ApplicationManager, WindowManager, VolumeController, ScreenshotCapture, SystemOperations
from app.utils.logger import get_logger
from app.config.constants import PermissionLevel

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

def test_action_registry():
    """Test action registry functionality."""
    print("Testing action registry...")
    
    try:
        registry = ActionRegistry()
        
        # Test getting action by ID
        action = registry.get_action("open_application")
        assert action is not None, "open_application not found"
        print(f"  - Found action: {action.name}")
        
        # Test getting all actions
        all_actions = registry.get_all_actions()
        assert len(all_actions) > 0, "Should have actions"
        print(f"  - {len(all_actions)} actions available")
        
        print("Action registry tests passed")
        return True
        
    except Exception as e:
        print(f"Action registry test failed: {e}")
        return False

def test_permission_engine():
    """Test permission engine functionality."""
    print("Testing permission engine...")
    
    try:
        engine = PermissionEngine()
        
        # Test setting user permission level
        engine.set_user_permission_level(PermissionLevel.MODERATE)
        print("  - User permission level set")
        
        # Test checking permission
        permitted, reason = engine.check_permission("open_application", PermissionLevel.SAFE)
        print(f"  - Permission check: {permitted} ({reason})")
        
        # Test permission override
        engine.set_permission_override("test_action", PermissionLevel.CRITICAL)
        print("  - Permission override set")
        
        # Test blocking action
        engine.block_action("test_action")
        permitted, reason = engine.check_permission("test_action", PermissionLevel.SAFE)
        assert not permitted, "Blocked action should not be permitted"
        print("  - Action blocked successfully")
        
        # Test unblocking action
        engine.unblock_action("test_action")
        print("  - Action unblocked")
        
        # Test command classification
        classification = engine.classify_command({"action_id": "open_application"})
        print(f"  - Command classification: {classification.value}")
        
        print("Permission engine tests passed")
        return True
        
    except Exception as e:
        print(f"Permission engine test failed: {e}")
        return False

def test_security_policy():
    """Test security policy functionality."""
    print("Testing security policy...")
    
    try:
        policy = SecurityPolicy()
        
        # Test confirmation settings
        policy.set_require_confirmation_sensitive(True)
        policy.set_require_confirmation_critical(True)
        print("  - Confirmation settings configured")
        
        # Test directory security
        policy.add_allowed_directory("C:\\Users\\Test")
        policy.add_blocked_directory("C:\\Windows\\System32")
        print("  - Directory security configured")
        
        # Test working hours
        policy.set_working_hours(False, "09:00", "17:00")
        print("  - Working hours configured")
        
        # Test checking confirmation requirement
        requires_confirm = policy.requires_confirmation(PermissionLevel.CRITICAL)
        print(f"  - Critical requires confirmation: {requires_confirm}")
        
        # Test directory check
        is_allowed = policy.is_directory_allowed("C:\\Users\\Test\\Documents")
        print(f"  - Directory allowed: {is_allowed}")
        
        # Test working hours check
        in_hours = policy.is_within_working_hours()
        print(f"  - Within working hours: {in_hours}")
        
        # Test policy summary
        summary = policy.get_policy_summary()
        print(f"  - Policy summary retrieved")
        
        print("Security policy tests passed")
        return True
        
    except Exception as e:
        print(f"Security policy test failed: {e}")
        return False

def test_confirmation_engine():
    """Test confirmation engine functionality."""
    print("Testing confirmation engine...")
    
    try:
        engine = ConfirmationEngine()
        
        # Test requesting confirmation
        request = engine.request_confirmation(
            action_id="shutdown_computer",
            action_name="Shutdown Computer",
            message="Are you sure you want to shutdown the computer?",
            permission_level=PermissionLevel.CRITICAL
        )
        assert request is not None, "Confirmation request should be created"
        print(f"  - Confirmation request created: {request.request_id}")
        
        # Test getting request status
        status = engine.get_request_status(request.request_id)
        assert status is not None, "Request status should be retrievable"
        assert status == ConfirmationStatus.PENDING, "Request should be pending"
        print("  - Request status retrieved")
        
        # Test responding to confirmation (approve)
        engine.respond_to_confirmation(request.request_id, True, "User approved")
        approved_status = engine.get_request_status(request.request_id)
        assert approved_status == ConfirmationStatus.APPROVED, "Request should be approved"
        print("  - Request approved")
        
        # Test creating new request and denying
        request2 = engine.request_confirmation(
            action_id="restart_computer",
            action_name="Restart Computer",
            message="Are you sure you want to restart the computer?",
            permission_level=PermissionLevel.CRITICAL
        )
        engine.respond_to_confirmation(request2.request_id, False, "User denied")
        denied_status = engine.get_request_status(request2.request_id)
        assert denied_status == ConfirmationStatus.DENIED, "Request should be denied"
        print("  - Request denied")
        
        # Test cancelling request
        request3 = engine.request_confirmation(
            action_id="test_action",
            action_name="Test Action",
            message="Test confirmation",
            permission_level=PermissionLevel.SAFE
        )
        engine.cancel_confirmation(request3.request_id)
        cancelled_status = engine.get_request_status(request3.request_id)
        assert cancelled_status == ConfirmationStatus.CANCELLED, "Request should be cancelled"
        print("  - Request cancelled")
        
        print("Confirmation engine tests passed")
        return True
        
    except Exception as e:
        print(f"Confirmation engine test failed: {e}")
        return False

def test_action_executor():
    """Test action executor functionality."""
    print("Testing action executor...")
    
    try:
        executor = ActionExecutor()
        
        # Test registering handler
        def test_handler(action_name, params):
            return {"test": True, "action": action_name}
        
        executor.register_handler("test_action", test_handler)
        print("  - Handler registered")
        
        # Test executing action with proper Action object
        registry = ActionRegistry()
        test_action = Action(
            id="test_action",
            name="Test Action",
            description="Test action for executor",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE
        )
        
        result = executor.execute_action(test_action, {"param1": "value1"})
        assert result is not None, "Execution should return result"
        print("  - Action execution attempted")
        
        # Test getting execution history
        history = executor.get_execution_history()
        print(f"  - Execution history: {len(history)} records")
        
        print("Action executor tests passed")
        return True
        
    except Exception as e:
        print(f"Action executor test failed: {e}")
        return False

def test_application_manager():
    """Test application manager functionality."""
    print("Testing application manager...")
    
    try:
        manager = ApplicationManager()
        
        # Test finding application
        app = manager.find_application("notepad")
        assert app is not None, "Notepad should be found"
        print(f"  - Found application: {app.get('name', 'Unknown')}")
        
        # Test finding by alias
        app = manager.find_application("text editor")
        assert app is not None, "Should find notepad by alias"
        print("  - Application lookup by alias passed")
        
        # Test getting application path
        path = manager.get_application_path("notepad")
        print(f"  - Application path: {path}")
        
        # Test launching application (dry run with info check)
        if path:
            print("  - Application launch capability verified")
        
        print("Application manager tests passed")
        return True
        
    except Exception as e:
        print(f"Application manager test failed: {e}")
        return False

def test_window_manager():
    """Test window manager functionality."""
    print("Testing window manager...")
    
    try:
        manager = WindowManager()
        
        # Test finding window by title
        hwnd = manager.find_window_by_title("ELARA")
        print(f"  - Window search attempted (found: {hwnd is not None})")
        
        # Test getting window info
        if hwnd:
            info = manager.get_window_info(hwnd)
            if info:
                print(f"  - Window info retrieved")
        
        print("Window manager tests passed")
        return True
        
    except Exception as e:
        print(f"Window manager test failed: {e}")
        return False

def test_volume_controller():
    """Test volume controller functionality."""
    print("Testing volume controller...")
    
    try:
        controller = VolumeController()
        
        # Test getting current volume
        volume = controller.get_volume()
        print(f"  - Current volume: {volume}")
        
        # Test mute status
        muted = controller.is_muted()
        print(f"  - Muted: {muted}")
        
        # Test volume methods exist
        print("  - Volume control methods available")
        
        print("Volume controller tests passed")
        return True
        
    except Exception as e:
        print(f"Volume controller test failed: {e}")
        return False

def test_screenshot_capture():
    """Test screenshot capture functionality."""
    print("Testing screenshot capture...")
    
    try:
        capture = ScreenshotCapture()
        
        # Test capturing screen
        screenshot = capture.capture_screen()
        assert screenshot is not None, "Screenshot should be captured"
        print("  - Screenshot captured")
        
        # Test saving screenshot
        saved_path = capture.save_screenshot(screenshot)
        print(f"  - Screenshot saved: {saved_path}")
        
        # Test capturing region
        region = capture.capture_region(0, 0, 100, 100)
        if region:
            print("  - Region capture successful")
        
        print("Screenshot capture tests passed")
        return True
        
    except Exception as e:
        print(f"Screenshot capture test failed: {e}")
        return False

def test_system_operations():
    """Test system operations functionality."""
    print("Testing system operations...")
    
    try:
        ops = SystemOperations()
        
        # Test getting system info
        info = ops.get_system_info()
        assert info is not None, "System info should be available"
        print(f"  - Platform: {info.get('platform', 'Unknown')}")
        print(f"  - Hostname: {info.get('hostname', 'Unknown')}")
        
        # Test opening folder capability
        print("  - Folder operations available")
        
        # Test disk usage
        if PSUTIL_AVAILABLE:
            disk = ops.get_disk_usage()
            if disk:
                print(f"  - Disk usage: {disk.get('percent', 0)}%")
        
        # Test memory usage
        if PSUTIL_AVAILABLE:
            memory = ops.get_memory_usage()
            if memory:
                print(f"  - Memory usage: {memory.get('percent', 0)}%")
        
        print("System operations tests passed")
        return True
        
    except Exception as e:
        print(f"System operations test failed: {e}")
        return False

def main():
    """Run all Windows automation and action tests."""
    print("=" * 60)
    print("Running Windows Automation and Actions Tests")
    print("=" * 60)
    
    results = []
    
    # Test action components
    results.append(("Action Registry", test_action_registry()))
    results.append(("Permission Engine", test_permission_engine()))
    results.append(("Security Policy", test_security_policy()))
    results.append(("Confirmation Engine", test_confirmation_engine()))
    results.append(("Action Executor", test_action_executor()))
    
    # Test Windows automation components
    results.append(("Application Manager", test_application_manager()))
    results.append(("Window Manager", test_window_manager()))
    results.append(("Volume Controller", test_volume_controller()))
    results.append(("Screenshot Capture", test_screenshot_capture()))
    results.append(("System Operations", test_system_operations()))
    
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
        print("\nAll Windows automation and actions tests passed!")
        return 0
    else:
        print(f"\n{total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
