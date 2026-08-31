"""
ELARA - Main Application
This module contains the main ElaraApp class that coordinates all components.
"""

import sys
import signal
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer, QObject

from app.config.settings import get_settings
from app.config.constants import AssistantState, VERSION
from app.utils.logger import setup_logging, get_logger
from app.utils.paths import ensure_directory
from app.memory.database import initialize_database
from app.core.lifecycle import LifecycleManager
from app.core.state import StateManager
from app.core.event_bus import EventBus
from app.ui import MainWindow, PYSIDE6_AVAILABLE, AssistantStatus


class ElaraApp(QObject):
    """Main ELARA application class."""
    
    def __init__(self):
        super().__init__()
        self.logger = None
        self.settings = None
        self.qt_app = None
        self.state_manager = None
        self.event_bus = None
        self.lifecycle_manager = None
        self._is_running = False
        
        # Initialize the application
        self._initialize()
    
    def _initialize(self):
        """Initialize all application components."""
        try:
            # Setup logging first
            self._setup_logging()
            
            self.logger.info(f"ELARA v{VERSION} starting initialization")
            
            # Load settings
            self._load_settings()
            
            # Setup directories
            self._setup_directories()
            
            # Initialize database
            self._initialize_database()
            
            # Initialize core components
            self._initialize_core()
            
            # Setup signal handlers
            self._setup_signal_handlers()
            
            self.logger.info("ELARA initialization completed successfully")
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to initialize ELARA: {e}")
            else:
                print(f"Failed to initialize ELARA: {e}")
            raise
    
    def _setup_logging(self):
        """Setup the logging system."""
        settings = get_settings()
        setup_logging(
            log_dir=settings.logging.log_dir,
            log_level=settings.logging.level
        )
        self.logger = get_logger("elara")
        self.logger.info("Logging system initialized")
    
    def _load_settings(self):
        """Load application settings."""
        self.settings = get_settings()
        self.logger.info("Settings loaded successfully")
    
    def _setup_directories(self):
        """Setup required directories."""
        directories = [
            self.settings.logging.log_dir,
            self.settings.database.path.parent,
            self.settings.security.workspace,
            Path("models"),
            Path("data")
        ]
        
        for directory in directories:
            ensure_directory(directory)
        
        self.logger.info("Required directories created/verified")
    
    def _initialize_database(self):
        """Initialize the database."""
        initialize_database()
        self.logger.info("Database initialized")
    
    def _initialize_core(self):
        """Initialize core components."""
        # Initialize event bus
        self.event_bus = EventBus()
        self.logger.info("Event bus initialized")
        
        # Initialize state manager
        self.state_manager = StateManager(self.event_bus)
        self.logger.info("State manager initialized")
        
        # Initialize lifecycle manager
        self.lifecycle_manager = LifecycleManager(
            self.event_bus,
            self.state_manager
        )
        self.logger.info("Lifecycle manager initialized")
        
        # Store references to audio components from lifecycle
        self._setup_audio_components()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_audio_components(self):
        """Setup audio components references from lifecycle manager."""
        # These will be initialized during lifecycle startup
        self.microphone = None
        self.vad = None
        self.stt = None
        self.tts = None
        self.audio_processor = None
        
        # Authentication components
        self.wake_word_detector = None
        self.voice_enrollment = None
        self.speaker_verifier = None
        self.voice_profile_manager = None
        
        # Action components
        self.action_registry = None
        self.permission_engine = None
        self.security_policy = None
        self.confirmation_engine = None
        self.action_executor = None
        
        # Windows automation components
        self.application_manager = None
        self.window_manager = None
        self.volume_controller = None
        self.screenshot_capture = None
        self.system_operations = None
        
        # AI components
        self.ai_manager = None
        self.intent_parser = None
        self.llm_manager = None
        self.action_generator = None
        self.response_generator = None
        
        # UI components
        self.main_window = None
        
        # Voice loop component
        self.voice_loop = None
    
    def _get_audio_components(self):
        """Get audio component references from lifecycle manager."""
        self.microphone = self.lifecycle_manager.microphone
        self.vad = self.lifecycle_manager.vad
        self.stt = self.lifecycle_manager.stt
        self.tts = self.lifecycle_manager.tts
        self.audio_processor = self.lifecycle_manager.audio_processor
        
        # Get authentication components
        self.wake_word_detector = self.lifecycle_manager.wake_word_detector
        self.voice_enrollment = self.lifecycle_manager.voice_enrollment
        self.speaker_verifier = self.lifecycle_manager.speaker_verifier
        self.voice_profile_manager = self.lifecycle_manager.voice_profile_manager
        
        # Get action components
        self.action_registry = self.lifecycle_manager.action_registry
        self.permission_engine = self.lifecycle_manager.permission_engine
        self.security_policy = self.lifecycle_manager.security_policy
        self.confirmation_engine = self.lifecycle_manager.confirmation_engine
        self.action_executor = self.lifecycle_manager.action_executor
        
        # Get Windows automation components
        self.application_manager = self.lifecycle_manager.application_manager
        self.window_manager = self.lifecycle_manager.window_manager
        self.volume_controller = self.lifecycle_manager.volume_controller
        self.screenshot_capture = self.lifecycle_manager.screenshot_capture
        self.system_operations = self.lifecycle_manager.system_operations
        
        # Get AI components
        self.ai_manager = self.lifecycle_manager.ai_manager
        self.intent_parser = self.lifecycle_manager.intent_parser
        self.llm_manager = self.lifecycle_manager.llm_manager
        self.action_generator = self.lifecycle_manager.action_generator
        self.response_generator = self.lifecycle_manager.response_generator
        
        # Get voice loop component
        self.voice_loop = self.lifecycle_manager.voice_loop
        
        if self.microphone is None:
            self.logger.warning("Microphone not available (PortAudio may not be installed)")
        
        self.logger.info("Audio, authentication, action, Windows automation, AI, and voice loop components references obtained")
    
    def _connect_ui_signals(self):
        """Connect UI signals to AI system."""
        if not self.main_window or not self.ai_manager:
            return
        
        # Connect command signals
        self.main_window.command_received.connect(self._on_ui_command)
        self.main_window.status_changed.connect(self._on_status_changed)
        
        # Connect voice loop to UI
        if self.voice_loop:
            self.voice_loop.set_command_callback(self._on_voice_command)
            self.main_window.toggle_listening.connect(self._on_toggle_listening)
        
        self.logger.info("UI signals connected to AI system")
    
    def _on_toggle_listening(self, start: bool):
        """Handle toggle listening from UI."""
        if not self.voice_loop:
            return
        
        if start:
            self.voice_loop.start_listening()
            self.logger.info("Voice listening started from UI")
        else:
            self.voice_loop.stop_listening()
            self.logger.info("Voice listening stopped from UI")
    
    def _on_ui_command(self, command: str):
        """Handle command from UI."""
        try:
            self.logger.info(f"UI command received: {command}")
            
            # Set processing status
            self.main_window.set_status(AssistantStatus.PROCESSING)
            self.main_window.update_last_action("Processing...")
            
            # Process through AI manager
            from app.ai import AIRequest
            request = AIRequest(user_input=command)
            response = self.ai_manager.process_request(request)
            
            # Update UI with response
            self.main_window.add_response(response.response_text)
            
            if response.generated_action:
                self.main_window.update_last_action(response.generated_action.action_name)
            
            # Update action result
            if response.action_result:
                success = response.action_result.get("success", False)
                if not success:
                    error = response.action_result.get("error", "Unknown error")
                    self.main_window.show_error(error)
            
            # Speak response (optional for UI commands)
            if self.voice_loop and response.response_text:
                try:
                    self.voice_loop.speak(response.response_text)
                except Exception as e:
                    self.logger.error(f"Error speaking response: {e}")
            
            # Reset status
            self.main_window.set_status(AssistantStatus.IDLE)
            
        except Exception as e:
            self.logger.error(f"Error processing UI command: {e}")
            self.main_window.show_error(str(e))
            self.main_window.set_status(AssistantStatus.ERROR)
    
    def _on_status_changed(self, status: str):
        """Handle status change from UI."""
        self.logger.info(f"Status changed: {status}")
        # Could trigger additional status handling here
    
    def _on_voice_command(self, command: str):
        """Handle command from voice loop."""
        try:
            self.logger.info(f"Voice command received: {command}")
            
            # Set processing status
            if self.main_window:
                self.main_window.set_status(AssistantStatus.PROCESSING)
                self.main_window.update_last_action("Processing...")
            
            # Process through AI manager
            from app.ai import AIRequest
            request = AIRequest(user_input=command)
            response = self.ai_manager.process_request(request)
            
            # Update UI with response
            if self.main_window:
                self.main_window.add_response(response.response_text)
            
            if response.generated_action:
                if self.main_window:
                    self.main_window.update_last_action(response.generated_action.action_name)
            
            # Update action result
            if response.action_result:
                success = response.action_result.get("success", False)
                if not success:
                    error = response.action_result.get("error", "Unknown error")
                    if self.main_window:
                        self.main_window.show_error(error)
            
            # Speak response (for voice commands)
            if self.voice_loop and response.response_text:
                # Update UI to show speaking status
                if self.main_window:
                    self.main_window.set_status(AssistantStatus.SPEAKING)
                
                try:
                    self.voice_loop.speak(response.response_text)
                finally:
                    # Reset status after speaking
                    if self.main_window:
                        self.main_window.set_status(AssistantStatus.IDLE)
            
            # Speak response
            if self.voice_loop and response.response_text:
                # Update UI to show speaking status
                if self.main_window:
                    self.main_window.set_status(AssistantStatus.SPEAKING)
                
                try:
                    self.voice_loop.speak(response.response_text)
                finally:
                    # Reset status after speaking
                    if self.main_window:
                        self.main_window.set_status(AssistantStatus.IDLE)
            
        except Exception as e:
            self.logger.error(f"Error processing voice command: {e}")
            if self.main_window:
                self.main_window.show_error(str(e))
                self.main_window.set_status(AssistantStatus.ERROR)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}, initiating shutdown")
        self.shutdown()
    
    def run(self):
        """Run the ELARA application."""
        try:
            self.logger.info("Starting ELARA application")
            self._is_running = True
            
            # Create Qt application
            self.qt_app = QApplication(sys.argv)
            self.qt_app.setApplicationName("ELARA")
            self.qt_app.setApplicationVersion(VERSION)
            self.qt_app.setOrganizationName("ELARA")
            
            # Initialize lifecycle
            self.lifecycle_manager.initialize()
            
            # Get audio component references
            self._get_audio_components()
            
            # Create and setup main window
            if PYSIDE6_AVAILABLE:
                self.main_window = MainWindow()
                self._connect_ui_signals()
                self.main_window.show()
                self.logger.info("Main window displayed")
            else:
                self.logger.warning("PySide6 not available, running in headless mode")
            
            # Start the application
            self.logger.info("ELARA application started")
            
            # Run Qt event loop
            result = self.qt_app.exec()
            
            self.logger.info(f"ELARA application exited with code {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error running ELARA: {e}")
            raise
    
    def shutdown(self):
        """Shutdown the ELARA application gracefully."""
        if not self._is_running:
            return
        
        self.logger.info("Initiating ELARA shutdown")
        self._is_running = False
        
        try:
            # Shutdown lifecycle manager
            if self.lifecycle_manager:
                self.lifecycle_manager.shutdown()
            
            # Close database connections
            from app.memory.database import get_database_manager
            db_manager = get_database_manager()
            db_manager.close()
            
            # Quit Qt application
            if self.qt_app:
                self.qt_app.quit()
            
            self.logger.info("ELARA shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
    
    def get_state(self) -> AssistantState:
        """Get the current assistant state."""
        if self.state_manager:
            return self.state_manager.get_state()
        return AssistantState.IDLE
    
    def set_state(self, state: AssistantState):
        """Set the assistant state."""
        if self.state_manager:
            self.state_manager.set_state(state)


def main():
    """Main entry point."""
    try:
        app = ElaraApp()
        return app.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
