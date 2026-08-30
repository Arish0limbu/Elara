"""
ELARA - Memory Management
This module handles user memory storage and retrieval operations.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime

from sqlalchemy.orm import Session

from app.memory.database import get_database_manager
from app.memory.models import Memory
from app.utils.logger import get_logger


class MemoryManager:
    """Manages user memory storage and retrieval."""
    
    def __init__(self):
        self.logger = get_logger("elara.memory")
        self.db = get_database_manager()
    
    def store_memory(
        self,
        category: str,
        key: str,
        value: str,
        meta_data: Optional[Dict[str, Any]] = None,
        is_sensitive: bool = False
    ) -> Memory:
        """
        Store a memory item.
        
        Args:
            category: Memory category
            key: Memory key
            value: Memory value
            meta_data: Optional metadata dictionary
            is_sensitive: Whether the memory contains sensitive information
            
        Returns:
            The created/updated Memory object
        """
        with self.db.get_session() as session:
            try:
                # Check if memory already exists
                memory = session.query(Memory).filter(
                    Memory.category == category,
                    Memory.key == key
                ).first()
                
                if memory:
                    # Update existing memory
                    memory.value = value
                    memory.meta_data = meta_data
                    memory.is_sensitive = is_sensitive
                    memory.updated_at = datetime.utcnow()
                    self.logger.info(f"Updated memory: {category}/{key}")
                else:
                    # Create new memory
                    memory = Memory(
                        category=category,
                        key=key,
                        value=value,
                        meta_data=meta_data,
                        is_sensitive=is_sensitive
                    )
                    session.add(memory)
                    self.logger.info(f"Stored new memory: {category}/{key}")
                
                session.commit()
                session.refresh(memory)
                return memory
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Failed to store memory: {e}")
                raise
    
    def retrieve_memory(self, category: str, key: str) -> Optional[Memory]:
        """
        Retrieve a specific memory item.
        
        Args:
            category: Memory category
            key: Memory key
            
        Returns:
            The Memory object if found, None otherwise
        """
        with self.db.get_session() as session:
            try:
                memory = session.query(Memory).filter(
                    Memory.category == category,
                    Memory.key == key
                ).first()
                
                if memory:
                    self.logger.debug(f"Retrieved memory: {category}/{key}")
                
                return memory
                
            except Exception as e:
                self.logger.error(f"Failed to retrieve memory: {e}")
                return None
    
    def get_category_memories(self, category: str) -> List[Memory]:
        """
        Retrieve all memories in a category.
        
        Args:
            category: Memory category
            
        Returns:
            List of Memory objects
        """
        with self.db.get_session() as session:
            try:
                memories = session.query(Memory).filter(
                    Memory.category == category
                ).all()
                
                self.logger.debug(f"Retrieved {len(memories)} memories from category: {category}")
                return memories
                
            except Exception as e:
                self.logger.error(f"Failed to retrieve category memories: {e}")
                return []
    
    def search_memories(self, query: str, category: Optional[str] = None) -> List[Memory]:
        """
        Search for memories matching a query.
        
        Args:
            query: Search query
            category: Optional category to restrict search
            
        Returns:
            List of matching Memory objects
        """
        with self.db.get_session() as session:
            try:
                query_filter = Memory.key.contains(query) | Memory.value.contains(query)
                
                if category:
                    memories = session.query(Memory).filter(
                        Memory.category == category,
                        query_filter
                    ).all()
                else:
                    memories = session.query(Memory).filter(query_filter).all()
                
                self.logger.debug(f"Found {len(memories)} memories matching query: {query}")
                return memories
                
            except Exception as e:
                self.logger.error(f"Failed to search memories: {e}")
                return []
    
    def delete_memory(self, category: str, key: str) -> bool:
        """
        Delete a specific memory item.
        
        Args:
            category: Memory category
            key: Memory key
            
        Returns:
            True if deleted, False otherwise
        """
        with self.db.get_session() as session:
            try:
                memory = session.query(Memory).filter(
                    Memory.category == category,
                    Memory.key == key
                ).first()
                
                if memory:
                    session.delete(memory)
                    session.commit()
                    self.logger.info(f"Deleted memory: {category}/{key}")
                    return True
                
                return False
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Failed to delete memory: {e}")
                return False
    
    def delete_category(self, category: str) -> int:
        """
        Delete all memories in a category.
        
        Args:
            category: Memory category
            
        Returns:
            Number of memories deleted
        """
        with self.db.get_session() as session:
            try:
                count = session.query(Memory).filter(
                    Memory.category == category
                ).delete()
                
                session.commit()
                self.logger.info(f"Deleted {count} memories from category: {category}")
                return count
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Failed to delete category memories: {e}")
                return 0
    
    def update_memory(
        self,
        category: str,
        key: str,
        value: Optional[str] = None,
        meta_data: Optional[Dict[str, Any]] = None,
        is_sensitive: Optional[bool] = None
    ) -> Optional[Memory]:
        """
        Update an existing memory item.
        
        Args:
            category: Memory category
            key: Memory key
            value: New value (optional)
            meta_data: New metadata (optional)
            is_sensitive: New sensitive flag (optional)
            
        Returns:
            The updated Memory object if found, None otherwise
        """
        with self.db.get_session() as session:
            try:
                memory = session.query(Memory).filter(
                    Memory.category == category,
                    Memory.key == key
                ).first()
                
                if memory:
                    if value is not None:
                        memory.value = value
                    if meta_data is not None:
                        memory.meta_data = meta_data
                    if is_sensitive is not None:
                        memory.is_sensitive = is_sensitive
                    
                    memory.updated_at = datetime.utcnow()
                    session.commit()
                    session.refresh(memory)
                    
                    self.logger.info(f"Updated memory: {category}/{key}")
                    return memory
                
                return None
                
            except Exception as e:
                session.rollback()
                self.logger.error(f"Failed to update memory: {e}")
                return None
    
    def get_all_categories(self) -> List[str]:
        """
        Get all unique memory categories.
        
        Returns:
            List of category names
        """
        with self.db.get_session() as session:
            try:
                categories = session.query(Memory.category).distinct().all()
                return [cat[0] for cat in categories]
                
            except Exception as e:
                self.logger.error(f"Failed to get categories: {e}")
                return []
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        with self.db.get_session() as session:
            try:
                total_memories = session.query(Memory).count()
                categories = session.query(Memory.category).distinct().count()
                sensitive_count = session.query(Memory).filter(
                    Memory.is_sensitive == True
                ).count()
                
                return {
                    "total_memories": total_memories,
                    "categories": categories,
                    "sensitive_count": sensitive_count
                }
                
            except Exception as e:
                self.logger.error(f"Failed to get memory stats: {e}")
                return {}


# Global memory manager instance
_memory_manager: Optional[MemoryManager] = None


def get_memory_manager() -> MemoryManager:
    """Get the global memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
