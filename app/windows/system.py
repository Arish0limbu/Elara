"""
ELARA - System Operations
This module handles Windows system operations.
"""

from typing import Optional, Dict, Any
import subprocess
import os
from pathlib import Path

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from app.utils.logger import get_logger


class SystemOperations:
    """Handles Windows system operations."""
    
    def __init__(self):
        self.logger = get_logger("elara.system")
        
        if not PSUTIL_AVAILABLE:
            self.logger.warning("psutil not available for some system operations")
        
        self.logger.info("System operations initialized")
    
    def get_system_info(self) -> Dict[str, Any]:
        """
        Get system information.
        
        Returns:
            Dictionary with system information
        """
        info = {
            'platform': 'Windows',
            'hostname': os.getenv('COMPUTERNAME', 'Unknown'),
            'username': os.getenv('USERNAME', 'Unknown')
        }
        
        if PSUTIL_AVAILABLE:
            try:
                info['cpu_count'] = psutil.cpu_count()
                info['memory_total'] = psutil.virtual_memory().total
                info['memory_available'] = psutil.virtual_memory().available
                info['disk_usage'] = psutil.disk_usage('/').percent
            except Exception as e:
                self.logger.error(f"Failed to get detailed system info: {e}")
        
        return info
    
    def lock_computer(self) -> bool:
        """
        Lock the computer.
        
        Returns:
            True if successful
        """
        try:
            subprocess.run(['rundll32.exe', 'user32.dll,LockWorkStation'], check=True)
            self.logger.info("Computer locked")
            return True
        except Exception as e:
            self.logger.error(f"Failed to lock computer: {e}")
            return False
    
    def restart_computer(self, force: bool = False) -> bool:
        """
        Restart the computer.
        
        Args:
            force: Force restart without confirmation
            
        Returns:
            True if command initiated successfully
        """
        try:
            if force:
                subprocess.run(['shutdown', '/r', '/f', '/t', '0'], check=True)
            else:
                subprocess.run(['shutdown', '/r', '/t', '30'], check=True)
            
            self.logger.info("Computer restart initiated")
            return True
        except Exception as e:
            self.logger.error(f"Failed to restart computer: {e}")
            return False
    
    def shutdown_computer(self, force: bool = False) -> bool:
        """
        Shutdown the computer.
        
        Args:
            force: Force shutdown without confirmation
            
        Returns:
            True if command initiated successfully
        """
        try:
            if force:
                subprocess.run(['shutdown', '/s', '/f', '/t', '0'], check=True)
            else:
                subprocess.run(['shutdown', '/s', '/t', '30'], check=True)
            
            self.logger.info("Computer shutdown initiated")
            return True
        except Exception as e:
            self.logger.error(f"Failed to shutdown computer: {e}")
            return False
    
    def cancel_shutdown(self) -> bool:
        """
        Cancel a scheduled shutdown or restart.
        
        Returns:
            True if successful
        """
        try:
            subprocess.run(['shutdown', '/a'], check=True)
            self.logger.info("Shutdown cancelled")
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel shutdown: {e}")
            return False
    
    def log_off(self) -> bool:
        """
        Log off the current user.
        
        Returns:
            True if successful
        """
        try:
            subprocess.run(['shutdown', '/l'], check=True)
            self.logger.info("User logged off")
            return True
        except Exception as e:
            self.logger.error(f"Failed to log off: {e}")
            return False
    
    def sleep_computer(self) -> bool:
        """
        Put the computer to sleep.
        
        Returns:
            True if successful
        """
        try:
            subprocess.run(['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0'], check=True)
            self.logger.info("Computer put to sleep")
            return True
        except Exception as e:
            self.logger.error(f"Failed to sleep computer: {e}")
            return False
    
    def hibernate_computer(self) -> bool:
        """
        Hibernate the computer.
        
        Returns:
            True if successful
        """
        try:
            subprocess.run(['shutdown', '/h'], check=True)
            self.logger.info("Computer hibernated")
            return True
        except Exception as e:
            self.logger.error(f"Failed to hibernate computer: {e}")
            return False
    
    def open_folder(self, folder_path: str) -> bool:
        """
        Open a folder in File Explorer.
        
        Args:
            folder_path: Path to folder
            
        Returns:
            True if successful
        """
        try:
            path = Path(folder_path)
            if not path.exists():
                self.logger.warning(f"Folder not found: {folder_path}")
                return False
            
            os.startfile(str(path))
            self.logger.info(f"Opened folder: {folder_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to open folder: {e}")
            return False
    
    def get_running_processes(self) -> list:
        """
        Get list of running processes.
        
        Returns:
            List of process information
        """
        if not PSUTIL_AVAILABLE:
            return []
        
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'username']):
                try:
                    processes.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'username': proc.info['username']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            return processes
        except Exception as e:
            self.logger.error(f"Failed to get running processes: {e}")
            return []
    
    def kill_process(self, pid: int) -> bool:
        """
        Kill a process by PID.
        
        Args:
            pid: Process ID
            
        Returns:
            True if successful
        """
        if not PSUTIL_AVAILABLE:
            return False
        
        try:
            proc = psutil.Process(pid)
            proc.kill()
            self.logger.info(f"Killed process: {pid}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to kill process {pid}: {e}")
            return False
    
    def get_disk_usage(self, path: str = '/') -> Optional[Dict]:
        """
        Get disk usage information.
        
        Args:
            path: Path to check
            
        Returns:
            Dictionary with disk usage info
        """
        if not PSUTIL_AVAILABLE:
            return None
        
        try:
            usage = psutil.disk_usage(path)
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent
            }
        except Exception as e:
            self.logger.error(f"Failed to get disk usage: {e}")
            return None
    
    def get_memory_usage(self) -> Optional[Dict]:
        """
        Get memory usage information.
        
        Returns:
            Dictionary with memory usage info
        """
        if not PSUTIL_AVAILABLE:
            return None
        
        try:
            mem = psutil.virtual_memory()
            return {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'percent': mem.percent
            }
        except Exception as e:
            self.logger.error(f"Failed to get memory usage: {e}")
            return None
    
    def get_cpu_usage(self) -> Optional[float]:
        """
        Get current CPU usage.
        
        Returns:
            CPU usage percentage or None
        """
        if not PSUTIL_AVAILABLE:
            return None
        
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            self.logger.error(f"Failed to get CPU usage: {e}")
            return None
    
    def empty_recycle_bin(self) -> bool:
        """
        Empty the recycle bin.
        
        Returns:
            True if successful
        """
        try:
            subprocess.run(['powershell', '-Command', 'Clear-RecycleBin', '-Force'], check=True)
            self.logger.info("Recycle bin emptied")
            return True
        except Exception as e:
            self.logger.error(f"Failed to empty recycle bin: {e}")
            return False
    
    def get_uptime(self) -> Optional[str]:
        """
        Get system uptime.
        
        Returns:
            Formatted uptime string or None
        """
        if not PSUTIL_AVAILABLE:
            return None
        
        try:
            uptime = psutil.boot_time()
            from datetime import datetime
            boot_time = datetime.fromtimestamp(uptime)
            uptime_delta = datetime.now() - boot_time
            
            days = uptime_delta.days
            hours, remainder = divmod(uptime_delta.seconds, 3600)
            minutes, _ = divmod(remainder, 60)
            
            return f"{days}d {hours}h {minutes}m"
        except Exception as e:
            self.logger.error(f"Failed to get uptime: {e}")
            return None
