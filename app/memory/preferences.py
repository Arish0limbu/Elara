"""
ELARA - User Preferences Management
This module handles user preferences storage and retrieval.
"""

from typing import Optional, Any, Dict
from datetime import datetime

from sqlalchemy.orm import Session

from app.memory.database import get_database_manager
from app.memory.models import UserPreference
from app.utils.logger import get_logger


class PreferencesManager:
    """Manages user preferences storage and retrieval."""
    
    def __init__(self):
        self.logger = get_logger("elara.preferences")
        self.db = get_database_manager()
    
    def set_preference(
        self,
        user_id: str,
        category: str,
        key: str,
        value: Any,
        value_type: str = "string",
        description: Optional[str] = None
    ) -> UserPreference:
        """
        Set a user preference.
        
        Args:
            user_id: User identifier
            category: Preference category
            key: Preference key
            value: Preference value
            value_type: Type of the value ('string', 'int', 'bool', 'json')
            description: Optional description
            
        Returns:
            The created/updated UserPreference object
        """
        import json
        
        # Convert value to string based on type
        if value_type == "json":
            str_value = json.dumps(value)
        elif value_type == "bool":
            str_value = str(value).lower()
        else:
            str_value = str(value)
        
        with self.db.get_session() as session:
            try:
                # Check if preference already exists
                preference = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id,
                    UserPreference.category == category,
                    UserPreference.key == key
                ).first()
                
                if preference:
                    # Update existing preference
                    preference.value = str_value
                    preference.value_type = value_type
                    preference.description = description
                    preference.updated_at = datetime.utcnow()
                    self.logger.info(f"Updated preference: {user_id}/{category}/{key}")
                else:
                    # Create new preference
                    preference = UserPreference(
                        user_id=user_id,
                        category=category,
                        key=key,
                        value=str_value,
                        value_type=value_type,
                        description=description
                    )
                    session.add(preference)
                    self.logger.info(f"Set new preference: {user_id}/{category}/{key}")
                
                session.commit()
                session.refresh(preference)
                return preference
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Failed to set preference: {e}")
                raise
    
    def get_preference(
        self,
        user_id: str,
        category: str,
        key: str,
        default: Any = None
    ) -> Any:
        """
        Get a user preference.
        
        Args:
            user_id: User identifier
            category: Preference category
            key: Preference key
            default: Default value if not found
            
        Returns:
            The preference value
        """
        import json
        
        with self.db.get_session() as session:
            try:
                preference = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id,
                    UserPreference.category == category,
                    UserPreference.key == key
                ).first()
                
                if preference:
                    return self._parse_preference_value(preference)
                
                return default
                
            except Exception as e:
                self.logger.error(f"Failed to get preference: {e}")
                return default
    
    def get_category_preferences(
        self,
        user_id: str,
        category: str
    ) -> Dict[str, Any]:
        """
        Get all preferences in a category for a user.
        
        Args:
            user_id: User identifier
            category: Preference category
            
        Returns:
            Dictionary of preference key-value pairs
        """
        with self.db.get_session() as session:
            try:
                preferences = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id,
                    UserPreference.category == category
                ).all()
                
                return {
                    pref.key: self._parse_preference_value(pref)
                    for pref in preferences
                }
                
            except Exception as e:
                self.logger.error(f"Failed to get category preferences: {e}")
                return {}
    
    def get_all_preferences(self, user_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all preferences for a user organized by category.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary of categories containing preference dictionaries
        """
        with self.db.get_session() as session:
            try:
                preferences = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id
                ).all()
                
                result = {}
                for pref in preferences:
                    if pref.category not in result:
                        result[pref.category] = {}
                    result[pref.category][pref.key] = self._parse_preference_value(pref)
                
                return result
                
            except Exception as e:
                self.logger.error(f"Failed to get all preferences: {e}")
                return {}
    
    def delete_preference(
        self,
        user_id: str,
        category: str,
        key: str
    ) -> bool:
        """
        Delete a user preference.
        
        Args:
            user_id: User identifier
            category: Preference category
            key: Preference key
            
        Returns:
            True if deleted, False otherwise
        """
        with self.db.get_session() as session:
            try:
                preference = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id,
                    UserPreference.category == category,
                    UserPreference.key == key
                ).first()
                
                if preference:
                    session.delete(preference)
                    session.commit()
                    self.logger.info(f"Deleted preference: {user_id}/{category}/{key}")
                    return True
                
                return False
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Failed to delete preference: {e}")
                return False
    
    def delete_category_preferences(
        self,
        user_id: str,
        category: str
    ) -> int:
        """
        Delete all preferences in a category for a user.
        
        Args:
            user_id: User identifier
            category: Preference category
            
        Returns:
            Number of preferences deleted
        """
        with self.db.get_session() as session:
            try:
                count = session.query(UserPreference).filter(
                    UserPreference.user_id == user_id,
                    UserPreference.category == category
                ).delete()
                
                session.commit()
                self.logger.info(f"Deleted {count} preferences from {user_id}/{category}")
                return count
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Failed to delete category preferences: {e}")
                return 0
    
    def _parse_preference_value(self, preference: UserPreference) -> Any:
        """
        Parse a preference value based on its type.
        
        Args:
            preference: UserPreference object
            
        Returns:
            Parsed value
        """
        import json
        
        if preference.value_type == "int":
            return int(preference.value)
        elif preference.value_type == "bool":
            return preference.value.lower() == "true"
        elif preference.value_type == "json":
            try:
                return json.loads(preference.value)
            except json.JSONDecodeError:
                return preference.value
        else:
            return preference.value


# Global preferences manager instance
_preferences_manager: Optional[PreferencesManager] = None


def get_preferences_manager() -> PreferencesManager:
    """Get the global preferences manager instance."""
    global _preferences_manager
    if _preferences_manager is None:
        _preferences_manager = PreferencesManager()
    return _preferences_manager
