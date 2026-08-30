"""
ELARA - Memory Module
This module handles database operations, memory storage, and user preferences.
"""

from .database import DatabaseManager, get_database_manager, initialize_database
from .models import (
    Base,
    Setting,
    Memory,
    Application,
    Workspace,
    CommandHistory,
    AuditEvent,
    VoiceProfile,
    Conversation,
    Project,
    GitRepository,
    UserPreference,
    SecurityEvent,
    ScheduledTask
)
from .memory import MemoryManager, get_memory_manager
from .preferences import PreferencesManager, get_preferences_manager

__all__ = [
    # Database
    "DatabaseManager",
    "get_database_manager",
    "initialize_database",
    # Models
    "Base",
    "Setting",
    "Memory",
    "Application",
    "Workspace",
    "CommandHistory",
    "AuditEvent",
    "VoiceProfile",
    "Conversation",
    "Project",
    "GitRepository",
    "UserPreference",
    "SecurityEvent",
    "ScheduledTask",
    # Memory
    "MemoryManager",
    "get_memory_manager",
    # Preferences
    "PreferencesManager",
    "get_preferences_manager"
]
