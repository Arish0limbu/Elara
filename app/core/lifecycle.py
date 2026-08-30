"""
ELARA - Lifecycle Manager
This module manages the application lifecycle including startup and shutdown procedures.
"""

from typing import Optional
from threading import Thread, Event

from app.utils.logger import get_logger
from app.config.constants import AssistantState
from app.core.event_bus import EventBus, EventType
from app.core.state import StateManager


class LifecycleManager:
    """Manages the application lifecycle."""
    
    def __init__(self, event_bus: EventBus, state_manager: StateManager):
        self.logger = get_logger("elara.lifecycle")
        self.event_bus = event_bus
        self.state_manager = state_manager
        self._is_initialized = False
        self._is_running = False
        self._shutdown_event = Event()
        self._startup_thread: Optional[Thread] = None
        
        # Audio components (will be initialized during startup)
        self.microphone = None
        self.vad = None
        self.stt = None
        self.tts = None
        self.audio_processor = None
        
        # Authentication components (will be initialized during startup)
        self.wake_word_detector = None
        self.voice_enrollment = None
        self.speaker_verifier = None
        self.voice_profile_manager = None
        
        # Action components (will be initialized during startup)
        self.action_registry = None
        self.permission_engine = None
        self.security_policy = None
        self.confirmation_engine = None
        self.action_executor = None
        
        # Windows automation components (will be initialized during startup)
        self.application_manager = None
        self.window_manager = None
        self.volume_controller = None
        self.screenshot_capture = None
        self.system_operations = None
        
        # AI components (will be initialized during startup)
        self.ai_manager = None
        self.intent_parser = None
        self.llm_manager = None
        self.action_generator = None
        self.response_generator = None
    
    def initialize(self) -> None:
        """Initialize the application lifecycle."""
        if self._is_initialized:
            self.logger.warning("Lifecycle manager already initialized")
            return
        
        self.logger.info("Starting ELARA lifecycle initialization")
        
        try:
            # Set initial state
            self.state_manager.set_state(AssistantState.IDLE)
            
            # Perform startup sequence
            self._perform_startup_sequence()
            
            self._is_initialized = True
            self._is_running = True
            
            # Publish system ready event
            self.event_bus.publish(EventType.SYSTEM_READY, {
                "version": "0.1.0"
            })
            
            self.logger.info("ELARA lifecycle initialization completed")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize lifecycle: {e}")
            self.state_manager.set_state(AssistantState.ERROR)
            raise
    
    def _perform_startup_sequence(self) -> None:
        """Perform the startup sequence in the correct order."""
        self.logger.info("Starting startup sequence")
        
        # Phase 1: Core components
        self._startup_phase_core()
        
        # Phase 2: Audio components
        self._startup_phase_audio()
        
        # Phase 3: AI components
        self._startup_phase_ai()
        
        # Phase 4: Action components
        self._startup_phase_actions()
        
        # Phase 5: UI components
        self._startup_phase_ui()
        
        # Phase 6: Authentication components
        self._startup_phase_authentication()
        
        # Phase 7: Windows automation components
        self._startup_phase_windows_automation()
        
        # Phase 8: AI components
        self._startup_phase_ai_integration()
        
        self.logger.info("Startup sequence completed")
    
    def _startup_phase_core(self) -> None:
        """Initialize core components."""
        self.logger.info("Phase 1: Initializing core components")
        # Core components are already initialized in main.py
        pass
    
    def _startup_phase_audio(self) -> None:
        """Initialize audio components."""
        self.logger.info("Phase 2: Initializing audio components")
        
        try:
            from app.voice import VoiceActivityDetector, SpeechToText
            from app.tts import TextToSpeech
            from app.voice.audio import AudioProcessor
            
            # Initialize VAD (doesn't require audio hardware)
            self.vad = VoiceActivityDetector()
            self.logger.info("Voice Activity Detector initialized")
            
            # Initialize STT (doesn't require audio hardware)
            self.stt = SpeechToText()
            self.logger.info("Speech-to-Text initialized")
            
            # Initialize TTS (doesn't require audio hardware)
            self.tts = TextToSpeech()
            self.tts.load_model()
            self.logger.info("Text-to-Speech initialized")
            
            # Initialize audio processor (doesn't require audio hardware)
            self.audio_processor = AudioProcessor()
            self.logger.info("Audio processor initialized")
            
            # Try to initialize microphone (requires audio hardware)
            try:
                from app.voice import Microphone
                self.microphone = Microphone()
                self.logger.info("Microphone initialized")
            except Exception as mic_error:
                self.logger.warning(f"Microphone initialization failed (may require PortAudio): {mic_error}")
                self.microphone = None
            
        except Exception as e:
            self.logger.error(f"Failed to initialize audio components: {e}")
            raise
    
    def _startup_phase_ai(self) -> None:
        """Initialize AI components."""
        self.logger.info("Phase 3: Initializing AI components")
        # Will be fully initialized in Phase 8 after action components are ready
        pass
    
    def _startup_phase_actions(self) -> None:
        """Initialize action components."""
        self.logger.info("Phase 4: Initializing action components")
        
        try:
            from app.actions import ActionRegistry, PermissionEngine, SecurityPolicy, ConfirmationEngine, ActionExecutor
            
            # Initialize action registry
            self.action_registry = ActionRegistry()
            self.logger.info("Action registry initialized")
            
            # Initialize permission engine
            self.permission_engine = PermissionEngine()
            self.logger.info("Permission engine initialized")
            
            # Initialize security policy
            self.security_policy = SecurityPolicy()
            self.logger.info("Security policy initialized")
            
            # Initialize confirmation engine
            self.confirmation_engine = ConfirmationEngine()
            self.logger.info("Confirmation engine initialized")
            
            # Initialize action executor
            self.action_executor = ActionExecutor()
            self.logger.info("Action executor initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize action components: {e}")
            raise
    
    def _startup_phase_ui(self) -> None:
        """Initialize UI components."""
        self.logger.info("Phase 5: Initializing UI components")
        # TODO: Initialize UI components in Phase 5
        pass
    
    def _startup_phase_authentication(self) -> None:
        """Initialize authentication components."""
        self.logger.info("Phase 6: Initializing authentication components")
        
        try:
            from app.wakeword import WakeWordDetector
            from app.authentication import VoiceEnrollment, SpeakerVerifier, VoiceProfileManager
            
            # Initialize wake word detector
            self.wake_word_detector = WakeWordDetector()
            self.wake_word_detector.load_model()
            self.logger.info("Wake word detector initialized")
            
            # Initialize voice enrollment
            self.voice_enrollment = VoiceEnrollment()
            self.logger.info("Voice enrollment system initialized")
            
            # Initialize speaker verifier
            self.speaker_verifier = SpeakerVerifier()
            self.speaker_verifier.load_model()
            self.logger.info("Speaker verifier initialized")
            
            # Initialize voice profile manager
            self.voice_profile_manager = VoiceProfileManager()
            self.logger.info("Voice profile manager initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize authentication components: {e}")
            raise
    
    def _startup_phase_windows_automation(self) -> None:
        """Initialize Windows automation components."""
        self.logger.info("Phase 7: Initializing Windows automation components")
        
        try:
            from app.windows import ApplicationManager, WindowManager, VolumeController, ScreenshotCapture, SystemOperations
            
            # Initialize application manager
            self.application_manager = ApplicationManager()
            self.logger.info("Application manager initialized")
            
            # Initialize window manager
            self.window_manager = WindowManager()
            self.logger.info("Window manager initialized")
            
            # Initialize volume controller
            self.volume_controller = VolumeController()
            self.logger.info("Volume controller initialized")
            
            # Initialize screenshot capture
            self.screenshot_capture = ScreenshotCapture()
            self.logger.info("Screenshot capture initialized")
            
            # Initialize system operations
            self.system_operations = SystemOperations()
            self.logger.info("System operations initialized")
            
            # Register action handlers
            self._register_action_handlers()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize Windows automation components: {e}")
            raise
    
    def _register_action_handlers(self) -> None:
        """Register Windows automation handlers with action executor."""
        try:
            # Application handlers
            self.action_executor.register_handler("open_application", self._handle_open_application)
            self.action_executor.register_handler("close_application", self._handle_close_application)
            
            # Window handlers
            self.action_executor.register_handler("minimize_window", self._handle_minimize_window)
            self.action_executor.register_handler("maximize_window", self._handle_maximize_window)
            
            # Volume handlers
            self.action_executor.register_handler("volume_up", self._handle_volume_up)
            self.action_executor.register_handler("volume_down", self._handle_volume_down)
            self.action_executor.register_handler("mute", self._handle_mute)
            self.action_executor.register_handler("unmute", self._handle_unmute)
            
            # Screenshot handlers
            self.action_executor.register_handler("take_screenshot", self._handle_take_screenshot)
            
            # System handlers
            self.action_executor.register_handler("lock_computer", self._handle_lock_computer)
            self.action_executor.register_handler("restart_computer", self._handle_restart_computer)
            self.action_executor.register_handler("shutdown_computer", self._handle_shutdown_computer)
            
            # File handlers
            self.action_executor.register_handler("open_folder", self._handle_open_folder)
            
            # Browser handlers
            self.action_executor.register_handler("open_url", self._handle_open_url)
            self.action_executor.register_handler("browser_search", self._handle_browser_search)
            
            self.logger.info("Action handlers registered")
            
        except Exception as e:
            self.logger.error(f"Failed to register action handlers: {e}")
    
    def _startup_phase_ai_integration(self) -> None:
        """Initialize AI components and integrate with action system."""
        self.logger.info("Phase 8: Initializing AI components")
        
        try:
            from app.ai import AIManager, IntentParser, LLMProviderManager, ActionGenerator, ResponseGenerator
            
            # Initialize AI manager with action components
            self.ai_manager = AIManager(
                action_registry=self.action_registry,
                permission_engine=self.permission_engine,
                security_policy=self.security_policy,
                confirmation_engine=self.confirmation_engine,
                action_executor=self.action_executor
            )
            self.logger.info("AI manager initialized")
            
            # Initialize individual AI components for direct access
            self.intent_parser = self.ai_manager.intent_parser
            self.llm_manager = self.ai_manager.llm_manager
            self.action_generator = self.ai_manager.action_generator
            self.response_generator = self.ai_manager.response_generator
            
            self.logger.info("AI components integrated with action system")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize AI components: {e}")
            raise
    
    def _handle_open_application(self, application: str, args: Optional[list] = None) -> dict:
        """Handle open application action."""
        if self.application_manager:
            success = self.application_manager.launch_application(application, args)
            return {"launched": success}
        return {"launched": False}
    
    def _handle_close_application(self, application: str) -> dict:
        """Handle close application action."""
        if self.application_manager:
            success = self.application_manager.close_application(application)
            return {"closed": success}
        return {"closed": False}
    
    def _handle_minimize_window(self, window_title: Optional[str] = None) -> dict:
        """Handle minimize window action."""
        if self.window_manager and window_title:
            hwnd = self.window_manager.find_window_by_title(window_title)
            if hwnd:
                success = self.window_manager.minimize_window(hwnd)
                return {"minimized": success}
        return {"minimized": False}
    
    def _handle_maximize_window(self, window_title: Optional[str] = None) -> dict:
        """Handle maximize window action."""
        if self.window_manager and window_title:
            hwnd = self.window_manager.find_window_by_title(window_title)
            if hwnd:
                success = self.window_manager.maximize_window(hwnd)
                return {"maximized": success}
        return {"maximized": False}
    
    def _handle_volume_up(self, increment: float = 0.1) -> dict:
        """Handle volume up action."""
        if self.volume_controller:
            success = self.volume_controller.volume_up(increment)
            return {"volume_up": success}
        return {"volume_up": False}
    
    def _handle_volume_down(self, decrement: float = 0.1) -> dict:
        """Handle volume down action."""
        if self.volume_controller:
            success = self.volume_controller.volume_down(decrement)
            return {"volume_down": success}
        return {"volume_down": False}
    
    def _handle_mute(self) -> dict:
        """Handle mute action."""
        if self.volume_controller:
            success = self.volume_controller.mute()
            return {"muted": success}
        return {"muted": False}
    
    def _handle_unmute(self) -> dict:
        """Handle unmute action."""
        if self.volume_controller:
            success = self.volume_controller.unmute()
            return {"unmuted": success}
        return {"unmuted": False}
    
    def _handle_take_screenshot(self, save_path: Optional[str] = None) -> dict:
        """Handle screenshot action."""
        if self.screenshot_capture:
            screenshot = self.screenshot_capture.capture_screen()
            if screenshot:
                saved_path = self.screenshot_capture.save_screenshot(screenshot)
                return {"screenshot_taken": saved_path is not None, "path": str(saved_path) if saved_path else None}
        return {"screenshot_taken": False}
    
    def _handle_lock_computer(self) -> dict:
        """Handle lock computer action."""
        if self.system_operations:
            success = self.system_operations.lock_computer()
            return {"locked": success}
        return {"locked": False}
    
    def _handle_restart_computer(self, force: bool = False) -> dict:
        """Handle restart computer action."""
        if self.system_operations:
            success = self.system_operations.restart_computer(force)
            return {"restart_initiated": success}
        return {"restart_initiated": False}
    
    def _handle_shutdown_computer(self, force: bool = False) -> dict:
        """Handle shutdown computer action."""
        if self.system_operations:
            success = self.system_operations.shutdown_computer(force)
            return {"shutdown_initiated": success}
        return {"shutdown_initiated": False}
    
    def _handle_open_folder(self, path: str) -> dict:
        """Handle open folder action."""
        if self.system_operations:
            success = self.system_operations.open_folder(path)
            return {"folder_opened": success}
        return {"folder_opened": False}
    
    def _handle_open_url(self, url: str) -> dict:
        """Handle open URL action."""
        if self.application_manager:
            success = self.application_manager.open_url(url)
            return {"url_opened": success}
        return {"url_opened": False}
    
    def _handle_browser_search(self, query: str, engine: str = "google") -> dict:
        """Handle browser search action."""
        if self.application_manager:
            search_url = f"https://{engine}.com/search?q={query}"
            success = self.application_manager.open_url(search_url)
            return {"search_performed": success}
        return {"search_performed": False}
    
    def _startup_phase_authentication(self) -> None:
        """Initialize authentication components."""
        self.logger.info("Phase 6: Initializing authentication components")
        
        try:
            from app.wakeword import WakeWordDetector
            from app.authentication import VoiceEnrollment, SpeakerVerifier, VoiceProfileManager
            
            # Initialize wake word detector
            self.wake_word_detector = WakeWordDetector()
            self.wake_word_detector.load_model()
            self.logger.info("Wake word detector initialized")
            
            # Initialize voice enrollment
            self.voice_enrollment = VoiceEnrollment()
            self.logger.info("Voice enrollment system initialized")
            
            # Initialize speaker verifier
            self.speaker_verifier = SpeakerVerifier()
            self.speaker_verifier.load_model()
            self.logger.info("Speaker verifier initialized")
            
            # Initialize voice profile manager
            self.voice_profile_manager = VoiceProfileManager()
            self.logger.info("Voice profile manager initialized")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize authentication components: {e}")
            raise
    
    def shutdown(self) -> None:
        """Shutdown the application gracefully."""
        if not self._is_running:
            self.logger.warning("Application is not running")
            return
        
        self.logger.info("Starting ELARA shutdown sequence")
        
        try:
            # Signal shutdown
            self._shutdown_event.set()
            
            # Perform shutdown sequence
            self._perform_shutdown_sequence()
            
            # Update state
            self.state_manager.set_state(AssistantState.IDLE)
            
            # Publish shutdown event
            self.event_bus.publish(EventType.SYSTEM_SHUTDOWN, {})
            
            self._is_running = False
            self._is_initialized = False
            
            self.logger.info("ELARA shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")
            raise
    
    def _perform_shutdown_sequence(self) -> None:
        """Perform the shutdown sequence in reverse order."""
        self.logger.info("Starting shutdown sequence")
        
        # Phase 8: UI components (reverse order)
        self._shutdown_phase_ui()
        
        # Phase 7: Authentication components
        self._shutdown_phase_authentication()
        
        # Phase 6: AI components
        self._shutdown_phase_ai_integration()
        
        # Phase 5: Action components
        self._shutdown_phase_actions()
        
        # Phase 4: Windows automation components
        self._shutdown_phase_windows_automation()
        
        # Phase 3: Audio components
        self._shutdown_phase_audio()
        
        # Phase 2: Core components
        self._shutdown_phase_core()
        
        self.logger.info("Shutdown sequence completed")
    
    def _shutdown_phase_ui(self) -> None:
        """Shutdown UI components."""
        self.logger.info("Phase 6: Shutting down UI components")
        # TODO: Shutdown UI components in Phase 6
        pass
    
    def _shutdown_phase_authentication(self) -> None:
        """Shutdown authentication components."""
        self.logger.info("Phase 7: Shutting down authentication components")
        
        try:
            # Stop wake word detector
            if hasattr(self, 'wake_word_detector') and self.wake_word_detector is not None:
                self.wake_word_detector.stop_listening()
                self.wake_word_detector.unload_model()
                self.logger.info("Wake word detector stopped")
            
            # Cancel voice enrollment
            if hasattr(self, 'voice_enrollment') and self.voice_enrollment is not None:
                self.voice_enrollment.cancel_enrollment()
                self.logger.info("Voice enrollment cancelled")
            
            # Unload speaker verifier
            if hasattr(self, 'speaker_verifier') and self.speaker_verifier is not None:
                self.speaker_verifier.unload_model()
                self.logger.info("Speaker verifier unloaded")
            
        except Exception as e:
            self.logger.error(f"Error shutting down authentication components: {e}")
    
    def _shutdown_phase_ai_integration(self) -> None:
        """Shutdown AI components."""
        self.logger.info("Phase 6: Shutting down AI components")
        
        try:
            # Clear conversation history
            if hasattr(self, 'ai_manager') and self.ai_manager is not None:
                self.ai_manager.clear_conversation_history()
                self.logger.info("Conversation history cleared")
            
            # AI components don't require explicit cleanup
            self.logger.info("AI components cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error shutting down AI components: {e}")
    
    def _shutdown_phase_windows_automation(self) -> None:
        """Shutdown Windows automation components."""
        self.logger.info("Phase 5: Shutting down Windows automation components")
        
        try:
            # Cleanup application manager
            if hasattr(self, 'application_manager') and self.application_manager is not None:
                # Application manager doesn't need explicit cleanup
                self.logger.info("Application manager cleaned up")
            
            # Window manager doesn't need explicit cleanup
            if hasattr(self, 'window_manager') and self.window_manager is not None:
                self.logger.info("Window manager cleaned up")
            
            # Volume controller cleanup
            if hasattr(self, 'volume_controller') and self.volume_controller is not None:
                # Volume controller doesn't need explicit cleanup
                self.logger.info("Volume controller cleaned up")
            
            # Screenshot capture cleanup
            if hasattr(self, 'screenshot_capture') and self.screenshot_capture is not None:
                # Screenshot capture doesn't need explicit cleanup
                self.logger.info("Screenshot capture cleaned up")
            
            # System operations cleanup
            if hasattr(self, 'system_operations') and self.system_operations is not None:
                # System operations doesn't need explicit cleanup
                self.logger.info("System operations cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error shutting down Windows automation components: {e}")
    
    def _shutdown_phase_actions(self) -> None:
        """Shutdown action components."""
        self.logger.info("Phase 4: Shutting down action components")
        
        try:
            # Action components don't require explicit cleanup
            self.logger.info("Action components cleaned up")
            
        except Exception as e:
            self.logger.error(f"Error shutting down action components: {e}")
    
    def _shutdown_phase_audio(self) -> None:
        """Shutdown audio components."""
        self.logger.info("Phase 2: Shutting down audio components")
        
        try:
            # Cleanup microphone
            if hasattr(self, 'microphone') and self.microphone is not None:
                self.microphone.cleanup()
                self.logger.info("Microphone cleaned up")
            
            # Unload STT model
            if hasattr(self, 'stt') and self.stt is not None:
                self.stt.unload_model()
                self.logger.info("Speech-to-Text model unloaded")
            
            # Unload TTS model
            if hasattr(self, 'tts') and self.tts is not None:
                self.tts.unload_model()
                self.logger.info("Text-to-Speech model unloaded")
            
            # Stop any ongoing audio processing
            if hasattr(self, 'tts') and self.tts is not None:
                self.tts.stop_speaking()
                self.logger.info("Audio playback stopped")
            
        except Exception as e:
            self.logger.error(f"Error shutting down audio components: {e}")
    
    def _shutdown_phase_core(self) -> None:
        """Shutdown core components."""
        self.logger.info("Phase 1: Shutting down core components")
        # Core components cleanup if needed
        pass
    
    def is_running(self) -> bool:
        """Check if the application is running."""
        return self._is_running
    
    def is_initialized(self) -> bool:
        """Check if the application is initialized."""
        return self._is_initialized
    
    def restart(self) -> None:
        """Restart the application."""
        self.logger.info("Restarting ELARA")
        self.shutdown()
        self.initialize()
