"""
ELARA - Action Registry
This module provides a centralized registry for all actions that ELARA can perform.
"""

from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid

from app.config.constants import PermissionLevel
from app.utils.logger import get_logger


class CommandType(Enum):
    """Command classification for security."""
    SAFE = "safe"
    CONFIRM = "confirm"
    BLOCK = "block"


@dataclass
class Action:
    """Represents an action that ELARA can perform."""
    id: str
    name: str
    description: str
    permission_level: PermissionLevel
    command_type: CommandType
    parameters: Dict[str, Any] = field(default_factory=dict)
    handler: Optional[Callable] = None
    timeout: float = 30.0
    confirmation_required: bool = False
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the action.
        
        Args:
            **kwargs: Action parameters
            
        Returns:
            Execution result dictionary
        """
        if self.handler is None:
            return {
                'success': False,
                'error': 'No handler registered for this action'
            }
        
        try:
            result = self.handler(**kwargs)
            return {
                'success': True,
                'result': result
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


class ActionRegistry:
    """Central registry for all ELARA actions."""
    
    def __init__(self):
        self.logger = get_logger("elara.actions.registry")
        self._actions: Dict[str, Action] = {}
        self._action_aliases: Dict[str, str] = {}
        
        # Register built-in actions
        self._register_builtin_actions()
        
        self.logger.info("Action registry initialized")
    
    def _register_builtin_actions(self):
        """Register built-in actions."""
        # Application actions
        self.register_action(
            action_id="open_application",
            name="Open Application",
            description="Launch a Windows application",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "application": {"type": "string", "required": True, "description": "Application name or alias"},
                "args": {"type": "list", "required": False, "description": "Command line arguments"}
            }
        )
        
        self.register_action(
            action_id="close_application",
            name="Close Application",
            description="Close a running application",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "application": {"type": "string", "required": True, "description": "Application name or alias"}
            }
        )
        
        # Window actions
        self.register_action(
            action_id="minimize_window",
            name="Minimize Window",
            description="Minimize a window",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "window_title": {"type": "string", "required": False, "description": "Window title"}
            }
        )
        
        self.register_action(
            action_id="maximize_window",
            name="Maximize Window",
            description="Maximize a window",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "window_title": {"type": "string", "required": False, "description": "Window title"}
            }
        )
        
        # Volume actions
        self.register_action(
            action_id="volume_up",
            name="Volume Up",
            description="Increase system volume",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "increment": {"type": "float", "required": False, "description": "Volume increment"}
            }
        )
        
        self.register_action(
            action_id="volume_down",
            name="Volume Down",
            description="Decrease system volume",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "decrement": {"type": "float", "required": False, "description": "Volume decrement"}
            }
        )
        
        self.register_action(
            action_id="mute",
            name="Mute",
            description="Mute system audio",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={}
        )
        
        self.register_action(
            action_id="unmute",
            name="Unmute",
            description="Unmute system audio",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={}
        )
        
        # Screenshot actions
        self.register_action(
            action_id="take_screenshot",
            name="Take Screenshot",
            description="Capture screen screenshot",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "save_path": {"type": "string", "required": False, "description": "Save path"}
            }
        )
        
        # System actions
        self.register_action(
            action_id="lock_computer",
            name="Lock Computer",
            description="Lock the computer",
            permission_level=PermissionLevel.MODERATE,
            command_type=CommandType.CONFIRM,
            parameters={},
            confirmation_required=True
        )
        
        self.register_action(
            action_id="restart_computer",
            name="Restart Computer",
            description="Restart the computer",
            permission_level=PermissionLevel.CRITICAL,
            command_type=CommandType.CONFIRM,
            parameters={
                "force": {"type": "boolean", "required": False, "description": "Force restart"}
            },
            confirmation_required=True
        )
        
        self.register_action(
            action_id="shutdown_computer",
            name="Shutdown Computer",
            description="Shutdown the computer",
            permission_level=PermissionLevel.CRITICAL,
            command_type=CommandType.CONFIRM,
            parameters={
                "force": {"type": "boolean", "required": False, "description": "Force shutdown"}
            },
            confirmation_required=True
        )
        
        # File actions
        self.register_action(
            action_id="open_folder",
            name="Open Folder",
            description="Open a folder in File Explorer",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "path": {"type": "string", "required": True, "description": "Folder path"}
            }
        )
        
        self.register_action(
            action_id="create_folder",
            name="Create Folder",
            description="Create a new folder",
            permission_level=PermissionLevel.MODERATE,
            command_type=CommandType.CONFIRM,
            parameters={
                "path": {"type": "string", "required": True, "description": "Folder path"},
                "name": {"type": "string", "required": False, "description": "Folder name"}
            }
        )
        
        # Browser actions
        self.register_action(
            action_id="open_url",
            name="Open URL",
            description="Open a URL in default browser",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "url": {"type": "string", "required": True, "description": "URL to open"}
            }
        )
        
        self.register_action(
            action_id="browser_search",
            name="Browser Search",
            description="Search in default browser",
            permission_level=PermissionLevel.SAFE,
            command_type=CommandType.SAFE,
            parameters={
                "query": {"type": "string", "required": True, "description": "Search query"},
                "engine": {"type": "string", "required": False, "description": "Search engine"}
            }
        )
        
        self.logger.info(f"Registered {len(self._actions)} built-in actions")
    
    def register_action(
        self,
        action_id: str,
        name: str,
        description: str,
        permission_level: PermissionLevel,
        command_type: CommandType,
        parameters: Dict[str, Any],
        handler: Optional[Callable] = None,
        timeout: float = 30.0,
        confirmation_required: bool = False,
        aliases: Optional[List[str]] = None
    ) -> bool:
        """
        Register a new action.
        
        Args:
            action_id: Unique action identifier
            name: Display name
            description: Action description
            permission_level: Required permission level
            command_type: Command classification
            parameters: Parameter definitions
            handler: Optional handler function
            timeout: Execution timeout
            confirmation_required: Whether confirmation is required
            aliases: Optional action aliases
            
        Returns:
            True if registered successfully
        """
        try:
            action = Action(
                id=action_id,
                name=name,
                description=description,
                permission_level=permission_level,
                command_type=command_type,
                parameters=parameters,
                handler=handler,
                timeout=timeout,
                confirmation_required=confirmation_required
            )
            
            self._actions[action_id] = action
            
            # Register aliases
            if aliases:
                for alias in aliases:
                    self._action_aliases[alias.lower()] = action_id
            
            self.logger.info(f"Registered action: {name} ({action_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register action: {e}")
            return False
    
    def get_action(self, action_id: str) -> Optional[Action]:
        """
        Get an action by ID or alias.
        
        Args:
            action_id: Action ID or alias
            
        Returns:
            Action object or None
        """
        # Check direct ID
        if action_id in self._actions:
            return self._actions[action_id]
        
        # Check aliases
        action_id_lower = action_id.lower()
        if action_id_lower in self._action_aliases:
            return self._actions[self._action_aliases[action_id_lower]]
        
        return None
    
    def get_all_actions(self) -> List[Action]:
        """Get all registered actions."""
        return list(self._actions.values())
    
    def get_actions_by_permission(self, permission_level: PermissionLevel) -> List[Action]:
        """
        Get actions by permission level.
        
        Args:
            permission_level: Permission level
            
        Returns:
            List of actions
        """
        return [
            action for action in self._actions.values()
            if action.permission_level == permission_level
        ]
    
    def unregister_action(self, action_id: str) -> bool:
        """
        Unregister an action.
        
        Args:
            action_id: Action ID
            
        Returns:
            True if unregistered successfully
        """
        if action_id in self._actions:
            del self._actions[action_id]
            
            # Remove aliases
            aliases_to_remove = [alias for alias, target in self._action_aliases.items() if target == action_id]
            for alias in aliases_to_remove:
                del self._action_aliases[alias]
            
            self.logger.info(f"Unregistered action: {action_id}")
            return True
        
        return False
    
    def set_action_handler(self, action_id: str, handler: Callable) -> bool:
        """
        Set or update the handler for an action.
        
        Args:
            action_id: Action ID
            handler: Handler function
            
        Returns:
            True if handler set successfully
        """
        action = self.get_action(action_id)
        if action:
            action.handler = handler
            self.logger.info(f"Handler set for action: {action_id}")
            return True
        
        return False
    
    def validate_parameters(self, action_id: str, parameters: Dict[str, Any]) -> tuple:
        """
        Validate action parameters.
        
        Args:
            action_id: Action ID
            parameters: Parameters to validate
            
        Returns:
            Tuple of (is_valid, errors)
        """
        action = self.get_action(action_id)
        if not action:
            return (False, ["Action not found"])
        
        errors = []
        
        # Check required parameters
        for param_name, param_def in action.parameters.items():
            if param_def.get('required', False) and param_name not in parameters:
                errors.append(f"Missing required parameter: {param_name}")
        
        # Validate parameter types
        for param_name, param_value in parameters.items():
            if param_name in action.parameters:
                param_def = action.parameters[param_name]
                expected_type = param_def.get('type')
                
                if expected_type:
                    if expected_type == 'string' and not isinstance(param_value, str):
                        errors.append(f"Parameter {param_name} should be string")
                    elif expected_type == 'int' and not isinstance(param_value, int):
                        errors.append(f"Parameter {param_name} should be integer")
                    elif expected_type == 'float' and not isinstance(param_value, (int, float)):
                        errors.append(f"Parameter {param_name} should be number")
                    elif expected_type == 'bool' and not isinstance(param_value, bool):
                        errors.append(f"Parameter {param_name} should be boolean")
                    elif expected_type == 'list' and not isinstance(param_value, list):
                        errors.append(f"Parameter {param_name} should be list")
        
        return (len(errors) == 0, errors)
    
    def search_actions(self, query: str) -> List[Action]:
        """
        Search for actions by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching actions
        """
        query_lower = query.lower()
        
        return [
            action for action in self._actions.values()
            if query_lower in action.name.lower() or
               query_lower in action.description.lower() or
               query_lower in action.id.lower()
        ]
    
    def get_action_count(self) -> int:
        """Get total number of registered actions."""
        return len(self._actions)
