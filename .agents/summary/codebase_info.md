# Codebase Information

## Project Identity

- **Name**: halloween-motion-detector
- **Version**: 0.2.0
- **License**: GPL-3.0-or-later
- **Python**: ≥3.11
- **Author**: Andy Browne

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11+ |
| Motion sensor | gpiozero (MotionSensor) |
| Camera | picamera2 (H264Encoder) |
| Audio | pygame (mixer) |
| Configuration | tomllib (stdlib) |
| CLI | argparse (stdlib) |
| Logging | logging (stdlib) |
| Build | hatchling |
| Testing | pytest, pytest-cov, pytest-mock |

## Directory Structure

```
halloween-motion-detector/
├── halloween_motion_detector/     # Application package
│   ├── __init__.py                # Version metadata
│   ├── __main__.py                # CLI entry point
│   ├── config.py                  # Config dataclass + TOML loading
│   ├── audio.py                   # AudioPlayer (pygame.mixer)
│   ├── video.py                   # VideoRecorder (picamera2)
│   ├── detector.py                # Detection loop orchestration
│   └── mp3/                       # Bundled sound effects (7 files)
├── tests/                         # pytest test suite
│   ├── conftest.py                # Shared fixtures + hardware mocks
│   ├── test_config.py             # Config unit tests
│   ├── test_audio.py              # Audio unit tests
│   ├── test_video.py              # Video unit tests
│   ├── test_detector.py           # Detector unit tests
│   └── test_integration.py        # Integration tests
├── pyproject.toml                 # Project metadata + build config
├── config.example.toml            # Example configuration file
├── README.md                      # User documentation
├── AGENTS.md                      # AI assistant context
├── LICENSE                        # GPL-3.0
└── .agents/summary/               # Generated documentation
```

## Entry Points

| Entry Point | Location | Purpose |
|-------------|----------|---------|
| CLI command | `halloween-motion-detector` | Installed script via pyproject.toml |
| Module execution | `python -m halloween_motion_detector` | Direct module invocation |
| Function | `halloween_motion_detector.__main__:main` | Programmatic entry |

## Target Platform

- Raspberry Pi 3/4/5
- Raspberry Pi OS Bookworm or later
- Hardware: PIR sensor (HC-SR501), Pi Camera module, USB speakers
