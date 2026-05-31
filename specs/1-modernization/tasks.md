# Implementation Tasks — Halloween Motion Detector Modernization

## Task Group 1: Project Scaffolding

**Dependency:** None (start here)
**Estimate:** 1–2 hours

### Task 1.1: Create `pyproject.toml`

- Define project metadata (name, version, description, author, license, Python ≥3.11)
- Declare runtime dependencies: `gpiozero`, `picamera2`, `pygame`
- Declare dev dependencies: `pytest`, `pytest-cov`, `pytest-mock`
- Configure build backend (`hatchling`)
- Define entry point: `halloween-motion-detector = "halloween_motion_detector.__main__:main"`
- Include `halloween_motion_detector/mp3/` as package data

**Completion criteria:** `pip install -e .` succeeds; `halloween-motion-detector --help` runs.

### Task 1.2: Remove legacy packaging files

- Delete `setup.py`, `setup.cfg`, `tox.ini`, `MANIFEST.in`
- Delete `requirements_dev.txt`

**Completion criteria:** No legacy packaging files remain; install still works via pyproject.toml.

### Task 1.3: Create module skeleton

- Create `halloween_motion_detector/__main__.py` (empty `main()`)
- Create `halloween_motion_detector/config.py` (empty)
- Create `halloween_motion_detector/audio.py` (empty)
- Create `halloween_motion_detector/video.py` (empty)
- Create `halloween_motion_detector/detector.py` (empty)
- Update `halloween_motion_detector/__init__.py` (version only)

**Completion criteria:** Package imports without error; all modules exist.

---

## Task Group 2: Configuration

**Dependency:** Task Group 1
**Estimate:** 1–2 hours

### Task 2.1: Implement `Config` dataclass

- Define `Config` dataclass with all fields and defaults per design.md
- Implement `load_config(path: Path | None) -> Config`:
  - If path is None or file doesn't exist → return defaults
  - If file exists → parse with `tomllib`, override defaults
  - If TOML is invalid → log error, `sys.exit(1)`
- Validate volume is 0.0–1.0, pin is valid BCM number

**Completion criteria:** Unit tests pass for valid, missing, and invalid config files.

### Task 2.2: Implement CLI argument parsing

- In `__main__.py`: use `argparse` for `--config PATH` argument
- Wire `parse_args()` → `load_config()` → pass to components

**Completion criteria:** `halloween-motion-detector --config /path/to/config.toml` parses correctly; `--help` shows usage.

---

## Task Group 3: Audio Player

**Dependency:** Task Group 2
**Estimate:** 1–2 hours

### Task 3.1: Implement `AudioPlayer`

- `__init__`: receive `mp3_dir` and `volume`, discover `.mp3` files, init pygame mixer
- Fatal exit if no MP3 files found
- `play_random()`: `random.choice` from discovered files, load and play
- `stop()`: stop playback
- `quit()`: quit mixer

**Completion criteria:** Unit tests pass with mocked pygame; MP3 discovery works against a temp directory with test files.

---

## Task Group 4: Video Recorder

**Dependency:** Task Group 2
**Estimate:** 1–2 hours

### Task 4.1: Implement `VideoRecorder`

- `__init__`: attempt to init `picamera2`; if import/init fails, set `self.available = False` and log warning
- Apply vflip/hflip configuration
- `start()`: create output dir if needed, generate timestamped filename, start recording
- `stop()`: stop recording (no-op if not recording)
- `close()`: release camera resources

**Completion criteria:** Unit tests pass with mocked picamera2; graceful degradation tested when camera unavailable.

---

## Task Group 5: Detection Loop

**Dependency:** Task Groups 3 and 4
**Estimate:** 1–2 hours

### Task 5.1: Implement `Detector`

