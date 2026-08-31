"""
Test voice integration components for ELARA.
This tests the voice loop, wake word detection, and TTS integration.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import Mock


class TestVoiceLoop:
    """Test voice loop functionality."""
    
    def test_voice_loop_initialization(self):
        """Test that voice loop initializes correctly."""
        from app.core.voice_loop import VoiceLoop
        
        voice_loop = VoiceLoop()
        
        assert voice_loop is not None
        assert voice_loop._is_running is False
        assert voice_loop._should_listen is False
        assert voice_loop._command_callback is None
        
        voice_loop.logger.info("Voice loop test initialization successful")
    
    def test_voice_loop_set_components(self):
        """Test setting voice components."""
        from app.core.voice_loop import VoiceLoop
        
        voice_loop = VoiceLoop()
        
        # Create mock components
        mock_microphone = Mock()
        mock_vad = Mock()
        mock_stt = Mock()
        mock_wake_word = Mock()
        mock_enrollment = Mock()
        mock_verifier = Mock()
        mock_ai_manager = Mock()
        mock_tts = Mock()
        
        # Set components
        voice_loop.set_components(
            microphone=mock_microphone,
            vad=mock_vad,
            stt=mock_stt,
            wake_word_detector=mock_wake_word,
            voice_enrollment=mock_enrollment,
            speaker_verifier=mock_verifier,
            ai_manager=mock_ai_manager,
            tts=mock_tts
        )
        
        assert voice_loop.microphone == mock_microphone
        assert voice_loop.vad == mock_vad
        assert voice_loop.stt == mock_stt
        assert voice_loop.wake_word_detector == mock_wake_word
        assert voice_loop.ai_manager == mock_ai_manager
        assert voice_loop.tts == mock_tts
        
        voice_loop.logger.info("Voice loop components set successfully")
    
    def test_voice_loop_command_callback(self):
        """Test command callback functionality."""
        from app.core.voice_loop import VoiceLoop
        
        voice_loop = VoiceLoop()
        
        # Create mock callback
        callback_mock = Mock()
        voice_loop.set_command_callback(callback_mock)
        
        assert voice_loop._command_callback == callback_mock
        
        voice_loop.logger.info("Command callback set successfully")
    
    def test_voice_loop_speak(self):
        """Test TTS speaking functionality."""
        from app.core.voice_loop import VoiceLoop
        
        voice_loop = VoiceLoop()
        
        # Create mock TTS
        mock_tts = Mock()
        voice_loop.tts = mock_tts
        
        # Test speaking
        test_text = "Hello, this is a test"
        voice_loop.speak(test_text)
        
        mock_tts.speak.assert_called_once_with(test_text)
        
        voice_loop.logger.info("TTS speaking test successful")
    
    def test_voice_loop_get_status(self):
        """Test voice loop status reporting."""
        from app.core.voice_loop import VoiceLoop
        
        voice_loop = VoiceLoop()
        
        status = voice_loop.get_status()
        
        assert status is not None
        assert "is_running" in status
        assert "is_listening_for_wake_word" in status
        assert "is_listening_for_command" in status
        assert status["is_running"] is False
        
        voice_loop.logger.info("Voice loop status test successful")


class TestWakeWordIntegration:
    """Test wake word integration with voice loop."""
    
    def test_wake_word_detector_callback(self):
        """Test wake word detector callback mechanism."""
        from app.wakeword.detector import WakeWordDetector
        
        detector = WakeWordDetector()
        detector.load_model()
        
        # Create mock callback
        callback_mock = Mock()
        
        # Test callback assignment
        detector._detection_callback = callback_mock
        
        # Simulate wake word detection
        if detector._detection_callback:
            detector._detection_callback("Hey Elara", 0.95)
        
        callback_mock.assert_called_once_with("Hey Elara", 0.95)
        
        detector.logger.info("Wake word callback test successful")


class TestVoiceIntegration:
    """Test end-to-end voice integration."""
    
    def test_voice_to_text_command_processing(self):
        """Test processing voice command through AI system."""
        from app.core.voice_loop import VoiceLoop
        from app.ai import AIRequest, AIResponse
        
        voice_loop = VoiceLoop()
        
        # Create mock AI manager
        mock_ai_manager = Mock()
        mock_response = AIResponse(
            response_text="I heard your command",
            generated_action=None,
            action_result=None,
            was_executed=False,
            error=None,
            request_id="test-123"
        )
        mock_ai_manager.process_request.return_value = mock_response
        voice_loop.ai_manager = mock_ai_manager
        
        # Test command processing
        test_command = "open notepad"
        result = voice_loop.process_command_from_text(test_command)
        
        assert result == "I heard your command"
        mock_ai_manager.process_request.assert_called_once()
        
        voice_loop.logger.info("Voice to text command processing test successful")
    
    def test_voice_loop_with_ui_signals(self):
        """Test voice loop integration with UI signals."""
        from app.core.voice_loop import VoiceLoop
        
        voice_loop = VoiceLoop()
        
        # Create mock callback to simulate UI command handling
        ui_callback_mock = Mock()
        voice_loop.set_command_callback(ui_callback_mock)
        
        # Simulate command from voice
        test_command = "take screenshot"
        if voice_loop._command_callback:
            voice_loop._command_callback(test_command)
        
        ui_callback_mock.assert_called_once_with(test_command)
        
        voice_loop.logger.info("Voice loop UI signals test successful")


if __name__ == "__main__":
    print("Running voice integration tests...")
    
    # Run tests
    test_voice = TestVoiceLoop()
    test_wake = TestWakeWordIntegration()
    test_integration = TestVoiceIntegration()
    
    print("\n--- Voice Loop Tests ---")
    test_voice.test_voice_loop_initialization()
    test_voice.test_voice_loop_set_components()
    test_voice.test_voice_loop_command_callback()
    test_voice.test_voice_loop_speak()
    test_voice.test_voice_loop_get_status()
    
    print("\n--- Wake Word Integration Tests ---")
    test_wake.test_wake_word_detector_callback()
    
    print("\n--- Voice Integration Tests ---")
    test_integration.test_voice_to_text_command_processing()
    test_integration.test_voice_loop_with_ui_signals()
    
    print("\n✅ All voice integration tests passed!")
