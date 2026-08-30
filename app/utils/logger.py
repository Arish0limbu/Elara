"""
ELARA - Logging System
This module provides a centralized logging system with rotating log files.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

from app.config.settings import get_settings
from app.config.constants import PROJECT_ROOT


class ElaraLogger:
    """Centralized logger for ELARA application with rotating log files."""

    _loggers: dict = {}
    _initialized: bool = False

    @classmethod
    def setup_logging(cls, log_dir: Optional[Path] = None, log_level: Optional[str] = None):
        """Setup the logging system with rotating file handlers."""
        if cls._initialized:
            return

        settings = get_settings()
        
        if log_dir is None:
            log_dir = settings.logging.log_dir
        if log_level is None:
            log_level = settings.logging.level

        # Ensure log directory exists
        log_dir = Path(log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create formatters
        detailed_formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        simple_formatter = logging.Formatter(
            fmt='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Setup main application logger
        main_logger = cls.get_logger("elara")
        main_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        main_logger.addHandler(console_handler)

        # File handler for all logs
        all_logs_file = log_dir / "elara.log"
        file_handler = logging.handlers.RotatingFileHandler(
            all_logs_file,
            maxBytes=settings.logging.max_bytes,
            backupCount=settings.logging.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        main_logger.addHandler(file_handler)

        # Separate file for errors
        error_logs_file = log_dir / "errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_logs_file,
            maxBytes=settings.logging.max_bytes,
            backupCount=settings.logging.backup_count,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)
        main_logger.addHandler(error_handler)

        # Separate file for security events
        security_logs_file = log_dir / "security.log"
        security_handler = logging.handlers.RotatingFileHandler(
            security_logs_file,
            maxBytes=settings.logging.max_bytes,
            backupCount=settings.logging.backup_count,
            encoding='utf-8'
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(detailed_formatter)
        
        security_logger = cls.get_logger("elara.security")
        security_logger.setLevel(logging.WARNING)
        security_logger.addHandler(security_handler)

        cls._initialized = True
        main_logger.info("ELARA logging system initialized")

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a logger with the specified name."""
        if name not in cls._loggers:
            logger = logging.getLogger(name)
            cls._loggers[name] = logger
            
            # If main logger is initialized, set up this logger similarly
            if cls._initialized and name != "elara":
                settings = get_settings()
                logger.setLevel(getattr(logging, settings.logging.level.upper(), logging.INFO))
                
                # Add console handler if not already present
                if not logger.handlers:
                    console_handler = logging.StreamHandler(sys.stdout)
                    console_handler.setLevel(logging.INFO)
                    console_handler.setFormatter(logging.Formatter(
                        fmt='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S'
                    ))
                    logger.addHandler(console_handler)

        return cls._loggers[name]

    @classmethod
    def log_command(cls, command: str, result: str, user_id: Optional[str] = None):
        """Log a command execution for audit purposes."""
        logger = cls.get_logger("elara.commands")
        if not logger.handlers:
            settings = get_settings()
            log_dir = settings.logging.log_dir
            log_dir.mkdir(parents=True, exist_ok=True)
            
            command_file = log_dir / "commands.log"
            handler = logging.handlers.RotatingFileHandler(
                command_file,
                maxBytes=settings.logging.max_bytes,
                backupCount=settings.logging.backup_count,
                encoding='utf-8'
            )
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter(
                fmt='%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        user_info = f"[{user_id}] " if user_id else ""
        logger.info(f"{user_info}Command: {command} | Result: {result}")

    @classmethod
    def log_security_event(cls, event_type: str, details: str, severity: str = "WARNING"):
        """Log a security-related event."""
        logger = cls.get_logger("elara.security")
        log_method = getattr(logger, severity.lower(), logger.warning)
        log_method(f"SECURITY: {event_type} - {details}")

    @classmethod
    def log_voice_event(cls, event: str, success: bool, details: str = ""):
        """Log voice-related events."""
        logger = cls.get_logger("elara.voice")
        if not logger.handlers:
            settings = get_settings()
            log_dir = settings.logging.log_dir
            log_dir.mkdir(parents=True, exist_ok=True)
            
            voice_file = log_dir / "voice.log"
            handler = logging.handlers.RotatingFileHandler(
                voice_file,
                maxBytes=settings.logging.max_bytes,
                backupCount=settings.logging.backup_count,
                encoding='utf-8'
            )
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter(
                fmt='%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        status = "SUCCESS" if success else "FAILED"
        logger.info(f"{event}: {status} {details}")

    @classmethod
    def log_ai_event(cls, event: str, model: str, tokens_used: Optional[int] = None, duration_ms: Optional[float] = None):
        """Log AI-related events."""
        logger = cls.get_logger("elara.ai")
        if not logger.handlers:
            settings = get_settings()
            log_dir = settings.logging.log_dir
            log_dir.mkdir(parents=True, exist_ok=True)
            
            ai_file = log_dir / "ai.log"
            handler = logging.handlers.RotatingFileHandler(
                ai_file,
                maxBytes=settings.logging.max_bytes,
                backupCount=settings.logging.backup_count,
                encoding='utf-8'
            )
            handler.setLevel(logging.INFO)
            handler.setFormatter(logging.Formatter(
                fmt='%(asctime)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)

        token_info = f" | Tokens: {tokens_used}" if tokens_used else ""
        duration_info = f" | Duration: {duration_ms:.2f}ms" if duration_ms else ""
        logger.info(f"{event} | Model: {model}{token_info}{duration_info}")


def get_logger(name: str) -> logging.Logger:
    """Convenience function to get a logger."""
    return ElaraLogger.get_logger(name)


def setup_logging(log_dir: Optional[Path] = None, log_level: Optional[str] = None):
    """Convenience function to setup logging."""
    ElaraLogger.setup_logging(log_dir, log_level)
