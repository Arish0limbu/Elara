"""
ELARA - Microphone Handling
This module handles microphone input and audio capture.
"""

import sounddevice as sd
import numpy as np
from typing import Optional, Callable
from threading import Thread, Event
import queue

from app.config.settings import get_settings
from app.config.constants import DEFAULT_SAMPLE_RATE, DEFAULT_CHANNELS, DEFAULT_CHUNK_SIZE
from app.utils.logger import get_logger


class Microphone:
    """Handles microphone input and audio capture."""
    
    def __init__(self):
        self.logger = get_logger("elara.microphone")
        self.settings = get_settings()
        
        # Audio parameters
        self.sample_rate = self.settings.audio.sample_rate
        self.channels = self.settings.audio.channels
        self.chunk_size = self.settings.audio.chunk_size
        
        # Device selection
        self.input_device = self.settings.audio.input_device
        self.output_device = self.settings.audio.output_device
        
        # State
        self._is_recording = False
        self._recording_thread: Optional[Thread] = None
        self._stop_event = Event()
        self._audio_queue = queue.Queue()
        
        # Callback function
        self._audio_callback: Optional[Callable] = None
        
        # Device initialization (with error handling)
        self._devices = {'input': [], 'output': []}
        self._is_available = False
        
        try:
            # Get available devices
            self._devices = self._get_audio_devices()
            self._is_available = True
            self.logger.info("Microphone initialized")
        except Exception as e:
            self.logger.warning(f"Microphone hardware not available: {e}")
            self._is_available = False
    
    def _get_audio_devices(self) -> dict:
        """Get available audio devices."""
        try:
            devices = sd.query_devices()
            input_devices = []
            output_devices = []
            
            for i, device in enumerate(devices):
                if device['max_input_channels'] > 0:
                    input_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_input_channels'],
                        'sample_rate': device['default_samplerate']
                    })
                if device['max_output_channels'] > 0:
                    output_devices.append({
                        'index': i,
                        'name': device['name'],
                        'channels': device['max_output_channels'],
                        'sample_rate': device['default_samplerate']
                    })
            
            self.logger.info(f"Found {len(input_devices)} input devices, {len(output_devices)} output devices")
            return {
                'input': input_devices,
                'output': output_devices
            }
            
        except Exception as e:
            self.logger.error(f"Error getting audio devices: {e}")
            return {'input': [], 'output': []}
    
    def get_input_devices(self) -> list:
        """Get list of available input devices."""
        return self._devices['input']
    
    def get_output_devices(self) -> list:
        """Get list of available output devices."""
        return self._devices['output']
    
    def set_input_device(self, device_name: Optional[str] = None, device_index: Optional[int] = None) -> bool:
        """
        Set the input device.
        
        Args:
            device_name: Device name to select
            device_index: Device index to select
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if device_index is not None:
                if 0 <= device_index < len(self._devices['input']):
                    self.input_device = self._devices['input'][device_index]['name']
                    sd.default.device[0] = device_index
                    self.logger.info(f"Input device set to index {device_index}")
                    return True
            elif device_name:
                for device in self._devices['input']:
                    if device['name'] == device_name:
                        self.input_device = device_name
                        sd.default.device[0] = device['index']
                        self.logger.info(f"Input device set to {device_name}")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error setting input device: {e}")
            return False
    
    def set_output_device(self, device_name: Optional[str] = None, device_index: Optional[int] = None) -> bool:
        """
        Set the output device.
        
        Args:
            device_name: Device name to select
            device_index: Device index to select
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if device_index is not None:
                if 0 <= device_index < len(self._devices['output']):
                    self.output_device = self._devices['output'][device_index]['name']
                    sd.default.device[1] = device_index
                    self.logger.info(f"Output device set to index {device_index}")
                    return True
            elif device_name:
                for device in self._devices['output']:
                    if device['name'] == device_name:
                        self.output_device = device_name
                        sd.default.device[1] = device['index']
                        self.logger.info(f"Output device set to {device_name}")
                        return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error setting output device: {e}")
            return False
    
    def test_microphone(self, duration: float = 3.0) -> Optional[np.ndarray]:
        """
        Test the microphone by recording for a short duration.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Recorded audio data or None if failed
        """
        if not self._is_available:
            self.logger.warning("Microphone not available for testing")
            return None
        
        try:
            self.logger.info(f"Testing microphone for {duration} seconds")
            
            # Record audio
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16'
            )
            sd.wait()
            
            self.logger.info(f"Microphone test completed, captured {len(recording)} samples")
            return recording
            
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return None
    
    def start_recording(self, callback: Optional[Callable] = None) -> bool:
        """
        Start continuous recording.
        
        Args:
            callback: Optional callback function for audio data
            
        Returns:
            True if recording started successfully
        """
        if not self._is_available:
            self.logger.warning("Microphone not available")
            return False
        
        if self._is_recording:
            self.logger.warning("Already recording")
            return False
        
        try:
            self._audio_callback = callback
            self._is_recording = True
            self._stop_event.clear()
            
            # Start recording thread
            self._recording_thread = Thread(target=self._recording_loop, daemon=True)
            self._recording_thread.start()
            
            self.logger.info("Recording started")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start recording: {e}")
            self._is_recording = False
            return False
    
    def _recording_loop(self):
        """Main recording loop."""
        try:
            def audio_callback(indata, frames, time, status):
                """Callback for audio stream."""
                if status:
                    self.logger.warning(f"Audio callback status: {status}")
                
                if self._is_recording:
                    # Put audio data in queue
                    self._audio_queue.put(indata.copy())
                    
                    # Call user callback if provided
                    if self._audio_callback:
                        try:
                            self._audio_callback(indata.copy())
                        except Exception as e:
                            self.logger.error(f"Error in audio callback: {e}")
            
            # Start audio stream
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                callback=audio_callback,
                blocksize=self.chunk_size
            ):
                self.logger.info("Audio stream started")
                
                # Keep recording until stop event
                while not self._stop_event.is_set():
                    self._stop_event.wait(0.1)
                
                self.logger.info("Audio stream stopped")
                
        except Exception as e:
            self.logger.error(f"Error in recording loop: {e}")
            self._is_recording = False
    
    def stop_recording(self) -> bool:
        """
        Stop continuous recording.
        
        Returns:
            True if recording stopped successfully
        """
        if not self._is_recording:
            self.logger.warning("Not recording")
            return False
        
        try:
            self._stop_event.set()
            self._is_recording = False
            
            if self._recording_thread:
                self._recording_thread.join(timeout=2.0)
            
            self.logger.info("Recording stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop recording: {e}")
            return False
    
    def read_audio_chunk(self, timeout: float = 1.0) -> Optional[np.ndarray]:
        """
        Read a chunk of audio from the queue.
        
        Args:
            timeout: Timeout in seconds
            
        Returns:
            Audio chunk or None if timeout
        """
        try:
            return self._audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def record_duration(self, duration: float) -> Optional[np.ndarray]:
        """
        Record audio for a specific duration.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Recorded audio data or None if failed
        """
        try:
            self.logger.info(f"Recording for {duration} seconds")
            
            # Record audio
            recording = sd.rec(
                int(duration * self.sample_rate),
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype='int16'
            )
            sd.wait()
            
            self.logger.info(f"Recording completed, captured {len(recording)} samples")
            return recording
            
        except Exception as e:
            self.logger.error(f"Recording failed: {e}")
            return None
    
    def get_is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording
    
    def is_available(self) -> bool:
        """Check if microphone is available."""
        return self._is_available
    
    def cleanup(self):
        """Cleanup resources."""
        self.stop_recording()
        self.logger.info("Microphone cleaned up")
