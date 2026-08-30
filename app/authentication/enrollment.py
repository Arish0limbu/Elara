"""
ELARA - Voice Enrollment System
This module handles the voice enrollment process for speaker verification.
"""

import numpy as np
from typing import Optional, List, Callable
from pathlib import Path
from datetime import datetime

from app.config.settings import get_settings
from app.config.constants import DEFAULT_SAMPLE_RATE
from app.utils.logger import get_logger


class VoiceEnrollment:
    """Manages the voice enrollment process."""
    
    def __init__(self):
        self.logger = get_logger("elara.enrollment")
        self.settings = get_settings()
        
        # Enrollment parameters
        self.required_phrases = self.settings.voice.enrollment_phrases
        self.enrollment_phrases = [
            "Hey Elara, this is my voice",
            "My voice is my password",
            "Elara, recognize me"
        ]
        
        # Audio parameters
        self.sample_rate = DEFAULT_SAMPLE_RATE
        self.recording_duration = 3.0  # seconds per phrase
        
        # State
        self._current_phrase_index = 0
        self._recordings: List[np.ndarray] = []
        self._is_enrolling = False
        self._user_id: Optional[str] = None
        self._user_name: Optional[str] = None
        
        # Callbacks
        self._progress_callback: Optional[Callable] = None
        self._completion_callback: Optional[Callable] = None
        
        self.logger.info("Voice enrollment system initialized")
    
    def start_enrollment(
        self,
        user_id: str,
        user_name: str,
        progress_callback: Optional[Callable] = None,
        completion_callback: Optional[Callable] = None
    ) -> bool:
        """
        Start the enrollment process.
        
        Args:
            user_id: User identifier
            user_name: User display name
            progress_callback: Optional callback for progress updates
            completion_callback: Optional callback when enrollment completes
            
        Returns:
            True if enrollment started successfully
        """
        if self._is_enrolling:
            self.logger.warning("Enrollment already in progress")
            return False
        
        try:
            self._user_id = user_id
            self._user_name = user_name
            self._progress_callback = progress_callback
            self._completion_callback = completion_callback
            
            self._current_phrase_index = 0
            self._recordings = []
            self._is_enrolling = True
            
            self.logger.info(f"Started enrollment for user: {user_name} ({user_id})")
            
            # Notify progress
            if self._progress_callback:
                self._progress_callback(0, self.required_phrases, self.get_current_phrase())
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start enrollment: {e}")
            return False
    
    def get_current_phrase(self) -> str:
        """Get the current phrase to record."""
        if self._current_phrase_index < len(self.enrollment_phrases):
            return self.enrollment_phrases[self._current_phrase_index]
        return ""
    
    def get_progress(self) -> tuple:
        """Get current enrollment progress."""
        return (self._current_phrase_index, self.required_phrases)
    
    def submit_recording(self, audio: np.ndarray) -> bool:
        """
        Submit a recording for the current phrase.
        
        Args:
            audio: Audio recording
            
        Returns:
            True if recording accepted
        """
        if not self._is_enrolling:
            self.logger.warning("No enrollment in progress")
            return False
        
        try:
            # Validate recording
            if not self._validate_recording(audio):
                self.logger.warning("Invalid recording submitted")
                return False
            
            # Store recording
            self._recordings.append(audio)
            self._current_phrase_index += 1
            
            self.logger.info(f"Recording {self._current_phrase_index}/{self.required_phrases} accepted")
            
            # Check if enrollment complete
            if self._current_phrase_index >= self.required_phrases:
                self._complete_enrollment()
            else:
                # Notify progress
                if self._progress_callback:
                    self._progress_callback(
                        self._current_phrase_index,
                        self.required_phrases,
                        self.get_current_phrase()
                    )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to submit recording: {e}")
            return False
    
    def _validate_recording(self, audio: np.ndarray) -> bool:
        """
        Validate audio recording.
        
        Args:
            audio: Audio recording
            
        Returns:
            True if recording is valid
        """
        # Check duration
        duration = len(audio) / self.sample_rate
        if duration < 1.0 or duration > 10.0:
            self.logger.warning(f"Recording duration invalid: {duration:.2f}s")
            return False
        
        # Check audio levels
        rms = np.sqrt(np.mean(audio ** 2))
        if rms < 0.01:
            self.logger.warning("Recording too quiet")
            return False
        if rms > 0.9:
            self.logger.warning("Recording too loud (possible clipping)")
            return False
        
        # Check for sufficient content
        if np.max(np.abs(audio)) < 0.1:
            self.logger.warning("Recording insufficient audio content")
            return False
        
        return True
    
    def _complete_enrollment(self):
        """Complete the enrollment process."""
        try:
            self._is_enrolling = False
            
            # Create voice profile from recordings
            voice_profile = self._create_voice_profile()
            
            self.logger.info(f"Enrollment completed for user: {self._user_name}")
            
            # Call completion callback
            if self._completion_callback:
                try:
                    self._completion_callback(True, voice_profile)
                except Exception as e:
                    self.logger.error(f"Error in completion callback: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to complete enrollment: {e}")
            self._is_enrolling = False
            
            if self._completion_callback:
                try:
                    self._completion_callback(False, None)
                except Exception as e:
                    self.logger.error(f"Error in completion callback: {e}")
    
    def _create_voice_profile(self) -> dict:
        """
        Create voice profile from recordings.
        
        Returns:
            Voice profile dictionary
        """
        # This is a placeholder for actual embedding extraction
        # In production, this would use SpeechBrain or similar
        
        # Calculate basic audio features as placeholder
        features = []
        for recording in self._recordings:
            feature = self._extract_audio_features(recording)
            features.append(feature)
        
        # Average features
        avg_features = np.mean(features, axis=0)
        
        profile = {
            'user_id': self._user_id,
            'user_name': self._user_name,
            'embedding': avg_features.tolist(),
            'enrollment_date': datetime.now().isoformat(),
            'num_recordings': len(self._recordings),
            'phrases_used': self.enrollment_phrases[:len(self._recordings)]
        }
        
        return profile
    
    def _extract_audio_features(self, audio: np.ndarray) -> np.ndarray:
        """
        Extract audio features for voice profile.
        
        Args:
            audio: Audio recording
            
        Returns:
            Feature vector
        """
        # Placeholder feature extraction
        # In production, this would use a proper speaker embedding model
        
        # Extract basic features as placeholder
        features = []
        
        # RMS energy
        rms = np.sqrt(np.mean(audio ** 2))
        features.append(rms)
        
        # Zero crossing rate
        zcr = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))
        features.append(zcr)
        
        # Spectral centroid (simplified)
        fft = np.fft.fft(audio)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
        spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
        features.append(abs(spectral_centroid))
        
        # Add more features to reach desired dimension
        while len(features) < 256:  # Target embedding size
            features.append(0.0)
        
        return np.array(features[:256])
    
    def cancel_enrollment(self) -> bool:
        """
        Cancel the current enrollment.
        
        Returns:
            True if cancelled successfully
        """
        if not self._is_enrolling:
            return False
        
        self._is_enrolling = False
        self._recordings = []
        self._current_phrase_index = 0
        
        self.logger.info("Enrollment cancelled")
        return True
    
    def is_enrolling(self) -> bool:
        """Check if enrollment is in progress."""
        return self._is_enrolling
    
    def get_required_phrases(self) -> List[str]:
        """Get the list of required phrases."""
        return self.enrollment_phrases[:self.required_phrases]
    
    def set_enrollment_phrases(self, phrases: List[str]):
        """
        Set custom enrollment phrases.
        
        Args:
            phrases: List of phrases to use
        """
        if len(phrases) >= 3:
            self.enrollment_phrases = phrases
            self.logger.info(f"Updated enrollment phrases: {len(phrases)} phrases")
        else:
            self.logger.warning("Need at least 3 phrases for enrollment")
    
    def reset(self):
        """Reset the enrollment system."""
        self._is_enrolling = False
        self._recordings = []
        self._current_phrase_index = 0
        self._user_id = None
        self._user_name = None
        self._progress_callback = None
        self._completion_callback = None
        self.logger.debug("Enrollment system reset")


class EnrollmentConfig:
    """Configuration for voice enrollment."""
    
    def __init__(
        self,
        required_phrases: int = 3,
        recording_duration: float = 3.0,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        min_audio_level: float = 0.01,
        max_audio_level: float = 0.9
    ):
        self.required_phrases = required_phrases
        self.recording_duration = recording_duration
        self.sample_rate = sample_rate
        self.min_audio_level = min_audio_level
        self.max_audio_level = max_audio_level
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'required_phrases': self.required_phrases,
            'recording_duration': self.recording_duration,
            'sample_rate': self.sample_rate,
            'min_audio_level': self.min_audio_level,
            'max_audio_level': self.max_audio_level
        }
    
    @classmethod
    def from_dict(cls, config: dict) -> 'EnrollmentConfig':
        """Create from dictionary."""
        return cls(
            required_phrases=config.get('required_phrases', 3),
            recording_duration=config.get('recording_duration', 3.0),
            sample_rate=config.get('sample_rate', DEFAULT_SAMPLE_RATE),
            min_audio_level=config.get('min_audio_level', 0.01),
            max_audio_level=config.get('max_audio_level', 0.9)
        )
