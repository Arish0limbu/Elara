"""
ELARA - Voice Loop
This module handles the continuous voice listening and command processing loop.
"""

from typing import Optional, Callable
from threading import Thread, Event
import time
from queue import Queue, Empty

from app.utils.logger import get_logger


class VoiceLoop:
    """Manages the continuous voice listening and command processing loop."""
    
    def __init__(self):
        self.logger = get_logger("elara.voice_loop")
        
        # Voice components (will be set from lifecycle)
        self.microphone = None
        self.vad = None
        self.stt = None
        self.wake_word_detector = None
        self.voice_enrollment = None
        self.speaker_verifier = None
        self.ai_manager = None
        self.tts = None
        
        # Control
        self._is_running = False
        self._should_listen = False
        self._stop_event = Event()
        
        # Command processing
        self._command_queue = Queue()
        self._command_callback: Optional[Callable] = None
        
        # Voice loop thread
        self._voice_thread: Optional[Thread] = None
        
        # State
        self._is_listening_for_wake_word = False
        self._is_listening_for_command = False
        self._wake_word_detected = False
        
        self.logger.info("Voice loop initialized")
    
    def set_components(
        self,
        microphone=None,
        vad=None,
        stt=None,
        wake_word_detector=None,
        voice_enrollment=None,
        speaker_verifier=None,
        ai_manager=None,
        tts=None
    ):
        """Set voice components."""
        self.microphone = microphone
        self.vad = vad
        self.stt = stt
        self.wake_word_detector = wake_word_detector
        self.voice_enrollment = voice_enrollment
        self.speaker_verifier = speaker_verifier
        self.ai_manager = ai_manager
        self.tts = tts
        self.logger.info("Voice loop components set")
    
    def set_command_callback(self, callback: Callable):
        """Set callback for when commands are detected."""
        self._command_callback = callback
        self.logger.info("Command callback set")
    
    def start_listening(self):
        """Start the voice listening loop."""
        if self._is_running:
            self.logger.warning("Voice loop already running")
            return
        
        if not self.microphone:
            self.logger.error("Cannot start listening: microphone not available")
            return
        
        self._is_running = True
        self._should_listen = True
        self._stop_event.clear()
        
        # Start voice thread
        self._voice_thread = Thread(target=self._voice_loop_main, daemon=True)
        self._voice_thread.start()
        
        self.logger.info("Voice listening loop started")
    
    def stop_listening(self):
        """Stop the voice listening loop."""
        self._should_listen = False
        self._stop_event.set()
        self._is_running = False
        
        if self._voice_thread and self._voice_thread.is_alive():
            self._voice_thread.join(timeout=5.0)
        
        self.logger.info("Voice listening loop stopped")
    
    def _voice_loop_main(self):
        """Main voice listening loop."""
        self.logger.info("Voice loop thread started")
        
        while self._should_listen and not self._stop_event.is_set():
            try:
                # Start by listening for wake word
                self._listen_for_wake_word()
                
                # If wake word detected, listen for command
                if self._stop_event.is_set():
                    break
                
                command = self._listen_for_command()
                
                if command and self._command_callback:
                    self._command_callback(command)
                
                # Small delay before next cycle
                time.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error in voice loop: {e}")
                time.sleep(1.0)
        
        self.logger.info("Voice loop thread ended")
    
    def _listen_for_wake_word(self):
        """Listen for wake word."""
        if not self.wake_word_detector:
            self.logger.warning("Wake word detector not available, skipping wake word detection")
            # Skip to command listening directly
            self._wake_word_detected = True
            return
        
        self._is_listening_for_wake_word = True
        self.logger.info("Listening for wake word...")
        
        try:
            # Set callback for wake word detection
            self._wake_word_detected = False
            
            def on_wake_word_detected(wake_word, confidence):
                self.logger.info(f"Wake word detected: '{wake_word}' with confidence {confidence:.2f}")
                self._wake_word_detected = True
                self._stop_event.set()  # Signal to exit wake word listening
                
                # Speak acknowledgment
                if self.tts:
                    try:
                        self.tts.speak("Yes, I'm listening. How can I help you?")
                        self.logger.info("Spoke wake word acknowledgment")
                    except Exception as e:
                        self.logger.error(f"Error speaking wake word acknowledgment: {e}")
            
            # Start wake word listening with callback
            self.wake_word_detector.start_listening(callback=on_wake_word_detected)
            
            # Wait for wake word detection or timeout
            timeout = 15.0  # Listen for 15 seconds max (reduced from 30 for better responsiveness)
            start_time = time.time()
            
            while time.time() - start_time < timeout and not self._stop_event.is_set():
                time.sleep(0.1)
            
            # Stop wake word listening
            self.wake_word_detector.stop_listening()
            
            # Reset stop event for next phase
            self._stop_event.clear()
            
            # Check if wake word was detected
            if self._wake_word_detected:
                self.logger.info("Wake word confirmed, transitioning to command listening")
            else:
                self.logger.info("Wake word timeout, continuing to listen")
                # For better responsiveness, still try to listen for command
                self._wake_word_detected = True
                
        except Exception as e:
            self.logger.error(f"Error listening for wake word: {e}")
            # Even if wake word fails, continue to command listening
            self._wake_word_detected = True
        
        finally:
            self._is_listening_for_wake_word = False
    
    def _listen_for_command(self) -> Optional[str]:
        """Listen for user command after wake word."""
        if not self.microphone or not self.stt:
            self.logger.warning("Microphone or STT not available for command listening")
            return None
        
        self._is_listening_for_command = True
        self.logger.info("Listening for command...")
        
        try:
            # Record audio for command (shorter timeout for better responsiveness)
            command_timeout = 5.0  # Listen for command for 5 seconds
            audio_data = self.microphone.record_audio(duration=command_timeout)
            
            if not audio_data:
                self.logger.warning("No audio data captured")
                return None
            
            # Process with VAD to get speech segments
            speech_segments = self.vad.detect_speech(audio_data)
            
            if not speech_segments:
                self.logger.warning("No speech detected in audio")
                return None
            
            # Convert speech to text
            command_text = self.stt.transcribe_audio(audio_data)
            
            if command_text:
                self.logger.info(f"Command detected: '{command_text}'")
                return command_text.strip()
            else:
                self.logger.warning("Could not transcribe speech to text")
                return None
                
        except Exception as e:
            self.logger.error(f"Error listening for command: {e}")
            return None
        finally:
            self._is_listening_for_command = False
    
    def process_command_from_text(self, text: str) -> Optional[str]:
        """Process a command from text input (alternative to voice)."""
        if self.ai_manager:
            from app.ai import AIRequest
            request = AIRequest(user_input=text)
            response = self.ai_manager.process_request(request)
            return response.response_text
        return None
    
    def speak(self, text: str):
        """Speak text using TTS."""
        if self.tts:
            try:
                self.logger.info(f"Speaking: '{text[:50]}...'")
                self.tts.speak(text)
                self.logger.info("Speech completed")
            except Exception as e:
                self.logger.error(f"Error speaking: {e}")
        else:
            self.logger.warning("TTS not available for speech output")
    
    def is_listening(self) -> bool:
        """Check if voice loop is currently listening."""
        return self._is_running and (self._is_listening_for_wake_word or self._is_listening_for_command)
    
    def get_status(self) -> dict:
        """Get current voice loop status."""
        return {
            "is_running": self._is_running,
            "is_listening_for_wake_word": self._is_listening_for_wake_word,
            "is_listening_for_command": self._is_listening_for_command,
            "microphone_available": self.microphone is not None,
            "wake_word_detector_available": self.wake_word_detector is not None,
            "stt_available": self.stt is not None,
            "tts_available": self.tts is not None
        }
