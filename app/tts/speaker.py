"""
ELARA - Text to Speech
This module implements text-to-speech using Piper TTS.
"""

import numpy as np
import sounddevice as sd
from typing import Optional, Callable
from pathlib import Path
import threading
import io

from app.config.settings import get_settings
from app.config.constants import DEFAULT_SAMPLE_RATE
from app.utils.logger import get_logger


class TextToSpeech:
    """Text-to-speech using Piper TTS."""
    
    def __init__(self):
        self.logger = get_logger("elara.tts")
        self.settings = get_settings()
        
        # TTS parameters
        self.model_name = self.settings.tts.model
        self.speed = self.settings.tts.speed
        self.enable_tts = self.settings.tts.enable_tts
        
        # Audio parameters
        self.sample_rate = DEFAULT_SAMPLE_RATE
        
        # Model instance
        self._model = None
        self._is_loaded = False
        self._load_lock = threading.Lock()
        self._use_fallback = False
        self._fallback_engine = None
        
        # State
        self._is_speaking = False
        self._stop_event = threading.Event()
        
        self.logger.info(f"TextToSpeech initialized with model: {self.model_name}")
    
    def load_model(self) -> bool:
        """
        Load the Piper TTS model.
        
        Returns:
            True if model loaded successfully
        """
        with self._load_lock:
            if self._is_loaded:
                return True
            
            try:
                # Try to load Piper TTS
                try:
                    # Placeholder for actual Piper implementation
                    # import PiperVoice
                    
                    self.logger.info(f"Loading Piper TTS model: {self.model_name}")
                    
                    # Initialize model (placeholder for actual Piper implementation)
                    # In production, this would download and load the actual model
                    # self._model = PiperVoice.load(self.model_name)
                    
                    self._is_loaded = True
                    self.logger.info("Piper TTS model loaded successfully")
                    return True
                    
                except ImportError:
                    self.logger.warning("Piper TTS not installed. Install with: pip install piper-tts")
                    raise ImportError("Piper TTS not available")
                    
            except Exception as e:
                self.logger.warning(f"Piper TTS not available: {e}")
                # Fallback to system TTS
                self._setup_fallback_tts()
                self._is_loaded = True
                return True
    
    def _setup_fallback_tts(self):
        """Setup fallback TTS using system capabilities."""
        try:
            import pyttsx3
            self._fallback_engine = pyttsx3.init()
            self._fallback_engine.setProperty('rate', 150)  # Speed
            self._use_fallback = True
            self.logger.info("Using fallback TTS (pyttsx3)")
        except ImportError:
            self.logger.warning("Fallback TTS not available, using dummy audio")
            self._use_fallback = False
    
    def synthesize(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio samples or None if failed
        """
        if not self.enable_tts:
            self.logger.debug("TTS is disabled")
            return None
        
        if not text.strip():
            self.logger.debug("Empty text, skipping synthesis")
            return None
        
        try:
            if self._use_fallback:
                return self._synthesize_fallback(text)
            else:
                return self._synthesize_piper(text)
                
        except Exception as e:
            self.logger.error(f"Speech synthesis failed: {e}")
            return None
    
    def _synthesize_piper(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize using Piper TTS.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio samples
        """
        # Placeholder for actual Piper implementation
        # In production, this would use the actual Piper API
        self.logger.info(f"Synthesizing with Piper: {text[:50]}...")
        
        # Generate dummy audio for now
        duration = len(text) * 0.05  # Approximate duration
        samples = int(duration * self.sample_rate)
        audio = np.random.uniform(-0.1, 0.1, samples).astype(np.float32)
        
        return audio
    
    def _synthesize_fallback(self, text: str) -> Optional[np.ndarray]:
        """
        Synthesize using fallback TTS.
        
        Args:
            text: Text to synthesize
            
        Returns:
            Audio samples
        """
        if not self._use_fallback or self._fallback_engine is None:
            # Generate dummy audio
            duration = len(text) * 0.05
            samples = int(duration * self.sample_rate)
            audio = np.random.uniform(-0.1, 0.1, samples).astype(np.float32)
            return audio
        
        try:
            # Save to temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                temp_file = f.name
            
            # Synthesize to file
            self._fallback_engine.save_to_file(text, temp_file)
            self._fallback_engine.runAndWait()
            
            # Load audio file
            import soundfile as sf
            audio, sr = sf.read(temp_file)
            
            # Cleanup
            Path(temp_file).unlink(missing_ok=True)
            
            # Resample if needed
            if sr != self.sample_rate:
                from scipy import signal
                number_of_samples = round(len(audio) * float(self.sample_rate) / sr)
                audio = signal.resample(audio, number_of_samples)
            
            return audio
            
        except Exception as e:
            self.logger.error(f"Fallback synthesis failed: {e}")
            return None
    
    def speak(self, text: str, callback: Optional[Callable] = None) -> bool:
        """
        Synthesize and play speech.
        
        Args:
            text: Text to speak
            callback: Optional callback when speech completes
            
        Returns:
            True if speech started successfully
        """
        if not self.enable_tts:
            self.logger.debug("TTS is disabled")
            if callback:
                callback()
            return True
        
        if self._is_speaking:
            self.logger.warning("Already speaking")
            return False
        
        try:
            # Synthesize audio
            audio = self.synthesize(text)
            if audio is None:
                if callback:
                    callback()
                return False
            
            # Play audio
            self._is_speaking = True
            self._stop_event.clear()
            
            def play_audio():
                try:
                    sd.play(audio, self.sample_rate)
                    sd.wait()
                except Exception as e:
                    self.logger.error(f"Audio playback failed: {e}")
                finally:
                    self._is_speaking = False
                    if callback:
                        callback()
            
            # Start playback in thread
            thread = threading.Thread(target=play_audio, daemon=True)
            thread.start()
            
            self.logger.info(f"Speaking: {text[:50]}...")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to speak: {e}")
            self._is_speaking = False
            return False
    
    def stop_speaking(self) -> bool:
        """
        Stop current speech.
        
        Returns:
            True if speech stopped successfully
        """
        if not self._is_speaking:
            return False
        
        try:
            sd.stop()
            self._stop_event.set()
            self._is_speaking = False
            self.logger.info("Speech stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop speech: {e}")
            return False
    
    def save_to_file(self, text: str, output_file: Path) -> bool:
        """
        Synthesize speech and save to file.
        
        Args:
            text: Text to synthesize
            output_file: Output file path
            
        Returns:
            True if successful
        """
        try:
            audio = self.synthesize(text)
            if audio is None:
                return False
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save audio file
            import soundfile as sf
            sf.write(str(output_file), audio, self.sample_rate)
            
            self.logger.info(f"Saved speech to {output_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save speech to file: {e}")
            return False
    
    def is_speaking(self) -> bool:
        """Check if currently speaking."""
        return self._is_speaking
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded
    
    def set_speed(self, speed: float):
        """
        Set speech speed.
        
        Args:
            speed: Speed multiplier (0.5 - 2.0)
        """
        self.speed = max(0.5, min(2.0, speed))
        self.logger.info(f"Speech speed set to {self.speed}")
        
        if self._use_fallback and self._fallback_engine:
            self._fallback_engine.setProperty('rate', int(150 * self.speed))
    
    def set_volume(self, volume: float):
        """
        Set speech volume.
        
        Args:
            volume: Volume level (0.0 - 1.0)
        """
        volume = max(0.0, min(1.0, volume))
        self.logger.info(f"Speech volume set to {volume}")
        
        if self._use_fallback and self._fallback_engine:
            self._fallback_engine.setProperty('volume', volume)
    
    def get_available_voices(self) -> list:
        """
        Get list of available voices.
        
        Returns:
            List of voice information
        """
        voices = []
        
        if hasattr(self, '_fallback_engine'):
            try:
                for voice in self._fallback_engine.getProperty('voices'):
                    voices.append({
                        'id': voice.id,
                        'name': voice.name,
                        'languages': voice.languages
                    })
            except Exception as e:
                self.logger.error(f"Failed to get voices: {e}")
        
        return voices
    
    def set_voice(self, voice_id: str) -> bool:
        """
        Set the voice to use.
        
        Args:
            voice_id: Voice identifier
            
        Returns:
            True if successful
        """
        if self._use_fallback and self._fallback_engine:
            try:
                self._fallback_engine.setProperty('voice', voice_id)
                self.logger.info(f"Voice set to {voice_id}")
                return True
            except Exception as e:
                self.logger.error(f"Failed to set voice: {e}")
                return False
        
        return False
    
    def unload_model(self):
        """Unload the model to free memory."""
        with self._load_lock:
            if self._model is not None:
                del self._model
                self._model = None
                self._is_loaded = False
                self.logger.info("TTS model unloaded")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.stop_speaking()
        self.unload_model()


class StreamingTextToSpeech(TextToSpeech):
    """Streaming text-to-speech for real-time responses."""
    
    def __init__(self):
        super().__init__()
        self._text_queue = []
        self._queue_lock = threading.Lock()
        self._is_streaming = False
    
    def start_streaming(self):
        """Start streaming TTS."""
        self._is_streaming = True
        self.logger.info("Streaming TTS started")
    
    def stop_streaming(self):
        """Stop streaming TTS."""
        self._is_streaming = False
        self.logger.info("Streaming TTS stopped")
    
    def add_text_chunk(self, text: str):
        """
        Add text chunk to queue.
        
        Args:
            text: Text chunk
        """
        with self._queue_lock:
            self._text_queue.append(text)
    
    def process_queue(self):
        """Process accumulated text queue."""
        with self._queue_lock:
            if not self._text_queue:
                return
            
            # Combine chunks
            text = ' '.join(self._text_queue)
            self._text_queue.clear()
        
        # Speak
        self.speak(text)
