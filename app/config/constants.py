"""
ELARA - Configuration Constants
This module contains all constant values used throughout the application.
"""

from enum import Enum
from pathlib import Path


class AssistantState(Enum):
    """ELARA assistant states for the state machine."""
    IDLE = "idle"
    LISTENING_FOR_WAKEWORD = "listening_for_wakeword"
    WAKEWORD_DETECTED = "wakeword_detected"
    VERIFYING_USER = "verifying_user"
    LISTENING_FOR_COMMAND = "listening_for_command"
    PROCESSING = "processing"
    WAITING_FOR_CONFIRMATION = "waiting_for_confirmation"
    EXECUTING = "executing"
    SPEAKING = "speaking"
    ERROR = "error"


class PermissionLevel(Enum):
    """Permission levels for actions."""
    SAFE = 0
    MODERATE = 1
    SENSITIVE = 2
    CRITICAL = 3


class CommandType(Enum):
    """Command classification for security."""
    SAFE = "safe"
    CONFIRM = "confirm"
    BLOCK = "block"


class MemoryCategory(Enum):
    """Memory categories for user data storage."""
    USER_PREFERENCES = "user_preferences"
    PROJECTS = "projects"
    WORKSPACES = "workspaces"
    APPLICATIONS = "applications"
    COMMAND_HISTORY = "command_history"
    ASSISTANT_SETTINGS = "assistant_settings"


# Directory constants
PROJECT_ROOT = Path(__file__).parent.parent.parent
APP_DIR = PROJECT_ROOT / "app"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
WORKSPACE_DIR = PROJECT_ROOT / "workspace"
MODELS_DIR = PROJECT_ROOT / "models"
SCRIPTS_DIR = PROJECT_ROOT / "scripts"

# Audio constants
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHANNELS = 1
DEFAULT_CHUNK_SIZE = 1024
DEFAULT_AUDIO_FORMAT = "int16"

# Wake word constants
DEFAULT_WAKE_WORD = "Hey Elara"
WAKE_WORD_TIMEOUT = 5.0  # seconds
COMMAND_TIMEOUT = 10.0  # seconds

# Voice verification constants
DEFAULT_VOICE_THRESHOLD = 0.75
ENROLLMENT_REQUIRED_PHRASES = 3
ENROLLMENT_PHRASES = [
    "Hey Elara, this is my voice",
    "My voice is my password",
    "Elara, recognize me"
]

# Speech recognition constants
DEFAULT_STT_MODEL = "base"
DEFAULT_STT_LANGUAGE = "en"
STT_DEVICE = "cpu"  # or "cuda" if available

# TTS constants
DEFAULT_TTS_MODEL = "en_US-lessac-medium"
DEFAULT_TTS_SPEED = 1.0

# AI constants
DEFAULT_AI_PROVIDER = "openai"
DEFAULT_AI_MODEL = "gpt-4"
AI_MAX_TOKENS = 2000
AI_TEMPERATURE = 0.7

# Security constants
DEFAULT_WORKSPACE = PROJECT_ROOT / "workspace"
BLOCKED_SYSTEM_PATHS = [
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\System32",
    "C:\\Windows\\System32"
]

# Log constants
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5
DEFAULT_LOG_LEVEL = "INFO"

# Database constants
DATABASE_PATH = DATA_DIR / "elara.db"
DATABASE_ECHO = False

# UI constants
WINDOW_TITLE = "ELARA - Personal AI Assistant"
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600

# Version
VERSION = "0.1.0"
