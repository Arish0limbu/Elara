"""
ELARA - Windows Module
This module handles Windows-specific operations including application control, window management, volume control, screenshots, and system operations.
"""

from .applications import ApplicationManager, ApplicationLauncher
from .windows import WindowManager
from .volume import VolumeController, SimpleVolumeController
from .screenshots import ScreenshotCapture
from .system import SystemOperations

__all__ = [
    "ApplicationManager",
    "ApplicationLauncher",
    "WindowManager",
    "VolumeController",
    "SimpleVolumeController",
    "ScreenshotCapture",
    "SystemOperations"
]
