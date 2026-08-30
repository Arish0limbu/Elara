"""
ELARA - Confirmation Engine
This module handles user confirmation for sensitive actions.
"""

from typing import Optional, Callable, Dict, Any
from enum import Enum
import threading
import time

from app.config.constants import PermissionLevel
from app.utils.logger import get_logger


class ConfirmationStatus(Enum):
    """Status of confirmation requests."""
    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class ConfirmationRequest:
    """Represents a confirmation request."""
    
    def __init__(
        self,
        request_id: str,
        action_id: str,
        action_name: str,
        message: str,
        permission_level: PermissionLevel,
        timeout: float = 30.0
    ):
        self.request_id = request_id
        self.action_id = action_id
        self.action_name = action_name
        self.message = message
        self.permission_level = permission_level
        self.timeout = timeout
        self.status = ConfirmationStatus.PENDING
        self.response = None
        self.created_at = time.time()
        self.responded_at = None


class ConfirmationEngine:
    """Manages user confirmation for sensitive actions."""
    
    def __init__(self):
        self.logger = get_logger("elara.confirmations")
        
        # Active confirmation requests
        self._active_requests: Dict[str, ConfirmationRequest] = {}
        
        # Request callbacks
        self._request_callback: Optional[Callable] = None
        
        # Default timeout
        self._default_timeout = 30.0
        
        # Lock for thread safety
        self._lock = threading.Lock()
        
        self.logger.info("Confirmation engine initialized")
    
    def set_request_callback(self, callback: Callable) -> None:
        """
        Set callback for new confirmation requests.
        
        Args:
            callback: Callback function
        """
        self._request_callback = callback
        self.logger.info("Confirmation request callback set")
    
    def request_confirmation(
        self,
        action_id: str,
        action_name: str,
        message: str,
        permission_level: PermissionLevel,
        timeout: Optional[float] = None
    ) -> ConfirmationRequest:
        """
        Request user confirmation for an action.
        
        Args:
            action_id: Action ID
            action_name: Action display name
            message: Confirmation message
            permission_level: Permission level
            timeout: Request timeout
            
        Returns:
            Confirmation request object
        """
        request_id = self._generate_request_id()
        
        timeout = timeout or self._default_timeout
        
        request = ConfirmationRequest(
            request_id=request_id,
            action_id=action_id,
            action_name=action_name,
            message=message,
            permission_level=permission_level,
            timeout=timeout
        )
        
        with self._lock:
            self._active_requests[request_id] = request
        
        self.logger.info(f"Confirmation requested: {action_name} ({request_id})")
        
        # Notify callback if set
        if self._request_callback:
            try:
                self._request_callback(request)
            except Exception as e:
                self.logger.error(f"Error in confirmation callback: {e}")
        
        return request
    
    def respond_to_confirmation(
        self,
        request_id: str,
        approved: bool,
        response: Optional[str] = None
    ) -> bool:
        """
        Respond to a confirmation request.
        
        Args:
            request_id: Request ID
            approved: Whether action is approved
            response: Optional response message
            
        Returns:
            True if response recorded successfully
        """
        with self._lock:
            if request_id not in self._active_requests:
                self.logger.warning(f"Confirmation request not found: {request_id}")
                return False
            
            request = self._active_requests[request_id]
            
            if request.status != ConfirmationStatus.PENDING:
                self.logger.warning(f"Confirmation request already resolved: {request_id}")
                return False
            
            request.status = ConfirmationStatus.APPROVED if approved else ConfirmationStatus.DENIED
            request.response = response
            request.responded_at = time.time()
            
            self.logger.info(f"Confirmation {'approved' if approved else 'denied'}: {request_id}")
            
            return True
    
    def cancel_confirmation(self, request_id: str) -> bool:
        """
        Cancel a confirmation request.
        
        Args:
            request_id: Request ID
            
        Returns:
            True if cancelled successfully
        """
        with self._lock:
            if request_id not in self._active_requests:
                return False
            
            request = self._active_requests[request_id]
            request.status = ConfirmationStatus.CANCELLED
            request.responded_at = time.time()
            
            self.logger.info(f"Confirmation cancelled: {request_id}")
            
            return True
    
    def get_request_status(self, request_id: str) -> Optional[ConfirmationStatus]:
        """
        Get the status of a confirmation request.
        
        Args:
            request_id: Request ID
            
        Returns:
            Confirmation status or None
        """
        with self._lock:
            if request_id in self._active_requests:
                return self._active_requests[request_id].status
        
        return None
    
    def wait_for_confirmation(
        self,
        request_id: str,
        timeout: Optional[float] = None
    ) -> tuple:
        """
        Wait for a confirmation response.
        
        Args:
            request_id: Request ID
            timeout: Maximum wait time
            
        Returns:
            Tuple of (approved, response)
        """
        timeout = timeout or self._default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_request_status(request_id)
            
            if status == ConfirmationStatus.APPROVED:
                request = self._active_requests.get(request_id)
                return (True, request.response if request else None)
            elif status == ConfirmationStatus.DENIED:
                request = self._active_requests.get(request_id)
                return (False, request.response if request else None)
            elif status in [ConfirmationStatus.CANCELLED, ConfirmationStatus.TIMEOUT]:
                return (False, "Request cancelled or timed out")
            
            time.sleep(0.1)
        
        # Timeout
        with self._lock:
            if request_id in self._active_requests:
                self._active_requests[request_id].status = ConfirmationStatus.TIMEOUT
        
        return (False, "Confirmation request timed out")
    
    def cleanup_old_requests(self, max_age: float = 60.0) -> int:
        """
        Clean up old confirmation requests.
        
        Args:
            max_age: Maximum age in seconds
            
        Returns:
            Number of requests cleaned up
        """
        current_time = time.time()
        cleaned_count = 0
        
        with self._lock:
            requests_to_remove = []
            
            for request_id, request in self._active_requests.items():
                age = current_time - request.created_at
                if age > max_age or request.status != ConfirmationStatus.PENDING:
                    requests_to_remove.append(request_id)
            
            for request_id in requests_to_remove:
                del self._active_requests[request_id]
                cleaned_count += 1
        
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old confirmation requests")
        
        return cleaned_count
    
    def get_active_requests(self) -> list:
        """Get list of active (pending) confirmation requests."""
        with self._lock:
            return [
                request for request in self._active_requests.values()
                if request.status == ConfirmationStatus.PENDING
            ]
    
    def get_all_requests(self) -> list:
        """Get all confirmation requests."""
        with self._lock:
            return list(self._active_requests.values())
    
    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        import uuid
        return str(uuid.uuid4())
    
    def set_default_timeout(self, timeout: float) -> None:
        """
        Set the default confirmation timeout.
        
        Args:
            timeout: Timeout in seconds
        """
        self._default_timeout = max(1.0, timeout)
        self.logger.info(f"Default confirmation timeout set to {self._default_timeout}s")


class AutoConfirmation(ConfirmationEngine):
    """Auto-confirmation for testing or specific scenarios."""
    
    def __init__(self, auto_approve_safe: bool = False):
        super().__init__()
        self._auto_approve_safe = auto_approve_safe
        self.logger.info(f"Auto-confirmation enabled (safe: {auto_approve_safe})")
    
    def request_confirmation(
        self,
        action_id: str,
        action_name: str,
        message: str,
        permission_level: PermissionLevel,
        timeout: Optional[float] = None
    ) -> ConfirmationRequest:
        """
        Request confirmation with auto-approval for safe actions.
        
        Args:
            action_id: Action ID
            action_name: Action display name
            message: Confirmation message
            permission_level: Permission level
            timeout: Request timeout
            
        Returns:
            Confirmation request object
        """
        request = super().request_confirmation(
            action_id, action_name, message, permission_level, timeout
        )
        
        # Auto-approve safe actions if enabled
        if self._auto_approve_safe and permission_level == PermissionLevel.SAFE:
            self.respond_to_confirmation(request.request_id, True, "Auto-approved (safe action)")
        
        return request
