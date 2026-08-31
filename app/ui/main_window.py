"""
ELARA - Main Window
This module provides the main PySide6 GUI window for ELARA.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum

try:
    from PySide6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLabel, QPushButton, QTextEdit, QStatusBar,
        QProgressBar, QGroupBox, QScrollArea, QFrame,
        QSizePolicy, QSplitter
    )
    from PySide6.QtCore import Qt, QTimer, Signal, Slot
    from PySide6.QtGui import QFont, QColor, QPalette
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

from app.config.settings import get_settings
from app.config.constants import AssistantState
from app.utils.logger import get_logger


class AssistantStatus(Enum):
    """Assistant status for UI display."""
    IDLE = "Idle"
    LISTENING = "Listening..."
    PROCESSING = "Processing..."
    SPEAKING = "Speaking..."
    ERROR = "Error"


class MainWindow(QMainWindow):
    """Main ELARA application window."""
    
    # Signals for communication
    command_received = Signal(str)
    status_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger("elara.ui.main_window")
        self.settings = get_settings()
        
        self.current_status = AssistantStatus.IDLE
        self.conversation_history = []
        
        if not PYSIDE6_AVAILABLE:
            self.logger.error("PySide6 not available for GUI")
            return
        
        self._setup_ui()
        self._setup_styling()
        self._setup_timers()
        
        self.logger.info("Main window initialized")
    
    def _setup_ui(self):
        """Setup the user interface."""
        self.setWindowTitle("ELARA - Personal AI Voice Assistant")
        self.setMinimumSize(1000, 700)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header section
        header_layout = self._create_header()
        main_layout.addLayout(header_layout)
        
        # Main content area with splitter
        content_splitter = QSplitter(Qt.Vertical)
        
        # Status and visualization area
        status_area = self._create_status_area()
        content_splitter.addWidget(status_area)
        
        # Conversation area
        conversation_area = self._create_conversation_area()
        content_splitter.addWidget(conversation_area)
        
        content_splitter.setStretchFactor(0, 1)
        content_splitter.setStretchFactor(1, 3)
        main_layout.addWidget(content_splitter)
        
        # Control buttons
        control_layout = self._create_controls()
        main_layout.addLayout(control_layout)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("ELARA initialized and ready")
    
    def _create_header(self) -> QHBoxLayout:
        """Create header section."""
        layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("ELARA")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setStyleSheet("color: #00ff00;")
        layout.addWidget(title_label)
        
        layout.addStretch()
        
        # Status indicator
        self.status_indicator = QLabel("●")
        self.status_indicator.setFont(QFont("Arial", 16))
        self.status_indicator.setStyleSheet("color: #00ff00;")
        layout.addWidget(self.status_indicator)
        
        self.status_text = QLabel("Ready")
        layout.addWidget(self.status_text)
        
        return layout
    
    def _create_status_area(self) -> QGroupBox:
        """Create status visualization area."""
        group = QGroupBox("Status")
        layout = QVBoxLayout()
        
        # Assistant state
        state_layout = QHBoxLayout()
        state_layout.addWidget(QLabel("State:"))
        self.state_label = QLabel("Idle")
        self.state_label.setStyleSheet("font-weight: bold; color: #00ff00;")
        state_layout.addWidget(self.state_label)
        state_layout.addStretch()
        layout.addLayout(state_layout)
        
        # Voice indicator
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("Voice:"))
        self.voice_indicator = QLabel("○")
        self.voice_indicator.setFont(QFont("Arial", 14))
        self.voice_indicator.setStyleSheet("color: #888888;")
        voice_layout.addWidget(self.voice_indicator)
        voice_layout.addStretch()
        layout.addLayout(voice_layout)
        
        # Volume level
        volume_layout = QHBoxLayout()
        volume_layout.addWidget(QLabel("Volume:"))
        self.volume_bar = QProgressBar()
        self.volume_bar.setRange(0, 100)
        self.volume_bar.setValue(50)
        self.volume_bar.setFixedWidth(200)
        volume_layout.addWidget(self.volume_bar)
        volume_layout.addStretch()
        layout.addLayout(volume_layout)
        
        # Last action
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("Last Action:"))
        self.last_action_label = QLabel("None")
        self.last_action_label.setStyleSheet("color: #888888;")
        action_layout.addWidget(self.last_action_label)
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        group.setLayout(layout)
        return group
    
    def _create_conversation_area(self) -> QGroupBox:
        """Create conversation display area."""
        group = QGroupBox("Conversation")
        layout = QVBoxLayout()
        
        # Conversation history
        self.conversation_display = QTextEdit()
        self.conversation_display.setReadOnly(True)
        self.conversation_display.setPlaceholderText("Your conversation with ELARA will appear here...")
        layout.addWidget(self.conversation_display)
        
        # Input field
        input_layout = QHBoxLayout()
        self.command_input = QTextEdit()
        self.command_input.setMaximumHeight(60)
        self.command_input.setPlaceholderText("Type a command or press the microphone button...")
        input_layout.addWidget(self.command_input)
        
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._on_send_command)
        input_layout.addWidget(self.send_button)
        
        layout.addLayout(input_layout)
        group.setLayout(layout)
        return group
    
    def _create_controls(self) -> QHBoxLayout:
        """Create control buttons."""
        layout = QHBoxLayout()
        
        # Microphone button
        self.mic_button = QPushButton("🎤 Start Listening")
        self.mic_button.setCheckable(True)
        self.mic_button.clicked.connect(self._on_mic_button_clicked)
        layout.addWidget(self.mic_button)
        
        layout.addStretch()
        
        # Mute button
        self.mute_button = QPushButton("🔊 Mute")
        self.mute_button.setCheckable(True)
        self.mute_button.clicked.connect(self._on_mute_button_clicked)
        layout.addWidget(self.mute_button)
        
        # Screenshot button
        self.screenshot_button = QPushButton("📷 Screenshot")
        self.screenshot_button.clicked.connect(self._on_screenshot_clicked)
        layout.addWidget(self.screenshot_button)
        
        # Settings button
        self.settings_button = QPushButton("⚙ Settings")
        self.settings_button.clicked.connect(self._on_settings_clicked)
        layout.addWidget(self.settings_button)
        
        # Quit button
        self.quit_button = QPushButton("✕ Quit")
        self.quit_button.clicked.connect(self.close)
        layout.addWidget(self.quit_button)
        
        return layout
    
    def _setup_styling(self):
        """Setup window styling."""
        # Dark theme
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.Base, QColor(40, 40, 40))
        palette.setColor(QPalette.AlternateBase, QColor(50, 50, 50))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        palette.setColor(QPalette.Button, QColor(60, 60, 60))
        palette.setColor(QPalette.ButtonText, QColor(220, 220, 220))
        palette.setColor(QPalette.BrightText, QColor(255, 255, 255))
        palette.setColor(QPalette.Highlight, QColor(0, 120, 215))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
        # Group box styling
        self.setStyleSheet("""
            QGroupBox {
                border: 1px solid #444;
                border-radius: 5px;
                margin-top: 10px;
                font-weight: bold;
                color: #00ff00;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
            QPushButton {
                background-color: #444;
                color: #fff;
                border: 1px solid #555;
                border-radius: 3px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #555;
            }
            QPushButton:checked {
                background-color: #00aa00;
                border-color: #00ff00;
            }
            QTextEdit {
                background-color: #333;
                color: #ddd;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 5px;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00ff00;
            }
        """)
    
    def _setup_timers(self):
        """Setup update timers."""
        # Status update timer
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self._update_status_display)
        self.status_timer.start(1000)  # Update every second
    
    def _update_status_display(self):
        """Update status display."""
        # Update time
        current_time = datetime.now().strftime("%H:%M:%S")
        self.status_bar.showMessage(f"ELARA - {current_time} - {self.current_status.value}")
    
    def _on_send_command(self):
        """Handle send button click."""
        command = self.command_input.toPlainText().strip()
        if command:
            self.command_input.clear()
            self.command_received.emit(command)
            self._add_conversation_entry("You", command)
    
    def _on_mic_button_clicked(self):
        """Handle microphone button click."""
        if self.mic_button.isChecked():
            self.mic_button.setText("🎤 Stop Listening")
            self.voice_indicator.setText("●")
            self.voice_indicator.setStyleSheet("color: #00ff00;")
            self.set_status(AssistantStatus.LISTENING)
        else:
            self.mic_button.setText("🎤 Start Listening")
            self.voice_indicator.setText("○")
            self.voice_indicator.setStyleSheet("color: #888888;")
            self.set_status(AssistantStatus.IDLE)
    
    def _on_mute_button_clicked(self):
        """Handle mute button click."""
        if self.mute_button.isChecked():
            self.mute_button.setText("🔇 Unmute")
            self.volume_bar.setValue(0)
        else:
            self.mute_button.setText("🔊 Mute")
            self.volume_bar.setValue(50)
    
    def _on_screenshot_clicked(self):
        """Handle screenshot button click."""
        self.command_received.emit("take screenshot")
        self._add_conversation_entry("You", "take screenshot")
    
    def _on_settings_clicked(self):
        """Handle settings button click."""
        self._add_conversation_entry("System", "Settings panel not yet implemented")
    
    def set_status(self, status: AssistantStatus):
        """Set the current status."""
        self.current_status = status
        self.status_text.setText(status.value)
        
        # Update color based on status
        if status == AssistantStatus.IDLE:
            self.status_indicator.setStyleSheet("color: #00ff00;")
            self.state_label.setStyleSheet("font-weight: bold; color: #00ff00;")
        elif status == AssistantStatus.LISTENING:
            self.status_indicator.setStyleSheet("color: #ffff00;")
            self.state_label.setStyleSheet("font-weight: bold; color: #ffff00;")
        elif status == AssistantStatus.PROCESSING:
            self.status_indicator.setStyleSheet("color: #00ffff;")
            self.state_label.setStyleSheet("font-weight: bold; color: #00ffff;")
        elif status == AssistantStatus.SPEAKING:
            self.status_indicator.setStyleSheet("color: #ff00ff;")
            self.state_label.setStyleSheet("font-weight: bold; color: #ff00ff;")
        elif status == AssistantStatus.ERROR:
            self.status_indicator.setStyleSheet("color: #ff0000;")
            self.state_label.setStyleSheet("font-weight: bold; color: #ff0000;")
        
        self.status_changed.emit(status.value)
    
    def _add_conversation_entry(self, speaker: str, text: str):
        """Add an entry to the conversation display."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if speaker == "You":
            entry = f"[{timestamp}] You: {text}\n"
            color = "#00aaff"
        else:
            entry = f"[{timestamp}] ELARA: {text}\n"
            color = "#00ff00"
        
        # Store in history
        self.conversation_history.append({"speaker": speaker, "text": text, "timestamp": timestamp})
        
        # Add to display with color
        cursor = self.conversation_display.textCursor()
        self.conversation_display.moveCursor(cursor.End)
        self.conversation_display.insertHtml(f'<span style="color: {color};">{entry}</span>')
        self.conversation_display.moveCursor(cursor.End)
        self.conversation_display.ensureCursorVisible()
    
    def add_response(self, response: str):
        """Add ELARA's response to the conversation."""
        self._add_conversation_entry("ELARA", response)
        self.set_status(AssistantStatus.IDLE)
    
    def update_last_action(self, action: str):
        """Update the last action display."""
        self.last_action_label.setText(action)
        self.last_action_label.setStyleSheet("color: #00ff00;")
    
    def show_error(self, error: str):
        """Show an error message."""
        self._add_conversation_entry("System", f"Error: {error}")
        self.set_status(AssistantStatus.ERROR)
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Main window closing")
        super().closeEvent(event)
