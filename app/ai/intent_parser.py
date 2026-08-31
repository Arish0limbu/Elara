"""
ELARA - AI Intent Parser
This module handles natural language understanding and intent extraction.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime

from app.utils.logger import get_logger


class IntentCategory(Enum):
    """Categories of user intents."""
    APPLICATION = "application"
    WINDOW = "window"
    VOLUME = "volume"
    SCREENSHOT = "screenshot"
    SYSTEM = "system"
    FILE = "file"
    BROWSER = "browser"
    SEARCH = "search"
    CODING = "coding"
    GIT = "git"
    INFORMATION = "information"
    UNKNOWN = "unknown"


class IntentAction(Enum):
    """Specific actions within categories."""
    # Application actions
    OPEN_APPLICATION = "open_application"
    CLOSE_APPLICATION = "close_application"
    
    # Window actions
    MINIMIZE_WINDOW = "minimize_window"
    MAXIMIZE_WINDOW = "maximize_window"
    RESTORE_WINDOW = "restore_window"
    CLOSE_WINDOW = "close_window"
    
    # Volume actions
    VOLUME_UP = "volume_up"
    VOLUME_DOWN = "volume_down"
    SET_VOLUME = "set_volume"
    MUTE = "mute"
    UNMUTE = "unmute"
    
    # Screenshot actions
    TAKE_SCREENSHOT = "take_screenshot"
    TAKE_REGION_SCREENSHOT = "take_region_screenshot"
    
    # System actions
    LOCK_COMPUTER = "lock_computer"
    RESTART_COMPUTER = "restart_computer"
    SHUTDOWN_COMPUTER = "shutdown_computer"
    SLEEP_COMPUTER = "sleep_computer"
    LOG_OFF = "log_off"
    
    # File actions
    OPEN_FOLDER = "open_folder"
    CREATE_FOLDER = "create_folder"
    DELETE_FILE = "delete_file"
    MOVE_FILE = "move_file"
    COPY_FILE = "copy_file"
    
    # Browser actions
    OPEN_URL = "open_url"
    CLOSE_BROWSER = "close_browser"
    BROWSER_SEARCH = "browser_search"
    
    # Information actions
    GET_SYSTEM_INFO = "get_system_info"
    GET_TIME = "get_time"
    GET_WEATHER = "get_weather"
    UNKNOWN_ACTION = "unknown_action"


@dataclass
class Intent:
    """Represents a parsed user intent."""
    category: IntentCategory
    action: IntentAction
    confidence: float
    parameters: Dict[str, Any]
    original_text: str
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


@dataclass
class Parameter:
    """Represents a parameter extracted from user text."""
    name: str
    value: Any
    confidence: float
    start_pos: int
    end_pos: int


class IntentParser:
    """Parses natural language text into structured intents."""
    
    def __init__(self):
        self.logger = get_logger("elara.intent_parser")
        
        # Initialize patterns and mappings
        self._initialize_patterns()
        self._initialize_applications()
        self._initialize_directories()
        
        self.logger.info("Intent parser initialized")
    
    def _initialize_patterns(self):
        """Initialize regex patterns for intent recognition."""
        self.patterns = {
            # Application patterns
            IntentCategory.APPLICATION: [
                (r"(?:open|launch|start|run)\s+(.+?)(?:\s+for\s+me)?$", IntentAction.OPEN_APPLICATION),
                (r"(?:close|quit|exit|stop)\s+(.+?)(?:\s+for\s+me)?$", IntentAction.CLOSE_APPLICATION),
            ],
            
            # Window patterns
            IntentCategory.WINDOW: [
                (r"(?:minimize|min)\s+(?:the\s+)?(?:window\s+)?(.+?)(?:\s+for\s+me)?$", IntentAction.MINIMIZE_WINDOW),
                (r"(?:maximize|max)\s+(?:the\s+)?(?:window\s+)?(.+?)(?:\s+for\s+me)?$", IntentAction.MAXIMIZE_WINDOW),
                (r"(?:restore)\s+(?:the\s+)?(?:window\s+)?(.+?)(?:\s+for\s+me)?$", IntentAction.RESTORE_WINDOW),
            ],
            
            # Volume patterns
            IntentCategory.VOLUME: [
                (r"(?:turn|volume)?\s*(?:up|increase|raise)(?:\s+(?:the\s+)?(?:volume|audio|sound))?(?:\s+by\s+(\d+)(?:%|percent)?)?$", IntentAction.VOLUME_UP),
                (r"(?:turn|volume)?\s*(?:down|decrease|lower)(?:\s+(?:the\s+)?(?:volume|audio|sound))?(?:\s+by\s+(\d+)(?:%|percent)?)?$", IntentAction.VOLUME_DOWN),
                (r"(?:set|turn)?\s*(?:the\s+)?(?:volume|audio|sound)?\s+(?:to\s+)?(\d+)(?:%|percent)?$", IntentAction.SET_VOLUME),
                (r"(?:mute|silence)(?:\s+(?:the\s+)?(?:audio|sound|volume))?$", IntentAction.MUTE),
                (r"(?:unmute|un-silence)(?:\s+(?:the\s+)?(?:audio|sound|volume))?$", IntentAction.UNMUTE),
            ],
            
            # Screenshot patterns
            IntentCategory.SCREENSHOT: [
                (r"(?:take|capture|grab)\s+(?:a\s+)?(?:screenshot|screen\s+shot|screen\s+capture)(?:\s+of\s+(.+?))?$", IntentAction.TAKE_SCREENSHOT),
                (r"(?:take|capture|grab)\s+(?:a\s+)?(?:region|area)\s+(?:screenshot|screen\s+shot)(?:\s+(?:of|at)\s+(.+?))?$", IntentAction.TAKE_REGION_SCREENSHOT),
            ],
            
            # System patterns
            IntentCategory.SYSTEM: [
                (r"(?:lock|lock\s+screen|lock\s+computer)(?:\s+for\s+me)?$", IntentAction.LOCK_COMPUTER),
                (r"(?:restart|reboot|re-start)\s+(?:the\s+)?(?:computer|pc|system)(?:\s+for\s+me)?$", IntentAction.RESTART_COMPUTER),
                (r"(?:shutdown|shut\s+down|turn\s+off)\s+(?:the\s+)?(?:computer|pc|system)(?:\s+for\s+me)?$", IntentAction.SHUTDOWN_COMPUTER),
                (r"(?:sleep|hibernate)\s+(?:the\s+)?(?:computer|pc|system)(?:\s+for\s+me)?$", IntentAction.SLEEP_COMPUTER),
                (r"(?:log\s+off|sign\s+out|logout)(?:\s+for\s+me)?$", IntentAction.LOG_OFF),
            ],
            
            # File patterns
            IntentCategory.FILE: [
                (r"(?:open|go\s+to|navigate\s+to)\s+(?:my\s+)?(.+?)(?:\s+folder)?(?:\s+for\s+me)?\s*$", IntentAction.OPEN_FOLDER),
                (r"(?:create|make|new)\s+(?:a\s+)?(?:folder|directory)\s+(?:called|named)?\s*(.+?)(?:\s+for\s+me)?\s*$", IntentAction.CREATE_FOLDER),
            ],
            
            # Browser patterns
            IntentCategory.BROWSER: [
                (r"(?:open|launch|go\s+to)\s+(?:https?:\/\/)?(?:www\.)?(.+?)(?:\s+for\s+me)?$", IntentAction.OPEN_URL),
                (r"(?:search|google|look\s+up)\s+(?:for\s+)?(.+?)(?:\s+on\s+(?:google|the\s+web|internet))?(?:\s+for\s+me)?$", IntentAction.BROWSER_SEARCH),
            ],
            
            # Information patterns
            IntentCategory.INFORMATION: [
                (r"(?:what\s+)?(?:time|date|day)\s+is\s+it\??$", IntentAction.GET_TIME),
                (r"(?:tell\s+me\s+)?(?:the\s+)?(?:time|date|day)\??$", IntentAction.GET_TIME),
                (r"(?:what\s+is\s+)?(?:the\s+)?(?:weather|temperature)(?:\s+(?:like|outside|today))?\??$", IntentAction.GET_WEATHER),
                (r"(?:tell\s+me\s+)?(?:about\s+)?(?:my\s+)?(?:computer|system|pc)(?:\s+info|information)?\??$", IntentAction.GET_SYSTEM_INFO),
            ],
        }
    
    def _initialize_applications(self):
        """Initialize common application aliases."""
        self.application_aliases = {
            "chrome": ["chrome", "google chrome", "browser", "web browser"],
            "vscode": ["vscode", "visual studio code", "code", "vs code"],
            "notepad": ["notepad", "text editor", "notepad++"],
            "explorer": ["explorer", "file explorer", "windows explorer", "files"],
            "edge": ["edge", "microsoft edge", "ms edge"],
            "discord": ["discord"],
            "spotify": ["spotify", "music"],
            "slack": ["slack"],
            "teams": ["teams", "microsoft teams"],
            "word": ["word", "microsoft word", "ms word"],
            "excel": ["excel", "microsoft excel", "ms excel"],
            "powerpoint": ["powerpoint", "microsoft powerpoint", "ms powerpoint", "ppt"],
            "outlook": ["outlook", "microsoft outlook", "ms outlook", "mail"],
            "photoshop": ["photoshop", "adobe photoshop", "ps"],
            "illustrator": ["illustrator", "adobe illustrator", "ai"],
        }
    
    def _initialize_directories(self):
        """Initialize common directory aliases."""
        self.directory_aliases = {
            "downloads": ["downloads", "my downloads", "download folder"],
            "documents": ["documents", "my documents", "docs", "my docs"],
            "desktop": ["desktop", "my desktop"],
            "pictures": ["pictures", "my pictures", "photos", "images"],
            "music": ["music", "my music"],
            "videos": ["videos", "my videos"],
            "workspace": ["workspace", "projects", "git", "coding"],
            "home": ["home", "user folder", "user directory"],
        }
    
    def parse(self, text: str) -> Intent:
        """
        Parse natural language text into an intent.
        
        Args:
            text: User input text
            
        Returns:
            Parsed intent object
        """
        text = text.strip().lower()
        self.logger.info(f"Parsing text: '{text}'")
        
        # Try to match patterns for each category
        for category, patterns in self.patterns.items():
            for pattern, action in patterns:
                match = re.match(pattern, text, re.IGNORECASE)
                if match:
                    # Extract parameters from match groups
                    parameters = self._extract_parameters(match, action, text)
                    
                    # Calculate confidence based on pattern specificity
                    confidence = self._calculate_confidence(match, pattern, text)
                    
                    intent = Intent(
                        category=category,
                        action=action,
                        confidence=confidence,
                        parameters=parameters,
                        original_text=text
                    )
                    
                    self.logger.info(f"Parsed intent: {category.value}/{action.value} (confidence: {confidence:.2f})")
                    return intent
        
        # If no pattern matched, return unknown intent
        self.logger.warning(f"No pattern matched for text: '{text}'")
        return Intent(
            category=IntentCategory.UNKNOWN,
            action=IntentAction.UNKNOWN_ACTION,
            confidence=0.0,
            parameters={},
            original_text=text
        )
    
    def _extract_parameters(self, match, action: IntentAction, text: str) -> Dict[str, Any]:
        """
        Extract parameters from regex match.
        
        Args:
            match: Regex match object
            action: Detected action
            text: Original text
            
        Returns:
            Dictionary of parameters
        """
        parameters = {}
        
        if match.groups():
            groups = match.groups()
            
            # Extract common parameters based on action
            if action in [IntentAction.OPEN_APPLICATION, IntentAction.CLOSE_APPLICATION]:
                if groups[0]:
                    app_name = groups[0].strip()
                    # Normalize application name
                    parameters["application"] = self._normalize_application_name(app_name)
            
            elif action in [IntentAction.MINIMIZE_WINDOW, IntentAction.MAXIMIZE_WINDOW, IntentAction.RESTORE_WINDOW]:
                if groups[0]:
                    parameters["window_title"] = groups[0].strip()
            
            elif action == IntentAction.SET_VOLUME:
                if groups[0]:
                    try:
                        parameters["volume"] = int(groups[0]) / 100.0  # Convert percentage to 0-1 range
                    except ValueError:
                        pass
            
            elif action in [IntentAction.VOLUME_UP, IntentAction.VOLUME_DOWN]:
                if len(groups) > 0 and groups[0]:
                    try:
                        parameters["increment"] = int(groups[0]) / 100.0
                    except ValueError:
                        parameters["increment"] = 0.1  # Default increment
            
            elif action in [IntentAction.TAKE_SCREENSHOT, IntentAction.TAKE_REGION_SCREENSHOT]:
                if groups[0]:
                    parameters["description"] = groups[0].strip()
            
            elif action == IntentAction.OPEN_FOLDER:
                if groups[0]:
                    folder_name = groups[0].strip()
                    parameters["folder"] = self._normalize_directory_name(folder_name)
            
            elif action == IntentAction.CREATE_FOLDER:
                if groups[0]:
                    parameters["folder_name"] = groups[0].strip()
            
            elif action == IntentAction.OPEN_URL:
                if groups[0]:
                    url = groups[0].strip()
                    # Add protocol if missing
                    if not url.startswith(('http://', 'https://')):
                        url = 'https://' + url
                    parameters["url"] = url
            
            elif action == IntentAction.BROWSER_SEARCH:
                if groups[0]:
                    parameters["query"] = groups[0].strip()
        
        return parameters
    
    def _normalize_application_name(self, name: str) -> str:
        """
        Normalize application name to match known aliases.
        
        Args:
            name: Application name from user input
            
        Returns:
            Normalized application name
        """
        name_lower = name.lower().strip()
        
        # Check aliases
        for app_id, aliases in self.application_aliases.items():
            if name_lower in aliases:
                return app_id
        
        # Return original if no match found
        return name_lower
    
    def _normalize_directory_name(self, name: str) -> str:
        """
        Normalize directory name to match known aliases.
        
        Args:
            name: Directory name from user input
            
        Returns:
            Normalized directory name
        """
        name_lower = name.lower().strip()
        
        # Check aliases
        for dir_id, aliases in self.directory_aliases.items():
            if name_lower in aliases:
                return dir_id
        
        # Return original if no match found
        return name_lower
    
    def _calculate_confidence(self, match, pattern: str, text: str) -> float:
        """
        Calculate confidence score for the match.
        
        Args:
            match: Regex match object
            pattern: Pattern that matched
            text: Original text
            
        Returns:
            Confidence score (0.0 to 1.0)
        """
        base_confidence = 0.8
        
        # Increase confidence for exact matches
        if match.group() == text:
            base_confidence += 0.15
        
        # Increase confidence for patterns with specific parameters
        if match.groups() and any(match.groups()):
            base_confidence += 0.05
        
        # Cap at 1.0
        return min(base_confidence, 1.0)
    
    def parse_batch(self, texts: List[str]) -> List[Intent]:
        """
        Parse multiple texts in batch.
        
        Args:
            texts: List of user input texts
            
        Returns:
            List of parsed intents
        """
        return [self.parse(text) for text in texts]
    
    def get_supported_actions(self) -> List[Dict[str, str]]:
        """
        Get list of supported actions.
        
        Returns:
            List of action information dictionaries
        """
        actions = []
        for category in IntentCategory:
            for action in IntentAction:
                # Filter actions by category (simplified logic)
                if category.name.lower() in action.value.lower() or action == IntentAction.UNKNOWN_ACTION:
                    actions.append({
                        "category": category.value,
                        "action": action.value,
                        "description": self._get_action_description(action)
                    })
        return actions
    
    def _get_action_description(self, action: IntentAction) -> str:
        """Get human-readable description for an action."""
        descriptions = {
            IntentAction.OPEN_APPLICATION: "Open an application",
            IntentAction.CLOSE_APPLICATION: "Close an application",
            IntentAction.MINIMIZE_WINDOW: "Minimize a window",
            IntentAction.MAXIMIZE_WINDOW: "Maximize a window",
            IntentAction.RESTORE_WINDOW: "Restore a window",
            IntentAction.VOLUME_UP: "Increase volume",
            IntentAction.VOLUME_DOWN: "Decrease volume",
            IntentAction.SET_VOLUME: "Set volume to specific level",
            IntentAction.MUTE: "Mute audio",
            IntentAction.UNMUTE: "Unmute audio",
            IntentAction.TAKE_SCREENSHOT: "Take a screenshot",
            IntentAction.LOCK_COMPUTER: "Lock the computer",
            IntentAction.RESTART_COMPUTER: "Restart the computer",
            IntentAction.SHUTDOWN_COMPUTER: "Shutdown the computer",
            IntentAction.OPEN_FOLDER: "Open a folder",
            IntentAction.CREATE_FOLDER: "Create a new folder",
            IntentAction.OPEN_URL: "Open a URL in browser",
            IntentAction.BROWSER_SEARCH: "Search the web",
            IntentAction.GET_TIME: "Get current time",
            IntentAction.GET_WEATHER: "Get weather information",
            IntentAction.GET_SYSTEM_INFO: "Get system information",
            IntentAction.UNKNOWN_ACTION: "Unknown action",
        }
        return descriptions.get(action, "No description available")
