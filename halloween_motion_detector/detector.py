"""Motion detection loop orchestration."""

import logging
import time

from gpiozero import MotionSensor

from .audio import AudioPlayer
from .config import Config
from .video import VideoRecorder

logger = logging.getLogger(__name__)


class Detector:
    """Orchestrates motion detection → audio + video → cooldown cycle."""

    def __init__(self, config: Config, audio: AudioPlayer, video: VideoRecorder) -> None:
        self._config = config
        self._audio = audio
        self._video = video
        self._sensor = MotionSensor(config.pir_pin)

    def run(self) -> None:
        """Run the detection loop until KeyboardInterrupt."""
        logger.info("Detector ready on BCM pin %d. Waiting for motion...", self._config.pir_pin)
        try:
            while True:
                self._sensor.wait_for_motion()
                self._on_motion()
                self._sensor.wait_for_no_motion()
                self._on_no_motion()
        except KeyboardInterrupt:
            logger.info("Interrupted. Shutting down...")
            self.shutdown()

    def _on_motion(self) -> None:
        logger.info("Motion detected!")
        self._audio.play_random()
        if self._video.available:
            self._video.start()

    def _on_no_motion(self) -> None:
        logger.info("Motion stopped.")
        if self._video.available:
            self._video.stop()
        logger.info("Cooldown: %d seconds", self._config.cooldown_seconds)
        time.sleep(self._config.cooldown_seconds)

    def shutdown(self) -> None:
        """Clean up all resources."""
        self._audio.stop()
        self._audio.quit()
        self._video.close()
        logger.info("Shutdown complete.")
