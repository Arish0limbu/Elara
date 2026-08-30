"""
ELARA - Window Management
This module handles Windows window management operations.
"""

from typing import Optional, List, Dict, Any
import time

try:
    import win32gui
    import win32con
    import win32process
    import win32api
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

from app.utils.logger import get_logger


class WindowManager:
    """Manages Windows window operations."""
    
    def __init__(self):
        self.logger = get_logger("elara.windows")
        
        if not WIN32_AVAILABLE:
            self.logger.warning("pywin32 not available for window management")
        
        self.logger.info("Window manager initialized")
    
    def find_window_by_title(self, title: str) -> Optional[int]:
        """
        Find window handle by title.
        
        Args:
            title: Window title (partial match)
            
        Returns:
            Window handle or None
        """
        if not WIN32_AVAILABLE:
            return None
        
        try:
            title_lower = title.lower()
            
            def callback(hwnd, windows):
                """Callback to enumerate windows."""
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if title_lower in window_title.lower():
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            
            return windows[0] if windows else None
            
        except Exception as e:
            self.logger.error(f"Failed to find window: {e}")
            return None
    
    def find_windows_by_process(self, process_name: str) -> List[int]:
        """
        Find windows by process name.
        
        Args:
            process_name: Process executable name
            
        Returns:
            List of window handles
        """
        if not WIN32_AVAILABLE:
            return []
        
        try:
            process_name_lower = process_name.lower()
            windows = []
            
            def callback(hwnd, extra):
                """Callback to enumerate windows."""
                try:
                    if not win32gui.IsWindowVisible(hwnd):
                        return
                    
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                    
                    try:
                        name = win32process.GetModuleFileNameEx(handle, 0)
                        if process_name_lower in name.lower():
                            windows.append(hwnd)
                    finally:
                        win32api.CloseHandle(handle)
                except:
                    pass
                return True
            
            win32gui.EnumWindows(callback, None)
            
            return windows
            
        except Exception as e:
            self.logger.error(f"Failed to find windows by process: {e}")
            return []
    
    def minimize_window(self, hwnd: int) -> bool:
        """
        Minimize a window.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful
        """
        if not WIN32_AVAILABLE:
            return False
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            self.logger.debug(f"Minimized window: {hwnd}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to minimize window: {e}")
            return False
    
    def maximize_window(self, hwnd: int) -> bool:
        """
        Maximize a window.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful
        """
        if not WIN32_AVAILABLE:
            return False
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            self.logger.debug(f"Maximized window: {hwnd}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to maximize window: {e}")
            return False
    
    def restore_window(self, hwnd: int) -> bool:
        """
        Restore a window to normal size.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful
        """
        if not WIN32_AVAILABLE:
            return False
        
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            self.logger.debug(f"Restored window: {hwnd}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restore window: {e}")
            return False
    
    def close_window(self, hwnd: int) -> bool:
        """
        Close a window.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful
        """
        if not WIN32_AVAILABLE:
            return False
        
        try:
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            self.logger.debug(f"Closed window: {hwnd}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to close window: {e}")
            return False
    
    def set_foreground_window(self, hwnd: int) -> bool:
        """
        Bring a window to the foreground.
        
        Args:
            hwnd: Window handle
            
        Returns:
            True if successful
        """
        if not WIN32_AVAILABLE:
            return False
        
        try:
            # Check if window is minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.1)
            
            # Bring to foreground
            win32gui.SetForegroundWindow(hwnd)
            self.logger.debug(f"Set foreground window: {hwnd}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set foreground window: {e}")
            return False
    
    def get_window_info(self, hwnd: int) -> Optional[Dict]:
        """
        Get information about a window.
        
        Args:
            hwnd: Window handle
            
        Returns:
            Window information dictionary
        """
        if not WIN32_AVAILABLE:
            return None
        
        try:
            rect = win32gui.GetWindowRect(hwnd)
            title = win32gui.GetWindowText(hwnd)
            class_name = win32gui.GetClassName(hwnd)
            
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            
            return {
                'hwnd': hwnd,
                'title': title,
                'class': class_name,
                'pid': pid,
                'rect': {
                    'left': rect[0],
                    'top': rect[1],
                    'right': rect[2],
                    'bottom': rect[3]
                },
                'width': rect[2] - rect[0],
                'height': rect[3] - rect[1]
            }
        except Exception as e:
            self.logger.error(f"Failed to get window info: {e}")
            return None
    
    def get_all_windows(self) -> List[Dict]:
        """
        Get information about all visible windows.
        
        Returns:
            List of window information dictionaries
        """
        if not WIN32_AVAILABLE:
            return []
        
        try:
            windows = []
            
            def callback(hwnd, extra):
                """Callback to enumerate windows."""
                try:
                    if win32gui.IsWindowVisible(hwnd):
                        info = self.get_window_info(hwnd)
                        if info and info['title']:  # Only include windows with titles
                            windows.append(info)
                except:
                    pass
                return True
            
            win32gui.EnumWindows(callback, None)
            
            return windows
            
        except Exception as e:
            self.logger.error(f"Failed to get all windows: {e}")
            return []
    
    def move_window(self, hwnd: int, x: int, y: int, width: int, height: int) -> bool:
        """
        Move and resize a window.
        
        Args:
            hwnd: Window handle
            x: New X position
            y: New Y position
            width: New width
            height: New height
            
        Returns:
            True if successful
        """
        if not WIN32_AVAILABLE:
            return False
        
        try:
            win32gui.SetWindowPos(hwnd, None, x, y, width, height, 0)
            self.logger.debug(f"Moved window {hwnd} to ({x}, {y}) with size {width}x{height}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to move window: {e}")
            return False


try:
    import win32api
except ImportError:
    pass
