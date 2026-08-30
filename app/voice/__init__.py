"""
ELARA - Voice Module
This module handles all voice-related functionality including microphone input, voice activity detection, speech-to-text, and audio processing.
"""

from .microphone import Microphone
from .vad import VoiceActivityDetector, SileroVAD
from .speech_to_text import SpeechToText, StreamingSpeechToText
from .audio import AudioProcessor, create_audio_processor

__all__ = [
    "Microphone",
    "VoiceActivityDetector", 
    "SileroVAD",
    "SpeechToText",
    "StreamingSpeechToText",
    "AudioProcessor",
    "create_audio_processor"
]
