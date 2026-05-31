"""Integration tests — exercise full application flow with mocked hardware."""

import sys
from unittest.mock import MagicMock, patch
from pathlib import Path

import pytest

from halloween_motion_detector.config import Config


class TestIntegrationFullCycle:
    """Test the complete detection → play → record → stop → cooldown cycle."""

    @patch("halloween_motion_detector.detector.MotionSensor")
    @patch("halloween_motion_detector.detector.time.sleep")
    def test_detection_cycle_with_video(self, mock_sleep, mock_sensor_cls, tmp_mp3_dir, tmp_video_dir):
        from halloween_motion_detector.audio import AudioPlayer
        from halloween_motion_detector.video import VideoRecorder
        from halloween_motion_detector.detector import Detector

        config = Config(mp3_dir=tmp_mp3_dir, video_dir=tmp_video_dir, cooldown_seconds=5)

        audio = AudioPlayer(tmp_mp3_dir, 0.7)
        video = VideoRecorder(tmp_video_dir, vflip=True, hflip=True)

        sensor = mock_sensor_cls.return_value
        sensor.wait_for_motion.side_effect = [None, KeyboardInterrupt]

        detector = Detector(config, audio, video)
        detector.run()

        # Audio played
        sys.modules["pygame"].mixer.music.play.assert_called()
        # Cooldown happened
        mock_sleep.assert_called_with(5)

    @patch("halloween_motion_detector.detector.MotionSensor")
    @patch("halloween_motion_detector.detector.time.sleep")
    def test_audio_only_when_camera_unavailable(self, mock_sleep, mock_sensor_cls, tmp_mp3_dir, tmp_video_dir):
        from halloween_motion_detector.audio import AudioPlayer
        from halloween_motion_detector.detector import Detector

        config = Config(mp3_dir=tmp_mp3_dir, video_dir=tmp_video_dir, cooldown_seconds=0)

        audio = AudioPlayer(tmp_mp3_dir, 0.7)

        # Create a video recorder that's unavailable
        video = MagicMock()
        video.available = False

        sensor = mock_sensor_cls.return_value
        sensor.wait_for_motion.side_effect = [None, KeyboardInterrupt]

        detector = Detector(config, audio, video)
        detector.run()

        # Audio still played
        sys.modules["pygame"].mixer.music.play.assert_called()
        # Video never started
        video.start.assert_not_called()


class TestIntegrationGracefulShutdown:
    """Test that Ctrl+C during operation cleans up properly."""

    @patch("halloween_motion_detector.detector.MotionSensor")
    def test_interrupt_during_wait(self, mock_sensor_cls, tmp_mp3_dir, tmp_video_dir):
        from halloween_motion_detector.audio import AudioPlayer
        from halloween_motion_detector.video import VideoRecorder
        from halloween_motion_detector.detector import Detector

        config = Config(mp3_dir=tmp_mp3_dir, video_dir=tmp_video_dir, cooldown_seconds=0)
        audio = AudioPlayer(tmp_mp3_dir, 0.7)
        video = VideoRecorder(tmp_video_dir, vflip=True, hflip=True)

        sensor = mock_sensor_cls.return_value
        sensor.wait_for_motion.side_effect = KeyboardInterrupt

        detector = Detector(config, audio, video)
        detector.run()  # Should not raise

        # Mixer was quit
        sys.modules["pygame"].mixer.quit.assert_called()


class TestIntegrationConfigOverride:
    """Test that config values propagate to components."""

    def test_custom_config_applied(self, tmp_path):
        toml_file = tmp_path / "config.toml"
        mp3_dir = tmp_path / "sounds"
        mp3_dir.mkdir()
        (mp3_dir / "test.mp3").write_bytes(b"fake")

        toml_file.write_text(
            f'[sensor]\npir_pin = 17\n\n'
            f'[audio]\nvolume = 0.3\nmp3_dir = "{mp3_dir}"\n\n'
            f'[app]\ncooldown_seconds = 30\nlog_level = "DEBUG"\n'
        )

        from halloween_motion_detector.config import load_config

        config = load_config(toml_file)
        assert config.pir_pin == 17
        assert config.volume == 0.3
        assert config.cooldown_seconds == 30
        assert config.log_level == "DEBUG"
        assert config.mp3_dir == mp3_dir