- `__init__`: receive `Config`, `AudioPlayer`, `VideoRecorder`; init `MotionSensor(config.pir_pin)`
- `run()`: infinite loop — wait_for_motion → play audio + start video → wait_for_no_motion → stop video → sleep cooldown
- Skip video operations if `video.available is False`
- `shutdown()`: stop video, close camera, quit audio
- Wrap `run()` in try/except `KeyboardInterrupt` → call `shutdown()`

**Completion criteria:** Integration test with mocked sensor/audio/video exercises full cycle.

---

## Task Group 6: Entry Point & Logging

**Dependency:** Task Group 5
**Estimate:** 30 minutes

### Task 6.1: Wire up `__main__.py`

- Parse args → load config → setup logging → instantiate components → call `detector.run()`
- Configure `logging.basicConfig` with level from config, timestamped format

**Completion criteria:** Application starts end-to-end (with mocked hardware in tests).

---

## Task Group 7: Tests

**Dependency:** Task Groups 1–6 (tests written alongside, finalized here)
**Estimate:** 2–3 hours

### Task 7.1: Unit tests

- `tests/test_config.py`: valid TOML, missing file defaults, invalid TOML exits, validation (volume range, pin)
- `tests/test_audio.py`: MP3 discovery, empty dir fatal, play_random calls pygame correctly
- `tests/test_video.py`: filename format, dir creation, camera unavailable degradation
- `tests/conftest.py`: shared fixtures (tmp dirs with fake MP3s, mock objects)

**Completion criteria:** `pytest tests/` passes; coverage ≥80% on config, audio, video modules.

### Task 7.2: Integration tests

- `tests/test_integration.py`:
  - Full detection cycle (mock sensor triggers motion → verify audio + video called → motion stops → verify stop + cooldown)
  - Graceful shutdown (simulate KeyboardInterrupt → verify cleanup)
  - Audio-only mode (camera unavailable → loop still runs with audio)
  - Config override (custom TOML → verify settings propagated)

**Completion criteria:** All integration tests pass with fully mocked hardware.

---

## Task Group 8: Documentation

**Dependency:** Task Groups 1–7
**Estimate:** 1 hour

### Task 8.1: Write `README.md`

- Project description and purpose
- Hardware requirements (Pi model, PIR HC-SR501, Pi Camera, USB speakers)
- Wiring: PIR signal → BCM pin 4, VCC → 5V, GND → GND
- Installation: clone, `python -m venv .venv`, activate, `pip install -e ".[dev]"`
- Configuration: example `config.toml` with all options documented
- Running: `halloween-motion-detector` or `halloween-motion-detector --config path/to/config.toml`
- Running tests: `pytest` and `pytest --cov`
- Troubleshooting section

### Task 8.2: Remove old `README.rst`

- Delete `README.rst`, `CONTRIBUTING.rst`, `AUTHORS.rst`, `HISTORY.rst`
- Remove Sphinx `docs/` directory (replaced by README.md)

**Completion criteria:** README.md is clear, complete, and renders correctly on GitHub.

---

## Task Group 9: Cleanup

**Dependency:** Task Group 8
**Estimate:** 30 minutes

### Task 9.1: Remove old application code

- Delete `halloween_motion_detector/halloween_motion_detector.py` (replaced by new modules)
- Verify package still installs and runs correctly
- Run full test suite one final time

**Completion criteria:** No legacy code remains; all tests pass; `halloween-motion-detector --help` works.

---

## Summary

| Group | Description | Estimate | Depends On |
|-------|-------------|----------|------------|
| 1 | Project scaffolding | 1–2h | — |
| 2 | Configuration | 1–2h | 1 |
| 3 | Audio player | 1–2h | 2 |
| 4 | Video recorder | 1–2h | 2 |
| 5 | Detection loop | 1–2h | 3, 4 |
| 6 | Entry point & logging | 30m | 5 |
| 7 | Tests | 2–3h | 1–6 |
| 8 | Documentation | 1h | 1–7 |
| 9 | Cleanup | 30m | 8 |

**Total estimate:** 10–15 hours
