"""Shared test fixtures."""

import sys
from unittest.mock import MagicMock

import pytest
from pathlib import Path

# Ensure hardware mocks are available for all test modules
sys.modules.setdefault("pygame", MagicMock())
sys.modules.setdefault("pygame.mixer", MagicMock())
sys.modules.setdefault("gpiozero", MagicMock())
sys.modules.setdefault("picamera2", MagicMock())
sys.modules.setdefault("picamera2.encoders", MagicMock())


@pytest.fixture
def tmp_mp3_dir(tmp_path):
    """Create a temp directory with fake MP3 files."""
    mp3_dir = tmp_path / "mp3"
    mp3_dir.mkdir()
    for name in ["spooky1.mp3", "spooky2.mp3", "thunder.mp3"]:
        (mp3_dir / name).write_bytes(b"fake mp3 data")
    return mp3_dir


@pytest.fixture
def tmp_video_dir(tmp_path):
    """Temp directory for video output."""
    return tmp_path / "videos"


@pytest.fixture
def sample_config(tmp_mp3_dir, tmp_video_dir):
    """Config with temp directories."""
    from halloween_motion_detector.config import Config

    return Config(mp3_dir=tmp_mp3_dir, video_dir=tmp_video_dir, cooldown_seconds=0)
