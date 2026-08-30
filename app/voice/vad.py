"""
ELARA - Voice Activity Detection
This module implements voice activity detection to identify when speech is present in audio.
"""

import numpy as np
from typing import Optional, Tuple
import collections

from app.config.settings import get_settings
from app.config.constants import DEFAULT_SAMPLE_RATE
from app.utils.logger import get_logger


class VoiceActivityDetector:
    """Detects voice activity in audio streams."""
    
    def __init__(
        self,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        threshold: float = 0.5,
        min_speech_duration: float = 0.3,
        min_silence_duration: float = 0.5,
        speech_pad: float = 0.3
    ):
        self.logger = get_logger("elara.vad")
        self.settings = get_settings()
        
        # Audio parameters
        self.sample_rate = sample_rate or self.settings.audio.sample_rate
        self.threshold = threshold
        self.min_speech_duration = min_speech_duration
        self.min_silence_duration = min_silence_duration
        self.speech_pad = speech_pad
        
        # Convert durations to sample counts
        self.min_speech_samples = int(self.min_speech_duration * self.sample_rate)
        self.min_silence_samples = int(self.min_silence_duration * self.sample_rate)
        self.speech_pad_samples = int(self.speech_pad * self.sample_rate)
        
        # State tracking
        self._is_speaking = False
        self._speech_start_sample = 0
        self._silence_start_sample = 0
        self._audio_buffer = collections.deque(maxlen=self.sample_rate * 2)  # 2 seconds buffer
        
        self.logger.info("Voice Activity Detector initialized")
    
    def compute_energy(self, audio: np.ndarray) -> float:
        """
        Compute the energy of audio signal.
        
        Args:
            audio: Audio samples
            
        Returns:
            Energy value
        """
        # Convert to float if needed
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        
        # Compute RMS energy
        energy = np.sqrt(np.mean(audio ** 2))
        return energy
    
    def compute_zero_crossing_rate(self, audio: np.ndarray) -> float:
        """
        Compute the zero crossing rate of audio signal.
        
        Args:
            audio: Audio samples
            
        Returns:
            Zero crossing rate
        """
        # Convert to float if needed
        if audio.dtype == np.int16:
            audio = audio.astype(np.float32) / 32768.0
        
        # Compute zero crossings
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))
        return zero_crossings
    
    def is_speech(self, audio: np.ndarray) -> bool:
        """
        Determine if audio contains speech.
        
        Args:
            audio: Audio samples
            
        Returns:
            True if speech is detected
        """
        if len(audio) == 0:
            return False
        
        # Compute features
        energy = self.compute_energy(audio)
        zcr = self.compute_zero_crossing_rate(audio)
        
        # Simple threshold-based detection
        # In a production system, you might use a trained model like Silero VAD
        is_speech = energy > self.threshold
        
        return is_speech
    
    def process_audio(self, audio: np.ndarray) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """
        Process audio chunk and detect speech segments.
        
        Args:
            audio: Audio samples
            
        Returns:
            Tuple of (is_speaking, speech_segment) where speech_segment is (start, end) in samples
        """
        # Add audio to buffer
        self._audio_buffer.extend(audio.flatten())
        
        # Get current buffer as array
        buffer_array = np.array(list(self._audio_buffer))
        
        # Check for speech
        current_is_speech = self.is_speech(buffer_array)
        
        speech_segment = None
        
        if current_is_speech and not self._is_speaking:
            # Speech started
            self._is_speaking = True
            self._speech_start_sample = len(self._audio_buffer) - len(audio)
            self.logger.debug("Speech started")
            
        elif not current_is_speech and self._is_speaking:
            # Speech ended
            self._is_speaking = False
            speech_end_sample = len(self._audio_buffer)
            
            # Check if speech duration is long enough
            speech_duration = speech_end_sample - self._speech_start_sample
            if speech_duration >= self.min_speech_samples:
                speech_segment = (self._speech_start_sample, speech_end_sample)
                self.logger.debug(f"Speech ended, duration: {speech_duration / self.sample_rate:.2f}s")
            else:
                self.logger.debug("Speech too short, ignoring")
        
        return (self._is_speaking, speech_segment)
    
    def detect_speech_segments(self, audio: np.ndarray, chunk_size: int = 1024) -> list:
        """
        Detect speech segments in a complete audio file.
        
        Args:
            audio: Complete audio samples
            chunk_size: Size of chunks to process
            
        Returns:
            List of (start, end) tuples in samples
        """
        segments = []
        current_segment = None
        silence_counter = 0
        
        for i in range(0, len(audio), chunk_size):
            chunk = audio[i:i + chunk_size]
            if len(chunk) < chunk_size:
                continue
            
            is_speech = self.is_speech(chunk)
            
            if is_speech:
                if current_segment is None:
                    current_segment = i
                silence_counter = 0
            else:
                if current_segment is not None:
                    silence_counter += chunk_size
                    if silence_counter >= self.min_silence_samples:
                        # End of speech segment
                        segments.append((current_segment, i))
                        current_segment = None
                        silence_counter = 0
        
        # Handle final segment
        if current_segment is not None:
            segments.append((current_segment, len(audio)))
        
        # Apply padding
        padded_segments = []
        for start, end in segments:
            padded_start = max(0, start - self.speech_pad_samples)
            padded_end = min(len(audio), end + self.speech_pad_samples)
            padded_segments.append((padded_start, padded_end))
        
        self.logger.info(f"Detected {len(padded_segments)} speech segments")
        return padded_segments
    
    def reset(self):
        """Reset the detector state."""
        self._is_speaking = False
        self._speech_start_sample = 0
        self._silence_start_sample = 0
        self._audio_buffer.clear()
        self.logger.debug("VAD reset")
    
    def get_is_speaking(self) -> bool:
        """Get current speaking state."""
        return self._is_speaking


class SileroVAD:
    """
    Silero VAD model for more accurate voice activity detection.
    This is a placeholder for implementing the actual Silero model.
    """
    
    def __init__(self):
        self.logger = get_logger("elara.silero_vad")
        self._model = None
        self._is_loaded = False
        
        # TODO: Load Silero VAD model
        # This would require downloading and loading the actual model
        self.logger.info("Silero VAD placeholder initialized")
    
    def load_model(self):
        """Load the Silero VAD model."""
        # TODO: Implement actual model loading
        # import torch
        # model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',
        #                               model='silero_vad',
        #                               force_reload=True)
        pass
    
    def is_speech(self, audio: np.ndarray, sample_rate: int) -> bool:
        """
        Detect speech using Silero VAD model.
        
        Args:
            audio: Audio samples
            sample_rate: Sample rate
            
        Returns:
            True if speech is detected
        """
        # TODO: Implement actual Silero VAD inference
        return False
    
    def process_audio(self, audio: np.ndarray, sample_rate: int) -> list:
        """
        Process audio and return speech timestamps.
        
        Args:
            audio: Audio samples
            sample_rate: Sample rate
            
        Returns:
            List of speech timestamps
        """
        # TODO: Implement actual Silero VAD processing
        return []
