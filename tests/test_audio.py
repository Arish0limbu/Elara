"""
Test audio components for ELARA.
This test verifies that audio components are properly initialized and functional.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import numpy as np


def test_audio_processor():
    """Test audio processor functionality."""
    from app.voice.audio import AudioProcessor
    
    processor = AudioProcessor(sample_rate=16000)
    
    # Test audio conversion
    audio_int16 = np.random.randint(-32768, 32767, 16000, dtype=np.int16)
    audio_float = processor.convert_to_float32(audio_int16)
    assert audio_float.dtype == np.float32
    
    # Test normalization
    normalized = processor.normalize_audio(audio_float)
    assert np.max(np.abs(normalized)) <= 1.0
    
    # Test mono conversion
    stereo_audio = np.column_stack([audio_float, audio_float])
    mono_audio = processor.convert_to_mono(stereo_audio)
    assert len(mono_audio.shape) == 1
    
    print("Audio processor tests passed")


def test_vad():
    """Test voice activity detection."""
    from app.voice.vad import VoiceActivityDetector
    
    vad = VoiceActivityDetector(sample_rate=16000)
    
    # Test with silence
    silence = np.zeros(16000, dtype=np.float32)
    is_speech_silence = vad.is_speech(silence)
    assert not is_speech_silence
    
    # Test with audio signal
    signal = np.random.uniform(-0.5, 0.5, 16000).astype(np.float32)
    is_speech_signal = vad.is_speech(signal)
    # With random noise, it might or might not be detected as speech
    # depending on the threshold
    
    print("VAD tests passed")


def test_stt_initialization():
    """Test speech-to-text initialization."""
    from app.voice.speech_to_text import SpeechToText
    
    stt = SpeechToText()
    
    # Test initialization
    assert stt is not None
    assert stt.model_name == "base"
    assert stt.language == "en"
    
    # Test that model is not loaded by default
    assert not stt.is_loaded()
    
    print("STT initialization tests passed")


def test_tts_initialization():
    """Test text-to-speech initialization."""
    from app.tts.speaker import TextToSpeech
    
    tts = TextToSpeech()
    
    # Test initialization
    assert tts is not None
    assert tts.model_name == "en_US-lessac-medium"
    assert tts.enable_tts == True
    
    # Test model loading
    result = tts.load_model()
    assert result
    assert tts.is_loaded()
    
    print("TTS initialization tests passed")


def test_tts_synthesis():
    """Test text-to-speech synthesis."""
    from app.tts.speaker import TextToSpeech
    
    tts = TextToSpeech()
    tts.load_model()
    
    # Test synthesis
    test_text = "Hello, this is a test."
    audio = tts.synthesize(test_text)
    
    # Check that audio was generated
    assert audio is not None
    assert len(audio) > 0
    assert audio.dtype == np.float32
    
    print("TTS synthesis tests passed")


def test_microphone_initialization():
    """Test microphone initialization."""
    from app.voice.microphone import Microphone
    
    mic = Microphone()
    
    # Test initialization
    assert mic is not None
    assert mic.sample_rate == 16000
    assert mic.channels == 1
    
    # Test device listing
    input_devices = mic.get_input_devices()
    output_devices = mic.get_output_devices()
    
    print(f"Found {len(input_devices)} input devices, {len(output_devices)} output devices")
    
    print("Microphone initialization tests passed")


if __name__ == "__main__":
    # Run tests
    print("Running audio component tests...")
    
    test_audio_processor()
    test_vad()
    test_stt_initialization()
    test_tts_initialization()
    test_tts_synthesis()
    test_microphone_initialization()
    
    print("\nAll audio component tests passed!")
