"""
ELARA - Windows Application Control
This module handles Windows application launching, closing, and management.
"""

import subprocess
import os
from typing import Optional, List, Dict, Any
from pathlib import Path
import time

try:
    import win32api
    import win32con
    import win32process
    import win32gui
    WIN32_AVAILABLE = True
except ImportError:
    WIN32_AVAILABLE = False

from app.config.settings import get_settings
from app.utils.logger import get_logger
from app.utils.paths import find_executable, is_executable


class ApplicationManager:
    """Manages Windows applications."""
    
    def __init__(self):
        self.logger = get_logger("elara.applications")
        self.settings = get_settings()
        
        # Application registry
        self._app_registry: Dict[str, Dict] = {}
        
        # Load built-in applications
        self._load_builtin_applications()
        
        self.logger.info("Application manager initialized")
    
    def _load_builtin_applications(self):
        """Load built-in application definitions."""
        builtin_apps = {
            "chrome": {
                "name": "Google Chrome",
                "aliases": ["chrome", "google chrome", "browser"],
                "executable": "chrome.exe",
                "paths": [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                ]
            },
            "vscode": {
                "name": "Visual Studio Code",
                "aliases": ["vscode", "code", "visual studio code"],
                "executable": "code.exe",
                "paths": [
                    r"C:\Users\{}\AppData\Local\Programs\Microsoft VS Code\Code.exe".format(os.getenv('USERNAME')),
                    r"C:\Program Files\Microsoft VS Code\Code.exe"
                ]
            },
            "discord": {
                "name": "Discord",
                "aliases": ["discord"],
                "executable": "Discord.exe",
                "paths": [
                    r"C:\Users\{}\AppData\Local\Discord\app-1.0.9*\Discord.exe".format(os.getenv('USERNAME')),
                    r"C:\Program Files\Discord\Discord.exe"
                ]
            },
            "notepad": {
                "name": "Notepad",
                "aliases": ["notepad", "text editor"],
                "executable": "notepad.exe",
                "paths": ["notepad.exe"]
            },
            "explorer": {
                "name": "File Explorer",
                "aliases": ["explorer", "file explorer", "windows explorer"],
                "executable": "explorer.exe",
                "paths": ["explorer.exe"]
            },
            "edge": {
                "name": "Microsoft Edge",
                "aliases": ["edge", "microsoft edge"],
                "executable": "msedge.exe",
                "paths": [
                    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
                ]
            }
        }
        
        for app_id, app_info in builtin_apps.items():
            self._app_registry[app_id] = app_info
        
        self.logger.info(f"Loaded {len(builtin_apps)} built-in applications")
    
    def find_application(self, name: str) -> Optional[Dict]:
        """
        Find an application by name or alias.
        
        Args:
            name: Application name or alias
            
        Returns:
            Application info dictionary or None
        """
        name_lower = name.lower().strip()
        
        # Search by exact ID
        if name_lower in self._app_registry:
            return self._app_registry[name_lower]
        
        # Search by aliases
        for app_id, app_info in self._app_registry.items():
            if name_lower in [alias.lower() for alias in app_info['aliases']]:
                return app_info
            
            if name_lower == app_info['name'].lower():
                return app_info
        
        return None
    
    def get_application_path(self, name: str) -> Optional[str]:
        """
        Get the executable path for an application.
        
        Args:
            name: Application name or alias
            
        Returns:
            Executable path or None
        """
        app_info = self.find_application(name)
        if not app_info:
            return None
        
        # Try registered paths
        for path in app_info.get('paths', []):
            if path == app_info['executable']:
                # System executable
                if self._is_system_executable(path):
                    return path
            else:
                # Full path
                if Path(path).exists():
                    return path
        
        # Try to find executable
        executable = find_executable(app_info['executable'])
        if executable:
            return str(executable)
        
        return None
    
    def _is_system_executable(self, name: str) -> bool:
        """Check if an executable is available in system PATH."""
        return find_executable(name) is not None
    
    def launch_application(
        self,
        name: str,
        args: Optional[List[str]] = None,
        wait: bool = False
    ) -> bool:
        """
        Launch an application.
        
        Args:
            name: Application name or alias
            args: Optional command line arguments
            wait: Whether to wait for application to start
            
        Returns:
            True if launched successfully
        """
        try:
            app_path = self.get_application_path(name)
            if not app_path:
                self.logger.warning(f"Application not found: {name}")
                return False
            
            self.logger.info(f"Launching application: {name} ({app_path})")
            
            # Build command
            cmd = [app_path]
            if args:
                cmd.extend(args)
            
            # Launch application
            if wait:
                subprocess.Popen(cmd, shell=True)
                time.sleep(2)  # Wait for application to start
            else:
                subprocess.Popen(cmd, shell=True)
            
            self.logger.info(f"Application launched: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to launch application {name}: {e}")
            return False
    
    def close_application(self, name: str) -> bool:
        """
        Close an application by name.
        
        Args:
            name: Application name or alias
            
        Returns:
            True if closed successfully
        """
        if not WIN32_AVAILABLE:
            self.logger.warning("pywin32 not available for application control")
            return False
        
        try:
            app_info = self.find_application(name)
            if not app_info:
                self.logger.warning(f"Application not found: {name}")
                return False
            
            executable_name = app_info['executable'].lower()
            
            # Find and close all matching processes
            closed_count = 0
            
            def window_callback(hwnd, extra):
                """Callback to enumerate windows."""
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                    
                    try:
                        name = win32process.GetModuleFileNameEx(handle, 0)
                        if executable_name in name.lower():
                            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
                            return True
                    finally:
                        win32api.CloseHandle(handle)
                except:
                    pass
                return False
            
            win32gui.EnumWindows(window_callback, None)
            
            self.logger.info(f"Closed application: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to close application {name}: {e}")
            return False
    
    def is_application_running(self, name: str) -> bool:
        """
        Check if an application is currently running.
        
        Args:
            name: Application name or alias
            
        Returns:
            True if application is running
        """
        if not WIN32_AVAILABLE:
            return False
        
        try:
            app_info = self.find_application(name)
            if not app_info:
                return False
            
            executable_name = app_info['executable'].lower()
            
            # Check if any process with this executable is running
            def window_callback(hwnd, extra):
                """Callback to enumerate windows."""
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                    
                    try:
                        name = win32process.GetModuleFileNameEx(handle, 0)
                        if executable_name in name.lower():
                            return True
                    finally:
                        win32api.CloseHandle(handle)
                except:
                    pass
                return False
            
            result = []
            win32gui.EnumWindows(lambda hwnd, param: result.append(window_callback(hwnd, param)), None)
            
            return any(result)
            
        except Exception as e:
            self.logger.error(f"Failed to check application status: {e}")
            return False
    
    def get_running_applications(self) -> List[Dict]:
        """
        Get list of currently running applications.
        
        Returns:
            List of application info dictionaries
        """
        if not WIN32_AVAILABLE:
            return []
        
        try:
            running_apps = []
            seen_processes = set()
            
            def window_callback(hwnd, extra):
                """Callback to enumerate windows."""
                try:
                    if not win32gui.IsWindowVisible(hwnd):
                        return
                    
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    
                    if pid in seen_processes:
                        return
                    
                    seen_processes.add(pid)
                    
                    handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
                    
                    try:
                        name = win32process.GetModuleFileNameEx(handle, 0)
                        title = win32gui.GetWindowText(hwnd)
                        
                        if name and title:
                            running_apps.append({
                                'pid': pid,
                                'name': Path(name).name,
                                'path': name,
                                'title': title
                            })
                    finally:
                        win32api.CloseHandle(handle)
                except:
                    pass
                return
            
            win32gui.EnumWindows(window_callback, None)
            
            return running_apps
            
        except Exception as e:
            self.logger.error(f"Failed to get running applications: {e}")
            return []
    
    def register_application(
        self,
        app_id: str,
        name: str,
        executable: str,
        paths: Optional[List[str]] = None,
        aliases: Optional[List[str]] = None
    ) -> bool:
        """
        Register a custom application.
        
        Args:
            app_id: Unique application identifier
            name: Display name
            executable: Executable name
            paths: List of possible paths
            aliases: List of aliases
            
        Returns:
            True if registered successfully
        """
        try:
            self._app_registry[app_id.lower()] = {
                'name': name,
                'executable': executable,
                'paths': paths or [],
                'aliases': aliases or []
            }
            
            self.logger.info(f"Registered application: {name} ({app_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register application: {e}")
            return False
    
    def unregister_application(self, app_id: str) -> bool:
        """
        Unregister an application.
        
        Args:
            app_id: Application identifier
            
        Returns:
            True if unregistered successfully
        """
        if app_id.lower() in self._app_registry:
            del self._app_registry[app_id.lower()]
            self.logger.info(f"Unregistered application: {app_id}")
            return True
        
        return False
    
    def list_applications(self) -> List[Dict]:
        """List all registered applications."""
        return [
            {
                'id': app_id,
                'name': app_info['name'],
                'aliases': app_info['aliases']
            }
            for app_id, app_info in self._app_registry.items()
        ]
    
    def open_url(self, url: str) -> bool:
        """
        Open a URL in the default browser.
        
        Args:
            url: URL to open
            
        Returns:
            True if opened successfully
        """
        try:
            import webbrowser
            webbrowser.open(url)
            self.logger.info(f"Opened URL: {url}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open URL: {e}")
            return False
    
    def open_file(self, file_path: str) -> bool:
        """
        Open a file with the default application.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if opened successfully
        """
        try:
            path = Path(file_path)
            if not path.exists():
                self.logger.warning(f"File not found: {file_path}")
                return False
            
            os.startfile(str(path))
            self.logger.info(f"Opened file: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to open file: {e}")
            return False


class ApplicationLauncher:
    """Simplified application launcher for common operations."""
    
    def __init__(self):
        self.logger = get_logger("elara.launcher")
        self.manager = ApplicationManager()
    
    def launch(self, name: str) -> bool:
        """Launch an application by name."""
        return self.manager.launch_application(name)
    
    def close(self, name: str) -> bool:
        """Close an application by name."""
        return self.manager.close_application(name)
    
    def is_running(self, name: str) -> bool:
        """Check if application is running."""
        return self.manager.is_application_running(name)
    
    def get_running(self) -> List[str]:
        """Get list of running application names."""
        apps = self.manager.get_running_applications()
        return [app['name'] for app in apps]
