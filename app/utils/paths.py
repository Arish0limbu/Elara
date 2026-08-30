"""
ELARA - Path Utilities
This module provides utility functions for handling file paths and directories.
"""

import os
import shutil
from pathlib import Path
from typing import Optional, List
import platform

from app.config.constants import PROJECT_ROOT, BLOCKED_SYSTEM_PATHS


def get_project_root() -> Path:
    """Get the project root directory."""
    return PROJECT_ROOT


def ensure_directory(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_safe_path(path: Path, allowed_directories: List[Path]) -> bool:
    """
    Check if a path is safe for operations.
    
    Args:
        path: The path to check
        allowed_directories: List of directories where operations are allowed
        
    Returns:
        True if the path is safe, False otherwise
    """
    path = Path(path).resolve()
    
    # Check against blocked system paths
    for blocked in BLOCKED_SYSTEM_PATHS:
        try:
            if path.is_relative_to(Path(blocked).resolve()):
                return False
        except (ValueError, TypeError):
            # Handle cases where paths can't be compared
            if str(path).lower().startswith(str(blocked).lower()):
                return False
    
    # Check if path is within allowed directories
    for allowed in allowed_directories:
        try:
            if path.is_relative_to(Path(allowed).resolve()):
                return True
        except (ValueError, TypeError):
            if str(path).lower().startswith(str(allowed).lower()):
                return True
    
    return False


def is_system_path(path: Path) -> bool:
    """Check if a path is a system path that should be protected."""
    path = Path(path).resolve()
    
    for blocked in BLOCKED_SYSTEM_PATHS:
        try:
            if path.is_relative_to(Path(blocked).resolve()):
                return True
        except (ValueError, TypeError):
            if str(path).lower().startswith(str(blocked).lower()):
                return True
    
    return False


def sanitize_path(path: Path) -> Path:
    """
    Sanitize a path to prevent path traversal attacks.
    
    Args:
        path: The path to sanitize
        
    Returns:
        A sanitized absolute path
    """
    path = Path(path).resolve()
    
    # Remove any parent directory references that might have been added
    # by resolving the path
    try:
        path = path.resolve()
    except (OSError, RuntimeError):
        # If resolution fails, try to create a safe path
        path = Path(str(path).replace("..", "").replace("~", ""))
    
    return path


def get_absolute_path(path: Path, base: Optional[Path] = None) -> Path:
    """
    Convert a relative path to an absolute path based on a base directory.
    
    Args:
        path: The path to convert
        base: The base directory (defaults to project root)
        
    Returns:
        An absolute path
    """
    if base is None:
        base = PROJECT_ROOT
    
    path = Path(path)
    if not path.is_absolute():
        path = (base / path).resolve()
    
    return path


def file_exists(path: Path) -> bool:
    """Check if a file exists."""
    return Path(path).exists() and Path(path).is_file()


def directory_exists(path: Path) -> bool:
    """Check if a directory exists."""
    return Path(path).exists() and Path(path).is_dir()


def get_file_size(path: Path) -> int:
    """Get the size of a file in bytes."""
    try:
        return Path(path).stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def get_unique_filename(path: Path) -> Path:
    """
    Generate a unique filename if the given path already exists.
    
    Args:
        path: The desired file path
        
    Returns:
        A unique file path
    """
    path = Path(path)
    if not path.exists():
        return path
    
    base = path.stem
    extension = path.suffix
    parent = path.parent
    
    counter = 1
    while True:
        new_path = parent / f"{base}_{counter}{extension}"
        if not new_path.exists():
            return new_path
        counter += 1


def clean_directory(path: Path, keep_files: Optional[List[str]] = None) -> None:
    """
    Clean a directory by removing all files except specified ones.
    
    Args:
        path: The directory to clean
        keep_files: List of filenames to keep
    """
    path = Path(path)
    if not path.exists() or not path.is_dir():
        return
    
    keep_files = keep_files or []
    
    for item in path.iterdir():
        if item.is_file() and item.name not in keep_files:
            try:
                item.unlink()
            except OSError:
                pass


def get_relative_path(path: Path, base: Path) -> Path:
    """
    Get the relative path from a base directory.
    
    Args:
        path: The target path
        base: The base directory
        
    Returns:
        The relative path
    """
    try:
        return Path(path).relative_to(Path(base))
    except ValueError:
        # If path is not relative to base, return absolute path
        return Path(path).resolve()


def is_windows() -> bool:
    """Check if the operating system is Windows."""
    return platform.system() == "Windows"


def get_home_directory() -> Path:
    """Get the user's home directory."""
    return Path.home()


def get_downloads_directory() -> Path:
    """Get the user's Downloads directory."""
    home = get_home_directory()
    if is_windows():
        downloads = home / "Downloads"
    else:
        downloads = home / "Downloads"
    
    return downloads if downloads.exists() else home


def get_documents_directory() -> Path:
    """Get the user's Documents directory."""
    home = get_home_directory()
    if is_windows():
        documents = home / "Documents"
    else:
        documents = home / "Documents"
    
    return documents if documents.exists() else home


def get_desktop_directory() -> Path:
    """Get the user's Desktop directory."""
    home = get_home_directory()
    if is_windows():
        desktop = home / "Desktop"
    else:
        desktop = home / "Desktop"
    
    return desktop if desktop.exists() else home


def find_executable(name: str) -> Optional[Path]:
    """
    Find an executable in the system PATH.
    
    Args:
        name: The name of the executable to find
        
    Returns:
        The path to the executable if found, None otherwise
    """
    from shutil import which
    result = which(name)
    return Path(result) if result else None


def is_executable(path: Path) -> bool:
    """Check if a file is executable."""
    path = Path(path)
    if not path.exists():
        return False
    
    if is_windows():
        return path.suffix.lower() in {'.exe', '.bat', '.cmd', '.ps1'}
    else:
        return os.access(path, os.X_OK)
