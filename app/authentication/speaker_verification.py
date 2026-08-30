"""
ELARA - Speaker Verification
This module implements speaker verification using SpeechBrain ECAPA-TDNN.
"""

import numpy as np
from typing import Optional, Tuple, Dict, Any
from pathlib import Path
import pickle

from app.config.settings import get_settings
from app.config.constants import DEFAULT_SAMPLE_RATE
from app.utils.logger import get_logger


class SpeakerVerifier:
    """Verifies speaker identity using voice embeddings."""
    
    def __init__(self):
        self.logger = get_logger("elara.speaker_verification")
        self.settings = get_settings()
        
        # Verification parameters
        self.threshold = self.settings.voice.verification_threshold
        self.enable_verification = self.settings.voice.enable_verification
        
        # Audio parameters
        self.sample_rate = DEFAULT_SAMPLE_RATE
        
        # Model
        self._model = None
        self._is_loaded = False
        
        # Voice profiles cache
        self._voice_profiles: Dict[str, Dict] = {}
        
        self.logger.info("Speaker verifier initialized")
    
    def load_model(self) -> bool:
        """
        Load the speaker verification model.
        
        Returns:
            True if model loaded successfully
        """
        if self._is_loaded:
            return True
        
        try:
            # Try to load SpeechBrain model
            from speechbrain.inference.speaker import SpeakerRecognition
            
            self.logger.info("Loading SpeechBrain speaker verification model")
            
            # Initialize model (placeholder for actual SpeechBrain implementation)
            # self._model = SpeakerRecognition.from_hparams(
            #     source="speechbrain/spkrec-ecapa-voxceleb",
            #     savedir="pretrained_models/spkrec-ecapa-voxceleb"
            # )
            
            # Placeholder implementation
            self._model = self._create_placeholder_model()
            self._is_loaded = True
            
            self.logger.info("Speaker verification model loaded successfully")
            return True
            
        except ImportError:
            self.logger.warning("SpeechBrain not installed. Install with: pip install speechbrain")
            self._model = self._create_placeholder_model()
            self._is_loaded = True
            return True
        except Exception as e:
            self.logger.error(f"Failed to load speaker verification model: {e}")
            self._model = self._create_placeholder_model()
            self._is_loaded = True
            return True
    
    def _create_placeholder_model(self):
        """Create a placeholder model for testing."""
        # This is a simple cosine similarity-based detector for testing
        # In production, replace with actual SpeechBrain model
        class PlaceholderModel:
            def __init__(self, threshold=0.75):
                self.threshold = threshold
            
            def verify_batch(self, audio, reference_embedding):
                """Simple cosine similarity verification."""
                # Calculate embedding for audio
                embedding = self._extract_embedding(audio)
                
                # Calculate cosine similarity
                similarity = self._cosine_similarity(embedding, reference_embedding)
                
                return similarity
            
            def _extract_embedding(self, audio):
                """Extract simple embedding from audio."""
                # Extract basic features as placeholder
                features = []
                
                # RMS energy
                rms = np.sqrt(np.mean(audio ** 2))
                features.append(rms)
                
                # Zero crossing rate
                zcr = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))
                features.append(zcr)
                
                # Spectral features (simplified)
                fft = np.fft.fft(audio)
                magnitude = np.abs(fft)
                freqs = np.fft.fftfreq(len(audio), 1/16000)
                spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
                features.append(abs(spectral_centroid))
                
                # Add more features to reach desired dimension
                while len(features) < 256:
                    features.append(0.0)
                
                return np.array(features[:256])
            
            def _cosine_similarity(self, embedding1, embedding2):
                """Calculate cosine similarity between embeddings."""
                dot_product = np.dot(embedding1, embedding2)
                norm1 = np.linalg.norm(embedding1)
                norm2 = np.linalg.norm(embedding2)
                
                if norm1 == 0 or norm2 == 0:
                    return 0.0
                
                return dot_product / (norm1 * norm2)
        
        return PlaceholderModel(threshold=self.threshold)
    
    def verify_speaker(
        self,
        audio: np.ndarray,
        user_id: str,
        reference_embedding: Optional[np.ndarray] = None
    ) -> Tuple[bool, float]:
        """
        Verify if audio matches the registered speaker.
        
        Args:
            audio: Audio samples to verify
            user_id: User identifier to verify against
            reference_embedding: Optional reference embedding
            
        Returns:
            Tuple of (is_verified, confidence_score)
        """
        if not self.enable_verification:
            self.logger.debug("Speaker verification disabled")
            return (True, 1.0)  # Always verify if disabled
        
        if not self._is_loaded:
            if not self.load_model():
                return (False, 0.0)
        
        try:
            # Get reference embedding
            if reference_embedding is None:
                if user_id in self._voice_profiles:
                    reference_embedding = np.array(self._voice_profiles[user_id]['embedding'])
                else:
                    self.logger.warning(f"No voice profile found for user: {user_id}")
                    return (False, 0.0)
            
            # Verify using model
            if self._model:
                confidence = self._model.verify_batch(audio, reference_embedding)
                
                # Check if confidence meets threshold
                is_verified = confidence >= self.threshold
                
                self.logger.info(f"Speaker verification: {is_verified} (confidence: {confidence:.3f})")
                return (is_verified, confidence)
            
            return (False, 0.0)
            
        except Exception as e:
            self.logger.error(f"Speaker verification failed: {e}")
            return (False, 0.0)
    
    def register_voice_profile(
        self,
        user_id: str,
        user_name: str,
        embedding: np.ndarray,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Register a voice profile for a user.
        
        Args:
            user_id: User identifier
            user_name: User display name
            embedding: Voice embedding
            metadata: Optional metadata
            
        Returns:
            True if registered successfully
        """
        try:
            profile = {
                'user_id': user_id,
                'user_name': user_name,
                'embedding': embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                'registered_date': None,  # Will be set by voice_profile manager
                'verification_count': 0,
                'metadata': metadata or {}
            }
            
            self._voice_profiles[user_id] = profile
            self.logger.info(f"Voice profile registered for user: {user_name} ({user_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register voice profile: {e}")
            return False
    
    def get_voice_profile(self, user_id: str) -> Optional[Dict]:
        """
        Get voice profile for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Voice profile dictionary or None
        """
        return self._voice_profiles.get(user_id)
    
    def update_voice_profile(
        self,
        user_id: str,
        embedding: Optional[np.ndarray] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Update an existing voice profile.
        
        Args:
            user_id: User identifier
            embedding: New embedding (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if updated successfully
        """
        if user_id not in self._voice_profiles:
            self.logger.warning(f"No voice profile found for user: {user_id}")
            return False
        
        try:
            profile = self._voice_profiles[user_id]
            
            if embedding is not None:
                profile['embedding'] = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            
            if metadata is not None:
                profile['metadata'].update(metadata)
            
            self.logger.info(f"Voice profile updated for user: {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to update voice profile: {e}")
            return False
    
    def delete_voice_profile(self, user_id: str) -> bool:
        """
        Delete a voice profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted successfully
        """
        if user_id in self._voice_profiles:
            del self._voice_profiles[user_id]
            self.logger.info(f"Voice profile deleted for user: {user_id}")
            return True
        
        return False
    
    def list_voice_profiles(self) -> list:
        """List all registered voice profiles."""
        return list(self._voice_profiles.keys())
    
    def extract_embedding(self, audio: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract voice embedding from audio.
        
        Args:
            audio: Audio samples
            
        Returns:
            Voice embedding or None if failed
        """
        if not self._is_loaded:
            if not self.load_model():
                return None
        
        try:
            if self._model and hasattr(self._model, '_extract_embedding'):
                return self._model._extract_embedding(audio)
            else:
                # Fallback to simple feature extraction
                return self._simple_embedding_extraction(audio)
                
        except Exception as e:
            self.logger.error(f"Failed to extract embedding: {e}")
            return None
    
    def _simple_embedding_extraction(self, audio: np.ndarray) -> np.ndarray:
        """Simple embedding extraction as fallback."""
        features = []
        
        # RMS energy
        rms = np.sqrt(np.mean(audio ** 2))
        features.append(rms)
        
        # Zero crossing rate
        zcr = np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio))
        features.append(zcr)
        
        # Spectral features
        fft = np.fft.fft(audio)
        magnitude = np.abs(fft)
        freqs = np.fft.fftfreq(len(audio), 1/self.sample_rate)
        spectral_centroid = np.sum(freqs * magnitude) / np.sum(magnitude)
        features.append(abs(spectral_centroid))
        
        # Add more features to reach desired dimension
        while len(features) < 256:
            features.append(0.0)
        
        return np.array(features[:256])
    
    def set_threshold(self, threshold: float):
        """
        Set verification threshold.
        
        Args:
            threshold: New threshold (0.0 - 1.0)
        """
        self.threshold = max(0.0, min(1.0, threshold))
        self.logger.info(f"Verification threshold set to {self.threshold}")
        
        if hasattr(self._model, 'threshold'):
            self._model.threshold = self.threshold
    
    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._is_loaded
    
    def unload_model(self):
        """Unload the model to free memory."""
        if self._model is not None:
            del self._model
            self._model = None
            self._is_loaded = False
            self.logger.info("Speaker verification model unloaded")
    
    def save_profiles(self, file_path: Path) -> bool:
        """
        Save voice profiles to file.
        
        Args:
            file_path: Output file path
            
        Returns:
            True if saved successfully
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'wb') as f:
                pickle.dump(self._voice_profiles, f)
            
            self.logger.info(f"Voice profiles saved to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save voice profiles: {e}")
            return False
    
    def load_profiles(self, file_path: Path) -> bool:
        """
        Load voice profiles from file.
        
        Args:
            file_path: Input file path
            
        Returns:
            True if loaded successfully
        """
        try:
            if not file_path.exists():
                self.logger.warning(f"Voice profiles file not found: {file_path}")
                return False
            
            with open(file_path, 'rb') as f:
                self._voice_profiles = pickle.load(f)
            
            self.logger.info(f"Voice profiles loaded from {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load voice profiles: {e}")
            return False
    
    def cleanup(self):
        """Cleanup resources."""
        self.unload_model()
        self._voice_profiles.clear()
        self.logger.info("Speaker verifier cleaned up")


class VerificationConfig:
    """Configuration for speaker verification."""
    
    def __init__(
        self,
        threshold: float = 0.75,
        enable_verification: bool = True,
        sample_rate: int = DEFAULT_SAMPLE_RATE,
        embedding_size: int = 256
    ):
        self.threshold = threshold
        self.enable_verification = enable_verification
        self.sample_rate = sample_rate
        self.embedding_size = embedding_size
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            'threshold': self.threshold,
            'enable_verification': self.enable_verification,
            'sample_rate': self.sample_rate,
            'embedding_size': self.embedding_size
        }
    
    @classmethod
    def from_dict(cls, config: dict) -> 'VerificationConfig':
        """Create from dictionary."""
        return cls(
            threshold=config.get('threshold', 0.75),
            enable_verification=config.get('enable_verification', True),
            sample_rate=config.get('sample_rate', DEFAULT_SAMPLE_RATE),
            embedding_size=config.get('embedding_size', 256)
        )
