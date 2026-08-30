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
        # TODO: Initialize AI components in Phase 3
        pass
    
    def _startup_phase_actions(self) -> None:
        """Initialize action components."""
        self.logger.info("Phase 4: Initializing action components")
        # TODO: Initialize action components in Phase 4
        pass
    
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
        
        # Phase 6: UI components (reverse order)
        self._shutdown_phase_ui()
        
        # Phase 5: Authentication components
        self._shutdown_phase_authentication()
        
        # Phase 4: Action components
        self._shutdown_phase_actions()
        
        # Phase 3: AI components
        self._shutdown_phase_ai()
        
        # Phase 2: Audio components
        self._shutdown_phase_audio()
        
        # Phase 1: Core components
        self._shutdown_phase_core()
        
        self.logger.info("Shutdown sequence completed")
    
    def _shutdown_phase_ui(self) -> None:
        """Shutdown UI components."""
        self.logger.info("Phase 6: Shutting down UI components")
        # TODO: Shutdown UI components in Phase 6
        pass
    
    def _shutdown_phase_authentication(self) -> None:
        """Shutdown authentication components."""
        self.logger.info("Phase 5: Shutting down authentication components")
        
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
    
    def _shutdown_phase_actions(self) -> None:
        """Shutdown action components."""
        self.logger.info("Phase 4: Shutting down action components")
        # TODO: Shutdown action components in Phase 4
        pass
    
    def _shutdown_phase_ai(self) -> None:
        """Shutdown AI components."""
        self.logger.info("Phase 3: Shutting down AI components")
        # TODO: Shutdown AI components in Phase 3
        pass
    
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
