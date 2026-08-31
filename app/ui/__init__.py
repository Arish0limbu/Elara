"""
ELARA - UI Module
This module provides the PySide6 graphical user interface.
"""

try:
    from app.ui.main_window import MainWindow, AssistantStatus
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False
    MainWindow = None
    AssistantStatus = None

__all__ = [
    'MainWindow',
    'AssistantStatus',
    'PYSIDE6_AVAILABLE'
]
