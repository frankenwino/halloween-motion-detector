"""Tests for video recorder module."""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from datetime import datetime


# Mock picamera2 before importing video module
mock_picamera2 = MagicMock()
sys.modules["picamera2"] = mock_picamera2
sys.modules["picamera2.encoders"] = mock_picamera2.encoders


class TestVideoRecorderUnavailable:
    def test_degrades_when_import_fails(self, tmp_path):
        """When picamera2 raises ImportError, available is False."""
        with patch.dict(sys.modules, {"picamera2": None, "picamera2.encoders": None}):
            # Force reimport
            if "halloween_motion_detector.video" in sys.modules:
                del sys.modules["halloween_motion_detector.video"]
            from halloween_motion_detector.video import VideoRecorder

            recorder = VideoRecorder(tmp_path, vflip=True, hflip=True)
            assert recorder.available is False

    def test_start_noop_when_unavailable(self, tmp_path):
        with patch.dict(sys.modules, {"picamera2": None, "picamera2.encoders": None}):
            if "halloween_motion_detector.video" in sys.modules:
                del sys.modules["halloween_motion_detector.video"]
            from halloween_motion_detector.video import VideoRecorder

            recorder = VideoRecorder(tmp_path, vflip=True, hflip=True)
            recorder.start()  # Should not raise
            assert not (tmp_path).exists() or not list(tmp_path.iterdir())

    def test_stop_noop_when_unavailable(self, tmp_path):
        with patch.dict(sys.modules, {"picamera2": None, "picamera2.encoders": None}):
            if "halloween_motion_detector.video" in sys.modules:
                del sys.modules["halloween_motion_detector.video"]
            from halloween_motion_detector.video import VideoRecorder

            recorder = VideoRecorder(tmp_path, vflip=True, hflip=True)
            recorder.stop()  # Should not raise


class TestVideoRecorderAvailable:
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        mock_picamera2.reset_mock()
        mock_picamera2.Picamera2.reset_mock()
        mock_picamera2.encoders.H264Encoder.reset_mock()

    def test_available_when_camera_present(self, tmp_path):
        from halloween_motion_detector.video import VideoRecorder

        recorder = VideoRecorder(tmp_path, vflip=True, hflip=True)
        assert recorder.available is True

    def test_start_creates_directory(self, tmp_path):
        video_dir = tmp_path / "videos"
        from halloween_motion_detector.video import VideoRecorder

        recorder = VideoRecorder(video_dir, vflip=True, hflip=True)
        recorder.start()
        assert video_dir.exists()

    def test_filename_format(self, tmp_path):
        from halloween_motion_detector.video import VideoRecorder

        recorder = VideoRecorder(tmp_path, vflip=True, hflip=True)
        recorder.start()
        # Verify start_recording was called with a path matching the format
        call_args = mock_picamera2.Picamera2().start_recording.call_args
        path_arg = call_args[0][1]
        filename = Path(path_arg).name
        # Should match YYYY-MM-DD_HH.MM.SS.h264
        assert filename.endswith(".h264")
        # Parse the timestamp part
        stem = filename.removesuffix(".h264")
        datetime.strptime(stem, "%Y-%m-%d_%H.%M.%S")

    def test_stop_noop_when_not_recording(self, tmp_path):
        from halloween_motion_detector.video import VideoRecorder

        recorder = VideoRecorder(tmp_path, vflip=True, hflip=True)
        recorder.stop()  # Should not raise, not recording

    def test_close_releases_camera(self, tmp_path):
        from halloween_motion_detector.video import VideoRecorder

        recorder = VideoRecorder(tmp_path, vflip=True, hflip=True)
        recorder.close()
        mock_picamera2.Picamera2().close.assert_called()
