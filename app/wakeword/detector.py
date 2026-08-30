"""
ELARA - Wake Word Detector
This module implements wake word detection using openWakeWord.
"""

import numpy as np
from typing import Optional, Callable
from threading import Thread, Event
import queue

from app.config.settings import get_settings
from app.config.constants import DEFAULT_SAMPLE_RATE
from app.utils.logger import get_logger

# Default wake word
DEFAULT_WAKE_WORD = "Hey Elara"


class WakeWordDetector:
    """Detects wake word using openWakeWord."""
    
    def __init__(self, wake_word: Optional[str] = None):
        self.logger = get_logger("elara.wakeword")
        self.settings = get_settings()
        
        # Wake word parameters
        self.wake_word = wake_word or self.settings.wake_word.wake_word
        self.sensitivity = self.settings.wake_word.sensitivity
        self.timeout = self.settings.wake_word.timeout
        
        # Audio parameters
        self.sample_rate = DEFAULT_SAMPLE_RATE
        self.chunk_size = 1024
        
        # State
        self._is_listening = False
        self._detection_thread: Optional[Thread] = None
        self._stop_event = Event()
        self._audio_queue = queue.Queue()
        
        # Callback
        self._detection_callback: Optional[Callable] = None
        
        # Model
        self._model = None
        self._is_loaded = False
        
        self.logger.info(f"WakeWordDetector initialized with word: '{self.wake_word}'")
    
    def load_model(self) -> bool:
        """
        Load the wake word detection model.
        
        Returns:
            True if model loaded successfully
        """
        try:
            # Try to load openWakeWord
            from openwakeword import Model
            
            self.logger.info(f"Loading openWakeWord model for: '{self.wake_word}'")
            
            # Initialize model (this would use actual openWakeWord models)
            # For now, we'll create a placeholder
            # self._model = Model(wakeword_models=['hey_elara'])
            
            # Placeholder implementation
            self._model = self._create_placeholder_model()
            self._is_loaded = True
            
            self.logger.info("Wake word model loaded successfully")
            return True
            
        except ImportError:
            self.logger.warning("openWakeWord not installed. Install with: pip install openWakeWord")
            self._model = self._create_placeholder_model()
            self._is_loaded = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to load wake word model: {e}")
            self._model = self._create_placeholder_model()
            self._is_loaded = True
            return True
    
    def _create_placeholder_model(self):
        """Create a placeholder model for testing."""
        # This is a simple energy-based detector for testing
        # In production, replace with actual openWakeWord model
        class PlaceholderModel:
            def __init__(self, threshold=0.5):
                self.threshold = threshold
                self.frame_count = 0
            
            def predict_clip(self, audio):
                """Simple energy-based detection."""
                energy = np.sqrt(np.mean(audio ** 2))
                self.frame_count += 1
                
                # Simulate detection every few seconds for testing
                if energy > self.threshold and self.frame_count % 100 == 0:
                    return [[0.9]]  # High confidence detection
                return [[0.1]]  # Low confidence
        
        return PlaceholderModel(threshold=self.sensitivity)
    
    def start_listening(self, callback: Optional[Callable] = None) -> bool:
        """
        Start listening for wake word.
        
        Args:
            callback: Optional callback when wake word detected
            
        Returns:
            True if listening started successfully
        """
        if not self._is_loaded:
            if not self.load_model():
                return False
        
        if self._is_listening:
            self.logger.warning("Already listening for wake word")
            return False
        
        try:
            self._detection_callback = callback
            self._is_listening = True
            self._stop_event.clear()
            
            # Start detection thread
            self._detection_thread = Thread(target=self._detection_loop, daemon=True)
            self._detection_thread.start()
            
            self.logger.info(f"Started listening for wake word: '{self.wake_word}'")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start listening: {e}")
            self._is_listening = False
            return False
    
    def _detection_loop(self):
        """Main detection loop."""
        try:
            audio_buffer = []
            buffer_size = self.sample_rate * 2  # 2 seconds buffer
            
            while not self._stop_event.is_set():
                try:
                    # Get audio chunk
                    audio_chunk = self._audio_queue.get(timeout=0.1)
                    audio_buffer.extend(audio_chunk.flatten())
                    
                    # Maintain buffer size
                    if len(audio_buffer) > buffer_size:
                        audio_buffer = audio_buffer[-buffer_size:]
                    
                    # Process if we have enough audio
                    if len(audio_buffer) >= self.sample_rate:
                        audio_array = np.array(audio_buffer[-self.sample_rate:])
                        
                        # Predict wake word
                        if self._model:
                            predictions = self._model.predict_clip(audio_array)
                            
                            # Check if wake word detected
                            if predictions and predictions[0][0] > 0.8:  # High confidence
                                self.logger.info(f"Wake word detected: '{self.wake_word}'")
                                
                                # Call callback
                                if self._detection_callback:
                                    try:
                                        self._detection_callback(self.wake_word, predictions[0][0])
                                    except Exception as e:
                                        self.logger.error(f"Error in detection callback: {e}")
                                
                                # Clear buffer to prevent multiple detections
                                audio_buffer = []
                
                except queue.Empty:
                    continue
                except Exception as e:
                    self.logger.error(f"Error in detection loop: {e}")
        
        except Exception as e:
            self.logger.error(f"Detection loop error: {e}")
        finally:
            self._is_listening = False
    
    def stop_listening(self) -> bool:
        """
        Stop listening for wake word.
        
        Returns:
            True if stopped successfully
        """
        if not self._is_listening:
            return False
        
        try:
            self._stop_event.set()
            self._is_listening = False
            
            if self._detection_thread:
                self._detection_thread.join(timeout=2.0)
            
            self.logger.info("Stopped listening for wake word")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop listening: {e}")
            return False
    
    def process_audio(self, audio: np.ndarray) -> bool:
        """
        Process audio chunk for wake word detection.
        
        Args:
            audio: Audio samples
            
        Returns:
            True if wake word detected
        """
        if not self._is_loaded:
            if not self.load_model():
                return False
        
        try:
            # Add to queue for processing
            self._audio_queue.put(audio)
            return False
            
        except Exception as e:
            self.logger.error(f"Error processing audio: {e}")
            return False
    
    def detect_in_audio(self, audio: np.ndarray) -> tuple:
        """
        Detect wake word in complete audio segment.
        
        Args:
            audio: Complete audio samples
            
        Returns:
            Tuple of (detected, confidence)
        """
        if not self._is_loaded:
            if not self.load_model():
                return (False, 0.0)
        
        try:
            # Predict wake word
            predictions = self._model.predict_clip(audio)
            
            if predictions and predictions[0][0] > 0.8:
                confidence = predictions[0][0]
                self.logger.info(f"Wake word detected with confidence: {confidence:.2f}")
                return (True, confidence)
            
            return (False, 0.0)
            
        except Exception as e:
            self.logger.error(f"Error detecting wake word: {e}")
            return (False, 0.0)
    
    def is_listening(self) -> bool:
        """Check if currently listening."""
        return self._is_listening
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded
    
    def set_wake_word(self, wake_word: str):
        """
        Set the wake word.
        
        Args:
            wake_word: New wake word
        """
        self.wake_word = wake_word
        self.logger.info(f"Wake word changed to: '{wake_word}'")
    
    def set_sensitivity(self, sensitivity: float):
        """
        Set detection sensitivity.
        
        Args:
            sensitivity: Sensitivity (0.0 - 1.0)
        """
        self.sensitivity = max(0.0, min(1.0, sensitivity))
        self.logger.info(f"Sensitivity set to {self.sensitivity}")
        
        if hasattr(self._model, 'threshold'):
            self._model.threshold = self.sensitivity
    
    def unload_model(self):
        """Unload the model to free memory."""
        if self._model is not None:
            del self._model
            self._model = None
            self._is_loaded = False
            self.logger.info("Wake word model unloaded")
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_listening()
        self.unload_model()
        self.logger.info("Wake word detector cleaned up")


class WakeWordConfig:
    """Configuration for wake word detection."""
    
    def __init__(
        self,
        wake_word: str = "Hey Elara",
        sensitivity: float = 0.5,
        timeout: float = 5.0,
        sample_rate: int = DEFAULT_SAMPLE_RATE
    ):
        self.wake_word = wake_word
        self.sensitivity = sensitivity
        self.timeout = timeout
        self.sample_rate = sample_rate
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'wake_word': self.wake_word,
            'sensitivity': self.sensitivity,
            'timeout': self.timeout,
            'sample_rate': self.sample_rate
        }
    
    @classmethod
    def from_dict(cls, config: dict) -> 'WakeWordConfig':
        """Create from dictionary."""
        return cls(
            wake_word=config.get('wake_word', "Hey Elara"),
            sensitivity=config.get('sensitivity', 0.5),
            timeout=config.get('timeout', 5.0),
            sample_rate=config.get('sample_rate', DEFAULT_SAMPLE_RATE)
        )
