# System Design — Halloween Motion Detector Modernization

## Architecture Overview

Single-process, multi-threaded Python application with an event-driven blocking loop. Hardware I/O is abstracted behind protocols (for testability) while keeping the design simple enough for a single-module prop.

```
┌─────────────────────────────────────────────────┐
│                    main()                        │
│  ┌───────────┐  ┌──────────┐  ┌─────────────┐  │
│  │  Config   │  │  Sensor  │  │  Detector   │  │
│  │  Loader   │→ │  (PIR)   │→ │    Loop     │  │
│  └───────────┘  └──────────┘  └──────┬──────┘  │
│                                      │          │
│                         ┌────────────┼────────┐ │
│                         ▼            ▼        │ │
│                   ┌──────────┐ ┌──────────┐   │ │
│                   │  Audio   │ │  Video   │   │ │
│                   │  Player  │ │ Recorder │   │ │
│                   └──────────┘ └──────────┘   │ │
│                   (threading)  (threading)    │ │
└─────────────────────────────────────────────────┘
```

## Module Structure

```
halloween_motion_detector/
├── __init__.py          # Package version
├── __main__.py          # Entry point: parse args, load config, run
├── config.py            # Config dataclass + TOML loading
├── detector.py          # Main detection loop orchestration
├── audio.py             # MP3 discovery and playback
├── video.py             # Video recording management
└── mp3/                 # Bundled sound effects (package data)
```

## Component Design

### Config (`config.py`)

```python
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class Config:
    pir_pin: int = 4
    cooldown_seconds: int = 15
    volume: float = 0.7
    mp3_dir: Path = field(default_factory=lambda: Path(__file__).parent / "mp3")
    video_dir: Path = field(default_factory=lambda: Path.home() / "halloween-videos")
    camera_vflip: bool = True
    camera_hflip: bool = True
    log_level: str = "INFO"
```

- Loaded from TOML via `tomllib` (stdlib 3.11+)
- CLI arg `--config PATH` overrides default location
- Missing config file → use all defaults (no error)
- Invalid TOML → exit with clear parse error

### Audio Player (`audio.py`)

Responsibilities:
- Discover `.mp3` files in configured directory at startup
- Validate at least one MP3 exists (fatal if not)
- Provide `play_random()` method that selects and plays a random sound
- Uses `pygame.mixer` for playback

```python
class AudioPlayer:
    def __init__(self, mp3_dir: Path, volume: float) -> None: ...
    def play_random(self) -> None: ...
    def stop(self) -> None: ...
    def quit(self) -> None: ...
```

### Video Recorder (`video.py`)

Responsibilities:
- Initialize camera (picamera2) with configured orientation
- Start/stop recording to timestamped files
- Handle missing camera gracefully (set `available = False`)

```python
class VideoRecorder:
    def __init__(self, video_dir: Path, vflip: bool, hflip: bool) -> None: ...
    @property
    def available(self) -> bool: ...
    def start(self) -> None: ...
    def stop(self) -> None: ...
    def close(self) -> None: ...
```

### Detector Loop (`detector.py`)

Responsibilities:
- Orchestrate the detection → respond → cooldown cycle
- Run audio and video concurrently using `threading.Thread`
- Handle graceful shutdown via `KeyboardInterrupt`

```python
class Detector:
    def __init__(self, config: Config, audio: AudioPlayer, video: VideoRecorder) -> None: ...
    def run(self) -> None: ...
    def _on_motion(self) -> None: ...
    def _on_no_motion(self) -> None: ...
    def shutdown(self) -> None: ...
```

### Entry Point (`__main__.py`)

```python
def main() -> None:
    config = load_config(parse_args())
    setup_logging(config.log_level)
    audio = AudioPlayer(config.mp3_dir, config.volume)
    video = VideoRecorder(config.video_dir, config.camera_vflip, config.camera_hflip)
    detector = Detector(config, audio, video)
    detector.run()
```

## Concurrency Model

**Threading** (not multiprocessing):
- `audio.play_random()` is non-blocking (pygame handles playback in its own thread internally)
- `video.start()` calls `picamera2.start_recording()` which is also non-blocking
- The main thread blocks on `pir.wait_for_no_motion()` then stops both

This means the detection loop itself is single-threaded — it just kicks off non-blocking I/O operations. No explicit `threading.Thread` needed for the happy path, but the design allows it if future needs arise.

## Data Flow

```
Startup:
  load config → validate MP3s exist → init audio → init video (or mark unavailable) → enter loop

Each cycle:
  wait_for_motion() [blocks]
    → audio.play_random()      (non-blocking, pygame internal thread)
    → video.start()            (non-blocking if available, picamera2 internal)
  wait_for_no_motion() [blocks]
    → video.stop()
    → sleep(cooldown)

Shutdown (Ctrl+C):
  → video.stop() + video.close()
  → audio.quit()
```

## Configuration File Format

`config.toml` (optional, all values have defaults):

```toml
[sensor]
pir_pin = 4

[audio]
volume = 0.7
mp3_dir = "/home/pi/halloween-motion-detector/halloween_motion_detector/mp3"

[video]
output_dir = "/home/pi/halloween-videos"
camera_vflip = true
camera_hflip = true

[app]
cooldown_seconds = 15
log_level = "INFO"
```

## Dependency Injection for Testing

Each component accepts its dependencies via constructor parameters:
- `AudioPlayer` receives `mp3_dir` and `volume` — tests can point to a temp directory
- `VideoRecorder` receives paths and settings — tests can mock `picamera2`
- `Detector` receives `AudioPlayer` and `VideoRecorder` instances — tests inject mocks

No global state. No module-level hardware initialization.

## Technology Stack

| Component | Library | Notes |
|-----------|---------|-------|
| Motion sensor | `gpiozero` | Stable, well-maintained, Pi-native |
| Camera | `picamera2` | Replaces deprecated `picamera`, required on Bookworm |
| Audio | `pygame` | Lightweight mixer, handles MP3 natively |
| Config | `tomllib` (stdlib) | No extra dependency, Python 3.11+ |
| CLI args | `argparse` (stdlib) | Single `--config` argument |
| Logging | `logging` (stdlib) | Standard Python logging |
| Testing | `pytest` + `pytest-cov` | Dev dependency only |
| Packaging | `hatchling` or `setuptools` | Build backend for pyproject.toml |

## Error Handling Strategy

| Scenario | Behavior |
|----------|----------|
| No MP3 files found | Log CRITICAL, `sys.exit(1)` |
| No PIR sensor | Log CRITICAL, `sys.exit(1)` |
| No camera | Log WARNING, continue audio-only |
| Invalid config TOML | Log ERROR with parse details, `sys.exit(1)` |
| Camera fails mid-recording | Log ERROR, continue loop (audio still works) |
| Audio device unavailable | Log CRITICAL, `sys.exit(1)` |

## File Output

- Videos: `{video_dir}/YYYY-MM-DD_HH.MM.SS.h264`
- Video directory created on first recording if missing
- No automatic cleanup/rotation (out of scope)

## Security Considerations

- No network access, no external APIs
- Runs as local user (no root required if user is in `video` and `gpio` groups)
- Config file is local, no secrets involved
