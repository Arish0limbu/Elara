"""
ELARA - Database Models
This module defines SQLAlchemy models for the SQLite database.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Setting(Base):
    """Model for application settings."""
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(255), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=True)
    category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Memory(Base):
    """Model for user memory storage."""
    __tablename__ = 'memory'
    
    id = Column(Integer, primary_key=True)
    category = Column(String(100), nullable=False, index=True)
    key = Column(String(255), nullable=False, index=True)
    value = Column(Text, nullable=True)
    meta_data = Column(JSON, nullable=True)
    is_sensitive = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )


class Application(Base):
    """Model for registered applications."""
    __tablename__ = 'applications'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    executable_path = Column(Text, nullable=False)
    aliases = Column(JSON, nullable=True)  # List of alias strings
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    enabled = Column(Boolean, default=True)
    auto_detected = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Workspace(Base):
    """Model for workspace directories."""
    __tablename__ = 'workspaces'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    path = Column(Text, nullable=False, unique=True)
    description = Column(Text, nullable=True)
    is_default = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class CommandHistory(Base):
    """Model for command execution history."""
    __tablename__ = 'command_history'
    
    id = Column(Integer, primary_key=True)
    user_input = Column(Text, nullable=False)
    transcript = Column(Text, nullable=True)
    intent = Column(String(255), nullable=True)
    action = Column(String(255), nullable=True)
    parameters = Column(JSON, nullable=True)
    permission_level = Column(String(50), nullable=True)
    required_confirmation = Column(Boolean, default=False)
    user_confirmed = Column(Boolean, nullable=True)
    execution_result = Column(Text, nullable=True)
    success = Column(Boolean, nullable=True)
    error_message = Column(Text, nullable=True)
    execution_time_ms = Column(Float, nullable=True)
    user_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class AuditEvent(Base):
    """Model for security audit events."""
    __tablename__ = 'audit_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False, index=True)
    severity = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    user_id = Column(String(100), nullable=True, index=True)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class VoiceProfile(Base):
    """Model for user voice profiles."""
    __tablename__ = 'voice_profiles'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    embedding_data = Column(JSON, nullable=True)  # Store voice embedding
    enrollment_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_verified = Column(DateTime, nullable=True)
    verification_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    threshold = Column(Float, default=0.75)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Conversation(Base):
    """Model for conversation history."""
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(50), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class Project(Base):
    """Model for coding projects."""
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    path = Column(Text, nullable=False, unique=True)
    project_type = Column(String(100), nullable=True)  # 'python', 'javascript', etc.
    language = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    workspace_id = Column(Integer, ForeignKey('workspaces.id'), nullable=True)
    meta_data = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    last_accessed = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    workspace = relationship("Workspace", backref="projects")


class GitRepository(Base):
    """Model for Git repositories."""
    __tablename__ = 'git_repositories'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
    path = Column(Text, nullable=False, unique=True)
    remote_url = Column(Text, nullable=True)
    branch = Column(String(255), nullable=True)
    last_commit = Column(String(100), nullable=True)
    last_sync = Column(DateTime, nullable=True)
    is_github = Column(Boolean, default=False)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    project = relationship("Project", backref="git_repositories")


class UserPreference(Base):
    """Model for user preferences."""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)
    value_type = Column(String(50), default='string')  # 'string', 'int', 'bool', 'json'
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        {'sqlite_autoincrement': True}
    )


class SecurityEvent(Base):
    """Model for security-related events."""
    __tablename__ = 'security_events'
    
    id = Column(Integer, primary_key=True)
    event_type = Column(String(100), nullable=False, index=True)
    risk_level = Column(String(50), nullable=False, index=True)  # 'low', 'medium', 'high', 'critical'
    description = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)  # 'voice', 'ai', 'user', 'system'
    details = Column(JSON, nullable=True)
    was_blocked = Column(Boolean, default=False)
    action_taken = Column(Text, nullable=True)
    user_id = Column(String(100), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)


class ScheduledTask(Base):
    """Model for scheduled tasks."""
    __tablename__ = 'scheduled_tasks'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    task_type = Column(String(100), nullable=False)
    schedule = Column(String(100), nullable=True)  # Cron expression or interval
    parameters = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    last_run = Column(DateTime, nullable=True)
    next_run = Column(DateTime, nullable=True)
    run_count = Column(Integer, default=0)
    last_result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
