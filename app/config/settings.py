"""
ELARA - Configuration Settings
This module handles application configuration management, environment variables,
and user settings loading.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from dotenv import load_dotenv

from app.config.constants import (
    PROJECT_ROOT,
    DEFAULT_WAKE_WORD,
    DEFAULT_VOICE_THRESHOLD,
    DEFAULT_STT_MODEL,
    DEFAULT_STT_LANGUAGE,
    STT_DEVICE,
    DEFAULT_TTS_MODEL,
    DEFAULT_TTS_SPEED,
    DEFAULT_AI_PROVIDER,
    DEFAULT_AI_MODEL,
    AI_MAX_TOKENS,
    AI_TEMPERATURE,
    DEFAULT_WORKSPACE,
    DEFAULT_LOG_LEVEL,
    DATABASE_PATH,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_CHANNELS,
    DEFAULT_CHUNK_SIZE,
    WAKE_WORD_TIMEOUT,
    COMMAND_TIMEOUT
)


@dataclass
class AudioSettings:
    """Audio configuration settings."""
    sample_rate: int = DEFAULT_SAMPLE_RATE
    channels: int = DEFAULT_CHANNELS
    chunk_size: int = DEFAULT_CHUNK_SIZE
    input_device: Optional[str] = None
    output_device: Optional[str] = None


@dataclass
class WakeWordSettings:
    """Wake word detection settings."""
    wake_word: str = DEFAULT_WAKE_WORD
    timeout: float = WAKE_WORD_TIMEOUT
    sensitivity: float = 0.5


@dataclass
class VoiceSettings:
    """Voice recognition and verification settings."""
    verification_threshold: float = DEFAULT_VOICE_THRESHOLD
    enrollment_phrases: int = 3
    enable_verification: bool = True


@dataclass
class SpeechToTextSettings:
    """Speech-to-text configuration settings."""
    model: str = DEFAULT_STT_MODEL
    language: str = DEFAULT_STT_LANGUAGE
    device: str = STT_DEVICE
    compute_type: str = "int8"


@dataclass
class TTSSettings:
    """Text-to-speech configuration settings."""
    model: str = DEFAULT_TTS_MODEL
    speed: float = DEFAULT_TTS_SPEED
    enable_tts: bool = True


@dataclass
class AISettings:
    """AI provider configuration settings."""
    provider: str = DEFAULT_AI_PROVIDER
    api_key: Optional[str] = None
    model: str = DEFAULT_AI_MODEL
    max_tokens: int = AI_MAX_TOKENS
    temperature: float = AI_TEMPERATURE
    base_url: Optional[str] = None
    conversation_style: str = "casual"
    max_history_length: int = 20
    enable_llm: bool = False
    use_rule_based_fallback: bool = True


@dataclass
class SecuritySettings:
    """Security and permission settings."""
    workspace: Path = field(default_factory=lambda: DEFAULT_WORKSPACE)
    enable_workspace_restriction: bool = True
    block_system_paths: bool = True
    require_confirmation_sensitive: bool = True
    require_confirmation_critical: bool = True
    log_commands: bool = True


@dataclass
class DatabaseSettings:
    """Database configuration settings."""
    path: Path = field(default_factory=lambda: DATABASE_PATH)
    echo: bool = False


@dataclass
class LoggingSettings:
    """Logging configuration settings."""
    level: str = DEFAULT_LOG_LEVEL
    log_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "logs")
    max_bytes: int = 10 * 1024 * 1024  # 10 MB
    backup_count: int = 5


@dataclass
class UISettings:
    """UI configuration settings."""
    theme: str = "dark"
    start_minimized: bool = False
    show_animations: bool = True
    window_width: int = 1200
    window_height: int = 800


@dataclass
class Settings:
    """Main application settings container."""
    audio: AudioSettings = field(default_factory=AudioSettings)
    wake_word: WakeWordSettings = field(default_factory=WakeWordSettings)
    voice: VoiceSettings = field(default_factory=VoiceSettings)
    stt: SpeechToTextSettings = field(default_factory=SpeechToTextSettings)
    tts: TTSSettings = field(default_factory=TTSSettings)
    ai: AISettings = field(default_factory=AISettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    logging: LoggingSettings = field(default_factory=LoggingSettings)
    ui: UISettings = field(default_factory=UISettings)

    @classmethod
    def load_from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        # Load .env file if it exists
        env_file = PROJECT_ROOT / ".env"
        if env_file.exists():
            load_dotenv(env_file)

        return cls(
            audio=AudioSettings(
                sample_rate=int(os.getenv("ELARA_SAMPLE_RATE", str(DEFAULT_SAMPLE_RATE))),
                channels=int(os.getenv("ELARA_CHANNELS", str(DEFAULT_CHANNELS))),
                chunk_size=int(os.getenv("ELARA_CHUNK_SIZE", str(DEFAULT_CHUNK_SIZE))),
                input_device=os.getenv("ELARA_INPUT_DEVICE"),
                output_device=os.getenv("ELARA_OUTPUT_DEVICE")
            ),
            wake_word=WakeWordSettings(
                wake_word=os.getenv("ELARA_WAKE_WORD", DEFAULT_WAKE_WORD),
                timeout=float(os.getenv("ELARA_WAKE_WORD_TIMEOUT", str(WAKE_WORD_TIMEOUT))),
                sensitivity=float(os.getenv("ELARA_WAKE_WORD_SENSITIVITY", "0.5"))
            ),
            voice=VoiceSettings(
                verification_threshold=float(os.getenv("ELARA_VOICE_THRESHOLD", str(DEFAULT_VOICE_THRESHOLD))),
                enrollment_phrases=int(os.getenv("ELARA_ENROLLMENT_PHRASES", "3")),
                enable_verification=os.getenv("ELARA_ENABLE_VERIFICATION", "true").lower() == "true"
            ),
            stt=SpeechToTextSettings(
                model=os.getenv("ELARA_STT_MODEL", DEFAULT_STT_MODEL),
                language=os.getenv("ELARA_STT_LANGUAGE", DEFAULT_STT_LANGUAGE),
                device=os.getenv("ELARA_STT_DEVICE", STT_DEVICE),
                compute_type=os.getenv("ELARA_STT_COMPUTE_TYPE", "int8")
            ),
            tts=TTSSettings(
                model=os.getenv("ELARA_TTS_MODEL", DEFAULT_TTS_MODEL),
                speed=float(os.getenv("ELARA_TTS_SPEED", str(DEFAULT_TTS_SPEED))),
                enable_tts=os.getenv("ELARA_ENABLE_TTS", "true").lower() == "true"
            ),
            ai=AISettings(
                provider=os.getenv("AI_PROVIDER", DEFAULT_AI_PROVIDER),
                api_key=os.getenv("AI_API_KEY"),
                model=os.getenv("AI_MODEL", DEFAULT_AI_MODEL),
                max_tokens=int(os.getenv("AI_MAX_TOKENS", str(AI_MAX_TOKENS))),
                temperature=float(os.getenv("AI_TEMPERATURE", str(AI_TEMPERATURE))),
                base_url=os.getenv("AI_BASE_URL"),
                conversation_style=os.getenv("AI_CONVERSATION_STYLE", "casual"),
                max_history_length=int(os.getenv("AI_MAX_HISTORY_LENGTH", "20")),
                enable_llm=os.getenv("AI_ENABLE_LLM", "false").lower() == "true",
                use_rule_based_fallback=os.getenv("AI_USE_RULE_BASED_FALLBACK", "true").lower() == "true"
            ),
            security=SecuritySettings(
                workspace=Path(os.getenv("ELARA_WORKSPACE", str(DEFAULT_WORKSPACE))),
                enable_workspace_restriction=os.getenv("ELARA_ENABLE_WORKSPACE_RESTRICTION", "true").lower() == "true",
                block_system_paths=os.getenv("ELARA_BLOCK_SYSTEM_PATHS", "true").lower() == "true",
                require_confirmation_sensitive=os.getenv("ELARA_REQUIRE_CONFIRMATION_SENSITIVE", "true").lower() == "true",
                require_confirmation_critical=os.getenv("ELARA_REQUIRE_CONFIRMATION_CRITICAL", "true").lower() == "true",
                log_commands=os.getenv("ELARA_LOG_COMMANDS", "true").lower() == "true"
            ),
            database=DatabaseSettings(
                path=Path(os.getenv("ELARA_DATABASE_PATH", str(DATABASE_PATH))),
                echo=os.getenv("ELARA_DATABASE_ECHO", "false").lower() == "true"
            ),
            logging=LoggingSettings(
                level=os.getenv("ELARA_LOG_LEVEL", DEFAULT_LOG_LEVEL),
                log_dir=Path(os.getenv("ELARA_LOG_DIR", str(PROJECT_ROOT / "logs"))),
                max_bytes=int(os.getenv("ELARA_LOG_MAX_BYTES", str(10 * 1024 * 1024))),
                backup_count=int(os.getenv("ELARA_LOG_BACKUP_COUNT", "5"))
            ),
            ui=UISettings(
                theme=os.getenv("ELARA_THEME", "dark"),
                start_minimized=os.getenv("ELARA_START_MINIMIZED", "false").lower() == "true",
                show_animations=os.getenv("ELARA_SHOW_ANIMATIONS", "true").lower() == "true",
                window_width=int(os.getenv("ELARA_WINDOW_WIDTH", "1200")),
                window_height=int(os.getenv("ELARA_WINDOW_HEIGHT", "800"))
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary for serialization."""
        return {
            "audio": self.audio.__dict__,
            "wake_word": self.wake_word.__dict__,
            "voice": self.voice.__dict__,
            "stt": self.stt.__dict__,
            "tts": self.tts.__dict__,
            "ai": {
                "provider": self.ai.provider,
                "model": self.ai.model,
                "max_tokens": self.ai.max_tokens,
                "temperature": self.ai.temperature,
                "base_url": self.ai.base_url
                # Note: api_key is intentionally excluded for security
            },
            "security": self.security.__dict__,
            "database": self.database.__dict__,
            "logging": self.logging.__dict__,
            "ui": self.ui.__dict__
        }


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get the global settings instance, loading from environment if not already loaded."""
    global _settings
    if _settings is None:
        _settings = Settings.load_from_env()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    global _settings
    _settings = Settings.load_from_env()
    return _settings
