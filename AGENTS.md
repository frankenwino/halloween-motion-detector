# AGENTS.md

<!-- tags: navigation, architecture, conventions -->

## Project Overview

Raspberry Pi Halloween prop: PIR sensor detects motion → plays random spooky MP3 + records video. Python 3.11+ with event-driven blocking loop and graceful degradation (audio-only if no camera).

**Entry point**: `halloween_motion_detector/__main__.py` → `main()`
**CLI**: `halloween-motion-detector [--config PATH]`

## Directory Map

```
halloween_motion_detector/     # Application package
├── __main__.py                # Entry: parse args → config → components → run
├── config.py                  # Config dataclass + TOML loading + validation
├── audio.py                   # AudioPlayer: MP3 discovery + pygame playback
├── video.py                   # VideoRecorder: picamera2, graceful degradation
├── detector.py                # Detection loop orchestration
└── mp3/                       # 7 bundled sound effects
tests/                         # pytest suite (33 tests, 100% coverage)
├── conftest.py                # Shared fixtures + hardware mocks
├── test_config.py             # Config unit tests
├── test_audio.py              # Audio unit tests
├── test_video.py              # Video unit tests
├── test_detector.py           # Detector unit tests
└── test_integration.py        # Full-flow integration tests
```

## Key Entry Points

| What | Where |
|------|-------|
| Application logic | `halloween_motion_detector/__main__.py` |
| Configuration | `halloween_motion_detector/config.py` → `Config` dataclass |
| Detection loop | `halloween_motion_detector/detector.py` → `Detector.run()` |
| Package config | `pyproject.toml` |
| Example config | `config.example.toml` |

## Architecture

Event-driven infinite loop with non-blocking I/O:
1. `sensor.wait_for_motion()` — blocks
2. `audio.play_random()` — non-blocking (pygame internal thread)
3. `video.start()` — non-blocking (picamera2 internal), skipped if unavailable
4. `sensor.wait_for_no_motion()` — blocks
5. `video.stop()`
6. `time.sleep(cooldown_seconds)`
7. Repeat

No explicit threading/multiprocessing. Both pygame and picamera2 handle background execution internally.

## Degradation Behavior

| Missing | Result |
|---------|--------|
| Camera | WARNING, continues audio-only |
| MP3 files | CRITICAL, `sys.exit(1)` |
| PIR sensor | RuntimeError on init, exits |

## Patterns That Deviate from Defaults

- **Lazy import of picamera2** inside `VideoRecorder.__init__()` — allows graceful degradation without try/except at module level
- **Camera orientation flipped** (vflip + hflip) — hardware mounted upside-down, configurable via TOML
- **Package-relative MP3 path** — `Path(__file__).parent / "mp3"` not CWD
- **Video output in home dir** — `~/halloween-videos/` not package directory

## Config System

TOML file with 4 sections (`[sensor]`, `[audio]`, `[video]`, `[app]`). All fields optional — defaults used for missing values. Validation: volume 0.0–1.0, pin 0–27. Invalid TOML or out-of-range values → fatal exit.

## Testing

All hardware mocked at `sys.modules` level (pygame, gpiozero, picamera2 not installed in dev). Tests run anywhere without Pi hardware.

## Detailed Documentation

See `.agents/summary/index.md` for the full documentation index with architecture, components, interfaces, data models, workflows, and dependency details.

## Custom Instructions
<!-- This section is for human and agent-maintained operational knowledge.
     Add repo-specific conventions, gotchas, and workflow rules here.
     This section is preserved exactly as-is when re-running codebase-summary. -->
