"""
ELARA - Permission Engine
This module handles permission checking and enforcement for actions.
"""

from typing import Dict, List, Tuple, Optional, Any
from enum import Enum

from app.config.constants import PermissionLevel
from app.utils.logger import get_logger


class CommandClassification(Enum):
    """Classification for commands."""
    SAFE = "safe"
    CONFIRM = "confirm"
    BLOCK = "block"


class PermissionEngine:
    """Manages permission checking for actions."""
    
    def __init__(self):
        self.logger = get_logger("elara.permissions")
        
        # Permission thresholds
        self._user_permission_level = PermissionLevel.MODERATE  # Default user level
        self._admin_permission_level = PermissionLevel.CRITICAL
        
        # Permission overrides
        self._permission_overrides: Dict[str, PermissionLevel] = {}
        
        # Block list
        self._blocked_actions: set = set()
        
        # Allow list
        self._allowed_actions: set = set()
        
        self.logger.info("Permission engine initialized")
    
    def set_user_permission_level(self, level: PermissionLevel) -> None:
        """
        Set the current user's permission level.
        
        Args:
            level: Permission level
        """
        self._user_permission_level = level
        self.logger.info(f"User permission level set to {level.value}")
    
    def get_user_permission_level(self) -> PermissionLevel:
        """Get the current user's permission level."""
        return self._user_permission_level
    
    def set_permission_override(self, action_id: str, level: PermissionLevel) -> None:
        """
        Set a permission override for a specific action.
        
        Args:
            action_id: Action ID
            level: Permission level
        """
        self._permission_overrides[action_id] = level
        self.logger.info(f"Permission override set for {action_id}: {level.value}")
    
    def check_permission(
        self,
        action_id: str,
        action_permission_level: PermissionLevel,
        user_id: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if an action is permitted.
        
        Args:
            action_id: Action ID
            action_permission_level: Required permission level
            user_id: Optional user ID
            
        Returns:
            Tuple of (is_permitted, reason)
        """
        # Check block list
        if action_id in self._blocked_actions:
            return (False, "Action is blocked")
        
        # Check allow list
        if action_id in self._allowed_actions:
            return (True, "Action is explicitly allowed")
        
        # Check permission override
        if action_id in self._permission_overrides:
            override_level = self._permission_overrides[action_id]
            if self._user_permission_level.value >= override_level.value:
                return (True, f"Permission override allows action")
            else:
                return (False, f"Permission override insufficient")
        
        # Check user permission level
        if self._user_permission_level.value >= action_permission_level.value:
            return (True, "User has sufficient permission")
        
        return (False, f"Insufficient permission (requires {action_permission_level.value}, user has {self._user_permission_level.value})")
    
    def classify_command(self, command_data: Dict[str, Any]) -> CommandClassification:
        """
        Classify a command for security purposes.
        
        Args:
            command_data: Command data dictionary
            
        Returns:
            Command classification
        """
        action_id = command_data.get('action_id', '')
        
        # Check block list
        if action_id in self._blocked_actions:
            return CommandClassification.BLOCK
        
        # Check for dangerous patterns
        dangerous_patterns = [
            'delete', 'remove', 'format', 'shutdown', 'restart',
            'sudo', 'admin', 'registry', 'system32'
        ]
        
        command_str = str(command_data).lower()
        for pattern in dangerous_patterns:
            if pattern in command_str:
                return CommandClassification.CONFIRM
        
        # Default to safe for most operations
        return CommandClassification.SAFE
    
    def block_action(self, action_id: str) -> None:
        """
        Block an action.
        
        Args:
            action_id: Action ID
        """
        self._blocked_actions.add(action_id)
        self.logger.info(f"Blocked action: {action_id}")
    
    def unblock_action(self, action_id: str) -> None:
        """
        Unblock an action.
        
        Args:
            action_id: Action ID
        """
        self._blocked_actions.discard(action_id)
        self.logger.info(f"Unblocked action: {action_id}")
    
    def allow_action(self, action_id: str) -> None:
        """
        Explicitly allow an action.
        
        Args:
            action_id: Action ID
        """
        self._allowed_actions.add(action_id)
        self.logger.info(f"Explicitly allowed action: {action_id}")
    
    def unallow_action(self, action_id: str) -> None:
        """
        Remove explicit allowance for an action.
        
        Args:
            action_id: Action ID
        """
        self._allowed_actions.discard(action_id)
        self.logger.info(f"Removed explicit allowance for {action_id}")
    
    def get_blocked_actions(self) -> set:
        """Get the set of blocked actions."""
        return self._blocked_actions.copy()
    
    def get_allowed_actions(self) -> set:
        """Get the set of explicitly allowed actions."""
        return self._allowed_actions.copy()
    
    def get_permission_overrides(self) -> Dict[str, PermissionLevel]:
        """Get permission overrides."""
        return self._permission_overrides.copy()
    
    def clear_permission_overrides(self) -> None:
        """Clear all permission overrides."""
        self._permission_overrides.clear()
        self.logger.info("Cleared all permission overrides")
    
    def is_action_blocked(self, action_id: str) -> bool:
        """
        Check if an action is blocked.
        
        Args:
            action_id: Action ID
            
        Returns:
            True if blocked
        """
        return action_id in self._blocked_actions
    
    def is_action_allowed(self, action_id: str) -> bool:
        """
        Check if an action is explicitly allowed.
        
        Args:
            action_id: Action ID
            
        Returns:
            True if explicitly allowed
        """
        return action_id in self._allowed_actions


class SecurityPolicy:
    """Defines security policies for the system."""
    
    def __init__(self):
        self.logger = get_logger("elara.security_policy")
        
        # Security settings
        self._require_confirmation_sensitive = True
        self._require_confirmation_critical = True
        self._log_all_commands = True
        self._block_unknown_commands = False
        
        # Path security
        self._allowed_directories = []
        self._blocked_directories = []
        
        # Time-based restrictions
        self._working_hours_only = False
        self._working_hours_start = "09:00"
        self._working_hours_end = "17:00"
        
        self.logger.info("Security policy initialized")
    
    def set_require_confirmation_sensitive(self, required: bool) -> None:
        """Set whether sensitive actions require confirmation."""
        self._require_confirmation_sensitive = required
        self.logger.info(f"Require confirmation for sensitive: {required}")
    
    def set_require_confirmation_critical(self, required: bool) -> None:
        """Set whether critical actions require confirmation."""
        self._require_confirmation_critical = required
        self.logger.info(f"Require confirmation for critical: {required}")
    
    def requires_confirmation(self, permission_level: PermissionLevel) -> bool:
        """
        Check if an action requires confirmation.
        
        Args:
            permission_level: Permission level
            
        Returns:
            True if confirmation required
        """
        if permission_level == PermissionLevel.CRITICAL:
            return self._require_confirmation_critical
        elif permission_level == PermissionLevel.SENSITIVE:
            return self._require_confirmation_sensitive
        return False
    
    def add_allowed_directory(self, directory: str) -> None:
        """Add an allowed directory."""
        self._allowed_directories.append(directory)
        self.logger.info(f"Added allowed directory: {directory}")
    
    def add_blocked_directory(self, directory: str) -> None:
        """Add a blocked directory."""
        self._blocked_directories.append(directory)
        self.logger.info(f"Added blocked directory: {directory}")
    
    def is_directory_allowed(self, directory: str) -> bool:
        """Check if a directory is allowed."""
        # Check blocked list
        for blocked in self._blocked_directories:
            if directory.startswith(blocked):
                return False
        
        # If allowed list is empty, allow everything except blocked
        if not self._allowed_directories:
            return True
        
        # Check allowed list
        for allowed in self._allowed_directories:
            if directory.startswith(allowed):
                return True
        
        return False
    
    def set_working_hours(self, enabled: bool, start: str = "09:00", end: str = "17:00") -> None:
        """Set working hours restrictions."""
        self._working_hours_only = enabled
        self._working_hours_start = start
        self._working_hours_end = end
        self.logger.info(f"Working hours: {enabled}, {start}-{end}")
    
    def is_within_working_hours(self) -> bool:
        """Check if current time is within working hours."""
        if not self._working_hours_only:
            return True
        
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M")
        
        return self._working_hours_start <= current_time <= self._working_hours_end
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get a summary of current security policies."""
        return {
            'require_confirmation_sensitive': self._require_confirmation_sensitive,
            'require_confirmation_critical': self._require_confirmation_critical,
            'log_all_commands': self._log_all_commands,
            'block_unknown_commands': self._block_unknown_commands,
            'allowed_directories': self._allowed_directories,
            'blocked_directories': self._blocked_directories,
            'working_hours_only': self._working_hours_only,
            'working_hours': f"{self._working_hours_start}-{self._working_hours_end}"
        }
