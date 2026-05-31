"""Tests for audio player module."""

import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Mock pygame before importing audio module
mock_pygame = MagicMock()
sys.modules["pygame"] = mock_pygame
sys.modules["pygame.mixer"] = mock_pygame.mixer


@pytest.fixture
def mp3_dir(tmp_path):
    """Directory with fake MP3 files."""
    for name in ["spooky1.mp3", "thunder.mp3", "scream.mp3"]:
        (tmp_path / name).write_bytes(b"fake")
    return tmp_path


@pytest.fixture
def empty_dir(tmp_path):
    """Empty directory."""
    d = tmp_path / "empty"
    d.mkdir()
    return d


@pytest.fixture(autouse=True)
def reset_mixer():
    """Reset mock state between tests."""
    mock_pygame.mixer.reset_mock()
    mock_pygame.mixer.music.reset_mock()


class TestAudioPlayer:
    def test_discovers_mp3_files(self, mp3_dir):
        from halloween_motion_detector.audio import AudioPlayer

        player = AudioPlayer(mp3_dir, 0.7)
        assert len(player._mp3_files) == 3

    def test_empty_dir_exits(self, empty_dir):
        from halloween_motion_detector.audio import AudioPlayer

        with pytest.raises(SystemExit):
            AudioPlayer(empty_dir, 0.7)

    def test_filters_non_mp3(self, tmp_path):
        (tmp_path / "notes.txt").write_text("not audio")
        (tmp_path / "sound.wav").write_bytes(b"wav")
        (tmp_path / "spooky.mp3").write_bytes(b"mp3")
        from halloween_motion_detector.audio import AudioPlayer

        player = AudioPlayer(tmp_path, 0.7)
        assert len(player._mp3_files) == 1
        assert player._mp3_files[0].name == "spooky.mp3"

    def test_sets_volume(self, mp3_dir):
        from halloween_motion_detector.audio import AudioPlayer

        AudioPlayer(mp3_dir, 0.5)
        mock_pygame.mixer.music.set_volume.assert_called_with(0.5)

    def test_play_random_calls_mixer(self, mp3_dir):
        from halloween_motion_detector.audio import AudioPlayer

        player = AudioPlayer(mp3_dir, 0.7)
        player.play_random()
        mock_pygame.mixer.music.load.assert_called_once()
        mock_pygame.mixer.music.play.assert_called_once()

    def test_stop_calls_mixer(self, mp3_dir):
        from halloween_motion_detector.audio import AudioPlayer

        player = AudioPlayer(mp3_dir, 0.7)
        player.stop()
        mock_pygame.mixer.music.stop.assert_called_once()

    def test_quit_calls_mixer(self, mp3_dir):
        from halloween_motion_detector.audio import AudioPlayer

        player = AudioPlayer(mp3_dir, 0.7)
        player.quit()
        mock_pygame.mixer.quit.assert_called_once()
