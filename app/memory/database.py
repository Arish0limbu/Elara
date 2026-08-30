"""
ELARA - Database Management
This module handles database initialization, connections, and operations.
"""

import os
from pathlib import Path
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from datetime import datetime, timedelta

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from sqlalchemy.exc import SQLAlchemyError

from app.memory.models import Base
from app.config.settings import get_settings
from app.utils.logger import get_logger
from app.utils.paths import ensure_directory


class DatabaseManager:
    """Manages database connections and operations for ELARA."""
    
    _instance: Optional['DatabaseManager'] = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._engine is not None:
            return
            
        self.logger = get_logger("elara.database")
        self.settings = get_settings()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize the database engine and session factory."""
        db_path = self.settings.database.path
        db_dir = db_path.parent
        
        # Ensure database directory exists
        ensure_directory(db_dir)
        
        # Create database URL
        database_url = f"sqlite:///{db_path}"
        
        self.logger.info(f"Initializing database at: {db_path}")
        
        # Create engine with connection pooling settings
        self._engine = create_engine(
            database_url,
            echo=self.settings.database.echo,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            pool_pre_ping=True
        )
        
        # Enable foreign key constraints for SQLite
        @event.listens_for(self._engine, "connect")
        def set_sqlite_pragma(dbapi_conn, connection_record):
            cursor = dbapi_conn.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        
        # Create session factory
        self._session_factory = sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
        
        # Create all tables
        self._create_tables()
        
        self.logger.info("Database initialized successfully")
    
    def _create_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(self._engine)
            self.logger.info("Database tables created successfully")
        except SQLAlchemyError as e:
            self.logger.error(f"Failed to create database tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Session:
        """Get a database session with automatic cleanup."""
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session_sync(self) -> Session:
        """Get a database session for manual management."""
        return self._session_factory()
    
    def backup_database(self, backup_path: Optional[Path] = None) -> Path:
        """
        Create a backup of the database.
        
        Args:
            backup_path: Optional path for the backup file
            
        Returns:
            Path to the backup file
        """
        import shutil
        from datetime import datetime
        
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = self.settings.database.path.parent / "backups"
            ensure_directory(backup_dir)
            backup_path = backup_dir / f"elara_backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.settings.database.path, backup_path)
            self.logger.info(f"Database backup created at: {backup_path}")
            return backup_path
        except Exception as e:
            self.logger.error(f"Failed to create database backup: {e}")
            raise
    
    def restore_database(self, backup_path: Path) -> None:
        """
        Restore database from a backup file.
        
        Args:
            backup_path: Path to the backup file
        """
        import shutil
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        try:
            # Close existing connections
            self._engine.dispose()
            
            # Restore from backup
            shutil.copy2(backup_path, self.settings.database.path)
            
            # Reinitialize database
            self._initialize_database()
            
            self.logger.info(f"Database restored from: {backup_path}")
        except Exception as e:
            self.logger.error(f"Failed to restore database: {e}")
            raise
    
    def cleanup_old_records(self, days: int = 30) -> int:
        """
        Clean up old records from the database.
        
        Args:
            days: Number of days to keep records
            
        Returns:
            Number of records deleted
        """
        from .models import CommandHistory, AuditEvent, Conversation
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        total_deleted = 0
        
        with self.get_session() as session:
            try:
                # Clean up old command history
                deleted_commands = session.query(CommandHistory).filter(
                    CommandHistory.created_at < cutoff_date
                ).delete()
                total_deleted += deleted_commands
                
                # Clean up old audit events
                deleted_audit = session.query(AuditEvent).filter(
                    AuditEvent.created_at < cutoff_date
                ).delete()
                total_deleted += deleted_audit
                
                # Clean up old conversations
                deleted_conversations = session.query(Conversation).filter(
                    Conversation.created_at < cutoff_date
                ).delete()
                total_deleted += deleted_conversations
                
                session.commit()
                self.logger.info(f"Cleaned up {total_deleted} old records")
                
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Failed to cleanup old records: {e}")
                raise
        
        return total_deleted
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with database statistics
        """
        stats = {
            "database_size": self.settings.database.path.stat().st_size if self.settings.database.path.exists() else 0,
            "tables": {}
        }
        
        with self.get_session() as session:
            try:
                from .models import (
                    Setting, Memory, Application, Workspace, CommandHistory,
                    AuditEvent, VoiceProfile, Conversation, Project, 
                    GitRepository, UserPreference, SecurityEvent, ScheduledTask
                )
                
                tables = [
                    ('settings', Setting),
                    ('memory', Memory),
                    ('applications', Application),
                    ('workspaces', Workspace),
                    ('command_history', CommandHistory),
                    ('audit_events', AuditEvent),
                    ('voice_profiles', VoiceProfile),
                    ('conversations', Conversation),
                    ('projects', Project),
                    ('git_repositories', GitRepository),
                    ('user_preferences', UserPreference),
                    ('security_events', SecurityEvent),
                    ('scheduled_tasks', ScheduledTask)
                ]
                
                for table_name, model in tables:
                    count = session.query(model).count()
                    stats["tables"][table_name] = count
                    
            except SQLAlchemyError as e:
                self.logger.error(f"Failed to get database stats: {e}")
        
        return stats
    
    def vacuum_database(self) -> None:
        """Vacuum the SQLite database to optimize storage."""
        with self.get_session() as session:
            try:
                session.execute("VACUUM")
                session.commit()
                self.logger.info("Database vacuumed successfully")
            except SQLAlchemyError as e:
                session.rollback()
                self.logger.error(f"Failed to vacuum database: {e}")
                raise
    
    def close(self) -> None:
        """Close the database connection."""
        if self._engine:
            self._engine.dispose()
            self.logger.info("Database connection closed")


# Global database manager instance
_db_manager: Optional[DatabaseManager] = None


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


def initialize_database() -> DatabaseManager:
    """Initialize the database and return the manager."""
    return get_database_manager()


# Import models for reference
from .models import (
    Setting, Memory, Application, Workspace, CommandHistory,
    AuditEvent, VoiceProfile, Conversation, Project,
    GitRepository, UserPreference, SecurityEvent, ScheduledTask
)
