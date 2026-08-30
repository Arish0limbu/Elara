"""
ELARA - Screenshot Capture
This module handles screenshot capture operations.
"""

from typing import Optional
from pathlib import Path
from datetime import datetime

try:
    from PIL import ImageGrab
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

from app.utils.logger import get_logger


class ScreenshotCapture:
    """Captures screenshots of the screen."""
    
    def __init__(self):
        self.logger = get_logger("elara.screenshots")
        
        if not PIL_AVAILABLE:
            self.logger.warning("PIL not available for screenshot capture")
        
        self.logger.info("Screenshot capture initialized")
    
    def capture_screen(self) -> Optional[object]:
        """
        Capture the entire screen.
        
        Returns:
            Screenshot image object or None
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            screenshot = ImageGrab.grab()
            self.logger.info("Screenshot captured")
            return screenshot
        except Exception as e:
            self.logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Optional[object]:
        """
        Capture a specific region of the screen.
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Region width
            height: Region height
            
        Returns:
            Screenshot image object or None
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            bbox = (x, y, x + width, y + height)
            screenshot = ImageGrab.grab(bbox=bbox)
            self.logger.info(f"Region screenshot captured: {bbox}")
            return screenshot
        except Exception as e:
            self.logger.error(f"Failed to capture region screenshot: {e}")
            return None
    
    def save_screenshot(
        self,
        screenshot: object,
        output_path: Optional[Path] = None,
        filename: Optional[str] = None
    ) -> Optional[Path]:
        """
        Save a screenshot to file.
        
        Args:
            screenshot: Screenshot image object
            output_path: Output directory path
            filename: Custom filename (without extension)
            
        Returns:
            Path to saved file or None
        """
        if not PIL_AVAILABLE or screenshot is None:
            return None
        
        try:
            # Generate filename if not provided
            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}"
            
            # Add extension
            if not filename.endswith('.png'):
                filename += '.png'
            
            # Determine output path
            if output_path is None:
                from app.config.constants import PROJECT_ROOT
                output_path = PROJECT_ROOT / "screenshots"
            
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
            
            full_path = output_path / filename
            
            # Save screenshot
            screenshot.save(str(full_path))
            self.logger.info(f"Screenshot saved to {full_path}")
            
            return full_path
            
        except Exception as e:
            self.logger.error(f"Failed to save screenshot: {e}")
            return None
    
    def capture_and_save(
        self,
        output_path: Optional[Path] = None,
        filename: Optional[str] = None
    ) -> Optional[Path]:
        """
        Capture and save screenshot in one operation.
        
        Args:
            output_path: Output directory path
            filename: Custom filename
            
        Returns:
            Path to saved file or None
        """
        screenshot = self.capture_screen()
        if screenshot is None:
            return None
        
        return self.save_screenshot(screenshot, output_path, filename)
    
    def capture_active_window(self) -> Optional[object]:
        """
        Capture the active window.
        
        Returns:
            Screenshot image object or None
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            # Get active window bounding box
            import win32gui
            hwnd = win32gui.GetForegroundWindow()
            rect = win32gui.GetWindowRect(hwnd)
            
            # Capture region
            screenshot = self.capture_region(rect[0], rect[1], rect[2] - rect[0], rect[3] - rect[1])
            
            self.logger.info("Active window screenshot captured")
            return screenshot
            
        except Exception as e:
            self.logger.error(f"Failed to capture active window: {e}")
            return None
    
    def get_screen_size(self) -> Optional[tuple]:
        """
        Get the screen dimensions.
        
        Returns:
            Tuple of (width, height) or None
        """
        if not PIL_AVAILABLE:
            return None
        
        try:
            screenshot = self.capture_screen()
            if screenshot:
                return screenshot.size
            return None
        except Exception as e:
            self.logger.error(f"Failed to get screen size: {e}")
            return None
