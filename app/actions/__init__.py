"""
ELARA - Actions Module
This module handles action registration, permission checking, confirmation, and execution.
"""

from .registry import ActionRegistry, Action, CommandType
from .permissions import PermissionEngine, SecurityPolicy, CommandClassification
from .confirmation import ConfirmationEngine, ConfirmationStatus, ConfirmationRequest, AutoConfirmation
from .executor import ActionExecutor

__all__ = [
    "ActionRegistry",
    "Action",
    "CommandType",
    "PermissionEngine",
    "SecurityPolicy",
    "CommandClassification",
    "ConfirmationEngine",
    "ConfirmationStatus",
    "ConfirmationRequest",
    "AutoConfirmation",
    "ActionExecutor"
]
