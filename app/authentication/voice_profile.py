"""
ELARA - Voice Profile Management
This module manages voice profiles in the database.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
import numpy as np

from app.memory.database import get_database_manager
from app.memory.models import VoiceProfile
from app.utils.logger import get_logger


class VoiceProfileManager:
    """Manages voice profiles in the database."""
    
    def __init__(self):
        self.logger = get_logger("elara.voice_profile")
        self.db = get_database_manager()
    
    def create_profile(
        self,
        user_id: str,
        name: str,
        embedding: np.ndarray,
        threshold: float = 0.75
    ) -> Optional[VoiceProfile]:
        """
        Create a new voice profile.
        
        Args:
            user_id: User identifier
            name: User display name
            embedding: Voice embedding array
            threshold: Verification threshold
            
        Returns:
            Created VoiceProfile or None if failed
        """
        try:
            with self.db.get_session() as session:
                # Check if profile already exists
                existing = session.query(VoiceProfile).filter(
                    VoiceProfile.user_id == user_id
                ).first()
                
                if existing:
                    self.logger.warning(f"Voice profile already exists for user: {user_id}")
                    return None
                
                # Create new profile
                profile = VoiceProfile(
                    user_id=user_id,
                    name=name,
                    embedding_data=embedding.tolist() if isinstance(embedding, np.ndarray) else embedding,
                    enrollment_date=datetime.utcnow(),
                    threshold=threshold,
                    is_active=True
                )
                
                session.add(profile)
                session.commit()
                session.refresh(profile)
                
                self.logger.info(f"Voice profile created for user: {name} ({user_id})")
                return profile
                
        except Exception as e:
            self.logger.error(f"Failed to create voice profile: {e}")
            return None
    
    def get_profile(self, user_id: str) -> Optional[VoiceProfile]:
        """
        Get voice profile by user ID.
        
        Args:
            user_id: User identifier
            
        Returns:
            VoiceProfile or None if not found
        """
        try:
            with self.db.get_session() as session:
                profile = session.query(VoiceProfile).filter(
                    VoiceProfile.user_id == user_id
                ).first()
                
                return profile
                
        except Exception as e:
            self.logger.error(f"Failed to get voice profile: {e}")
            return None
    
    def get_active_profiles(self) -> List[VoiceProfile]:
        """Get all active voice profiles."""
        try:
            with self.db.get_session() as session:
                profiles = session.query(VoiceProfile).filter(
                    VoiceProfile.is_active == True
                ).all()
                
                return profiles
                
        except Exception as e:
            self.logger.error(f"Failed to get active profiles: {e}")
            return []
    
    def update_profile(
        self,
        user_id: str,
        embedding: Optional[np.ndarray] = None,
        threshold: Optional[float] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """
        Update an existing voice profile.
        
        Args:
            user_id: User identifier
            embedding: New embedding (optional)
            threshold: New threshold (optional)
            is_active: New active status (optional)
            
        Returns:
            True if updated successfully
        """
        try:
            with self.db.get_session() as session:
                profile = session.query(VoiceProfile).filter(
                    VoiceProfile.user_id == user_id
                ).first()
                
                if not profile:
                    self.logger.warning(f"Voice profile not found for user: {user_id}")
                    return False
                
                if embedding is not None:
                    profile.embedding_data = embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
                
                if threshold is not None:
                    profile.threshold = threshold
                
                if is_active is not None:
                    profile.is_active = is_active
                
                profile.updated_at = datetime.utcnow()
                session.commit()
                
                self.logger.info(f"Voice profile updated for user: {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to update voice profile: {e}")
            return False
    
    def delete_profile(self, user_id: str) -> bool:
        """
        Delete a voice profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deleted successfully
        """
        try:
            with self.db.get_session() as session:
                profile = session.query(VoiceProfile).filter(
                    VoiceProfile.user_id == user_id
                ).first()
                
                if not profile:
                    self.logger.warning(f"Voice profile not found for user: {user_id}")
                    return False
                
                session.delete(profile)
                session.commit()
                
                self.logger.info(f"Voice profile deleted for user: {user_id}")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to delete voice profile: {e}")
            return False
    
    def record_verification(self, user_id: str, success: bool) -> bool:
        """
        Record a verification attempt.
        
        Args:
            user_id: User identifier
            success: Whether verification was successful
            
        Returns:
            True if recorded successfully
        """
        try:
            with self.db.get_session() as session:
                profile = session.query(VoiceProfile).filter(
                    VoiceProfile.user_id == user_id
                ).first()
                
                if not profile:
                    self.logger.warning(f"Voice profile not found for user: {user_id}")
                    return False
                
                profile.verification_count += 1
                if success:
                    profile.last_verified = datetime.utcnow()
                
                profile.updated_at = datetime.utcnow()
                session.commit()
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to record verification: {e}")
            return False
    
    def get_profile_stats(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a voice profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with profile statistics
        """
        try:
            profile = self.get_profile(user_id)
            if not profile:
                return None
            
            stats = {
                'user_id': profile.user_id,
                'name': profile.name,
                'enrollment_date': profile.enrollment_date.isoformat() if profile.enrollment_date else None,
                'last_verified': profile.last_verified.isoformat() if profile.last_verified else None,
                'verification_count': profile.verification_count,
                'threshold': profile.threshold,
                'is_active': profile.is_active,
                'embedding_size': len(profile.embedding_data) if profile.embedding_data else 0
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get profile stats: {e}")
            return None
    
    def list_profiles(self) -> List[Dict[str, Any]]:
        """List all voice profiles with basic info."""
        try:
            profiles = self.get_active_profiles()
            
            profile_list = []
            for profile in profiles:
                profile_list.append({
                    'user_id': profile.user_id,
                    'name': profile.name,
                    'enrollment_date': profile.enrollment_date.isoformat() if profile.enrollment_date else None,
                    'verification_count': profile.verification_count,
                    'is_active': profile.is_active
                })
            
            return profile_list
            
        except Exception as e:
            self.logger.error(f"Failed to list profiles: {e}")
            return []
    
    def deactivate_profile(self, user_id: str) -> bool:
        """
        Deactivate a voice profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if deactivated successfully
        """
        return self.update_profile(user_id, is_active=False)
    
    def activate_profile(self, user_id: str) -> bool:
        """
        Activate a voice profile.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if activated successfully
        """
        return self.update_profile(user_id, is_active=True)
    
    def get_embedding(self, user_id: str) -> Optional[np.ndarray]:
        """
        Get voice embedding for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Embedding array or None if not found
        """
        try:
            profile = self.get_profile(user_id)
            if not profile or not profile.embedding_data:
                return None
            
            return np.array(profile.embedding_data)
            
        except Exception as e:
            self.logger.error(f"Failed to get embedding: {e}")
            return None
    
    def backup_profiles(self, backup_path) -> bool:
        """
        Backup all voice profiles to a file.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if backup successful
        """
        try:
            import pickle
            from pathlib import Path
            
            profiles = self.get_active_profiles()
            backup_data = []
            
            for profile in profiles:
                backup_data.append({
                    'user_id': profile.user_id,
                    'name': profile.name,
                    'embedding_data': profile.embedding_data,
                    'threshold': profile.threshold,
                    'enrollment_date': profile.enrollment_date.isoformat() if profile.enrollment_date else None,
                    'verification_count': profile.verification_count
                })
            
            backup_path = Path(backup_path)
            backup_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(backup_path, 'wb') as f:
                pickle.dump(backup_data, f)
            
            self.logger.info(f"Voice profiles backed up to {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to backup profiles: {e}")
            return False
    
    def restore_profiles(self, backup_path) -> bool:
        """
        Restore voice profiles from a backup file.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if restore successful
        """
        try:
            import pickle
            from pathlib import Path
            
            backup_path = Path(backup_path)
            if not backup_path.exists():
                self.logger.warning(f"Backup file not found: {backup_path}")
                return False
            
            with open(backup_path, 'rb') as f:
                backup_data = pickle.load(f)
            
            for profile_data in backup_data:
                self.create_profile(
                    user_id=profile_data['user_id'],
                    name=profile_data['name'],
                    embedding=np.array(profile_data['embedding_data']),
                    threshold=profile_data.get('threshold', 0.75)
                )
            
            self.logger.info(f"Voice profiles restored from {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to restore profiles: {e}")
            return False
