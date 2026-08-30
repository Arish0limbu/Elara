"""
ELARA - Authentication Module
This module handles voice enrollment, speaker verification, and voice profile management.
"""

from .enrollment import VoiceEnrollment, EnrollmentConfig
from .speaker_verification import SpeakerVerifier, VerificationConfig
from .voice_profile import VoiceProfileManager

__all__ = [
    "VoiceEnrollment",
    "EnrollmentConfig",
    "SpeakerVerifier",
    "VerificationConfig",
    "VoiceProfileManager"
]
