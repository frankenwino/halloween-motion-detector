"""Tests for configuration loading and validation."""

import pytest
from pathlib import Path

from halloween_motion_detector.config import Config, load_config


class TestConfigDefaults:
    def test_default_values(self):
        config = Config()
        assert config.pir_pin == 4
        assert config.cooldown_seconds == 15
        assert config.volume == 0.7
        assert config.camera_vflip is True
        assert config.camera_hflip is True
        assert config.log_level == "INFO"

    def test_default_mp3_dir_is_package_relative(self):
        config = Config()
        assert config.mp3_dir.name == "mp3"
        assert "halloween_motion_detector" in str(config.mp3_dir)

    def test_default_video_dir_is_home_relative(self):
        config = Config()
        assert config.video_dir == Path.home() / "halloween-videos"


class TestLoadConfig:
    def test_missing_file_returns_defaults(self):
        config = load_config(Path("/nonexistent/config.toml"))
        assert config == Config()

    def test_none_path_returns_defaults(self):
        config = load_config(None)
        assert config == Config()

    def test_valid_toml(self, tmp_path):
        toml_file = tmp_path / "config.toml"
        toml_file.write_text(
            '[sensor]\npir_pin = 17\n\n[audio]\nvolume = 0.5\n\n'
            '[video]\ncamera_vflip = false\n\n[app]\ncooldown_seconds = 30\n'
        )
        config = load_config(toml_file)
        assert config.pir_pin == 17
        assert config.volume == 0.5
        assert config.camera_vflip is False
        assert config.cooldown_seconds == 30

    def test_partial_toml_uses_defaults_for_missing(self, tmp_path):
        toml_file = tmp_path / "config.toml"
        toml_file.write_text("[sensor]\npir_pin = 22\n")
        config = load_config(toml_file)
        assert config.pir_pin == 22
        assert config.volume == 0.7  # default

    def test_invalid_toml_exits(self, tmp_path):
        toml_file = tmp_path / "bad.toml"
        toml_file.write_text("invalid[[[toml")
        with pytest.raises(SystemExit):
            load_config(toml_file)

    def test_volume_out_of_range_exits(self, tmp_path):
        toml_file = tmp_path / "config.toml"
        toml_file.write_text("[audio]\nvolume = 10.0\n")
        with pytest.raises(SystemExit):
            load_config(toml_file)

    def test_pin_out_of_range_exits(self, tmp_path):
        toml_file = tmp_path / "config.toml"
        toml_file.write_text("[sensor]\npir_pin = 99\n")
        with pytest.raises(SystemExit):
            load_config(toml_file)
