"""
ELARA - Action Executor
This module handles the execution of validated actions.
"""

from typing import Dict, Any, Optional, Callable
import threading
import time
from datetime import datetime

from app.actions.registry import Action
from app.actions.permissions import PermissionEngine, SecurityPolicy
from app.actions.confirmation import ConfirmationEngine
from app.config.constants import PermissionLevel
from app.utils.logger import get_logger


class ActionExecutor:
    """Executes validated actions with proper security checks."""
    
    def __init__(self):
        self.logger = get_logger("elara.executor")
        
        # Security components
        self.permission_engine = PermissionEngine()
        self.security_policy = SecurityPolicy()
        self.confirmation_engine = ConfirmationEngine()
        
        # Execution tracking
        self._execution_history: list = []
        self._active_executions: Dict[str, threading.Thread] = {}
        
        # Handlers
        self._handlers: Dict[str, Callable] = {}
        
        # Setup confirmation callback
        self.confirmation_engine.set_request_callback(self._on_confirmation_request)
        
        self.logger.info("Action executor initialized")
    
    def _on_confirmation_request(self, request) -> None:
        """Handle confirmation request callback."""
        self.logger.info(f"Confirmation request: {request.action_name}")
        # In a real application, this would trigger UI notification
        # For now, we'll auto-approve for testing
        self.confirmation_engine.respond_to_confirmation(
            request.request_id,
            True,
            "Auto-approved for testing"
        )
    
    def register_handler(self, action_id: str, handler: Callable) -> None:
        """
        Register a handler for an action.
        
        Args:
            action_id: Action ID
            handler: Handler function
        """
        self._handlers[action_id] = handler
        self.logger.info(f"Handler registered for action: {action_id}")
    
    def execute_action(
        self,
        action: Action,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
        skip_confirmation: bool = False
    ) -> Dict[str, Any]:
        """
        Execute an action with full security checks.
        
        Args:
            action: Action to execute
            parameters: Action parameters
            user_id: Optional user ID
            skip_confirmation: Skip confirmation check
            
        Returns:
            Execution result dictionary
        """
        execution_id = self._generate_execution_id()
        start_time = time.time()
        
        # Record execution start
        execution_record = {
            'execution_id': execution_id,
            'action_id': action.id,
            'action_name': action.name,
            'parameters': parameters,
            'user_id': user_id,
            'start_time': datetime.now().isoformat(),
            'status': 'started'
        }
        
        try:
            # Step 1: Validate parameters
            from app.actions.registry import ActionRegistry
            registry = ActionRegistry()
            is_valid, errors = registry.validate_parameters(action.id, parameters)
            
            if not is_valid:
                return {
                    'success': False,
                    'error': f"Parameter validation failed: {', '.join(errors)}",
                    'execution_id': execution_id
                }
            
            # Step 2: Check permission
            is_permitted, permission_reason = self.permission_engine.check_permission(
                action.id,
                action.permission_level,
                user_id
            )
            
            if not is_permitted:
                self.logger.warning(f"Action not permitted: {action.name} - {permission_reason}")
                execution_record['status'] = 'permission_denied'
                execution_record['error'] = permission_reason
                self._execution_history.append(execution_record)
                
                return {
                    'success': False,
                    'error': permission_reason,
                    'execution_id': execution_id
                }
            
            # Step 3: Check confirmation requirement
            if action.confirmation_required and not skip_confirmation:
                requires_confirmation = self.security_policy.requires_confirmation(action.permission_level)
                
                if requires_confirmation:
                    # Request confirmation
                    confirmation = self.confirmation_engine.request_confirmation(
                        action.id,
                        action.name,
                        f"Execute {action.name}?",
                        action.permission_level,
                        action.timeout
                    )
                    
                    # Wait for response
                    approved, response = self.confirmation_engine.wait_for_confirmation(
                        confirmation.request_id,
                        action.timeout
                    )
                    
                    if not approved:
                        self.logger.info(f"Action denied by user: {action.name}")
                        execution_record['status'] = 'user_denied'
                        execution_record['error'] = response
                        self._execution_history.append(execution_record)
                        
                        return {
                            'success': False,
                            'error': f"Action denied: {response}",
                            'execution_id': execution_id
                        }
            
            # Step 4: Execute action
            execution_record['status'] = 'executing'
            
            # Use registered handler or action handler
            handler = self._handlers.get(action.id, action.handler)
            
            if handler:
                # Execute in thread for long-running actions
                def execute_thread():
                    try:
                        result = handler(**parameters)
                        execution_record['status'] = 'completed'
                        execution_record['result'] = result
                        execution_record['end_time'] = datetime.now().isoformat()
                        execution_record['duration'] = time.time() - start_time
                    except Exception as e:
                        execution_record['status'] = 'failed'
                        execution_record['error'] = str(e)
                        execution_record['end_time'] = datetime.now().isoformat()
                        execution_record['duration'] = time.time() - start_time
                    finally:
                        if execution_id in self._active_executions:
                            del self._active_executions[execution_id]
                
                thread = threading.Thread(target=execute_thread, daemon=True)
                thread.start()
                self._active_executions[execution_id] = thread
                
                return {
                    'success': True,
                    'execution_id': execution_id,
                    'async': True
                }
            else:
                # No handler available
                execution_record['status'] = 'no_handler'
                execution_record['error'] = 'No handler registered for this action'
                self._execution_history.append(execution_record)
                
                return {
                    'success': False,
                    'error': 'No handler registered for this action',
                    'execution_id': execution_id
                }
        
        except Exception as e:
            execution_record['status'] = 'error'
            execution_record['error'] = str(e)
            execution_record['end_time'] = datetime.now().isoformat()
            execution_record['duration'] = time.time() - start_time
            self._execution_history.append(execution_record)
            
            self.logger.error(f"Action execution failed: {action.name} - {e}")
            
            return {
                'success': False,
                'error': str(e),
                'execution_id': execution_id
            }
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict]:
        """
        Get the status of an execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution status dictionary or None
        """
        for record in self._execution_history:
            if record.get('execution_id') == execution_id:
                return record
        
        return None
    
    def get_execution_history(self, limit: int = 100) -> list:
        """
        Get execution history.
        
        Args:
            limit: Maximum number of records
            
        Returns:
            List of execution records
        """
        return self._execution_history[-limit:]
    
    def wait_for_execution(self, execution_id: str, timeout: float = 60.0) -> bool:
        """
        Wait for an execution to complete.
        
        Args:
            execution_id: Execution ID
            timeout: Maximum wait time
            
        Returns:
            True if execution completed successfully
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_execution_status(execution_id)
            
            if status and status['status'] in ['completed', 'failed', 'error', 'no_handler']:
                return status['status'] == 'completed'
            
            if execution_id in self._active_executions:
                thread = self._active_executions[execution_id]
                if thread.is_alive():
                    time.sleep(0.1)
                else:
                    break
            else:
                break
        
        return False
    
    def cancel_execution(self, execution_id: str) -> bool:
        """
        Cancel an active execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            True if cancelled successfully
        """
        if execution_id in self._active_executions:
            # Note: Actual cancellation would require thread termination logic
            # This is a simplified version
            del self._active_executions[execution_id]
            self.logger.info(f"Execution cancelled: {execution_id}")
            return True
        
        return False
    
    def _generate_execution_id(self) -> str:
        """Generate a unique execution ID."""
        import uuid
        return str(uuid.uuid4())
    
    def get_active_executions(self) -> list:
        """Get list of active execution IDs."""
        return list(self._active_executions.keys())
    
    def cleanup_history(self, max_age_hours: int = 24) -> int:
        """
        Clean up old execution history.
        
        Args:
            max_age_hours: Maximum age in hours
            
        Returns:
            Number of records cleaned up
        """
        from datetime import datetime, timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        new_history = []
        for record in self._execution_history:
            try:
                record_time = datetime.fromisoformat(record['start_time'])
                if record_time > cutoff_time:
                    new_history.append(record)
                else:
                    cleaned_count += 1
            except:
                new_history.append(record)  # Keep records with parsing errors
        
        self._execution_history = new_history
        
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} execution records")
        
        return cleaned_count
