# Interfaces

## CLI Interface

```
halloween-motion-detector [--config PATH]
```

| Argument | Type | Default | Description |
|----------|------|---------|-------------|
| `--config` | Path | None | Path to TOML configuration file |

## Configuration Interface (TOML)

```toml
[sensor]
pir_pin = 4              # BCM pin number (0-27)

[audio]
volume = 0.7             # Float 0.0-1.0
mp3_dir = "/path/to/mp3" # Directory containing .mp3 files

[video]
output_dir = "/path/to/videos"  # Video output directory
camera_vflip = true
camera_hflip = true

[app]
cooldown_seconds = 15
log_level = "INFO"       # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## Hardware Interfaces

| Device | Library | Connection | Notes |
|--------|---------|-----------|-------|
| PIR sensor | `gpiozero.MotionSensor` | BCM pin (default 4) | Blocking wait API |
| Pi Camera | `picamera2.Picamera2` | CSI ribbon cable | H264 encoding, optional |
| Speakers | `pygame.mixer` | USB or 3.5mm | Non-blocking playback |

## Internal Component Interfaces

### AudioPlayer

```python
AudioPlayer(mp3_dir: Path, volume: float) -> None  # Fatal if no MP3s
AudioPlayer.play_random() -> None                   # Non-blocking
AudioPlayer.stop() -> None
AudioPlayer.quit() -> None
```

### VideoRecorder

```python
VideoRecorder(video_dir: Path, vflip: bool, hflip: bool) -> None
VideoRecorder.available -> bool        # Property
VideoRecorder.start() -> None          # No-op if unavailable
VideoRecorder.stop() -> None           # No-op if not recording
VideoRecorder.close() -> None
```

### Detector

```python
Detector(config: Config, audio: AudioPlayer, video: VideoRecorder) -> None
Detector.run() -> None                 # Blocks until KeyboardInterrupt
Detector.shutdown() -> None
```
