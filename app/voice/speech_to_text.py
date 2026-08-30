"""
ELARA - Speech to Text
This module implements speech recognition using faster-whisper.
"""

import numpy as np
from typing import Optional, List, Dict, Any
from pathlib import Path
import threading

from app.config.settings import get_settings
from app.config.constants import DEFAULT_SAMPLE_RATE
from app.utils.logger import get_logger


class SpeechToText:
    """Speech recognition using faster-whisper."""
    
    def __init__(self):
        self.logger = get_logger("elara.stt")
        self.settings = get_settings()
        
        # Model parameters
        self.model_name = self.settings.stt.model
        self.language = self.settings.stt.language
        self.device = self.settings.stt.device
        self.compute_type = self.settings.stt.compute_type
        
        # Model instance
        self._model = None
        self._is_loaded = False
        self._load_lock = threading.Lock()
        
        # Audio parameters
        self.sample_rate = DEFAULT_SAMPLE_RATE
        
        self.logger.info(f"SpeechToText initialized with model: {self.model_name}")
    
    def load_model(self) -> bool:
        """
        Load the Whisper model.
        
        Returns:
            True if model loaded successfully
        """
        with self._load_lock:
            if self._is_loaded:
                return True
            
            try:
                from faster_whisper import WhisperModel
                
                self.logger.info(f"Loading Whisper model: {self.model_name}")
                
                # Initialize model
                self._model = WhisperModel(
                    self.model_name,
                    device=self.device,
                    compute_type=self.compute_type
                )
                
                self._is_loaded = True
                self.logger.info("Whisper model loaded successfully")
                return True
                
            except ImportError:
                self.logger.error("faster-whisper not installed. Install with: pip install faster-whisper")
                return False
            except Exception as e:
                self.logger.error(f"Failed to load Whisper model: {e}")
                return False
    
    def transcribe(
        self,
        audio: np.ndarray,
        language: Optional[str] = None,
        vad_filter: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.
        
        Args:
            audio: Audio samples (numpy array)
            language: Language code (e.g., 'en', 'es')
            vad_filter: Use voice activity detection filter
            
        Returns:
            Dictionary with transcription results
        """
        if not self._is_loaded:
            if not self.load_model():
                return {
                    'text': '',
                    'language': '',
                    'segments': [],
                    'error': 'Model not loaded'
                }
        
        try:
            # Use provided language or default
            lang = language or self.language
            
            # Convert audio to float32 if needed
            if audio.dtype == np.int16:
                audio = audio.astype(np.float32) / 32768.0
            
            # Transcribe
            segments, info = self._model.transcribe(
                audio,
                language=lang,
                vad_filter=vad_filter,
                beam_size=5
            )
            
            # Collect results
            text_segments = []
            full_text = []
            
            for segment in segments:
                segment_data = {
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip(),
                    'words': [{'word': word.word, 'start': word.start, 'end': word.end} 
                             for word in segment.words] if hasattr(segment, 'words') else []
                }
                text_segments.append(segment_data)
                full_text.append(segment.text.strip())
            
            result = {
                'text': ' '.join(full_text),
                'language': info.language,
                'language_probability': info.language_probability,
                'duration': info.duration,
                'segments': text_segments,
                'error': None
            }
            
            self.logger.info(f"Transcription completed: {len(result['text'])} characters")
            return result
            
        except Exception as e:
            self.logger.error(f"Transcription failed: {e}")
            return {
                'text': '',
                'language': '',
                'segments': [],
                'error': str(e)
            }
    
    def transcribe_file(
        self,
        audio_file: Path,
        language: Optional[str] = None,
        vad_filter: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.
        
        Args:
            audio_file: Path to audio file
            language: Language code (e.g., 'en', 'es')
            vad_filter: Use voice activity detection filter
            
        Returns:
            Dictionary with transcription results
        """
        if not audio_file.exists():
            return {
                'text': '',
                'language': '',
                'segments': [],
                'error': f'File not found: {audio_file}'
            }
        
        try:
            # Load audio file
            import soundfile as sf
            audio, sr = sf.read(str(audio_file))
            
            # Resample if needed
            if sr != self.sample_rate:
                from scipy import signal
                number_of_samples = round(len(audio) * float(self.sample_rate) / sr)
                audio = signal.resample(audio, number_of_samples)
            
            # Transcribe
            return self.transcribe(audio, language, vad_filter)
            
        except Exception as e:
            self.logger.error(f"Failed to transcribe file: {e}")
            return {
                'text': '',
                'language': '',
                'segments': [],
                'error': str(e)
            }
    
    def transcribe_stream(
        self,
        audio_generator,
        language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribe streaming audio.
        
        Args:
            audio_generator: Generator that yields audio chunks
            language: Language code (e.g., 'en', 'es')
            
        Returns:
            Dictionary with transcription results
        """
        if not self._is_loaded:
            if not self.load_model():
                return {
                    'text': '',
                    'language': '',
                    'segments': [],
                    'error': 'Model not loaded'
                }
        
        try:
            # Collect audio chunks
            audio_chunks = []
            for chunk in audio_generator:
                audio_chunks.append(chunk)
            
            # Combine chunks
            if audio_chunks:
                audio = np.concatenate(audio_chunks)
                return self.transcribe(audio, language)
            else:
                return {
                    'text': '',
                    'language': '',
                    'segments': [],
                    'error': 'No audio data'
                }
                
        except Exception as e:
            self.logger.error(f"Stream transcription failed: {e}")
            return {
                'text': '',
                'language': '',
                'segments': [],
                'error': str(e)
            }
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of language codes
        """
        # Common languages supported by Whisper
        languages = [
            'en', 'es', 'fr', 'de', 'it', 'pt', 'nl', 'ru', 'ja', 'ko',
            'zh', 'ar', 'tr', 'pl', 'sv', 'uk', 'vi', 'th', 'hi', 'id'
        ]
        return languages
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded
    
    def unload_model(self):
        """Unload the model to free memory."""
        with self._load_lock:
            if self._model is not None:
                del self._model
                self._model = None
                self._is_loaded = False
                self.logger.info("Whisper model unloaded")
    
    def __del__(self):
        """Cleanup when object is destroyed."""
        self.unload_model()


class StreamingSpeechToText(SpeechToText):
    """Streaming speech recognition with real-time transcription."""
    
    def __init__(self):
        super().__init__()
        self._audio_buffer = []
        self._buffer_lock = threading.Lock()
        self._is_streaming = False
        self._callback = None
    
    def start_streaming(self, callback):
        """
        Start streaming transcription.
        
        Args:
            callback: Function to call with transcription results
        """
        self._callback = callback
        self._is_streaming = True
        self.logger.info("Streaming transcription started")
    
    def stop_streaming(self):
        """Stop streaming transcription."""
        self._is_streaming = False
        self.logger.info("Streaming transcription stopped")
    
    def add_audio_chunk(self, audio: np.ndarray):
        """
        Add audio chunk to buffer.
        
        Args:
            audio: Audio samples
        """
        with self._buffer_lock:
            self._audio_buffer.append(audio)
    
    def process_buffer(self):
        """Process accumulated audio buffer."""
        with self._buffer_lock:
            if not self._audio_buffer:
                return
            
            # Combine chunks
            audio = np.concatenate(self._audio_buffer)
            self._audio_buffer.clear()
        
        # Transcribe
        result = self.transcribe(audio)
        
        # Call callback if provided
        if self._callback and result['text']:
            try:
                self._callback(result)
            except Exception as e:
                self.logger.error(f"Error in transcription callback: {e}")
