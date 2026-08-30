"""
ELARA - Text-to-Speech Module
This module handles text-to-speech functionality using Piper TTS.
"""

from .speaker import TextToSpeech, StreamingTextToSpeech

__all__ = [
    "TextToSpeech",
    "StreamingTextToSpeech"
]
