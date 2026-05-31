# Requirements — Halloween Motion Detector Modernization

## Goal

Modernize the halloween-motion-detector codebase: fix all known bugs, adopt Python 3.11+ idioms, and produce a maintainable, testable application.

## Target Users

- Raspberry Pi hobbyists running Raspberry Pi OS (Bookworm or later)
- The original author maintaining the project

## Functional Requirements

### FR-1: Motion Detection Loop

The application must detect motion via a PIR sensor and respond by simultaneously playing a random MP3 and recording video until motion stops.

**Acceptance Criteria:**
- Audio playback and video recording run concurrently (not sequentially as in the current broken implementation)
- A configurable cooldown period separates detection cycles
- The loop runs indefinitely until interrupted with Ctrl+C

### FR-2: Audio Playback

The application must play a randomly selected MP3 from a configured sound directory.

**Acceptance Criteria:**
- MP3 files are discovered from a directory relative to the package (not CWD)
- Random selection uses `random.choice` (not manual index math)
- Volume is configurable and within valid range (0.0–1.0)
- If no MP3 files are found, exit with a clear error message

### FR-3: Video Recording

The application must record video for the duration of detected motion.

**Acceptance Criteria:**
- Video files are saved to a configurable output directory
- Output directory is created automatically if missing
- File naming uses timestamp format: `YYYY-MM-DD_HH.MM.SS.h264`
- Camera orientation (vflip/hflip) is configurable

### FR-4: Configuration

The application must support external configuration rather than hardcoded values.

**Acceptance Criteria:**
- Configuration loaded from a YAML or TOML file (with sensible defaults if absent)
- Configurable values: PIR pin, cooldown time, volume, video output directory, MP3 directory, camera flip settings
- CLI argument to specify config file path

### FR-5: Graceful Shutdown

The application must clean up resources on exit.

**Acceptance Criteria:**
- Camera is closed on Ctrl+C or unhandled exception
- Pygame mixer is quit cleanly
- Any in-progress recording is finalized (not corrupted)

## Non-Functional Requirements

### NFR-1: Python 3.11+ Only

- Drop all Python 2.x and Python 3.x < 3.11 support
- Use modern features: type hints, `pathlib`, f-strings, `tomllib` (stdlib in 3.11+)

### NFR-2: Correct Dependencies

- All runtime dependencies declared in project metadata (including `pygame`)
- Use `pyproject.toml` instead of `setup.py`/`setup.cfg`

### NFR-3: Package-Relative Paths

- MP3 directory resolved relative to the installed package, not `os.getcwd()`
- Video output directory defaults to `~/halloween-videos/` (user-writable, not CWD-dependent)

### NFR-4: Error Handling

- Specific exceptions caught and logged (no bare `except`)
- Missing camera: log warning and continue in audio-only mode (play sounds, skip recording)
- Missing PIR sensor: clear error message and exit (core functionality impossible without it)
- Missing audio files: clear error message and exit (core functionality impossible without them)

### NFR-5: Logging

- Use Python `logging` module instead of `print()`
- Configurable log level (default: INFO)
- Timestamped log messages

### NFR-6: Testability

- Application logic separated from hardware I/O (dependency injection or abstraction)
- Test suite using `pytest`
- Minimum 80% coverage on non-hardware code

#### Unit Tests

- **Config loading**: valid TOML parsed correctly, missing file uses defaults, invalid TOML raises clear error
- **MP3 selection**: random choice from directory, empty directory returns None/logs warning, non-MP3 files filtered out
- **Video file naming**: correct timestamp format, output directory created if missing
- **Logging output**: correct messages emitted at appropriate levels

All unit tests run with mocked hardware (no Pi required).

#### Integration Tests

- **Detection loop lifecycle**: simulate motion detected → verify recording starts + audio plays → simulate motion stopped → verify recording stops and cooldown begins
- **Graceful shutdown**: simulate Ctrl+C during active recording → verify camera closed, mixer quit, no corrupted state
- **Config override**: launch with custom config file → verify all settings applied (pin, volume, paths, flip)
- **Missing resources**: missing MP3 directory → warning logged, app continues; missing camera → clear error and exit

Integration tests use mocked `gpiozero` and `picamera2` but exercise the full application flow (wiring between components).

### NFR-7: Documentation (README)

- Replace the existing `README.rst` with a clear `README.md` covering:
  - Project description and hardware requirements (Pi model, PIR sensor, camera, speakers)
  - Wiring diagram or pin reference
  - Installation steps (clone, create venv, install)
  - Configuration (how to create/edit the TOML config file, all available options with defaults)
  - Running the application
  - Running the tests
  - Troubleshooting common issues (no camera detected, no audio output, permission errors)

### NFR-8: Modern Packaging

- `pyproject.toml` as the single source of project metadata
- Remove `setup.py`, `setup.cfg`, `tox.ini`, `MANIFEST.in`
- Entry point defined so the app can be run via `halloween-motion-detector` CLI command

## Constraints

- Must run on Raspberry Pi (ARM, limited resources)
- Hardware dependencies (`gpiozero`, `picamera2`, `pygame`) cannot be fully tested off-device
- Existing MP3 files in `halloween_motion_detector/mp3/` must remain bundled as package data

## Out of Scope

- Web dashboard or remote control
- Multiple camera support
- Streaming video
- Migration to async/await (blocking `wait_for_motion` is appropriate for this use case)
