"""
ELARA - Utilities Module
This module provides utility functions for logging, path handling, and general helpers.
"""

from .logger import ElaraLogger, get_logger, setup_logging
from .paths import (
    get_project_root,
    ensure_directory,
    is_safe_path,
    is_system_path,
    sanitize_path,
    get_absolute_path,
    file_exists,
    directory_exists,
    get_file_size,
    get_unique_filename,
    clean_directory,
    get_relative_path,
    is_windows,
    get_home_directory,
    get_downloads_directory,
    get_documents_directory,
    get_desktop_directory,
    find_executable,
    is_executable
)
from .helpers import (
    async_wrapper,
    retry_on_failure,
    timing_decorator,
    generate_id,
    hash_string,
    sanitize_string,
    format_duration,
    format_file_size,
    parse_time_string,
    truncate_text,
    safe_json_loads,
    debounce,
    throttle,
    validate_email,
    validate_url,
    get_timestamp,
    parse_timestamp,
    is_expired,
    mask_sensitive_data
)

__all__ = [
    # Logger
    "ElaraLogger",
    "get_logger", 
    "setup_logging",
    # Paths
    "get_project_root",
    "ensure_directory",
    "is_safe_path",
    "is_system_path",
    "sanitize_path",
    "get_absolute_path",
    "file_exists",
    "directory_exists",
    "get_file_size",
    "get_unique_filename",
    "clean_directory",
    "get_relative_path",
    "is_windows",
    "get_home_directory",
    "get_downloads_directory",
    "get_documents_directory",
    "get_desktop_directory",
    "find_executable",
    "is_executable",
    # Helpers
    "async_wrapper",
    "retry_on_failure",
    "timing_decorator",
    "generate_id",
    "hash_string",
    "sanitize_string",
    "format_duration",
    "format_file_size",
    "parse_time_string",
    "truncate_text",
    "safe_json_loads",
    "debounce",
    "throttle",
    "validate_email",
    "validate_url",
    "get_timestamp",
    "parse_timestamp",
    "is_expired",
    "mask_sensitive_data"
]
