"""Entry point for halloween-motion-detector."""

import argparse
import logging
from pathlib import Path

from .audio import AudioPlayer
from .config import load_config
from .detector import Detector
from .video import VideoRecorder


def main() -> None:
    args = _parse_args()
    config = load_config(args.config)
    _setup_logging(config.log_level)

    audio = AudioPlayer(config.mp3_dir, config.volume)
    video = VideoRecorder(config.video_dir, config.camera_vflip, config.camera_hflip)
    detector = Detector(config, audio, video)
    detector.run()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="halloween-motion-detector",
        description="PIR motion sensor triggers spooky MP3 playback and video recording",
    )
    parser.add_argument("--config", type=Path, default=None, help="Path to config.toml")
    return parser.parse_args()


def _setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


if __name__ == "__main__":
    main()
