"""Video recording via picamera2 with graceful degradation."""

import logging
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)


class VideoRecorder:
    """Records video via picamera2. Degrades to no-op if camera unavailable."""

    def __init__(self, video_dir: Path, vflip: bool, hflip: bool) -> None:
        self._video_dir = video_dir
        self._camera = None
        self._encoder_cls = None
        self._recording = False

        try:
            from picamera2 import Picamera2
            from picamera2.encoders import H264Encoder

            self._encoder_cls = H264Encoder
            self._camera = Picamera2()
            config = self._camera.create_video_configuration(
                transform={"vflip": vflip, "hflip": hflip}
            )
            self._camera.configure(config)
            logger.info("Camera initialized (vflip=%s, hflip=%s)", vflip, hflip)
        except (ImportError, RuntimeError) as e:
            logger.warning("Camera unavailable: %s. Running in audio-only mode.", e)
            self._camera = None

    @property
    def available(self) -> bool:
        return self._camera is not None

    def start(self) -> None:
        """Start recording to a timestamped file."""
        if not self.available:
            return
        self._video_dir.mkdir(parents=True, exist_ok=True)
        filename = datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")
        output_path = self._video_dir / filename
        self._camera.start_recording(self._encoder_cls(), str(output_path))
        self._recording = True
        logger.info("Recording: %s", filename)

    def stop(self) -> None:
        """Stop recording (no-op if not recording)."""
        if not self.available or not self._recording:
            return
        self._camera.stop_recording()
        self._recording = False
        logger.info("Recording stopped")

    def close(self) -> None:
        """Release camera resources."""
        if self._camera is not None:
            self.stop()
            self._camera.close()
            logger.info("Camera closed")
