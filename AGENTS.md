# AGENTS.md

<!-- tags: navigation, architecture, conventions, gotchas -->

## Project Overview

Raspberry Pi Halloween prop: PIR sensor detects motion → plays random spooky MP3 + records video. Single-module Python app with event-driven blocking loop.

**Entry point**: `halloween_motion_detector/halloween_motion_detector.py` → `main()`

## Directory Map

```
halloween_motion_detector/     # Package
├── halloween_motion_detector.py  # ALL application logic (4 functions)
├── __init__.py                   # Version metadata only
└── mp3/                          # 7 bundled spooky sound effects
tests/                           # Placeholder tests (no real coverage)
docs/                            # Sphinx docs (template stubs)
```

## Key Entry Points

| What | Where |
|------|-------|
| Application logic | `halloween_motion_detector/halloween_motion_detector.py` |
| Package config | `setup.py` |
| Dev automation | `Makefile` (targets: clean, lint, test, docs, release) |
| Multi-env testing | `tox.ini` |

## Architecture

Event-driven infinite loop:
1. `pir.wait_for_motion()` — blocks
2. Start recording + play random MP3
3. `pir.wait_for_no_motion()` — blocks
4. Stop recording, sleep 15s, repeat

Hardware: PIR on BCM pin 4, PiCamera (vflip+hflip), USB speakers.

## Known Bugs and Gotchas

<!-- tags: bugs, gotchas -->

- **Multiprocessing is dead code**: `camera.start_recording(path)` and `mixer.music.play()` execute immediately in a list comprehension. Their return values (`None`) are passed to `Process(target=None)`. The processes do nothing — recording/playback happen synchronously in the main process.
- **pygame missing from install_requires**: `setup.py` declares only `gpiozero` and `picamera`. Installing the package won't pull in pygame.
- **Path resolution uses `os.getcwd()`**: The `mp3/` and `videos/` directories are resolved relative to CWD, not the package install location. Running from a different directory will fail.
- **No error handling**: Missing mp3 directory, empty file list, camera failures, and audio device issues all produce unhandled exceptions.
- **picamera is deprecated**: Replaced by `picamera2` on newer Raspberry Pi OS.

## Patterns That Deviate from Defaults

- Uses `multiprocessing` but doesn't actually achieve parallelism (see bug above)
- Camera is flipped both vertically and horizontally (mounted upside-down)
- Volume hardcoded to 10 (pygame scale 0.0–1.0, so this may be out of range)
- All configuration is hardcoded — no config file, no CLI args, no env vars

## Config Files

| File | Contains |
|------|----------|
| `setup.cfg` | bumpversion config, `[bdist_wheel] universal=1`, flake8 excludes `docs/` |
| `tox.ini` | Test envs: py26, py27, py33, py34, py35, flake8 |
| `Makefile` | Standard cookiecutter-pypackage targets |
| `MANIFEST.in` | Package data inclusion rules |

## Detailed Documentation

See `.agents/summary/index.md` for the full documentation index with architecture, components, interfaces, data models, workflows, and dependency details.

## Custom Instructions
<!-- This section is for human and agent-maintained operational knowledge.
     Add repo-specific conventions, gotchas, and workflow rules here.
     This section is preserved exactly as-is when re-running codebase-summary. -->
