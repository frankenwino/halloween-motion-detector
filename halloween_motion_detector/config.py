"""Configuration loading and validation."""

import logging
import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """Application configuration with sensible defaults."""

    pir_pin: int = 4
    cooldown_seconds: int = 15
    volume: float = 0.7
    mp3_dir: Path = field(default_factory=lambda: Path(__file__).parent / "mp3")
    video_dir: Path = field(default_factory=lambda: Path.home() / "halloween-videos")
    camera_vflip: bool = True
    camera_hflip: bool = True
    log_level: str = "INFO"


def load_config(config_path: Path | None = None) -> Config:
    """Load config from TOML file. Returns defaults if file is missing."""
    if config_path is None or not config_path.exists():
        return Config()

    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        logger.error("Invalid config file %s: %s", config_path, e)
        sys.exit(1)

    sensor = data.get("sensor", {})
    audio = data.get("audio", {})
    video = data.get("video", {})
    app = data.get("app", {})

    config = Config(
        pir_pin=sensor.get("pir_pin", Config.pir_pin),
        cooldown_seconds=app.get("cooldown_seconds", Config.cooldown_seconds),
        volume=audio.get("volume", Config.volume),
        mp3_dir=Path(audio["mp3_dir"]) if "mp3_dir" in audio else Config().mp3_dir,
        video_dir=Path(video["output_dir"]) if "output_dir" in video else Config().video_dir,
        camera_vflip=video.get("camera_vflip", Config.camera_vflip),
        camera_hflip=video.get("camera_hflip", Config.camera_hflip),
        log_level=app.get("log_level", Config.log_level),
    )

    _validate(config)
    return config


def _validate(config: Config) -> None:
    """Validate config values, exit on failure."""
    if not 0.0 <= config.volume <= 1.0:
        logger.error("Volume must be 0.0–1.0, got %s", config.volume)
        sys.exit(1)
    if not 0 <= config.pir_pin <= 27:
        logger.error("PIR pin must be 0–27 (BCM), got %s", config.pir_pin)
        sys.exit(1)
