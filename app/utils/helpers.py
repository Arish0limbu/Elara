"""
ELARA - Helper Functions
This module provides various utility helper functions used throughout the application.
"""

import asyncio
import functools
import time
from typing import Callable, Any, Optional, TypeVar, Coroutine
from datetime import datetime, timedelta
import hashlib
import secrets
import string

T = TypeVar('T')


def async_wrapper(coro: Coroutine[Any, Any, T]) -> T:
    """
    Wrapper to run async functions from sync code.
    
    Args:
        coro: The coroutine to run
        
    Returns:
        The result of the coroutine
    """
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


def retry_on_failure(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to retry a function on failure with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
        exceptions: Tuple of exceptions to catch and retry on
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            raise last_exception
        
        return wrapper
    return decorator


def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure and log function execution time.
    
    Args:
        func: The function to decorate
        
    Returns:
        The decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            raise e
    
    return wrapper


def generate_id(length: int = 16) -> str:
    """
    Generate a random unique identifier.
    
    Args:
        length: The length of the identifier
        
    Returns:
        A random string identifier
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def hash_string(value: str, algorithm: str = "sha256") -> str:
    """
    Hash a string using the specified algorithm.
    
    Args:
        value: The string to hash
        algorithm: The hashing algorithm to use
        
    Returns:
        The hexadecimal hash digest
    """
    hasher = hashlib.new(algorithm)
    hasher.update(value.encode('utf-8'))
    return hasher.hexdigest()


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize a string by removing potentially dangerous characters.
    
    Args:
        text: The string to sanitize
        max_length: Maximum length of the result string
        
    Returns:
        The sanitized string
    """
    # Remove null bytes and other control characters except newlines and tabs
    sanitized = ''.join(char for char in text if char == '\n' or char == '\t' or ord(char) >= 32)
    
    # Truncate if max_length is specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()


def format_duration(seconds: float) -> str:
    """
    Format a duration in seconds to a human-readable string.
    
    Args:
        seconds: The duration in seconds
        
    Returns:
        A formatted duration string
    """
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def format_file_size(bytes_size: int) -> str:
    """
    Format a file size in bytes to a human-readable string.
    
    Args:
        bytes_size: The size in bytes
        
    Returns:
        A formatted file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def parse_time_string(time_str: str) -> Optional[datetime]:
    """
    Parse a time string into a datetime object.
    
    Args:
        time_str: The time string to parse
        
    Returns:
        A datetime object or None if parsing fails
    """
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%H:%M:%S",
        "%H:%M"
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    
    return None


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with a suffix.
    
    Args:
        text: The text to truncate
        max_length: Maximum length of the result
        suffix: Suffix to add if truncated
        
    Returns:
        The truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse a JSON string with a default value on failure.
    
    Args:
        json_str: The JSON string to parse
        default: The default value if parsing fails
        
    Returns:
        The parsed JSON object or the default value
    """
    import json
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return default


def debounce(wait: float):
    """
    Decorator to debounce a function call.
    
    Args:
        wait: Minimum time between calls in seconds
    """
    def decorator(func: Callable) -> Callable:
        last_called = [0]
        timer = [None]
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            def call_function():
                last_called[0] = time.time()
                return func(*args, **kwargs)
            
            current_time = time.time()
            time_since_last_call = current_time - last_called[0]
            
            if time_since_last_call >= wait:
                return call_function()
            else:
                # Cancel any pending call
                if timer[0] is not None:
                    timer[0].cancel()
                
                # Schedule new call
                delay = wait - time_since_last_call
                import threading
                timer[0] = threading.Timer(delay, call_function)
                timer[0].start()
        
        return wrapper
    return decorator


def throttle(wait: float):
    """
    Decorator to throttle a function call.
    
    Args:
        wait: Minimum time between calls in seconds
    """
    def decorator(func: Callable) -> Callable:
        last_called = [0]
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_time = time.time()
            time_since_last_call = current_time - last_called[0]
            
            if time_since_last_call >= wait:
                last_called[0] = current_time
                return func(*args, **kwargs)
            else:
                # Skip this call
                return None
        
        return wrapper
    return decorator


def validate_email(email: str) -> bool:
    """
    Validate an email address format.
    
    Args:
        email: The email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """
    Validate a URL format.
    
    Args:
        url: The URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    import re
    pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return re.match(pattern, url) is not None


def get_timestamp() -> str:
    """
    Get the current timestamp as a formatted string.
    
    Returns:
        The current timestamp in ISO format
    """
    return datetime.now().isoformat()


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """
    Parse a timestamp string into a datetime object.
    
    Args:
        timestamp_str: The timestamp string to parse
        
    Returns:
        A datetime object or None if parsing fails
    """
    try:
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError):
        return None


def is_expired(timestamp: datetime, ttl_seconds: float) -> bool:
    """
    Check if a timestamp has expired based on a time-to-live.
    
    Args:
        timestamp: The timestamp to check
        ttl_seconds: Time-to-live in seconds
        
    Returns:
        True if expired, False otherwise
    """
    if isinstance(timestamp, str):
        timestamp = parse_timestamp(timestamp)
        if timestamp is None:
            return True
    
    return datetime.now() > timestamp + timedelta(seconds=ttl_seconds)


def mask_sensitive_data(data: str, visible_chars: int = 4, mask_char: str = "*") -> str:
    """
    Mask sensitive data by showing only a few characters.
    
    Args:
        data: The sensitive data to mask
        visible_chars: Number of characters to keep visible
        mask_char: Character to use for masking
        
    Returns:
        The masked data
    """
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)
