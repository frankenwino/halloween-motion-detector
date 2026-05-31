"""Tests for detection loop."""

import sys
from unittest.mock import MagicMock, patch, call

import pytest

# Mock hardware dependencies
sys.modules.setdefault("pygame", MagicMock())
sys.modules.setdefault("pygame.mixer", MagicMock())
sys.modules.setdefault("gpiozero", MagicMock())
sys.modules.setdefault("picamera2", MagicMock())
sys.modules.setdefault("picamera2.encoders", MagicMock())

from halloween_motion_detector.config import Config


class TestDetector:
    @pytest.fixture
    def mock_audio(self):
        audio = MagicMock()
        return audio

    @pytest.fixture
    def mock_video(self):
        video = MagicMock()
        video.available = True
        return video

    @pytest.fixture
    def config(self, tmp_path):
        return Config(
            mp3_dir=tmp_path / "mp3",
            video_dir=tmp_path / "videos",
            cooldown_seconds=0,  # No delay in tests
        )

    @patch("halloween_motion_detector.detector.MotionSensor")
    @patch("halloween_motion_detector.detector.time.sleep")
    def test_full_cycle(self, mock_sleep, mock_sensor_cls, config, mock_audio, mock_video):
        from halloween_motion_detector.detector import Detector

        # Sensor triggers motion once then raises KeyboardInterrupt
        sensor_instance = mock_sensor_cls.return_value
        sensor_instance.wait_for_motion.side_effect = [None, KeyboardInterrupt]

        detector = Detector(config, mock_audio, mock_video)
        detector.run()

        mock_audio.play_random.assert_called_once()
        mock_video.start.assert_called_once()
        mock_video.stop.assert_called()
        mock_sleep.assert_called_with(0)

    @patch("halloween_motion_detector.detector.MotionSensor")
    def test_audio_only_mode(self, mock_sensor_cls, config, mock_audio, mock_video):
        from halloween_motion_detector.detector import Detector

        mock_video.available = False
        sensor_instance = mock_sensor_cls.return_value
        sensor_instance.wait_for_motion.side_effect = [None, KeyboardInterrupt]

        with patch("halloween_motion_detector.detector.time.sleep"):
            detector = Detector(config, mock_audio, mock_video)
            detector.run()

        mock_audio.play_random.assert_called_once()
        mock_video.start.assert_not_called()
        mock_video.stop.assert_not_called()

    @patch("halloween_motion_detector.detector.MotionSensor")
    def test_shutdown_cleans_up(self, mock_sensor_cls, config, mock_audio, mock_video):
        from halloween_motion_detector.detector import Detector

        detector = Detector(config, mock_audio, mock_video)
        detector.shutdown()

        mock_audio.stop.assert_called_once()
        mock_audio.quit.assert_called_once()
        mock_video.close.assert_called_once()

    @patch("halloween_motion_detector.detector.MotionSensor")
    def test_keyboard_interrupt_triggers_shutdown(self, mock_sensor_cls, config, mock_audio, mock_video):
        from halloween_motion_detector.detector import Detector

        sensor_instance = mock_sensor_cls.return_value
        sensor_instance.wait_for_motion.side_effect = KeyboardInterrupt

        detector = Detector(config, mock_audio, mock_video)
        detector.run()

        # Shutdown should have been called
        mock_audio.quit.assert_called_once()
        mock_video.close.assert_called_once()
