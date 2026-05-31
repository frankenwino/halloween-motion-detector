"""Audio playback via pygame.mixer."""

import logging
import random
import sys
from pathlib import Path

from pygame import mixer

logger = logging.getLogger(__name__)


class AudioPlayer:
    """Discovers MP3 files and plays them randomly via pygame.mixer."""

    def __init__(self, mp3_dir: Path, volume: float) -> None:
        self._mp3_files = sorted(mp3_dir.glob("*.mp3"))
        if not self._mp3_files:
            logger.critical("No MP3 files found in %s", mp3_dir)
            sys.exit(1)
        mixer.init()
        mixer.music.set_volume(volume)
        logger.info("Audio ready: %d MP3 files, volume %.1f", len(self._mp3_files), volume)

    def play_random(self) -> None:
        """Play a randomly selected MP3."""
        track = random.choice(self._mp3_files)
        logger.info("Playing: %s", track.name)
        mixer.music.load(str(track))
        mixer.music.play()

    def stop(self) -> None:
        """Stop current playback."""
        mixer.music.stop()

    def quit(self) -> None:
        """Release mixer resources."""
        mixer.quit()
