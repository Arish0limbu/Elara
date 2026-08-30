"""
ELARA - Audio Utilities
This module provides utility functions for audio processing.
"""

import numpy as np
from typing import Optional, Tuple
from pathlib import Path

from app.config.constants import DEFAULT_SAMPLE_RATE
from app.utils.logger import get_logger


class AudioProcessor:
    """Utility class for audio processing operations."""
    
    def __init__(self, sample_rate: int = DEFAULT_SAMPLE_RATE):
        self.logger = get_logger("elara.audio")
        self.sample_rate = sample_rate
    
    def convert_to_float32(self, audio: np.ndarray) -> np.ndarray:
        """
        Convert audio to float32 format.
        
        Args:
            audio: Input audio array
            
        Returns:
            Audio in float32 format
        """
        if audio.dtype == np.int16:
            return audio.astype(np.float32) / 32768.0
        elif audio.dtype == np.int32:
            return audio.astype(np.float32) / 2147483648.0
        elif audio.dtype == np.uint8:
            return (audio.astype(np.float32) - 128.0) / 128.0
        else:
            return audio.astype(np.float32)
    
    def convert_to_int16(self, audio: np.ndarray) -> np.ndarray:
        """
        Convert audio to int16 format.
        
        Args:
            audio: Input audio array
            
        Returns:
            Audio in int16 format
        """
        if audio.dtype != np.int16:
            # Clip to valid range
            audio = np.clip(audio, -1.0, 1.0)
            # Convert to int16
            audio = (audio * 32768.0).astype(np.int16)
        return audio
    
    def normalize_audio(self, audio: np.ndarray, target_level: float = 0.9) -> np.ndarray:
        """
        Normalize audio to target level.
        
        Args:
            audio: Input audio array
            target_level: Target RMS level (0.0 - 1.0)
            
        Returns:
            Normalized audio
        """
        # Convert to float if needed
        if audio.dtype != np.float32:
            audio = self.convert_to_float32(audio)
        
        # Calculate current RMS
        current_rms = np.sqrt(np.mean(audio ** 2))
        
        if current_rms > 0:
            # Calculate gain
            gain = target_level / current_rms
            # Apply gain
            audio = audio * gain
            # Clip to prevent distortion
            audio = np.clip(audio, -1.0, 1.0)
        
        return audio
    
    def trim_silence(
        self,
        audio: np.ndarray,
        threshold: float = 0.01,
        frame_length: int = 2048
    ) -> np.ndarray:
        """
        Remove silence from beginning and end of audio.
        
        Args:
            audio: Input audio array
            threshold: Silence threshold
            frame_length: Frame length for analysis
            
        Returns:
            Trimmed audio
        """
        # Convert to float if needed
        if audio.dtype != np.float32:
            audio = self.convert_to_float32(audio)
        
        # Calculate energy in frames
        energy = []
        for i in range(0, len(audio), frame_length):
            frame = audio[i:i + frame_length]
            if len(frame) > 0:
                frame_energy = np.sqrt(np.mean(frame ** 2))
                energy.append(frame_energy)
        
        if not energy:
            return audio
        
        # Find first non-silent frame
        start_idx = 0
        for i, e in enumerate(energy):
            if e > threshold:
                start_idx = i * frame_length
                break
        
        # Find last non-silent frame
        end_idx = len(audio)
        for i in range(len(energy) - 1, -1, -1):
            if energy[i] > threshold:
                end_idx = (i + 1) * frame_length
                break
        
        # Trim audio
        trimmed = audio[start_idx:end_idx]
        
        self.logger.debug(f"Trimmed audio: {len(audio)} -> {len(trimmed)} samples")
        return trimmed
    
    def apply_gain(self, audio: np.ndarray, gain_db: float) -> np.ndarray:
        """
        Apply gain to audio.
        
        Args:
            audio: Input audio array
            gain_db: Gain in decibels
            
        Returns:
            Audio with gain applied
        """
        # Convert to float if needed
        if audio.dtype != np.float32:
            audio = self.convert_to_float32(audio)
        
        # Convert dB to linear scale
        gain_linear = 10 ** (gain_db / 20.0)
        
        # Apply gain
        audio = audio * gain_linear
        
        # Clip to prevent distortion
        audio = np.clip(audio, -1.0, 1.0)
        
        return audio
    
    def fade_in(
        self,
        audio: np.ndarray,
        duration: float = 0.1
    ) -> np.ndarray:
        """
        Apply fade-in to audio.
        
        Args:
            audio: Input audio array
            duration: Fade duration in seconds
            
        Returns:
            Audio with fade-in applied
        """
        # Convert to float if needed
        if audio.dtype != np.float32:
            audio = self.convert_to_float32(audio)
        
        # Calculate fade samples
        fade_samples = int(duration * self.sample_rate)
        fade_samples = min(fade_samples, len(audio))
        
        # Create fade curve
        fade_curve = np.linspace(0.0, 1.0, fade_samples)
        
        # Apply fade
        audio[:fade_samples] *= fade_curve
        
        return audio
    
    def fade_out(
        self,
        audio: np.ndarray,
        duration: float = 0.1
    ) -> np.ndarray:
        """
        Apply fade-out to audio.
        
        Args:
            audio: Input audio array
            duration: Fade duration in seconds
            
        Returns:
            Audio with fade-out applied
        """
        # Convert to float if needed
        if audio.dtype != np.float32:
            audio = self.convert_to_float32(audio)
        
        # Calculate fade samples
        fade_samples = int(duration * self.sample_rate)
        fade_samples = min(fade_samples, len(audio))
        
        # Create fade curve
        fade_curve = np.linspace(1.0, 0.0, fade_samples)
        
        # Apply fade
        audio[-fade_samples:] *= fade_curve
        
        return audio
    
    def resample(
        self,
        audio: np.ndarray,
        original_rate: int,
        target_rate: int
    ) -> np.ndarray:
        """
        Resample audio to different sample rate.
        
        Args:
            audio: Input audio array
            original_rate: Original sample rate
            target_rate: Target sample rate
            
        Returns:
            Resampled audio
        """
        if original_rate == target_rate:
            return audio
        
        try:
            from scipy import signal
            
            # Calculate number of samples
            number_of_samples = round(len(audio) * float(target_rate) / original_rate)
            
            # Resample
            resampled = signal.resample(audio, number_of_samples)
            
            self.logger.debug(f"Resampled audio: {original_rate}Hz -> {target_rate}Hz")
            return resampled
            
        except ImportError:
            self.logger.warning("scipy not available, using simple resampling")
            # Simple linear interpolation (less accurate)
            ratio = target_rate / original_rate
            new_length = int(len(audio) * ratio)
            indices = np.linspace(0, len(audio) - 1, new_length)
            resampled = np.interp(indices, np.arange(len(audio)), audio)
            return resampled
    
    def convert_to_mono(self, audio: np.ndarray) -> np.ndarray:
        """
        Convert multi-channel audio to mono.
        
        Args:
            audio: Input audio array
            
        Returns:
            Mono audio
        """
        if len(audio.shape) == 1:
            return audio  # Already mono
        
        # Average channels
        mono = np.mean(audio, axis=1)
        return mono
    
    def convert_channels(
        self,
        audio: np.ndarray,
        target_channels: int
    ) -> np.ndarray:
        """
        Convert audio to target number of channels.
        
        Args:
            audio: Input audio array
            target_channels: Target number of channels
            
        Returns:
            Audio with target channels
        """
        if len(audio.shape) == 1:
            # Mono to multi-channel
            if target_channels > 1:
                return np.column_stack([audio] * target_channels)
            return audio
        
        current_channels = audio.shape[1]
        
        if current_channels == target_channels:
            return audio
        
        if target_channels == 1:
            # Multi-channel to mono
            return self.convert_to_mono(audio)
        
        if current_channels < target_channels:
            # Add channels
            padding = np.zeros((len(audio), target_channels - current_channels))
            return np.column_stack([audio, padding])
        else:
            # Remove channels
            return audio[:, :target_channels]
    
    def calculate_rms(self, audio: np.ndarray) -> float:
        """
        Calculate RMS level of audio.
        
        Args:
            audio: Input audio array
            
        Returns:
            RMS level
        """
        # Convert to float if needed
        if audio.dtype != np.float32:
            audio = self.convert_to_float32(audio)
        
        return np.sqrt(np.mean(audio ** 2))
    
    def calculate_db(self, audio: np.ndarray) -> float:
        """
        Calculate dB level of audio.
        
        Args:
            audio: Input audio array
            
        Returns:
            dB level
        """
        rms = self.calculate_rms(audio)
        
        if rms > 0:
            return 20 * np.log10(rms)
        else:
            return -np.inf
    
    def detect_clipping(self, audio: np.ndarray, threshold: float = 0.95) -> bool:
        """
        Detect if audio has clipping.
        
        Args:
            audio: Input audio array
            threshold: Clipping threshold
            
        Returns:
            True if clipping detected
        """
        # Convert to float if needed
        if audio.dtype != np.float32:
            audio = self.convert_to_float32(audio)
        
        # Check for samples near the limits
        clipped_samples = np.sum(np.abs(audio) > threshold)
        total_samples = len(audio)
        
        clipping_ratio = clipped_samples / total_samples if total_samples > 0 else 0
        
        return clipping_ratio > 0.01  # More than 1% clipped
    
    def save_audio(
        self,
        audio: np.ndarray,
        file_path: Path,
        sample_rate: Optional[int] = None
    ) -> bool:
        """
        Save audio to file.
        
        Args:
            audio: Audio array to save
            file_path: Output file path
            sample_rate: Sample rate (uses default if not specified)
            
        Returns:
            True if successful
        """
        try:
            import soundfile as sf
            
            # Use default sample rate if not specified
            sr = sample_rate or self.sample_rate
            
            # Ensure directory exists
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to int16 if needed for better compatibility
            if audio.dtype == np.float32:
                audio = self.convert_to_int16(audio)
            
            # Save audio
            sf.write(str(file_path), audio, sr)
            
            self.logger.info(f"Saved audio to {file_path}")
            return True
            
        except ImportError:
            self.logger.error("soundfile not installed")
            return False
        except Exception as e:
            self.logger.error(f"Failed to save audio: {e}")
            return False
    
    def load_audio(self, file_path: Path) -> Optional[Tuple[np.ndarray, int]]:
        """
        Load audio from file.
        
        Args:
            file_path: Input file path
            
        Returns:
            Tuple of (audio, sample_rate) or None if failed
        """
        try:
            import soundfile as sf
            
            # Load audio
            audio, sr = sf.read(str(file_path))
            
            self.logger.info(f"Loaded audio from {file_path}: {len(audio)} samples at {sr}Hz")
            return audio, sr
            
        except ImportError:
            self.logger.error("soundfile not installed")
            return None
        except Exception as e:
            self.logger.error(f"Failed to load audio: {e}")
            return None
    
    def get_audio_info(self, audio: np.ndarray) -> dict:
        """
        Get information about audio.
        
        Args:
            audio: Input audio array
            
        Returns:
            Dictionary with audio information
        """
        info = {
            'shape': audio.shape,
            'dtype': str(audio.dtype),
            'duration': len(audio) / self.sample_rate,
            'channels': 1 if len(audio.shape) == 1 else audio.shape[1],
            'rms': self.calculate_rms(audio),
            'db': self.calculate_db(audio),
            'clipping': self.detect_clipping(audio)
        }
        
        return info


def create_audio_processor(sample_rate: int = DEFAULT_SAMPLE_RATE) -> AudioProcessor:
    """
    Create an audio processor instance.
    
    Args:
        sample_rate: Sample rate for audio processing
        
    Returns:
        AudioProcessor instance
    """
    return AudioProcessor(sample_rate)
