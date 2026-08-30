"""
ELARA - Volume Control
This module handles Windows volume control operations.
"""

from typing import Optional

try:
    import pycaw
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

from app.utils.logger import get_logger


class VolumeController:
    """Controls Windows system volume."""
    
    def __init__(self):
        self.logger = get_logger("elara.volume")
        
        if not PYCAW_AVAILABLE:
            self.logger.warning("pycaw not available for volume control")
            self._volume = None
        else:
            self._volume = self._get_default_volume_endpoint()
        
        self.logger.info("Volume controller initialized")
    
    def _get_default_volume_endpoint(self):
        """Get the default audio endpoint volume control."""
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            return volume
        except Exception as e:
            self.logger.error(f"Failed to get volume endpoint: {e}")
            return None
    
    def get_volume(self) -> Optional[float]:
        """
        Get current volume level.
        
        Returns:
            Volume level (0.0 to 1.0) or None
        """
        if not PYCAW_AVAILABLE or self._volume is None:
            return None
        
        try:
            return self._volume.GetMasterVolumeLevelScalar()
        except Exception as e:
            self.logger.error(f"Failed to get volume: {e}")
            return None
    
    def set_volume(self, level: float) -> bool:
        """
        Set volume level.
        
        Args:
            level: Volume level (0.0 to 1.0)
            
        Returns:
            True if successful
        """
        if not PYCAW_AVAILABLE or self._volume is None:
            return False
        
        try:
            level = max(0.0, min(1.0, level))
            self._volume.SetMasterVolumeLevelScalar(level, None)
            self.logger.info(f"Volume set to {level:.2f}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to set volume: {e}")
            return False
    
    def volume_up(self, increment: float = 0.1) -> bool:
        """
        Increase volume.
        
        Args:
            increment: Volume increment (0.0 to 1.0)
            
        Returns:
            True if successful
        """
        current = self.get_volume()
        if current is None:
            return False
        
        new_level = min(1.0, current + increment)
        return self.set_volume(new_level)
    
    def volume_down(self, decrement: float = 0.1) -> bool:
        """
        Decrease volume.
        
        Args:
            decrement: Volume decrement (0.0 to 1.0)
            
        Returns:
            True if successful
        """
        current = self.get_volume()
        if current is None:
            return False
        
        new_level = max(0.0, current - decrement)
        return self.set_volume(new_level)
    
    def mute(self) -> bool:
        """
        Mute audio.
        
        Returns:
            True if successful
        """
        if not PYCAW_AVAILABLE or self._volume is None:
            return False
        
        try:
            self._volume.SetMute(1, None)
            self.logger.info("Audio muted")
            return True
        except Exception as e:
            self.logger.error(f"Failed to mute: {e}")
            return False
    
    def unmute(self) -> bool:
        """
        Unmute audio.
        
        Returns:
            True if successful
        """
        if not PYCAW_AVAILABLE or self._volume is None:
            return False
        
        try:
            self._volume.SetMute(0, None)
            self.logger.info("Audio unmuted")
            return True
        except Exception as e:
            self.logger.error(f"Failed to unmute: {e}")
            return False
    
    def is_muted(self) -> Optional[bool]:
        """
        Check if audio is muted.
        
        Returns:
            True if muted, False if not muted, None if failed
        """
        if not PYCAW_AVAILABLE or self._volume is None:
            return None
        
        try:
            return self._volume.GetMute()
        except Exception as e:
            self.logger.error(f"Failed to get mute status: {e}")
            return None
    
    def toggle_mute(self) -> bool:
        """
        Toggle mute state.
        
        Returns:
            True if successful
        """
        current_muted = self.is_muted()
        if current_muted is None:
            return False
        
        if current_muted:
            return self.unmute()
        else:
            return self.mute()


class SimpleVolumeController:
    """Fallback volume controller using system commands."""
    
    def __init__(self):
        self.logger = get_logger("elara.simple_volume")
    
    def get_volume(self) -> Optional[float]:
        """Get current volume (simplified)."""
        # This is a placeholder - actual implementation would use Windows API
        return 0.5
    
    def set_volume(self, level: float) -> bool:
        """Set volume (simplified)."""
        # This is a placeholder - actual implementation would use Windows API
        self.logger.info(f"Volume set to {level:.2f} (placeholder)")
        return True
    
    def volume_up(self) -> bool:
        """Increase volume (simplified)."""
        current = self.get_volume()
        return self.set_volume(min(1.0, current + 0.1))
    
    def volume_down(self) -> bool:
        """Decrease volume (simplified)."""
        current = self.get_volume()
        return self.set_volume(max(0.0, current - 0.1))
    
    def mute(self) -> bool:
        """Mute (simplified)."""
        self.logger.info("Audio muted (placeholder)")
        return True
    
    def unmute(self) -> bool:
        """Unmute (simplified)."""
        self.logger.info("Audio unmuted (placeholder)")
        return True
    
    def toggle_mute(self) -> bool:
        """Toggle mute (simplified)."""
        self.logger.info("Mute toggled (placeholder)")
        return True
